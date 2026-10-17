# JLM Petrol Hybrid Treatment — Fast-Paced edit

The client's 18.8 s talking-head clip (presenter at a charger, holding the can), edited in the
style the client picked from `brand/jlm/EDIT_STYLES.md`.

- **Main style:** Fast-Paced / Retention (§3). Something new every 1–2.5 s:
  - punch-ins and reframes (onto the charger, then a close-up of the can);
  - word-pop captions on the shirt, kept clear of the can;
  - line-icon badges beside the head (هايبريد، محرّك بنزين، تنظيف مستمر، يمنع التراكم);
  - the product chip;
  - a linked pair, رواسب كربونية → تشحيم.
- **Jump Cut clean-up (§2):** the lead-in and the 0.4 s pause are cut. The clip ends on «نظام الاحتراق» because the source cuts off mid-word.
- **Vox board (§6)** over «بسبب تراكم مخلفات الاحتراق … المحرّك ما بيشتغل بصورة دايمة»:
  - an injector clogging with carbon;
  - the petrol ⇄ electric hand-over with the engine switching ON/OFF;
  - an arrow linking cause to result;
  - the presenter shown live in a photo card.
- **Kinetic close (§5):** «يمنع» lands with a hit, «الرواسب» dissolves, «ويشحّم» slides in with a sheen and a drop, then «نظام الاحتراق». The black CTA end screen follows.
- **Audio:**
  - the original voice;
  - a synthesized 112 BPM bed, about 14 dB under the voice, lifting for the close;
  - soft ticks and whooshes.

```
python3 scripts/edit_fast.py --src CLIENT_VIDEO --out out/jlm_hybrid_fast.mp4 [--stills 1,5,...]
```

Output: `out/jlm_hybrid_fast.mp4`, 1080×1920, 30 fps, 24.3 s, −15 LUFS, peak −2.3 dBFS.
