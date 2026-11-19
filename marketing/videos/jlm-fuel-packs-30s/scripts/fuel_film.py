"""JLM fuel-system cleaners — petrol vs diesel, each product on its own. 30 s, 9:16, Arabic.

    python3 fuel_film.py --out ../out/jlm_fuel_cleaners_30s.mp4 [--stills 2,6,14]

Each product is sold on its own (no bundles in the Palestinian store), so every
can is shown alone, one after another. The benefit points are the client's
lists, translated line by line and never merged: 5 for the petrol range, 9 for
the diesel range.

Reuses the brand engine of ../../jlm-promo-20s/scripts/render.py and the kit in
brand/jlm (charcoal + JLM yellow, ATL headline box, yellow footer, falling drop).
Petrol green / diesel red (from the packaging) appear only on small markers.
"""

import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parents[1] / "jlm-promo-20s" / "scripts"))
import render as R  # noqa: E402
import soundtrack  # noqa: E402
import storyboard as SB  # noqa: E402  (palette)

W, H, FPS = 1080, 1920, 30
DURATION = 30.0
GREEN = (150, 200, 60)
RED = (230, 20, 50)
Y, CH, WH = SB.YELLOW, SB.CHARCOAL, SB.WHITE

# ---------------------------------------------------------------- timeline --
# hook 0–2.6 · petrol 2.6–11 · diesel 11–22 · difference 22–25.6 · end 25.6–30
T_PETROL, T_DIESEL, T_DIFF, T_END = 2.6, 11.0, 22.0, 25.6
CUTS = [T_PETROL, T_DIESEL, T_DIFF, T_END]

HOOK = [[("بنزين", WH), ("أم", WH), ("ديزل؟", Y)]]
HOOK_SUB = "لكل محرّك منتجات تنظيف خاصة من JLM"

# role lines are taken from each can's own label
ROLES = {
    "extreme_clean": ("EXTREME CLEAN", "للتنظيف العميق لنظام الوقود", 720),
    "injector_cleaner": ("INJECTOR CLEANER", "لتنظيف البخاخات والصمامات", 840),
    "fuel_system_cleaner": ("FUEL SYSTEM CLEANER", "للعناية الدورية بنظام الوقود", 840),
}

LINES = [
    {
        "key": "petrol", "accent": GREEN, "start": T_PETROL, "end": T_DIESEL,
        "headline": [[("لمحرّكات", WH), ("البنزين", Y)]], "tag": "PETROL",
        # Complete fuel system cleaning · Lower fuel consumption · Fewer workshop
        # visits · Reduced maintenance costs · Lower repair bills
        "benefits": [
            "تنظيف كامل لنظام الوقود",
            "استهلاك أقل للوقود",
            "زيارات أقل للورشة",
            "تكاليف صيانة أقل",
            "فواتير إصلاح أقل",
        ],
    },
    {
        "key": "diesel", "accent": RED, "start": T_DIESEL, "end": T_DIFF,
        "headline": [[("لمحرّكات", WH), ("الديزل", Y)]], "tag": "DIESEL",
        # Rapid DPF regeneration · Cleans without disassembly · No high revs needed ·
        # Lower fuel consumption · Less ash build-up · Longer filter life ·
        # Fewer workshop visits · Reduced maintenance costs · Lower repair bills
        "benefits": [
            "تجديد سريع لفلتر DPF",
            "تنظيف بدون فك القطع",
            "بدون الحاجة لرفع دورات المحرّك",
            "استهلاك أقل للوقود",
            "تراكم أقل للرماد",
            "عمر أطول للفلتر",
            "زيارات أقل للورشة",
            "تكاليف صيانة أقل",
            "فواتير إصلاح أقل",
        ],
    },
]

DIFF_HEAD = [[("ما", WH), ("الفرق؟", Y)]]
DIFF = [  # (label, accent, lines) — lines are points from the client's lists
    ("بنزين", GREEN, ["تنظيف كامل", "لنظام الوقود"]),
    ("ديزل", RED, ["تجديد سريع لفلتر DPF", "عمر أطول للفلتر"]),
]
END_HEAD = [[("زوروا", WH), ("موقعنا", WH)]]
END_L2 = "لاكتشاف العديد من المنتجات"
END_L3 = "التي يمكنكم طلبها"
END_BADGE = "مع توفر خدمة التوصيل"

# layout — two columns like the BTL templates: product large on the left,
# name / role / points in a right-aligned column (read first in RTL)
BOX_TOP = 118
PRODUCT_CX = 262
PRODUCT_BOTTOM = 1340
TEXT_RIGHT = 1032
NAME_Y = 470
ROLE_Y = 532
RULE_Y = 578
LIST_TOP = 612
LIST_STEP = 56
LIST_RIGHT = TEXT_RIGHT


def accent_dot(color, r=11):
    s = 4
    img = Image.new("RGBA", ((2 * r + 2) * s, (2 * r + 2) * s), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse([s, s, (2 * r + 1) * s, (2 * r + 1) * s], fill=tuple(color) + (255,))
    return R.to_premul(np.array(img.resize((2 * r + 2, 2 * r + 2), Image.LANCZOS)))


def benefit_line(T, text):
    """Arabic benefit with a small yellow drop bullet on its right (RTL)."""
    txt = T.line([(text, WH)], 42, bold=False, shadow=False, pad=0)
    drop, _ = R.drop_layer(12, Y)
    gap = 16
    h = max(txt.shape[0], drop.shape[0])
    out = np.zeros((h, txt.shape[1] + gap + drop.shape[1], 4), np.float32)
    R.paste_into(out, txt, 0, (h - txt.shape[0]) // 2)
    R.paste_into(out, drop, txt.shape[1] + gap, (h - drop.shape[0]) // 2)
    return out


def diff_card(T, label, color, lines):
    """Card: big drop in the line's accent colour, label, and its key points."""
    cw, chh = 470, 700
    out = np.zeros((chh, cw, 4), np.float32)
    R.paste_into(out, R.solid(cw - 8, chh - 8, SB.CHARCOAL_2, 0.9), 4, 4)
    R.paste_into(out, R.box_frame(cw, chh, Y, stroke=4), 0, 0)
    drop, (ax, ay) = R.drop_layer(95, color)
    R.paste_into(out, drop, int(cw / 2 - ax), int(300 - ay))
    lab = T.line([(label, color)], 72, shadow=False, pad=0)
    R.paste_into(out, lab, (cw - lab.shape[1]) // 2, 420)
    y = 520
    for ln in lines:
        l = T.line([(ln, WH)], 42, bold=False, shadow=False, pad=0)
        R.paste_into(out, l, (cw - l.shape[1]) // 2, y)
        y += 60
    return out


class FuelFilm:
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
        self.glow = R.build_glow(380, WH, 0.07)
        assets = HERE.parent / "assets"

        def load(name, h):
            im = Image.open(assets / name).convert("RGBA")
            hi = int(h * 1.08)
            im = im.resize((int(im.width * hi / im.height), hi), Image.LANCZOS)
            return R.to_premul(np.array(im)), h / hi

        self.lines = []
        for ln in LINES:
            prods = []
            for key, (latin, role, h) in ROLES.items():
                img, base = load(f"{ln['key']}_{key}.png", h)
                prods.append({
                    "img": img, "base": base,
                    "name": R.latin_layer(latin, 40, Y, 900, 0.04),
                    "role": T.line([(role, WH)], 40, bold=False, shadow=False, pad=0),
                })
            box, _ = R.headline_box(T, ln["headline"], ln["tag"])
            self.lines.append({**ln, "box": box, "prods": prods, "dot": accent_dot(ln["accent"]),
                               "rows": [benefit_line(T, b) for b in ln["benefits"]]})
        # hook: one can from each range, petrol on the right (read first)
        self.hook_box, _ = R.headline_box(T, HOOK, None)
        self.hook_sub = T.line([(HOOK_SUB, WH)], 52, bold=False)
        self.hook_cans = [load("petrol_fuel_system_cleaner.png", 720), load("diesel_fuel_system_cleaner.png", 720)]
        self.diff_box, _ = R.headline_box(T, DIFF_HEAD, None)
        self.cards = [diff_card(T, *d) for d in DIFF]
        self.end_box, _ = R.headline_box(T, END_HEAD, None)
        self.url = R.latin_layer("jlmstore.com", 112, Y, 900, 0.0)
        self.l2 = T.line([(END_L2, WH)], 50, bold=False)
        self.l3 = T.line([(END_L3, WH)], 50, bold=False)
        self.badge = R.badge(T, END_BADGE)
        self.nl = R.image_layer(kit / "labels" / "made_in_nl.png", 340)
        # end line-up: the six cans, each on its own, petrol trio on the right
        self.lineup = []
        for line in ("diesel", "petrol"):
            for key in ("fuel_system_cleaner", "injector_cleaner", "extreme_clean"):
                h = 300 if key != "extreme_clean" else 262
                im = Image.open(assets / f"{line}_{key}.png").convert("RGBA")
                im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
                self.lineup.append(R.to_premul(np.array(im)))

    draw_footer = R.Film.draw_footer
    draw_falling_drop = R.Film.draw_falling_drop
    centered = R.Film.centered
    box_in = R.Film.box_in
    light_sweep = R.Film.light_sweep

    # ---- scenes
    def draw_hook(self, f, t):
        if t > T_PETROL + 0.05:
            return
        out = R.ease_in_out((t - (T_PETROL - 0.32)) / 0.3)
        self.box_in(f, self.hook_box, 330, R.clamp01((t - 0.15) / 0.55), out)
        for k, (img, base) in enumerate(self.hook_cans):
            p = R.ease_out((t - 0.3 - 0.15 * k) / 0.6)
            side = 1 if k == 0 else -1
            cx = W / 2 + side * 210 + side * (1 - p) * 300
            layer, x, y = R.warp_premul(img, base, cx, 1230, (img.shape[1] / 2, img.shape[0]))
            R.over(f, layer, x, y, p * (1 - out))
            dot = self.lines[k]["dot"]
            R.over(f, dot, cx - dot.shape[1] / 2, 1255, p * (1 - out))
        p2 = R.ease_out((t - 0.9) / 0.5)
        self.centered(f, R.rtl_reveal(self.hook_sub, p2), 1370, 1 - out, dy=(1 - p2) * 18)

    def draw_line(self, f, t, ln):
        s0, s1 = ln["start"], ln["end"]
        if not (s0 - 0.05 <= t <= s1 + 0.05):
            return
        lt = t - s0
        pout = R.ease_in_out((t - (s1 - 0.3)) / 0.3)
        vis_sec = 1 - pout
        g = self.glow
        R.add_light(f, g, PRODUCT_CX - g.shape[1] // 2, 920 - g.shape[0] // 2, vis_sec)
        self.box_in(f, ln["box"], BOX_TOP, R.clamp01((lt - 0.05) / 0.55), pout)
        dot = ln["dot"]
        R.over(f, dot, W / 2 + ln["box"].shape[1] / 2 + 14, BOX_TOP + 40, R.clamp01(lt / 0.4) * vis_sec)

        # products: one at a time, equal share of the section
        n = len(ln["prods"])
        slot = (s1 - s0) / n
        for k, pr in enumerate(ln["prods"]):
            a0 = s0 + k * slot
            a1 = a0 + slot
            if not (a0 - 0.05 <= t <= a1 + 0.05):
                continue
            pl = t - a0
            pin = R.ease_out(pl / 0.45) if k > 0 else R.ease_out(pl / 0.55)
            pend = R.ease_in_out((t - (a1 - 0.28)) / 0.28)
            vis = pin * (1 - pend)
            img = self.light_sweep(pr["img"], (pl - 0.35) / 0.8)
            scale = pr["base"] * (0.93 + 0.07 * pin + 0.03 * R.clamp01(pl / slot))
            # incoming rises in from the left edge, outgoing sinks and fades
            cx = PRODUCT_CX - (1 - pin) * 140
            layer, x, y = R.warp_premul(img, scale, cx, PRODUCT_BOTTOM + (1 - pin) * 30 + pend * 40,
                                        (img.shape[1] / 2, img.shape[0]))
            R.over(f, layer, x, y, vis)
            nin = R.ease_out((pl - 0.15) / 0.4)
            nm, rl = pr["name"], pr["role"]
            R.over(f, nm, TEXT_RIGHT - nm.shape[1], NAME_Y - nm.shape[0] / 2 + (1 - nin) * 10, nin * (1 - pend))
            R.over(f, R.rtl_reveal(rl, R.ease_out((pl - 0.25) / 0.45)), TEXT_RIGHT - rl.shape[1],
                   ROLE_Y - rl.shape[0] / 2 + (1 - nin) * 10, 1 - pend)
        # short yellow rule between the product's name and the line's points
        rw = int(120 * R.ease_out((lt - 0.4) / 0.4))
        if rw > 1:
            f[RULE_Y:RULE_Y + 4, TEXT_RIGHT - rw:TEXT_RIGHT] = R.rgb01(Y) * vis_sec + f[RULE_Y:RULE_Y + 4, TEXT_RIGHT - rw:TEXT_RIGHT] * (1 - vis_sec)

        # the line's benefit points build up once and stay for the whole section
        for k, row in enumerate(ln["rows"]):
            p = R.ease_out((lt - 0.7 - 0.42 * k) / 0.42)
            if p > 0:
                R.over(f, R.rtl_reveal(row, p, soft=60), LIST_RIGHT - row.shape[1],
                       LIST_TOP + k * LIST_STEP + (1 - p) * 12, vis_sec)

    def draw_diff(self, f, t):
        s0, s1 = T_DIFF, T_END
        if not (s0 - 0.05 <= t <= s1 + 0.05):
            return
        lt = t - s0
        pout = R.ease_in_out((t - (s1 - 0.3)) / 0.3)
        self.box_in(f, self.diff_box, 150, R.clamp01(lt / 0.5), pout)
        for k, card in enumerate(self.cards):
            p = R.ease_out((lt - 0.2 - 0.2 * k) / 0.5)
            x = (W / 2 + 12) if k == 0 else (W / 2 - 12 - card.shape[1])  # petrol on the right
            R.over(f, card, x, 420 + (1 - p) * 60, p * (1 - pout))

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
        gap, mid_gap = 22, 60
        widths = [a.shape[1] for a in self.lineup]
        total = sum(widths) + gap * 4 + mid_gap
        x = (W - total) / 2
        base = 860
        for k, a in enumerate(self.lineup):
            pk = R.ease_out((lt - 0.15 - 0.06 * k) / 0.5)
            R.over(f, a, x, base - a.shape[0] + (1 - pk) * 50, pk)
            x += a.shape[1] + (mid_gap if k == 2 else gap)
        p3 = R.ease_out((lt - 0.8) / 0.5)
        self.centered(f, R.rtl_reveal(self.l2, p3), 960, 1, dy=(1 - p3) * 16)
        p4 = R.ease_out((lt - 1.0) / 0.5)
        self.centered(f, R.rtl_reveal(self.l3, p4), 1030, 1, dy=(1 - p4) * 16)
        p5 = R.ease_out((lt - 1.3) / 0.45)
        if p5 > 0:
            b = self.badge
            layer, bx, by = R.warp_premul(b, 0.85 + 0.15 * p5, W / 2, 1160, (b.shape[1] / 2, b.shape[0] / 2))
            R.over(f, layer, bx, by, p5)
        p6 = R.ease_out((lt - 1.65) / 0.45)
        self.centered(f, self.nl, 1320, p6, dy=(1 - p6) * 14)

    def frame(self, t):
        f = self.bg.frame(t).astype(np.float32)
        self.draw_hook(f, t)
        for ln in self.lines:
            self.draw_line(f, t, ln)
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
    film = FuelFilm()
    if a.stills:
        for s in a.stills.split(","):
            img = film.frame(float(s))
            cv2.imwrite(str(out.parent / f"still_{float(s):05.2f}.png"),
                        cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
        return
    wav = out.with_suffix(".wav")
    soundtrack.write(wav, DURATION, CUTS, T_END)
    tmp = out.with_name(out.stem + "_tmp.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
           "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
           "-af", "loudnorm=I=-14:TP=-2:LRA=9,alimiter=limit=0.66:level=false",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(tmp)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(int(DURATION * FPS)):
        img = film.frame(n / FPS)
        img = img + (np.random.default_rng(n).random(img.shape, dtype=np.float32) - 0.5) / 255.0
        proc.stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    proc.stdin.close()
    proc.wait()
    # hard cap at 30.0 s (AAC priming otherwise adds a few ms)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-t", "29.98", "-c", "copy",
                    "-movflags", "+faststart", str(out)], check=True)
    tmp.unlink(missing_ok=True)
    wav.unlink(missing_ok=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
