"""Track camera motion (frame -> reference) with ORB + RANSAC partial affine.

Writes transforms.npy: dict frame_index -> 2x3 matrix mapping REFERENCE coords
(1080x1920) to FRAME coords.
"""
import sys, cv2, numpy as np

src, out, ref_t, t0, t1 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
FPS = 30
SC = 0.5  # analysis scale

# polygons in 720x1280 coords -> excluded from feature detection (windows) and the driver area
S = 1080 / 720
SUNROOF = np.array([(0, 0), (720, 0), (720, 285), (400, 305), (160, 328), (0, 205)], np.float32) * S
WINDSHIELD = np.array([(148, 480), (340, 468), (560, 458), (720, 456), (720, 657), (540, 650),
                       (360, 645), (200, 648), (116, 654), (128, 560)], np.float32) * S
DRIVER = np.array([(0, 400), (180, 400), (360, 760), (470, 900), (420, 1010), (0, 1010)], np.float32) * S


def feat_mask(h, w):
    m = np.full((h, w), 255, np.uint8)
    for p in (SUNROOF, WINDSHIELD, DRIVER):
        cv2.fillPoly(m, [(p * SC).astype(np.int32)], 0)
    return m


cap = cv2.VideoCapture(src)
def frame_at(i):
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ok, f = cap.read()
    return f

orb = cv2.ORB_create(4000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING)
ri = int(round(ref_t * FPS))
ref = cv2.cvtColor(cv2.resize(frame_at(ri), None, fx=SC, fy=SC), cv2.COLOR_BGR2GRAY)
mask = feat_mask(*ref.shape)
kr, dr = orb.detectAndCompute(ref, mask)

res = {}
cap.set(cv2.CAP_PROP_POS_FRAMES, int(t0 * FPS))
for i in range(int(t0 * FPS), int(t1 * FPS)):
    ok, f = cap.read()
    if not ok:
        break
    g = cv2.cvtColor(cv2.resize(f, None, fx=SC, fy=SC), cv2.COLOR_BGR2GRAY)
    kf, df = orb.detectAndCompute(g, None)
    ms = [m for m, n in bf.knnMatch(dr, df, k=2) if m.distance < 0.75 * n.distance]
    A = None
    if len(ms) >= 12:
        p0 = np.float32([kr[m.queryIdx].pt for m in ms]) / SC
        p1 = np.float32([kf[m.trainIdx].pt for m in ms]) / SC
        A, inl = cv2.estimateAffinePartial2D(p0, p1, method=cv2.RANSAC, ransacReprojThreshold=6)
        ninl = int(inl.sum()) if inl is not None else 0
    res[i] = A
    if i % 15 == 0:
        print(i, round(i / FPS, 2), len(ms), None if A is None else np.round(A, 3).tolist())
np.save(out, res, allow_pickle=True)
