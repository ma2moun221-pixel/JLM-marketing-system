# JLM — «مين ورا JLM في فلسطين؟» (team reel, 18.5 s)

CapCut-style edit of the client's 22 s WhatsApp clip (presenter + workshop b-roll + JLM stand).
The style is the usual Clean + Kinetic look, plus three accents the client chose: a Kinetic hook,
Fast-Paced zooms and an animated jlmstore.com card.

    # put the client's clip at src/raw.mp4 (not committed)
    python3 scripts/edit.py --out out/jlm_team_palestine.mp4 [--stills 1,5,...]

## What the edit does

- **Pauses:** tightened. The voice runs 15.3 s instead of 21.7 s.
- **Cutting:** the b-roll is re-cut on the beat. The presenter shots stay lip-synced.
- **Hook:**
  - «مين ورا» pops in.
  - «JLM» slams in with a flash and a light shake, landing on the music drop.
  - «في فلسطين؟» comes in with a map pin.
- **Transitions:**
  - whip-slide with motion blur;
  - zoom punch;
  - light flash.
- **Zooms:** a 1.00 → 1.05 drift within each shot, plus punch-ins on key words.
- **Captions:** one line, karaoke-style, at 76.5 % height. A round line icon draws itself at
  the start of each caption: wrench, can, car, shop, cart, snowflake, bulb, tag, question.
- **jlmstore.com card:** a cart icon with a cursor click.
- **End card:** over the blurred video. It shows the logo, Driving your journey,
  «اطلبها الآن من خلال» jlmstore.com and «مع توفر خدمة التوصيل».
- **Audio:**
  - the voice is cleaned;
  - synthesised music (A minor, 120 BPM): a hook riser and drop on «JLM», a groove ducked
    under the voice, and the hook riff again on the CTA;
  - soft whooshes and ticks;
  - final level −14.6 LUFS.
