# JLM winter poster — «سيارتك جاهزة للشتا؟»

    python3 scripts/build.py          # out/jlm_winter_poster.png        1080×1350 (Facebook / Instagram feed)
    python3 scripts/build.py story    # out/jlm_winter_poster_story.png  1080×1920 (Stories)

## The scene

Painted in numpy:
- **Setting:** a winter night on a snowy road, with drifts, ice glints and snow falling in three depths.
- **Car:** the car from the winter campaign (`../jlm-winter-stories/assets/car-side.jpg`), cut out with
  rembg. It is night-graded, its hub badges are blacked out, and it has a thin snow cap on the roof line.
- **Light:** the headlights cast a warm beam that lights up the snowflakes.

## The overlay

HTML in the JLM fonts (Helvetica Neue LT Arabic + Albert Sans), rendered by Chromium:
- the official logo top-right, with no box and no shadow;
- the slogan «سيارتك جاهزة / للشتا؟» with a snowflake;
- «منتجات JLM معك هذا الشتاء»;
- the usual CTA: «اطلبها الآن من خلال» jlmstore.com · «مع توفر خدمة التوصيل».

There are no product claims.
