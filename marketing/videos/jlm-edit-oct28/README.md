# JLM GDI Injector Cleaner — reel (24.6 s, 1080×1920)

The client's 28.4 s clip (presenter + engine / injector / product shots + a white CTA card), edited in
the **usual JLM look** — the same as the Brake Cleaner reel: Clean / Minimal with a Kinetic opening
(brand/jlm/EDIT_STYLES.md §1 + §5, VIDEO_STYLE.md).

1. **Clean-up first** (`scripts/cut.py`): only the spoken parts are kept — pauses trimmed to ≈ 0.1 s,
   silent shot ends dropped, 15 ms audio fades on every cut. The clip's own white CTA card is dropped.
2. **Edit** (`scripts/edit.py`):
   - Kinetic hook: «لماذا يلزم نستخدم» word by word → «مضاف البخاخات» lands with a soft yellow spray
     mist → «من JLM في المحركات الجديدة؟»;
   - karaoke captions at 66 % height on a soft dark box (moved above the can on the product shot),
     Helvetica Neue LT Arabic / Albert Sans;
   - two linked icon pairs: تراكمات وترسّبات → على البخاخ (red), كفاءة أعلى → استهلاك أقل (yellow,
     the presenter's own words) and a «JLM GDI Injector Cleaner» tag on the product shot;
   - breathing zoom per shot, punch-in to 1.08 over the jump cuts;
   - the JLM logo top-left without the logo file's faint background box;
   - the usual CTA over the blurred product shot, under the presenter's spoken CTA: logo ·
     GDI Injector Cleaner · «اطلبه الآن من خلال» · jlmstore.com · «مع توفّر خدمة التوصيل».

Soft ≈ −40 dBFS icon ticks; voice untouched; −14 LUFS.

```bash
python3 scripts/cut.py src/raw.mp4 build/cut.mov
python3 scripts/edit.py --src build/cut.mov --out out/jlm_gdi_injector_cleaner.mp4
python3 scripts/edit.py --src build/cut.mov --out build/stills/x.mp4 --stills 2.2,9.7,12.6   # check frames
```
`scripts/vox.py` is the earlier Vox-style version of the same edit (paper board, photo card,
diagram stickers), kept for reference. `src/raw.mp4` is the client's footage (not committed).
