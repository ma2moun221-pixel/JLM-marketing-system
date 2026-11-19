# JLM — «مين ورا JLM في فلسطين؟» (team reel)

CapCut-style edit of the client's 22 s WhatsApp clip (presenter + workshop b-roll + JLM stand).
The style is the usual Clean + Kinetic look, plus three accents the client chose: a Kinetic hook,
Fast-Paced zooms and an animated jlmstore.com card.

    # put the client's clip at src/raw.mp4 (not committed)
    python3 scripts/edit.py --mode full22   --out out/jlm_team_palestine_full22.mp4    # 22.0 s
    python3 scripts/edit.py --mode fullcard --out out/jlm_team_palestine_fullcard.mp4  # 24.6 s
    python3 scripts/edit.py --mode tight    --out out/jlm_team_palestine_tight.mp4     # 18.5 s

The client asked for the clip as filmed: every shot kept at real speed and nothing removed.
`full22` and `fullcard` keep the clip's own timeline 1:1.

- `full22` is 22.0 s. The usual CTA runs as a bar at the bottom on the last shot, and the last
  caption lifts above it.
- `fullcard` adds the usual CTA end card after the clip.
- `tight` was the first cut: the pauses removed and the b-roll re-cut on the beat. The client
  rejected it.

## What the edit does

- **Hook:**
  - «مين ورا» pops in.
  - «JLM» slams in with a flash and a light shake, landing on the music drop.
  - «في فلسطين؟» comes in with a map pin.
- **Transitions:** none, at the client's request. The shots cut straight, as filmed.
- **Zooms:** a 1.00 → 1.05 drift within each shot, plus punch-ins on key words.
- **Captions:** one line, karaoke-style, at 76.5 % height.
- **Icons:** round line icons gather in a row on the right, above the caption, one row per idea:
  - wrench, can, car;
  - shop, cart;
  - snowflake, bulb, tag, question.

  Each icon pops in on its word, draws itself in about 0.55 s and stays until the idea is over
  (2 s or more on screen).
- **jlmstore.com card:** a cart icon with a cursor click.
- **End card (fullcard / tight):** over the blurred video. It shows the logo, Driving your journey,
  «اطلبها الآن من خلال» jlmstore.com and «مع توفر خدمة التوصيل».
- **Audio:**
  - the voice is cleaned;
  - synthesised music (A minor, 120 BPM): a hook riser and drop on «JLM», a groove ducked
    under the voice, and the hook riff again on the CTA;
  - soft whooshes and ticks;
  - final level ≈ −14.5 LUFS.
