"""Lokálna analýza desiatich textov záveru analytickej filozofie.

Vyhľadávanie a kontrola integrity sú plne offline. Volanie API je iba v app.py.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
import json
import math
from pathlib import Path
import re
import unicodedata
from zoneinfo import ZoneInfo

MAX_TURNS = 20
CONTENT_TYPES = frozenset({'paragraph', 'quotation', 'list_item'})
OTHER_TYPES = frozenset({'heading', 'note', 'bibliography', 'front_matter', 'translator_credit'})
TOKEN_PATTERN = re.compile(r'[^\W_]+', re.UNICODE)
ID_PATTERN = re.compile(r'ZAF\d{2}-\d{4}')
STOPWORDS = set('a aj ale ako ani aby by byť bol bola boli čo či do jeho jej ešte i iba je jej k kde keď ktorá ktorý ktoré kto len má majú medzi na nad ne nie od o po pod pre pri preto sa si som sú s t tak tam ten tento tieto to tomu tú v vo z za že že je the and from with which what how are of is or for'.split())
TITLES = ['Co ještě zbývá z analytické filosofie?', 'Súčasnosť a budúcnosť', 'Vzostup a pád analytickej filozofie', 'Kto sa chystá zabiť analytickú filozofiu?', 'Prečo vo filozofii nedochádza k väčšiemu pokroku?', 'Postanalytická filosofie', 'Kríza identity analytickej filozofie', 'Filozofický pokrok: Na obranu rozumného optimizmu – Úvod', 'Dnes a zajtra', 'Analytická filozofia na začiatku nového tisícročia']

class CorpusError(ValueError):
    """Súbor JSON je neúplný alebo v neznámom formáte."""


def load_corpus(path: str | Path) -> dict:
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding='utf-8-sig'))
    except FileNotFoundError as e:
        raise CorpusError(f'Chýba {path.name}. Nahrajte kompletný projekt.') from e
    except json.JSONDecodeError as e:
        raise CorpusError(f'Chybné dáta JSON na riadku {e.lineno}: {e.msg}.') from e
    if not isinstance(data,dict) or not isinstance(data.get('works'),list) or not isinstance(data.get('records'),list):
        raise CorpusError('Korpus musí obsahovať zoznamy works a records.')
    works, records = data['works'], data['records']
    if len(works)!=10 or [w.get('title') for w in works]!=TITLES:
        raise CorpusError('Očakávalo sa desať textov v pôvodnom poradí.')
    ids={w.get('id') for w in works}
    if ids!={'ZAF%02d'%i for i in range(1,11)}:
        raise CorpusError('Neplatné identifikátory desiatich textov.')
    for w in works:
        if not isinstance(w.get('author'),str) or not w['author'].strip():
            raise CorpusError(f'Štúdia {w["id"]} nemá autora.')
        if w.get('language') not in ('sk','cs'):
            raise CorpusError(f'Štúdia {w["id"]} má neznámy jazyk.')
    seen=set(); counts=Counter()
    for r in records:
        if not isinstance(r,dict): raise CorpusError('Záznam musí byť objekt.')
        rid=r.get('id')
        if not isinstance(rid,str) or not ID_PATTERN.fullmatch(rid) or rid in seen:
            raise CorpusError(f'Neplatné alebo duplicitné ID: {rid}')
        seen.add(rid)
        if r.get('work_id') not in ids or not rid.startswith(r['work_id']+'-'):
            raise CorpusError(f'Záznam {rid} má neplatné dielo.')
        if r.get('type') not in CONTENT_TYPES|OTHER_TYPES:
            raise CorpusError(f'Záznam {rid} má neznámy typ.')
        if not isinstance(r.get('text'),str) or not r['text'].strip():
            raise CorpusError(f'Záznam {rid} nemá text.')
        counts[r['work_id']]+=1
    for w in works:
        expected=[f'{w["id"]}-{n:04d}' for n in range(1,counts[w['id']]+1)]
        actual=[r['id'] for r in records if r['work_id']==w['id']]
        if expected!=actual:
            raise CorpusError(f'Chýba poradie záznamov diela {w["id"]}.')
        if not any(r['work_id']==w['id'] and r['type'] in CONTENT_TYPES for r in records):
            raise CorpusError(f'Štúdia {w["id"]} nemá obsah.')
    if len(records)!=1024:
        raise CorpusError(f'Neúplný korpus: {len(records)} záznamov, očakáva sa 1024.')
    return data


def normalize(value: str) -> str:
    norm=unicodedata.normalize('NFKD',str(value).casefold())
    return ''.join(ch for ch in norm if not unicodedata.combining(ch))


def terms(value: str) -> list[str]:
    words=[s for s in TOKEN_PATTERN.findall(normalize(value)) if len(s)>2 and s not in STOPWORDS]
    return [s[:7] if len(s)>8 else s for s in words]


def source_label(row: dict) -> str:
    parts=[row['author'],f'„{row["work_title"]}“']
    if row.get('section'): parts.append('oddiel '+str(row['section']))
    if row.get('source_paragraph') is not None:
        parts.append('pracovný odsek '+str(row['source_paragraph']))
    if row['type']=='quotation': parts.append('citovaná pasáž')
    if row.get('chapter_number'): parts.append('kapitola '+str(row['chapter_number']))
    parts.append('ID '+row['id'])
    return ' · '.join(parts)


class PassageIndex:
    """Ľahký BM25 index s možnosťou vyhľadávať len vo vymedzenom súbore textov."""
    def __init__(self,data:dict):
        self.works={w['id']:w for w in data['works']}
        self.rows=[r for r in data['records'] if r['type'] in CONTENT_TYPES]
        self.position={r['id']:i for i,r in enumerate(self.rows)}
        self.docs=[Counter(terms(' '.join([r['text'],r['author'],r['work_title'],str(r.get('section') or '')]))) for r in self.rows]
        self.docfreq=Counter(term for doc in self.docs for term in doc)
        self.lengths=[sum(doc.values()) for doc in self.docs]
        self.avg_length=sum(self.lengths)/max(1,len(self.lengths))

    def find(self,query:str,*,work_ids:set[str]|None=None,focus_id:str|None=None,limit:int=12) -> list[dict]:
        q=set(terms(query))
        n=len(self.rows)
        scored=[]
        norm_query=normalize(query)
        for i,r in enumerate(self.rows):
            if work_ids is not None and r['work_id'] not in work_ids: continue
            doc=self.docs[i]
            score=0.0
            for term in q:
                if term not in doc: continue
                tf=doc[term]
                idf=math.log(1+(n-self.docfreq[term]+.5)/(self.docfreq[term]+.5))
                score+=idf*tf*2.2/(tf+1.2*(.25+.75*self.lengths[i]/max(1,self.avg_length)))
            # Bez mena v dotaze sa dielo nenaťahuje umelo do rebríčka.
            if normalize(r['author']) in norm_query or normalize(r['author'].split()[-1]) in norm_query:
                score+=3
            if focus_id==r['id']: score+=1e5
            if score>0: scored.append((score,i))
        ranked=sorted(scored,key=lambda x:(-x[0],x[1]))
        if work_ids is None or len(work_ids)>1:
            # Ensure a cross-text query isn't monopolized by one longer study.
            from collections import defaultdict, deque
            groups=defaultdict(deque)
            for score,i in ranked:
                groups[self.rows[i]['work_id']].append(i)
            sorted_works=sorted(groups,key=lambda wid: next(
                -score for score,i in ranked if self.rows[i]['work_id']==wid))
            selected=[]
            while len(selected)<limit and any(groups.values()):
                for wid in sorted_works:
                    if groups[wid] and len(selected)<limit:
                        selected.append(groups[wid].popleft())
        else:
            selected=[i for _,i in ranked[:limit]]
        if focus_id in self.position:
            k=self.position[focus_id];r=self.rows[k]
            if work_ids is None or r['work_id'] in work_ids:
                near=[i for i in [k,k-1,k+1] if 0<=i<n and self.rows[i]['work_id']==r['work_id']]
                selected=list(dict.fromkeys(near+selected))[:limit]
        return [self.rows[i] for i in selected]


def evidence(index:PassageIndex,query:str,*,work_ids:set[str]|None=None,focus_id:str|None=None,limit:int=12,char_budget:int=16000)->str:
    hits=index.find(query,work_ids=work_ids,focus_id=focus_id,limit=limit)
    if not hits:return 'V korpuse sa nenašiel dostatočne relevantný podklad. Nepodsúvaj autorom nedoložené postoje.'
    parts=[];remaining=char_budget
    for r in hits:
        label=f'[PRIMÁRNY PODKLAD: {source_label(r)}]\n'
        room=min(4600 if r['id']==focus_id else 1950,remaining-len(label)-50)
        if room<180:break
        s=r['text']
        if len(s)>room:
            cut=s[:room].rsplit(' ',1)[0]
            s=cut+' […] [výňatok skrátený]'
        parts.append(label+s)
        remaining-=len(label)+len(s)+2
    return '\n\n'.join(parts)+'\n\nMetadáta: source_paragraph je číslo pracovného odseku DOCX, NIE pôvodná tlačená strana či autorský paragraf.'


def api_error(exc:Exception,model:str)->str:
    code=getattr(exc,'code',None)
    message=str(exc).lower()
    if code==429 or '429' in message or 'resource_exhausted' in message:
        return f'Gemini (429): Nedostupná alebo vyčerpaná kvóta pre {model}. Otázka sa nezapočítala.'
    if code==503 or '503' in message or 'unavailable' in message:
        return 'Gemini (503) je momentálne nedostupné. Otázku možno bezpečne zopakovať.'
    if code==404 or '404' in message or 'not_found' in message:
        return f'Model {model} sa nenašiel (404). Overte GEMINI_MODEL a dostupnosť v AI Studio.'
    if code in (401,403) or '401' in message or '403' in message:
        return 'Gemini odmietlo prístup (401/403). Skontrolujte API kľúč a projekt.'
    if any(s in message for s in ['timeout','timed out','deadline exceeded']):
        return 'Gemini neodpovedalo v časovom limite. Otázka sa nezapočítala; možno ju zopakovať.'
    return f'Volanie modelu sa nepodarilo dokončiť ({type(exc).__name__}). Pozrite serverové logy.'


def transcript(messages:list[dict],name:str,scope:str,model:str,session_id:str,when:datetime|None=None)->str:
    when=when or datetime.now(ZoneInfo('Europe/Bratislava'))
    lines=['ZÁVER – SÚČASNOSŤ A BUDÚCNOSŤ ANALYTICKEJ FILOZOFIE — SOKRATOVSKÝ DIALÓG','='*68,
        'Študent/ka: '+(name.strip() or '(neuvedené)'),
        'Dátum: '+when.strftime('%d. %m. %Y %H:%M %Z'),
        'Rozsah: '+scope,'Model: '+model,'Relácia: '+session_id,
        'Počet študentských vstupov: '+str(sum(m['role']=='user' for m in messages))+'/'+str(MAX_TURNS),'','PREPIS','='*68,'']
    for m in messages:
        lines.extend(['ŠTUDENT:' if m['role']=='user' else 'AI TÚTOR:',m['content'],''])
    return '\n'.join(lines)
