# Verzia s OpenAI API

Táto verzia **používa OpenAI Responses API namiesto Gemini**. Čítačka, lokálne JSON
texty, vyhľadávanie, výklad kliknutého odseku a 20-krokový sokratovský dialóg
sú zachované. Do API sa prenášajú iba relevantné výňatky a kontext spracúvanej
požiadavky, nie celý JSON automaticky. Model nemá pripojené vyhľadávanie na webe.

## Rýchle nasadenie

1. Nahrajte obsah *tohto* priečinka na GitHub (všetky súbory z projektu,
   vrátane `openai_backend.py`, `requirements.txt` a súborov JSON).
2. V Streamlit Community Cloud otvorte existujúcu aplikáciu, prípadne vytvorte
   novú, a nastavte správny repozitár, vetvu `main`/`master` a hlavný súbor `app.py`.
3. V **App settings → Secrets** zadajte (skutočný kľúč nikdy nevkladajte na GitHub):

```toml
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-6.1-sol"
OPENAI_REASONING_EFFORT = "low"
OPENAI_TIMEOUT_MS = 120000
```

Pre lacnejšiu prevádzku môžete vybrať `gpt-6-luna`, pre náročnejšie diskusie
`gpt-6.1-sol` a úsilie `medium` alebo `high`. Model musí byť dostupný
v danom projekte OpenAI API. Predplatné ChatGPT sa za API neúčtuje;
OpenAI API má vlastné fakturovanie podľa spotreby.

Kľúč vytvoríte na https://platform.openai.com/api-keys
Cenník: https://platform.openai.com/pricing

**Pozor na autorské práva k plným textom a prekladom**, ak má byť GitHub
repozitár verejný.

---

# AI tútor – Záver: Súčasnosť a budúcnosť analytickej filozofie

Samostatná aplikácia **Streamlit + Google Gemini** pre predmet *Súčasná filozofia 2 – Analytická filozofia*.

## Obsah a filozofické východiská

Obsahuje desať dodaných textov (1024 záznamov) v slovenčine a češtine:

1. **Peter Bieri – Co ještě zbývá z analytické filosofie?**; štúdia podľa dodanej prílohy.
2. **Hans-Johann Glock – Súčasnosť a budúcnosť** (kapitola 9); výňatok (kapitola knihy).
3. **Robert Hanna – Vzostup a pád analytickej filozofie**; štúdia podľa dodanej prílohy.
4. **Jaakko Hintikka – Kto sa chystá zabiť analytickú filozofiu?**; štúdia podľa dodanej prílohy.
5. **David J. Chalmers – Prečo vo filozofii nedochádza k väčšiemu pokroku?**; štúdia podľa dodanej prílohy.
6. **Jaroslav Peregrin – Postanalytická filosofie**; výňatok (kapitola knihy).
7. **Aaron Preston – Kríza identity analytickej filozofie** (kapitola 1); výňatok (kapitola knihy).
8. **Daniel Stoljar – Filozofický pokrok: Na obranu rozumného optimizmu – Úvod** (kapitola 1); výňatok (kapitola knihy).
9. **Avrum Stroll – Dnes a zajtra** (kapitola 9); výňatok (kapitola knihy).
10. **Tadeusz Szubka – Analytická filozofia na začiatku nového tisícročia**; štúdia podľa dodanej prílohy.

**Korpus je súbor poskytnutých prekladov, nie kritická edícia.** Texty neboli overované
voči originálnym vydaniam. Odseky možno citovať podľa interného ID; pracovné
`source_paragraph` je poradie odseku z dodaného Wordu, nie pôvodná tlačená strana.

## Čo aplikácia umožňuje

- Výber autora alebo štúdie; filtrovanie podľa autorov
- Jediná posuvná čítačka na všetky oddiely konkrétneho textu; navigácia podľa
  pôvodných nadpisov, v Stoljarovom texte podľa § 1–10; priamy skok na pracovný odsek
- Lokálne vyhľadávanie s navigáciou medzi výsledkami, jedným zvýrazneným nálezom
- Vyhľadávanie naprieč desiatimi textami (lexikálny offline BM25 index)
- Kliknutie na hlavný text/citáciu otvorí výklad odseku cez Gemini bez zmeny počtu dialógových vstupov
- 20 študentských vstupov v sokratovskom dialógu, s priebežným počítadlom,
  finálnym hodnotením a exportom kompletného prepisu do TXT
- Voľba rozsahu: vybraný text / vybraný autor / všetkých desať textov.
  Rozsah sa zamkne pri prvej úspešnej odpovedi. Neúspešný požiadavok nečerpá krok.
- Poznámky, prekladateľské informácie a bibliografia v čítačke zostávajú prítomné,
  ale sú z indexu filozofického výkladu vylúčené.

## Spustenie lokálne

1. Python 3.11 alebo novší
2. V koreňovom priečinku projektu:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

3. Uložte nastavenia do `.streamlit/secrets.toml` (podľa dodaného príkladu), napr.:

```toml
OPENAI_API_KEY = "VLOZTE_SVOJ_SKUTOCNY_KLUC"
OPENAI_MODEL = "gpt-6.1-sol"
OPENAI_TIMEOUT_MS = 120000
```

4. Spustite `streamlit run app.py`. Ak kľúč nezadáte, čítanie a vyhľadávanie
   zostanú dostupné; výklad a dialóg budú vypnuté.

Model nastavte na model dostupný vo vašom projekte OpenAI API.
Pri chybe 404 overte názov, pri 429 kvótu a limity.

## GitHub + Streamlit Community Cloud

1. Vytvorte nový repozitár `ai-tutor-zaver-analytickej-filozofie`.
2. Nahrajte súbory z archívu **do koreňa** repozitára (najmä `app.py`,
   `book_reader.py`, `tutor_core.py`, JSON a `requirements.txt`).
3. Streamlit Cloud: **New app**, vyberte repozitár a nastavte vstup `app.py`.
4. Vo **Settings → Secrets** zadajte skutočný API kľúč a model. Skutočný súbor
   `secrets.toml` nikdy nevkladajte do GitHubu.
5. Vyskúšajte kliknutie na odsek v Bieriho štúdii a porovnanie Chalmersa so Stoljarom.

**Autorské práva:** JSON obsahuje plné preklady. Pred vložením do verejného
repozitára alebo verejným sprístupnením je potrebné preveriť súhlas/oprávnenia
k textom a prekladom. Súkromný repozitár automaticky nerieši licencie.

## Testovanie

```bash
pip install pytest playwright
pytest -q tests/test_core.py
python tests/test_reader_browser.py
```

Pre testy prehliadača potrebujete lokálne Chromium (`/usr/bin/chromium`) alebo
upravte cestu v `tests/test_reader_browser.py` podľa svojho prostredia.
Živé OpenAI API volania nie sú súčasťou testov – vyžadujú funkčný kľúč a kvótu.

## Technické poznámky

- Streamlit `>=1.50`; ovládací komponent čítačky používa `st.components.v2.component`.
- Záznamy sú triedené podľa zdrojového dokumentu, nie podľa času vzniku diel.
- Offline BM25 poskytuje *lexikálne* vyhľadávanie, nie plnohodnotné sémantické
  prehľadávanie celých diel. Pri dlhých debatách sa staršie časti dialógu
  z dôvodov veľkosti požiadavky skracujú; finálny prepis zostáva úplný.
- Ak sa modelu nepodarí odpovedať, počet využitých vstupov sa nezvyšuje.
- V zdrojoch sa nevyhľadávajú poznámky a bibliografia ako autorov hlavný výklad.

## Základné súbory

- `app.py` – rozhranie, Gemini, dialóg, export a riadenie stavov
- `tutor_core.py` – validácia korpusu, vyhľadávanie a textový export
- `book_reader.py` – interaktívna čítačka s vlastným scrollbarom
- `zaver_sucasnost_a_buducnost_analytickej_filozofie_texty.json` – korpus
- `POZNAMKY_K_TEXTOM.md` – poznámky ku zdrojovému korpusu
- `.streamlit/secrets.toml.example` – šablóna API nastavení
- `tests/` – kontrola dát a testy prehliadača
