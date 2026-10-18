"""Cabin geometry of the Audi in IMG_4318 (reference frame t=12.0 s, 1080x1920)."""
import numpy as np

SUNROOF = np.array([(-120, -150), (1200, -150), (1200, 422), (1080, 424), (800, 439), (600, 454),
                    (400, 471), (205, 487), (0, 293), (-120, 200)], np.float32)
WINDSHIELD = np.array([(212, 727), (400, 713), (560, 706), (800, 695), (1080, 690), (1200, 690),
                       (1200, 961), (1080, 962), (780, 959), (480, 962), (250, 965), (205, 965),
                       (200, 900)], np.float32)
WHEEL_C, WHEEL_R = (375.0, 1068.0), 136.0          # steering-wheel rim (outer) + margin
SCREEN = np.array([(581, 941), (770, 941), (770, 1000), (581, 1000)], np.float32)
MIRROR = np.array([(632, 690), (698, 690), (700, 766), (748, 768), (752, 800), (738, 821), (582, 822),
                   (568, 802), (572, 768), (630, 766)], np.float32)
# zones where dark / skin pixels inside the glass are real foreground
PROTECT = [np.array([(-120, 560), (245, 560), (245, 1100), (-120, 1100)], np.float32),   # head / neck / hand
           np.array([(200, 880), (560, 880), (560, 1100), (200, 1100)], np.float32)]     # wheel + hands
