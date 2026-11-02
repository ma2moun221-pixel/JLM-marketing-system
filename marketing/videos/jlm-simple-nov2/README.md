# JLM AIRCO Foam Cleaner — simple clean-up (84 s, 1080×1920)

The client's finished clip, kept as it is (its own titles and narration) with no icons or animation —
only the shots improved, as asked (`scripts/clean.py`):
- upscaled 720×1280 → 1080×1920, light denoise, gentle sharpening, a touch more contrast and colour;
- the landscape inserts that sat in black bars (starting the car, dashboard, AC panel, the part shot,
  the recap) now fill the frame over a blurred, darkened copy of themselves; the AC-panel close-up with
  the red circle is zoomed to fill;
- the two longest pauses tightened; voice cleaned (high-pass, light denoise), −14 LUFS; soft fade at the end.

```bash
python3 scripts/clean.py --out out/jlm_airco_clean.mp4
```
`src/raw.mp4` is the client's clip (not committed).
