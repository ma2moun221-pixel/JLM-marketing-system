"""Copy, timing and layout for the JLM 20s promo — the single source of truth.

Every on-screen line is short (2–5 words) and stays up for at least 2.2 s, so
the whole script can be read comfortably at an Arabic reading pace of about
2.5 words per second.
"""

FPS = 30
DURATION = 20.0
SIZE = (1080, 1920)  # 9:16 — Reels / TikTok / Shorts / Stories

# JLM Liquid Tools palette (from the ATL templates and official logo files)
CHARCOAL = (37, 39, 41)
CHARCOAL_2 = (48, 50, 53)
YELLOW = (250, 184, 23)
SILVER = (192, 196, 199)
WHITE = (241, 240, 236)
# aliases kept so the copy below reads naturally
GOLD = YELLOW

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
        "height": 760,
        "tag": "ENDURADRIVE C3 · 5W-30",
        "watermark": "5W-30",
        "headline": [[("حماية", WHITE), ("تدوم", GOLD), ("طويلًا", WHITE)]],
        "chips": ["زيت اصطناعي", "متوافق مع فلاتر DPF"],
    },
    {
        "asset": "oil_5w40.png",
        "height": 760,
        "tag": "APEXDRIVE · 5W-40",
        "watermark": "5W-40",
        "headline": [[("أداء", WHITE), ("في", WHITE), ("القمّة", GOLD)]],
        "chips": ["زيت اصطناعي", "حماية فائقة للمحرّك"],
    },
    {
        "asset": "turbo_prelube.png",
        "height": 720,
        "tag": "TURBO PRE LUBE",
        "watermark": "TURBO",
        "headline": [[("حماية", WHITE), ("التيربو", WHITE)], [("من", GOLD), ("أول", GOLD), ("تشغيل", GOLD)]],
        "chips": ["يمنع التشغيل الجاف", "لكل أنواع الزيوت"],
    },
    {
        "asset": "stop_smoke.png",
        "height": 850,
        "tag": "STOP SMOKE",
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

# Layout (px, 1080x1920), mirroring the JLM ATL vertical template:
# headline box on top, product in the middle, yellow footer with the drop.
HEADLINE_Y = 250       # centre of the headline box
PRODUCT_BOTTOM = 1320
CHIPS_Y = 1440
FOOTER_Y = 1565        # top edge of the yellow footer band


def transitions():
    """Times at which the oil drop lands and the scene changes."""
    return [HOOK_END + SCENE_LEN * i for i in range(len(PRODUCTS) + 1)]
