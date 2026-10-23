# JLM Winter Campaign — 5-slide Instagram carousel (+ Stories version)

«منتجات رح تساعد سيارتك في الشتاء» — five slides from one master template (`scripts/build.py`): the carousel at 1080×1350 (4:5) in `out/carousel/`, the same design as Stories at 1080×1920 in `out/story/`. Kept separate from the November winter-check campaign: no check / preparation wording.

**Shared system:** night-rain background on wet asphalt (procedural, same file for all five); progress bars and `0N / 05` top-left; official `logo_on_dark.png` top-right in the same spot; headline in the JLM ATL yellow 5 px frame with a solid yellow tag; product standing on the wet floor with a reflection and a glow in its packaging category colour; info panel with the yellow brand drop. Fonts: Helvetica Neue LT Arabic + Albert Sans from `brand/jlm/fonts`. Colours: the brief palette (#FAB717, #252729, #376941, #F2F0EB, #C1C4C7).

| # | Story | Product (original catalogue image) | Category colour | Copy source |
|---|---|---|---|---|
| 1 | Opening | — (night car) | yellow | campaign brief |
| 2 | Cold mornings («الصباح البارد») | 5W-30 Premium Grade Performance Oil | oil gold (label) | label: synthetic, 5W30; SAE J300: "W" = winter grade |
| 3 | Rain and rust | Penetrating Oil | service blue (label) | label: dissolves rust and displaces moisture; penetrates rusted and frozen parts; loosens bolts and nuts |
| 4 | Clean fuel system | Fuel System Cleaner · Petrol | petrol green #376941 | label: deep cleans injectors and combustion chambers; prevents new deposits; routine fuel-system care |
| 5 | CTA | the three products | yellow | campaign brief; store URL jlmstore.com (brand bible) |

```
python3 scripts/build.py          # carousel → out/carousel/slide_01..05.png + overview.jpg
python3 scripts/build.py story    # stories  → out/story/story_01..05.png + overview.jpg
```
