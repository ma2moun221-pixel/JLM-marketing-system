# JLM Petrol Hybrid Treatment — Fast-Paced edit

The client's 18.8 s talking-head clip (presenter at a charger, holding the can), edited in the
style the client picked from `brand/jlm/EDIT_STYLES.md`.

- **Main style:** Fast-Paced / Retention (§3). Something new every 1–2.5 s on a calm camera:
  - **Camera (v3, client note):**
    - «بسيارات الهايبريد»: an eased push-in on the presenter.
    - «والبلَغ إن هايبريد»: a glide to the charger and its plug, then back at «بمحركات».
    - Both moves use a quintic ease and light motion blur. Otherwise there is one slow push per shot and one smooth move into the can when the product is named.
    - The jump cut is a short dissolve.
  - **Captions:** word-pop on the shirt, kept clear of the can. «بسيارات الهايبريد والبلَغ إن هايبريد» shares one caption frame.
  - **Hero icons (v6):** Hybrid and Plug-in Hybrid are introduced large in the centre with a yellow glow. The footage behind steps back (dim and soft-focus). Each icon then makes one quintic FLIP glide, with motion blur, into its slot. The «+» link draws after both have landed.
  - **Icons (v2):** always linked pairs at the bottom, first on the right, second on the left, same size and pop:
    - هايبريد + بلَغ إن هايبريد;
    - محرّك بنزين → تنظيف مستمر;
    - يمنع الرواسب + يشحّم.
  - **Product chip** at the top.
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
