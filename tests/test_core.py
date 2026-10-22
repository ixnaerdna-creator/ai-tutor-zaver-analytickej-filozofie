"""Offline quality checks for the ten texts, source isolation and 20-turn dialogue."""
from pathlib import Path
import json
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tutor_core import (
    load_corpus, CorpusError, PassageIndex, CONTENT_TYPES,
    MAX_TURNS, source_label, evidence, transcript, normalize, api_error,
)
CORPUS_NAME='zaver_sucasnost_a_buducnost_analytickej_filozofie_texty.json'

@pytest.fixture(scope='module')
def corpus():return load_corpus(ROOT/CORPUS_NAME)

@pytest.fixture(scope='module')
def index(corpus):return PassageIndex(corpus)

def test_works_unique_in_source_order(corpus):
    works=corpus['works']
    assert len(works)==len({w['author'] for w in works})==10
    assert [w['id'] for w in works]==[f'ZAF{i:02d}' for i in range(1,11)]
    assert [w['order'] for w in works]==list(range(1,11))

def test_all_records_preserved(corpus):
    rows=corpus['records']
    assert len(rows)==1024
    assert len({r['id'] for r in rows})==1024
    assert {r['work_id'] for r in rows}=={w['id'] for w in corpus['works']}
    assert sum(len(r['text']) for r in rows)>500000

def test_language(corpus):
    assert [w['language'] for w in corpus['works']].count('cs')==2
    assert [w['language'] for w in corpus['works']].count('sk')==8
    for w in corpus['works']:
        assert any(r['type'] in CONTENT_TYPES for r in corpus['records'] if r['work_id']==w['id'])

def test_notes_bibliography_available_not_in_evidence(corpus,index):
    rows=corpus['records']
    assert sum(r['type']=='note' for r in rows)==111
    assert sum(r['type']=='bibliography' for r in rows)==132
    assert not any(r['type'] in {'note','bibliography','front_matter'} for r in index.rows)

def test_stoljar_sections(corpus):
    rows=[r for r in corpus['records'] if r['work_id']=='ZAF08' and r['type']=='heading']
    assert [r['text'] for r in rows if r['text'].startswith('§ ')]==[f'§ {i}' for i in range(1,11)]

def test_chalmers_navigation_levels(corpus):
    headings=[r for r in corpus['records'] if r['work_id']=='ZAF05' and r['type']=='heading']
    assert {f'{i}. ' for i in range(1,8)}.issubset({r['text'][:3] for r in headings})
    for row in headings:
        if row['text'].startswith(tuple(f'{i}. ' for i in range(1,8))):
            assert row['section']==row['text']
            assert row['subsection'] is None

def test_book_excerpts(corpus):
    data={w['id']:w for w in corpus['works']}
    assert data['ZAF02']['original_chapter_number']==9
    assert data['ZAF07']['original_chapter_number']==1
    assert data['ZAF08']['original_chapter_number']==1
    assert data['ZAF09']['original_chapter_number']==9
    assert data['ZAF01']['language']=='cs'

def test_quote_and_work_attribution(index):
    assert len([r for r in index.rows if r['type']=='quotation'])==41
    assert 'citovaná pasáž' in source_label(next(r for r in index.rows if r['type']=='quotation'))

def test_focused_row_first(index):
    row=next(r for r in index.rows if r['work_id']=='ZAF05')
    matches=index.find('pokrok vo filozofii',work_ids={'ZAF05'},focus_id=row['id'])
    assert matches[0]['id']==row['id']
    assert all(m['work_id']=='ZAF05' for m in matches)

def test_scope_restriction(index):
    for scope in [{'ZAF01'},{'ZAF02','ZAF09'},{'ZAF05','ZAF08'}]:
        matches=index.find('filozofický pokrok',work_ids=scope,limit=12)
        assert matches and all(m['work_id'] in scope for m in matches)

def test_real_topic_cross_works(index):
    hits=index.find('analytická filozofia',limit=25)
    assert len({row['work_id'] for row in hits})>=3

def test_diacritics():
    assert normalize('SÚČASNOSŤ a BUDÚCNOSŤ')=='sucasnost a buducnost'

def test_citations_no_fake_page(index):
    row=index.rows[0]
    assert 'pracovný odsek' in source_label(row)
    assert 'strana' not in source_label(row)
    txt=evidence(index,'analytická filozofia pokrok',limit=12,char_budget=3000)
    assert '[PRIMÁRNY PODKLAD:' in txt
    assert len(txt)<4000

def test_transcript():
    assert MAX_TURNS==20
    msgs=[{'role':'user','content':'Čo je pokrok?'},{'role':'assistant','content':'Ako by ste ho vymedzili?'}]
    exp=transcript(msgs,'Študent','všetky texty','gemini-test','abc123')
    assert 'Čo je pokrok?' in exp and '1/20' in exp and 'abc123' in exp

def test_api_errors_are_retriable():
    assert '429' in api_error(Exception('429'),'model')
    assert '503' in api_error(Exception('503'),'model')
    assert '404' in api_error(Exception('404'),'model')
    assert 'časov' in api_error(Exception('ReadTimeout'),'model')

def test_reject_missing_record(tmp_path,corpus):
    data=json.loads(json.dumps(corpus,ensure_ascii=False))
    data['records'].pop()
    path=tmp_path/'broken.json';path.write_text(json.dumps(data,ensure_ascii=False),encoding='utf8')
    with pytest.raises(CorpusError):load_corpus(path)

def test_reject_cross_work_record(tmp_path,corpus):
    data=json.loads(json.dumps(corpus,ensure_ascii=False))
    data['records'][0]['work_id']='ZAF10'
    path=tmp_path/'bad.json';path.write_text(json.dumps(data,ensure_ascii=False),encoding='utf8')
    with pytest.raises(CorpusError):load_corpus(path)
