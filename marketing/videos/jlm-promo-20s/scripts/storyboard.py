"""Copy, timing and layout for the JLM 20s promo — the single source of truth.

Every on-screen line is short (2–5 words) and stays up for at least 2.2 s, so
the whole script can be read comfortably at an Arabic reading pace of about
2.5 words per second.
"""

FPS = 30
DURATION = 20.0
SIZE = (1080, 1920)  # 9:16 — Reels / TikTok / Shorts / Stories

# JLM palette: graphite + steel carry the frame, gold (the bronze printed on
# the "Premium Grade" label) marks the one thing to read first.
GRAPHITE = (13, 14, 16)
STEEL = (35, 38, 43)
SILVER = (201, 205, 210)
WHITE = (244, 244, 242)
GOLD = (200, 161, 101)
GOLD_HI = (236, 205, 150)

HOOK_END = 3.2
SCENE_LEN = 3.0

HOOK = {
    "headline": [("محرّكك", WHITE), ("قلب", GOLD), ("سيارتك", WHITE)],
    "sub": "امنحه العناية التي يستحقها",
}

# Benefits come from the product labels (5W30/5W40 "Premium Grade Performance
# Oil · Synthetic"; Turbo Pre Lube "Initial turbo start-up · Synthetic oil
# additive · All types of oil · Anti-wear"; Stop Smoke "Reduces exhaust smoke ·
# Improves engine performance · Prolongs service life · petrol, diesel, LPG &
# CNG") and from the ACEA C3 spec (DPF-compatible, mid-SAPS).
PRODUCTS = [
    {
        "asset": "oil_5w30.png",
        "height": 800,
        "tag": "ENDURADRIVE C3  ·  5W-30",
        "watermark": "5W-30",
        "headline": [[("حماية", WHITE), ("تدوم", GOLD), ("طويلًا", WHITE)]],
        "chips": ["زيت اصطناعي", "متوافق مع فلاتر DPF"],
    },
    {
        "asset": "oil_5w40.png",
        "height": 800,
        "tag": "APEXDRIVE  ·  5W-40",
        "watermark": "5W-40",
        "headline": [[("أداء", WHITE), ("في", WHITE), ("القمّة", GOLD)]],
        "chips": ["زيت اصطناعي", "حماية فائقة للمحرّك"],
    },
    {
        "asset": "turbo_prelube.png",
        "height": 880,
        "tag": "TURBO PRE LUBE",
        "watermark": "TURBO",
        "headline": [[("حماية", WHITE), ("التيربو", WHITE)], [("من", GOLD), ("أول", GOLD), ("تشغيل", GOLD)]],
        "chips": ["يمنع التشغيل الجاف", "لكل أنواع الزيوت"],
    },
    {
        "asset": "stop_smoke.png",
        "height": 900,
        "tag": "STOP SMOKE  ·  OIL TREATMENT",
        "watermark": "SMOKE",
        "headline": [[("قلّل", WHITE), ("دخان", GOLD), ("العادم", GOLD)]],
        "chips": ["يحسّن أداء المحرّك", "بنزين · ديزل · غاز"],
    },
]

END_START = HOOK_END + SCENE_LEN * len(PRODUCTS)  # 15.2 s → 4.8 s end card
END = {
    "line1": "زوروا موقعنا",
    "url": "jlmstore.com",
    "line2": "لاكتشاف العديد من المنتجات",
    "line3": "التي يمكنكم طلبها",
    "badge": "مع توفر خدمة التوصيل",
}

# Layout (px, 1080x1920). Bottom 12 % is left clear for the Reels/TikTok UI.
LOGO_Y = 150
TAG_Y = 312
PRODUCT_BOTTOM = 1225
HEADLINE_Y = 1370
CHIPS_Y = 1540


def transitions():
    """Times at which the gold pulse wipes from one scene to the next."""
    return [HOOK_END + SCENE_LEN * i for i in range(len(PRODUCTS) + 1)]
