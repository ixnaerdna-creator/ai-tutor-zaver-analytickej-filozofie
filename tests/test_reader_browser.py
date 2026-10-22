"""Chromium tests for the real JS reader; no API key required."""
import ast
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CORPUS='zaver_sucasnost_a_buducnost_analytickej_filozofie_texty.json'

def reader_assets():
    source=ast.parse((ROOT/'book_reader.py').read_text(encoding='utf8'))
    result={}
    for stmt in source.body:
        if isinstance(stmt,ast.Assign):
            for target in stmt.targets:
                if isinstance(target,ast.Name) and target.id in {'READER_HTML','READER_CSS','READER_JS'}:
                    result[target.id]=ast.literal_eval(stmt.value)
    return result

def run_work(work_id,expect=None,term='filozof',jump_to=None):
    data=json.loads((ROOT/CORPUS).read_text(encoding='utf8'))
    rows=[r for r in data['records'] if r['work_id']==work_id]
    assets=reader_assets()
    js=assets['READER_JS'].replace('export default function(', 'function mountReader(',1)
    payload=json.dumps({'paragraphs':rows,'selected':None,'jumpToId':jump_to,
          'bookKey':work_id+'-test'},ensure_ascii=False).replace('</','<\\/')
    html=(f'<!doctype html><html lang="sk"><head><meta charset="utf-8">'
          f'<style>{assets["READER_CSS"]}</style></head>'
          f'<body style="width:1100px;margin:0">{assets["READER_HTML"]}'
          f'<script>{js}\nwindow.selection=null;mountReader({{parentElement:document,data:{payload},'
          'setTriggerValue:(k,v)=>window.selection=v});</script></body></html>')
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1150,'height':900})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(html,wait_until='domcontentloaded')
        assert not errors,errors
        scroll=page.locator('#af-scroll')
        top=scroll.evaluate('(el)=>el.scrollHeight-el.clientHeight')
        assert top>200,(work_id,top)
        if jump_to:
            assert scroll.evaluate('(el)=>el.scrollTop')>50
            assert page.locator('.af-selected').count()>=1
        page.locator('#af-end-btn').click()
        assert abs(scroll.evaluate('(el)=>el.scrollTop')-top)<3,work_id
        assert page.locator('#af-bottom').is_visible()
        page.locator('#af-start').click()
        assert scroll.evaluate('(el)=>el.scrollTop')<3
        if expect:
            opts=page.locator('#af-chapters option').all_text_contents()
            assert expect in opts,(work_id,opts)
            page.locator('#af-chapters').select_option(label=expect)
            assert scroll.evaluate('(el)=>el.scrollTop')>0
        page.locator('#af-search').fill(term)
        assert page.locator('.af-hit').count()==1,(work_id,'find')
        page.locator('#af-next').click()
        assert page.locator('.af-hit').count()==1,(work_id,'next')
        target=[r for r in rows if r['type'] in {'paragraph','quotation','list_item'}][-1]
        page.locator('.af-paragraph').last.click()
        assert page.evaluate('window.selection')['id']==target['id']
        assert not errors,errors
        browser.close()
    return work_id,len(rows),top

def test_all():
    arguments={
        'ZAF01':('VIII. Co má zůstat a s čím pryč?', 'filosofie'),
        'ZAF02':('3. Kam smeruje analytická filozofia?', 'relativizmus'),
        'ZAF03':('Poznámky','analytick'),
        'ZAF04':('Systém referencie verzus systém identifikácie','wittgenstein'),
        'ZAF05':('7. Vyhliadky ďalšieho pokroku','pokrok'),
        'ZAF06':('Kontinentální filosofie: od klatby k dialogu?','filosofie'),
        'ZAF07':('Kríza analytickej filozofie','filozofia'),
        'ZAF08':('§ 10','pokrok'),
        'ZAF09':('Tretia časť','filozofia'),
        'ZAF10':('Metafilozofické diskusie','filozofia'),
    }
    for name,(heading,word) in arguments.items():
        print('PASS',run_work(name,expect=heading,term=word,
               jump_to='ZAF02-0098' if name=='ZAF02' else None))

if __name__=='__main__':test_all()
