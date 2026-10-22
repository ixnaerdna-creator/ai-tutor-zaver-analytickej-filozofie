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
OPENAI_MODEL = "gpt-6-luna"
OPENAI_REASONING_EFFORT = "medium"
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

## Preferované skúšobné nastavenie

V tejto verzii je predvolený **gpt-6-luna / medium** pre výklady aj dialógy. Nastavenia v Streamlit Secrets majú prednosť. Žiadne údaje o nákladoch sa nezobrazujú študentom. Pre zmenu modelu alebo úrovne uvažovania aktualizujte Secrets a reštartujte aplikáciu.
