# JLM GDI Injector Cleaner — Vox-style reel (24.6 s, 1080×1920)

The client's 28.4 s clip (presenter + engine / injector / product shots + a white CTA card), edited in
**Vox-style** with a light **Fast-Paced** zoom accent (brand/jlm/EDIT_STYLES.md §6 + §3).

1. **Clean-up first** (`scripts/cut.py`): only the spoken parts are kept — pauses trimmed to ≈ 0.1 s,
   silent shot ends dropped, 15 ms audio fades on every cut. The clip's own white CTA card is dropped.
2. **Vox board** (`scripts/vox.py`) in JLM colours — off-white paper, charcoal ink, yellow highlighter,
   red only for the problem:
   - the footage in a slightly tilted photo card; 1.00 ↔ 1.10 punch-ins hide the jump cuts;
   - a paper title strip: the question «لماذا يلزم مضاف البخاخات في المحركات الجديدة؟», then
     ١ السبب: مكان البخاخ · ٢ الحل: منظف JLM · ٣ النتيجة;
   - stickers: a direct-injection diagram (injector in the combustion chamber; red deposits grow on its
     tip on «تراكمات وترسّبات»), a red marker circle on the real injector's dirty tip, the label line
     "Cleans the Inside of GDI Injector" highlighted with «ينظّف البخاخ من الداخل» and a ✓ on «إزالة»,
     and two result cards (كفاءة أعلى للمحرك · استهلاك أقل للوقود — the presenter's own words);
   - karaoke captions on a paper strip in Helvetica Neue LT Arabic / Albert Sans;
   - the JLM logo (charcoal) at the top, drawn without the file's faint background box.
3. **Usual CTA** over the blurred product shot, under the presenter's spoken CTA: logo ·
   GDI Injector Cleaner · «اطلبه الآن من خلال» · jlmstore.com · «مع توفّر خدمة التوصيل».

Soft paper swells and ≈ −40 dBFS ticks; voice untouched; −14 LUFS.

```bash
python3 scripts/cut.py src/raw.mp4 build/cut.mov
python3 scripts/vox.py --src build/cut.mov --out out/jlm_gdi_injector_cleaner.mp4
python3 scripts/vox.py --src build/cut.mov --out build/stills/x.mp4 --stills 1.5,8.6,10.5   # check frames
```
`src/raw.mp4` is the client's footage (not committed).
