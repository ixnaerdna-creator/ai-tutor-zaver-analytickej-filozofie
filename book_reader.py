"""Klikateľná čítačka textov s jediným posuvným panelom.

Komponent Streamlit v2: HTML/CSS/JS sa vykonávajú na strane prehliadača.
Do Pythonu odosiela iba ID kliknutého odseku a identifikátor kliknutia.
"""
import streamlit as st

READER_HTML = """
<div class="af-shell" lang="sk">
  <div class="af-tools">
    <input type="search" id="af-search" placeholder="Hľadať v texte…" aria-label="Vyhľadávanie v štúdii" autocomplete="off" />
    <button type="button" id="af-prev" aria-label="Predchádzajúci nález" title="Predchádzajúci nález">↑</button>
    <button type="button" id="af-next" aria-label="Nasledujúci nález" title="Nasledujúci nález">↓</button>
    <select id="af-chapters" aria-label="Prejsť na kapitolu alebo oddiel"></select>
    <select id="af-paragraphs" aria-label="Prejsť na odsek (interné poradie)" hidden></select>
    <button type="button" id="af-start">Na začiatok</button>
    <button type="button" id="af-end-btn">Na koniec</button>
  </div>
  <div class="af-context" aria-live="polite">
    <span id="af-current"></span>
    <span id="af-found"></span>
  </div>
  <div class="af-scroll" id="af-scroll" tabindex="0" aria-label="Posuvný text vybranej štúdie">
    <div id="af-text"></div>
    <div id="af-bottom">Koniec vybraného textu · pozrite aj zdroje a poznámky</div>
  </div>
</div>
"""

READER_CSS = r"""
:host { display:block; width:100%; height:770px; }
*, *::before, *::after { box-sizing:border-box; }
.af-shell { height:770px; max-height:770px; min-height:770px; width:100%; overflow:hidden;
  display:flex; flex-direction:column; color:var(--st-text-color,#222);
  font-family:Georgia,'Times New Roman',serif; }
.af-tools { display:flex; flex:0 0 auto; flex-wrap:wrap; align-items:center;
  gap:6px; padding:5px 0 9px; font:12px system-ui,sans-serif; }
.af-tools input, .af-tools select { border:1px solid #9daab5; border-radius:5px;
  color:var(--st-text-color,#222); background:var(--st-background-color,#fff);
  padding:7px 8px; font:13px system-ui,sans-serif; min-height:35px; }
.af-tools input {flex:2 1 170px; min-width:130px;}
.af-tools select {flex:1 1 130px; min-width:120px; max-width:260px;}
.af-tools button {border:1px solid #aab4bf; color:var(--st-text-color,#222);
  background:var(--st-background-color,#fff); border-radius:5px; cursor:pointer;
  padding:7px 9px; min-height:35px; font:12px system-ui,sans-serif; white-space:nowrap;}
.af-tools button:hover {background:#e7edf3; color:#222;}
.af-tools button:focus-visible, .af-tools select:focus-visible, .af-tools input:focus-visible {
  outline:2px solid #3779b6; outline-offset:1px;}
.af-context {flex:0 0 auto; display:flex; justify-content:space-between; gap:8px; min-height:26px;
  color:var(--st-text-color,#555); opacity:.8; font:12px/1.3 system-ui,sans-serif;
  padding:0 4px 7px;}
#af-current {max-width:70%; overflow:hidden; white-space:nowrap; text-overflow:ellipsis;}
#af-found {flex:0 0 auto; white-space:nowrap;}
.af-scroll { flex:1 1 0; min-height:0; overflow-y:auto; overflow-x:hidden;
  scrollbar-width:auto; scrollbar-color:#59636e #e7eaef; scrollbar-gutter:stable;
  overscroll-behavior:contain; border-top:1px solid #d9dfe4;
  scroll-behavior:auto; }
.af-scroll::-webkit-scrollbar {width:16px;}
.af-scroll::-webkit-scrollbar-track {background:#e7eaef;}
.af-scroll::-webkit-scrollbar-thumb {background:#59636e; border:3px solid #e7eaef; border-radius:9px;}
#af-text {padding:12px 12px 4px 0;}
.af-heading {font:700 21px/1.4 Georgia,serif; margin:22px 0 14px;
  padding:0 0 9px; border-bottom:1px solid #bdc7d0; color:var(--st-text-color,#222);}
.af-heading:first-child {margin-top:0;}
.af-section-number {font-size:17px; margin:17px 0 7px; padding-bottom:3px; border-bottom:0;}
.af-continuation-heading,.af-notes-heading {font-size:15px; opacity:.75;}
.af-paragraph {display:block; width:100%; white-space:normal; text-align:left;
  background:transparent; color:var(--st-text-color,#222); border:0;
  border-left:3px solid transparent; padding:7px 9px 12px 10px; margin:0 0 7px;
  cursor:pointer; overflow-wrap:break-word;
  font:18px/1.55 Georgia,'Times New Roman',serif; border-radius:2px;}
.af-paragraph:hover {background:#edf4f9;}
.af-paragraph:focus-visible {outline:2px solid #3876ab; outline-offset:-2px;}
.af-paragraph.af-selected {border-left-color:#4a82ae; background:#edf5fc;}
.af-paragraph.af-hit {border-left-color:#ae7700; background:#ffecac; color:#272019;}
.af-location {display:block; color:#6b7480; margin-bottom:3px; font:11px/1.35 system-ui,sans-serif;}
.af-paragraph.af-hit .af-location {color:#735000;}
.af-picture {margin:10px 8px 20px; padding:10px; border:1px solid #aab7c2; border-radius:6px; max-width:100%;}
.af-picture img {display:block; max-width:100%; height:auto; margin:0 auto;}
.af-picture figcaption {font:12px/1.45 system-ui,sans-serif; color:var(--st-text-color,#444); padding:9px 2px 0;}
.af-quotation {font-style:italic; margin-left:12px; border-left-color:#8f9dba;}
.af-thesis {font-weight:600; border-left-color:#6a8796;}
.af-list-item {padding-left:22px;}
.af-formula {font-family:'Cambria Math',Georgia,serif; background:rgba(125,125,125,.04);}
.af-tablebutton {overflow-x:auto;}
.af-real-table {border-collapse:collapse; font:14px/1.4 Georgia,serif; width:100%; min-width:450px;}
.af-real-table th,.af-real-table td {border:1px solid #aab7c2; padding:7px; text-align:left; vertical-align:top; white-space:pre-wrap;}
.af-real-table th {font-weight:bold; background:rgba(125,125,125,.13);}
.af-note {font:14px/1.45 Georgia,serif; padding:4px 10px; margin:8px 0;
  border-left:2px solid #aeb7c2; opacity:.78;}
#af-bottom {padding:18px 8px 30px; margin:22px 0 0;
  border-top:1px solid #b9c1cb; color:var(--st-text-color,#555);
  font:13px system-ui,sans-serif;}
@media(max-width:700px){.af-paragraph{font-size:16px;} .af-tools button{padding:6px 7px;}}
"""

READER_JS = r"""
export default function({parentElement, data, setTriggerValue}) {
  const root=parentElement.querySelector('.af-shell');
  const scroll=root.querySelector('#af-scroll');
  const content=root.querySelector('#af-text');
  const searchInput=root.querySelector('#af-search');
  const chapterList=root.querySelector('#af-chapters');
  const paragraphList=root.querySelector('#af-paragraphs');
  const prev=root.querySelector('#af-prev');
  const next=root.querySelector('#af-next');
  const first=root.querySelector('#af-start');
  const last=root.querySelector('#af-end-btn');
  const found=root.querySelector('#af-found');
  const current=root.querySelector('#af-current');
  const rows=Array.isArray(data?.paragraphs)?data.paragraphs:[];
  const storageKey='af.reader.v1.'+(data?.bookKey||'default');
  const normalized=s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const entries=[], sections=[], paragraphSections=[];
  const fragment=document.createDocumentFragment();
  let hits=[], hitIndex=0, initialized=false, clickNumber=0;
  let rememberedScroll=0, rememberedSearch='';
  try {
    rememberedScroll=Number(sessionStorage.getItem(storageKey+'.scroll'))||0;
    rememberedSearch=sessionStorage.getItem(storageKey+'.search')||'';
  } catch(_) {}

  for (const row of rows) {
    if (row.type==='heading') {
      const h=document.createElement('h3');
      h.className='af-heading'; h.textContent=row.text;
      fragment.appendChild(h);
      sections.push({label:row.text,el:h});
      if (['poznámky','poznamky','bibliografia','bibliografie'].includes(normalized(row.text))) {
        h.classList.add('af-notes-heading');
      }
      continue;
    }
    if (['note','bibliography','translator_credit'].includes(row.type) || (row.type==='front_matter' && row.text.length<500)) {
      const note=document.createElement('div');
      note.className='af-note';
      const kind=row.type==='bibliography'?'Bibliografický údaj':row.type==='translator_credit'?'Prekladateľský údaj':row.type==='front_matter'?'Úvodné údaje':'Poznámka';
      note.textContent=kind+' — '+row.text;
      fragment.appendChild(note);
      continue;
    }
    if (row.type==='image') {
      const visual=(data?.visuals||[]).find(v=>v.id===row.visual_id);
      const box=document.createElement('figure'); box.className='af-picture';
      if (visual && visual.image_base64) {
        const img=document.createElement('img');
        img.src='data:image/png;base64,'+visual.image_base64;
        img.alt=visual.description_sk||row.text;
        img.loading='lazy'; box.appendChild(img);
      }
      const caption=document.createElement('figcaption');
      caption.textContent='Obrazová príloha – '+(visual?.description_sk||row.text);
      box.appendChild(caption); fragment.appendChild(box);
      continue;
    }
    if (!['paragraph','quotation','thesis','list_item','table'].includes(row.type) ) continue;
    const p=document.createElement('button');
    p.type='button';
    p.className='af-paragraph'+(row.id===data?.selected?' af-selected':'')+(row.type==='quotation'?' af-quotation':'')+(row.type==='thesis'?' af-thesis':'')+(row.type==='list_item'?' af-list-item':'')+(row.type==='table'?' af-tablebutton':'');
    p.setAttribute('aria-label','Otvoriť výklad '+row.id);
    const place=document.createElement('span'); place.className='af-location';
    const placeParts=[];
    if (row.section) placeParts.push(row.section);
    if (row.source_paragraph!=null) placeParts.push('pracovný odsek '+row.source_paragraph);
    if(row.type==='quotation') placeParts.push('citovaná pasáž');
    if(row.type==='thesis') placeParts.push('téza');
    place.textContent=placeParts.join(' · ');
    const body=document.createElement('span');
    if (row.type==='table' && Array.isArray(row.rows)) {
       const table=document.createElement('table'); table.className='af-real-table';
       for (const [n, cells] of row.rows.entries()) {
         const tr=document.createElement('tr');
         for (const cell of cells) {
           const item=document.createElement(n===0?'th':'td');
           item.textContent=String(cell); tr.appendChild(item);
         }
         table.appendChild(tr);
       }
       body.appendChild(table);
    } else { body.textContent=row.text; }
    p.append(place,body);
    p.addEventListener('click',()=>{
      for(const n of entries) n.el.classList.toggle('af-selected',n.id===row.id);
      remember(); setTriggerValue('selected', {id:row.id, nonce:Date.now()+'-'+(++clickNumber)});
    });
    fragment.appendChild(p);
    entries.push({id:row.id,el:p,searchable:normalized(
      [row.id,row.text,row.section||''].join(' '))});
    if(row.source_paragraph!=null)paragraphSections.push({number:row.source_paragraph,el:p});
  }
  content.replaceChildren(fragment);

  const topMax=()=>Math.max(0,scroll.scrollHeight-scroll.clientHeight);
  function remember() {
    if (!initialized) return;
    try {sessionStorage.setItem(storageKey+'.scroll',String(scroll.scrollTop));}catch(_){}
  }
  function jump(position) {
    scroll.scrollTop=Math.max(0,Math.min(topMax(),position));
    remember(); updateCurrent();
  }
  function reveal(node) {
    const diff=node.getBoundingClientRect().top-scroll.getBoundingClientRect().top;
    jump(scroll.scrollTop+diff-14);
  }
  function updateCurrent() {
    let label=sections.length?sections[0].label:'';
    const threshold=scroll.getBoundingClientRect().top+32;
    for(const section of sections) {
      if(section.el.getBoundingClientRect().top<=threshold) label=section.label;
      else break;
    }
    const firstVisible=entries.find(e=>e.el.getBoundingClientRect().bottom>scroll.getBoundingClientRect().top+12);
    if (firstVisible) { const foundPage=firstVisible.el.querySelector('.af-location')?.textContent||'';
      current.textContent=[label,foundPage].filter(Boolean).join(' · ');
    } else current.textContent=label;
  }
  function highlight() {
    for(const entry of entries) entry.el.classList.remove('af-hit');
    if(!hits.length) {found.textContent=searchInput.value.trim()?'Bez nálezov':'';return;}
    const chosen=entries[hits[hitIndex]];
    chosen.el.classList.add('af-hit');
    found.textContent=`Nález ${hitIndex+1} z ${hits.length} · ${chosen.id}`;
  }
  function runSearch(jumpToFirst=false) {
    const q=normalized(searchInput.value.trim());
    hits=[];
    if(q) entries.forEach((n,i)=>{if(n.searchable.includes(q))hits.push(i)});
    hitIndex=0;
    highlight();
    try {sessionStorage.setItem(storageKey+'.search',searchInput.value)}catch(_){}
    if(jumpToFirst&&hits.length)reveal(entries[hits[0]].el);
  }
  function nextHit(delta) {
    if(!hits.length)return;
    hitIndex=(hitIndex+delta+hits.length)%hits.length;
    highlight(); reveal(entries[hits[hitIndex]].el);
  }
  chapterList.replaceChildren();
  const beginning=document.createElement('option');
  beginning.value='top'; beginning.textContent='Začiatok textu'; chapterList.appendChild(beginning);
  sections.forEach((section,i)=>{
    const option=document.createElement('option');
    option.value=String(i); option.textContent=section.label;
    chapterList.appendChild(option);
  });

  chapterList.disabled=sections.length===0;
  paragraphList.hidden=paragraphSections.length===0;
  paragraphList.replaceChildren();
  if (paragraphSections.length) {
    const initial=document.createElement('option'); initial.value='';
    initial.textContent='Skok na pracovný odsek'; paragraphList.appendChild(initial);
    paragraphSections.forEach((item,i)=>{
      const option=document.createElement('option'); option.value=String(i);
      option.textContent='Odsek '+item.number; paragraphList.appendChild(option);
    });
  }
  const onChapter=()=>{
    const value=chapterList.value;
    if(value==='top')jump(0);
    else if(sections[Number(value)])reveal(sections[Number(value)].el);
  };
  const onParagraph=()=>{
    const value=paragraphList.value;
    if(value!==''&&paragraphSections[Number(value)])reveal(paragraphSections[Number(value)].el);
  };
  const onInput=()=>runSearch(true);
  const onSearchKey=e=>{
    if(e.key==='ArrowDown'||e.key==='Enter'){e.preventDefault();nextHit(1);}
    if(e.key==='ArrowUp'){e.preventDefault();nextHit(-1);}
  };
  const onPrev=()=>nextHit(-1), onNext=()=>nextHit(1);
  const onFirst=()=>jump(0), onLast=()=>jump(scroll.scrollHeight);
  const onScroll=()=>{remember(); updateCurrent();};
  searchInput.value=rememberedSearch;
  runSearch(false);
  chapterList.addEventListener('change',onChapter);
  paragraphList.addEventListener('change',onParagraph);
  searchInput.addEventListener('input',onInput);
  searchInput.addEventListener('keydown',onSearchKey);
  prev.addEventListener('click',onPrev);
  next.addEventListener('click',onNext);
  first.addEventListener('click',onFirst);
  last.addEventListener('click',onLast);
  scroll.addEventListener('scroll',onScroll,{passive:true});
  jump(rememberedScroll);
  initialized=true;
  if (data?.jumpToId) {
    const focused=entries.find(entry=>entry.id===data.jumpToId);
    if(focused){reveal(focused.el);focused.el.classList.add('af-selected');}
  }
  updateCurrent();
  return ()=>{
    chapterList.removeEventListener('change',onChapter);
    paragraphList.removeEventListener('change',onParagraph);
    searchInput.removeEventListener('input',onInput);
    searchInput.removeEventListener('keydown',onSearchKey);
    prev.removeEventListener('click',onPrev);
    next.removeEventListener('click',onNext);
    first.removeEventListener('click',onFirst);
    last.removeEventListener('click',onLast);
    scroll.removeEventListener('scroll',onScroll);
  };
}
"""

book_reader = st.components.v2.component(
    name="zaver_analyticka_reader_v1", html=READER_HTML,
    css=READER_CSS, js=READER_JS, isolate_styles=True,
)
