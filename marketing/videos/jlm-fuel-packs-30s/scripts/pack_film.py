"""JLM fuel-system cleaning packs — Petrol vs Diesel, 30 s, 9:16, Arabic.

    python3 pack_film.py --out ../out/jlm_fuel_packs_30s.mp4 [--stills 2,8,18]

Reuses the brand engine of ../../jlm-promo-20s/scripts/render.py (JLM kit in
brand/jlm: charcoal + yellow, ATL headline box, yellow footer, falling drop).
Each pack carries its packaging accent (petrol green / diesel red) only on
small markers, so JLM yellow stays the dominant brand colour.
"""

import argparse
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parents[1] / "jlm-promo-20s" / "scripts"))
import render as R  # noqa: E402
import soundtrack  # noqa: E402
import storyboard as SB  # noqa: E402  (palette + layout constants)

W, H, FPS = 1080, 1920, 30
DURATION = 30.0
GREEN = (150, 200, 60)
RED = (230, 20, 50)
Y, CH, WH = SB.YELLOW, SB.CHARCOAL, SB.WHITE

# ------------------------------------------------------------------ copy ----
# Timeline: hook 0–3 · petrol 3–12 · diesel 12–22 · difference 22–25.5 · end 25.5–30
T_PETROL, T_DIESEL, T_DIFF, T_END = 3.0, 12.0, 22.0, 25.5
CUTS = [T_PETROL, T_DIESEL, T_DIFF, T_END]

HOOK = [[("بنزين", WH), ("أم", WH), ("ديزل؟", Y)]]
HOOK_SUB = "لكل محرّك باكج تنظيف خاص من JLM"

PACKS = [
    {
        "asset": "petrol_pack.png", "accent": GREEN, "start": T_PETROL, "end": T_DIESEL,
        "headline": [[("باكج", WH), ("البنزين", Y)]], "tag": "PETROL PACK",
        "use": "يُضاف مباشرة إلى خزان الوقود",
        "benefits": [
            "تنظيف كامل لنظام الوقود",
            "استهلاك أقل للوقود",
            "زيارات أقل للورشة",
            "تكاليف صيانة أقل",
            "فواتير إصلاح أقل",
        ],
    },
    {
        "asset": "diesel_pack.png", "accent": RED, "start": T_DIESEL, "end": T_DIFF,
        "headline": [[("باكج", WH), ("الديزل", Y)]], "tag": "DIESEL PACK",
        "use": "يُضاف مباشرة إلى خزان الوقود",
        "benefits": [
            "تجديد سريع لفلتر DPF",
            "تنظيف بدون فك القطع",
            "بدون الحاجة لرفع دورات المحرّك",
            "استهلاك أقل ورماد أقل",
            "عمر أطول للفلتر",
            "صيانة وإصلاح بتكلفة أقل",
        ],
    },
]

DIFF_HEAD = [[("ما", WH), ("الفرق؟", Y)]]
DIFF = [
    ("بنزين", GREEN, "تنظيف شامل لنظام الوقود"),
    ("ديزل", RED, "تنظيف + تجديد فلتر DPF"),
]
END_HEAD = [[("زوروا", WH), ("موقعنا", WH)]]
END_L2 = "لاكتشاف العديد من المنتجات"
END_L3 = "التي يمكنكم طلبها"
END_BADGE = "مع توفر خدمة التوصيل"

LIST_TOP = 1060       # first benefit line (top)
LIST_STEP = 60


def accent_dot(color, r=11):
    """Small round marker in the pack's accent colour."""
    s = 4
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", ((2 * r + 2) * s, (2 * r + 2) * s), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse([s, s, (2 * r + 1) * s, (2 * r + 1) * s], fill=tuple(color) + (255,))
    return R.to_premul(np.array(img.resize((2 * r + 2, 2 * r + 2), Image.LANCZOS)))


def benefit_line(T, text, accent):
    """Arabic benefit with a yellow drop bullet on its right (RTL)."""
    txt = T.line([(text, WH)], 46, bold=False, shadow=False, pad=0)
    drop, _ = R.drop_layer(13, Y)
    gap = 18
    h = max(txt.shape[0], drop.shape[0])
    out = np.zeros((h, txt.shape[1] + gap + drop.shape[1], 4), np.float32)
    R.paste_into(out, txt, 0, (h - txt.shape[0]) // 2)
    R.paste_into(out, drop, txt.shape[1] + gap, (h - drop.shape[0]) // 2)
    return out


def side_card(T, label, color, text, pack_img):
    """Difference card: pack image, accent bar, label and one-line difference."""
    card_w, card_h = 470, 760
    out = np.zeros((card_h, card_w, 4), np.float32)
    frame = R.box_frame(card_w, card_h, Y, stroke=4)
    fill = R.solid(card_w - 8, card_h - 8, SB.CHARCOAL_2, 0.85)
    R.paste_into(out, fill, 4, 4)
    R.paste_into(out, frame, 0, 0)
    R.paste_into(out, R.solid(card_w - 8, 10, color), 4, 4)
    import cv2
    ph = 400
    pw = int(pack_img.shape[1] * ph / pack_img.shape[0])
    p = cv2.resize(pack_img, (pw, ph), interpolation=cv2.INTER_AREA)
    if pw > card_w - 30:
        pw = card_w - 30
        p = cv2.resize(pack_img, (pw, int(pack_img.shape[0] * pw / pack_img.shape[1])), interpolation=cv2.INTER_AREA)
    R.paste_into(out, p, (card_w - p.shape[1]) // 2, 40)
    lab = T.line([(label, color)], 64, shadow=False, pad=0)
    R.paste_into(out, lab, (card_w - lab.shape[1]) // 2, 470)
    words = text.split(" ")
    lines = [" ".join(words[: len(words) // 2 + 1]), " ".join(words[len(words) // 2 + 1:])]
    y = 570
    for ln in lines:
        if not ln:
            continue
        l = T.line([(ln, WH)], 42, bold=False, shadow=False, pad=0)
        R.paste_into(out, l, (card_w - l.shape[1]) // 2, y)
        y += 62
    return out


class PackFilm:
    def __init__(self):
        kit = ROOT / "brand" / "jlm"
        R.ALBERT_PATH = kit / "fonts" / "AlbertSans.ttf"
        T = R.Type(kit / "fonts")
        self.T = T
        self.bg = R.Backdrop(kit / "patterns" / "gears_mask.png")
        self.trans = CUTS
        self.logo_footer = R.image_layer(kit / "logos" / "logo_on_yellow.png", 360)
        self.url_footer = R.latin_layer("jlmstore.com", 30, CH, 700, 0.03)
        self.drop_big, self.drop_big_anchor = R.drop_layer(52, Y)
        self.drop_fall, self.drop_fall_anchor = R.drop_layer(30, Y, stretch=1.25)
        self.glow = R.build_glow(420, WH, 0.07)
        self.hook_box, _ = R.headline_box(T, HOOK, None)
        self.hook_sub = T.line([(HOOK_SUB, WH)], 54, bold=False)
        assets = HERE.parent / "assets"
        self.packs = []
        for p in PACKS:
            from PIL import Image
            im = Image.open(assets / p["asset"]).convert("RGBA")
            hi = 580
            im = im.resize((int(im.width * hi / im.height), hi), Image.LANCZOS)
            img = R.to_premul(np.array(im))
            box, _ = R.headline_box(T, p["headline"], p["tag"])
            self.packs.append({
                **p, "img": img, "box": box,
                "use_chip": R.chip(T, p["use"], 38),
                "lines": [benefit_line(T, b, p["accent"]) for b in p["benefits"]],
                "dot": accent_dot(p["accent"]),
            })
        self.hook_pair = [pk["img"] for pk in self.packs]
        self.diff_box, _ = R.headline_box(T, DIFF_HEAD, None)
        self.cards = [side_card(T, lab, col, txt, pk["img"]) for (lab, col, txt), pk in zip(DIFF, self.packs)]
        self.end_box, _ = R.headline_box(T, END_HEAD, None)
        self.url = R.latin_layer("jlmstore.com", 112, Y, 900, 0.0)
        self.l2 = T.line([(END_L2, WH)], 52, bold=False)
        self.l3 = T.line([(END_L3, WH)], 52, bold=False)
        self.badge = R.badge(T, END_BADGE)
        self.nl = R.image_layer(kit / "labels" / "made_in_nl.png", 360)

    # footer + falling drop come straight from the promo engine
    draw_footer = R.Film.draw_footer
    draw_falling_drop = R.Film.draw_falling_drop
    centered = R.Film.centered
    box_in = R.Film.box_in
    light_sweep = R.Film.light_sweep

    def draw_hook(self, f, t):
        if t > T_PETROL + 0.05:
            return
        out = R.ease_in_out((t - (T_PETROL - 0.35)) / 0.3)
        self.box_in(f, self.hook_box, 330, R.clamp01((t - 0.15) / 0.55), out)
        # the two packs slide in from either side, petrol right (read first)
        for k, img in enumerate(self.hook_pair):
            p = R.ease_out((t - 0.35 - 0.15 * k) / 0.6)
            s = 0.76
            side = 1 if k == 0 else -1
            cx = W / 2 + side * 255 + side * (1 - p) * 300
            layer, x, y = R.warp_premul(img, s, cx, 1200, (img.shape[1] / 2, img.shape[0]))
            R.over(f, layer, x, y, p * (1 - out))
            dot = self.packs[k]["dot"]
            R.over(f, dot, cx - dot.shape[1] / 2, 1225, p * (1 - out))
        p2 = R.ease_out((t - 1.1) / 0.5)
        self.centered(f, R.rtl_reveal(self.hook_sub, p2), 1350, 1 - out, dy=(1 - p2) * 18)

    def draw_pack(self, f, t, pk):
        s0, s1 = pk["start"], pk["end"]
        if not (s0 - 0.05 <= t <= s1 + 0.05):
            return
        lt = t - s0
        pin = R.ease_out(lt / 0.55)
        pout = R.ease_in_out((t - (s1 - 0.3)) / 0.3)
        vis = pin * (1 - pout)
        g = self.glow
        f[640 - g.shape[0] // 2: 640 + g.shape[0] // 2, W // 2 - g.shape[1] // 2: W // 2 + g.shape[1] // 2] += g * vis
        img = self.light_sweep(pk["img"], (lt - 0.6) / 0.9)
        scale = 0.92 + 0.08 * pin + 0.03 * R.clamp01(lt / (s1 - s0))
        layer, x, y = R.warp_premul(img, scale, W / 2, 940 + (1 - pin) * 80 + pout * 50,
                                    (img.shape[1] / 2, img.shape[0]))
        R.over(f, layer, x, y, vis)
        self.box_in(f, pk["box"], 120, R.clamp01((lt - 0.1) / 0.55), pout)
        # accent marker next to the tag
        dot = pk["dot"]
        R.over(f, dot, W / 2 + pk["box"].shape[1] / 2 + 14, 150, vis)
        cin = R.ease_out((lt - 0.55) / 0.45)
        c = pk["use_chip"]
        R.over(f, c, (W - c.shape[1]) / 2, 962 + (1 - cin) * 16, cin * (1 - pout))
        y = LIST_TOP
        for k, ln in enumerate(pk["lines"]):
            p = R.ease_out((lt - 1.0 - 0.45 * k) / 0.45)
            if p > 0:
                xr = W / 2 + 330  # right-aligned column for RTL reading
                R.over(f, R.rtl_reveal(ln, p, soft=60), xr - ln.shape[1], y + (1 - p) * 14, 1 - pout)
            y += LIST_STEP

    def draw_diff(self, f, t):
        s0, s1 = T_DIFF, T_END
        if not (s0 - 0.05 <= t <= s1 + 0.05):
            return
        lt = t - s0
        pout = R.ease_in_out((t - (s1 - 0.3)) / 0.3)
        self.box_in(f, self.diff_box, 130, R.clamp01(lt / 0.5), pout)
        for k, card in enumerate(self.cards):
            p = R.ease_out((lt - 0.2 - 0.2 * k) / 0.5)
            x = (W / 2 + 15) if k == 0 else (W / 2 - 15 - card.shape[1])  # petrol on the right
            R.over(f, card, x, 380 + (1 - p) * 60, p * (1 - pout))

    def draw_end(self, f, t):
        s0 = T_END
        if t < s0 - 0.05:
            return
        lt = t - s0
        self.box_in(f, self.end_box, 140, R.clamp01(lt / 0.5), 0)
        p = R.ease_out((lt - 0.3) / 0.5)
        if p > 0:
            layer, ux, uy = R.warp_premul(self.url, 0.94 + 0.06 * p, W / 2, 380,
                                          (self.url.shape[1] / 2, self.url.shape[0] / 2))
            R.over(f, layer, ux, uy, p)
        for k, img in enumerate(self.hook_pair):
            pk = R.ease_out((lt - 0.2 - 0.1 * k) / 0.55)
            cx = W / 2 + (240 if k == 0 else -240)
            layer, x, y = R.warp_premul(img, 0.62, cx, 940 + (1 - pk) * 50, (img.shape[1] / 2, img.shape[0]))
            R.over(f, layer, x, y, pk)
        p3 = R.ease_out((lt - 0.8) / 0.5)
        self.centered(f, R.rtl_reveal(self.l2, p3), 1030, 1, dy=(1 - p3) * 16)
        p4 = R.ease_out((lt - 1.0) / 0.5)
        self.centered(f, R.rtl_reveal(self.l3, p4), 1100, 1, dy=(1 - p4) * 16)
        p5 = R.ease_out((lt - 1.3) / 0.45)
        if p5 > 0:
            b = self.badge
            layer, bx, by = R.warp_premul(b, 0.85 + 0.15 * p5, W / 2, 1225, (b.shape[1] / 2, b.shape[0] / 2))
            R.over(f, layer, bx, by, p5)
        p6 = R.ease_out((lt - 1.7) / 0.45)
        self.centered(f, self.nl, 1370, p6, dy=(1 - p6) * 14)

    def frame(self, t):
        f = self.bg.frame(t).astype(np.float32)
        self.draw_hook(f, t)
        for pk in self.packs:
            self.draw_pack(f, t, pk)
        self.draw_diff(f, t)
        self.draw_end(f, t)
        self.draw_falling_drop(f, t)
        self.draw_footer(f, t)
        f *= R.ease_out(t / 0.3)
        return np.clip(f, 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--stills")
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    film = PackFilm()
    import cv2
    if a.stills:
        for s in a.stills.split(","):
            img = film.frame(float(s))
            cv2.imwrite(str(out.parent / f"still_{float(s):05.2f}.png"),
                        cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
        return
    wav = out.with_suffix(".wav")
    soundtrack.write(wav, DURATION, CUTS, T_END)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
           "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.6:level=false",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(int(DURATION * FPS)):
        img = film.frame(n / FPS)
        img = img + (np.random.default_rng(n).random(img.shape, dtype=np.float32) - 0.5) / 255.0
        proc.stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    proc.stdin.close()
    proc.wait()
    wav.unlink(missing_ok=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
