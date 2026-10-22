# Súpis zdrojov a poznámky k súboru JSON

**Tematický korpus:** Záver – Súčasnosť a budúcnosť analytickej filozofie
**Zdroj:** desať dokumentov DOCX vložených používateľom, presne v poradí príloh.
**Záznamov spolu:** 1024. **Znakov v textoch:** 521 146.

## Zoznam textov

| # | Autor | Text | Jazyk | Rozsah / typ | Záznamov |
|---:|---|---|:---:|---|---:|
| 1 | Peter Bieri | *Co ještě zbývá z analytické filosofie?* | cs | štúdia | 52 |
| 2 | Hans-Johann Glock | *Súčasnosť a budúcnosť* | sk | kapitola | 136 |
| 3 | Robert Hanna | *Vzostup a pád analytickej filozofie* | sk | štúdia | 54 |
| 4 | Jaakko Hintikka | *Kto sa chystá zabiť analytickú filozofiu?* | sk | štúdia | 133 |
| 5 | David J. Chalmers | *Prečo vo filozofii nedochádza k väčšiemu pokroku?* | sk | štúdia | 141 |
| 6 | Jaroslav Peregrin | *Postanalytická filosofie* | cs | kapitola | 142 |
| 7 | Aaron Preston | *Kríza identity analytickej filozofie* | sk | kapitola | 106 |
| 8 | Daniel Stoljar | *Filozofický pokrok: Na obranu rozumného optimizmu – Úvod* | sk | úvodná kapitola | 80 |
| 9 | Avrum Stroll | *Dnes a zajtra* | sk | kapitola | 109 |
| 10 | Tadeusz Szubka | *Analytická filozofia na začiatku nového tisícročia* | sk | štúdia | 71 |

## Klasifikácia a navigácia

Každý záznam má `id`, `work_id`, `author`, `work_title`, `language`, `type`, `text`, `section`, `subsection`, `chapter_number`, `source_paragraph` a `source_docx_style`. Možné typy: `paragraph` (hlavný autorský odsek), `heading` (nadpis), `quotation` (samostatná citácia s príslušným štýlom vo Worde), `list_item` (položka zoznamu), `note` (poznámka), `bibliography` (bibliografická položka), `front_matter` (titulné/zdrojové údaje) a `translator_credit`.

`source_paragraph` je poradové číslo odseku v poskytnutom DOCX (1 znamená prvý odsek dokumentu), **nie** stránka v originálnej publikácii. Pôvodné čísla strán sú zachované v `original_source_note` jednotlivých diel, ak boli v dokumentoch uvedené.

Záznamy `paragraph`, `quotation` a `list_item` majú `suitable_for_ai_explanation=true`; poznámky, bibliografia a titulné údaje majú hodnotu `false`. Všetky texty zostávajú dostupné na čítanie a vyhľadávanie.

### Osobitosti konkrétnych diel

- **Bieri:** 8 oddielov I–VIII; prekladateľ Martin Pokorný uvedený ako samostatný údaj; poznámky na konci.
- **Glock:** 9. kapitola knihy, tri pododdiely a poznámky k tejto kapitole.
- **Hanna:** samostatný text s poznámkami a bohatým zoznamom použitej literatúry.
- **Hintikka:** tematické pododdiely, 30 poznámok a bibliografia.
- **Chalmers:** 7 očíslovaných tematických oddielov; poznámky a literatúra na konci.
- **Peregrin:** kapitola s vloženým prehľadom postanalytických filozofov a odporúčaných kníh; na konci poznámky 88–99.
- **Preston:** prvá kapitola knihy, sedem tematických oddielov vrátane poznámok.
- **Stoljar:** len úvodná kapitola knihy, zachované pôvodné číslovanie § 1–10 a 13 poznámok.
- **Stroll:** deviata kapitola knihy, tri hlavné časti, dve samostatne štylizované citácie.
- **Szubka:** úvod, tematické časti, záver, poznámky a bibliografia.

## Obmedzenia a práca s textom

- Texty neboli prekladané ani opravované; prípadné preklepy prítomné v DOCX zostávajú zachované. Ak treba presnú vedeckú citáciu, skontrolujte ju s pôvodným vydaním.
- Formát zaznamenáva hranice jednotlivých odsekov z dokumentov Word, nie originálnu pagináciu. Samostatné citácie sú ako `quotation` označené vtedy, keď ich umožňuje rozpoznať štýl DOCX; citácie vložené priamo do odseku zostávajú jeho súčasťou.
- V tomto súbore nie sú celé knihy Glocka, Peregrina, Prestona, Stoljara ani Strolla — len dodané kapitoly.
- Pred verejným sprístupnením prekladov preveriť autorské práva a príslušné licencie.

## Overenie

- Overené: 10 diel, 1024 jedinečných identifikátorov, všetkých 1024 neprázdnych odsekov presne zhodných s textom DOCX.
- Rozdelenie podľa typov: `bibliography` 132, `front_matter` 23, `heading` 79, `list_item` 14, `note` 111, `paragraph` 623, `quotation` 41, `translator_credit` 1.
- Overené číslovanie § 1–10 v Stoljarovom úvode a správne rozlíšenie poznámok a bibliografie.
