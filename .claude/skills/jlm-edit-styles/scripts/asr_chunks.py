"""Offline chunked transcription with timestamps (Whisper turbo via sherpa-onnx).

    python3 asr_chunks.py MODEL_DIR VIDEO [LANG=ar] [START=0] [END=inf] > transcript.txt

MODEL_DIR holds turbo-encoder.int8.onnx, turbo-decoder.int8.onnx and turbo-tokens.txt.
It comes from the k2-fsa sherpa-onnx GitHub releases (asr-models), archive
sherpa-onnx-whisper-turbo.tar.bz2. The audio is split at the quietest point near every
22 s, and each chunk prints as "[start-end] text". Roughly 35 s of CPU per chunk.
"""
import subprocess
import sys

import numpy as np
import sherpa_onnx

md = sys.argv[1].rstrip("/") + "/"
f = sys.argv[2]
lang = sys.argv[3] if len(sys.argv) > 3 else "ar"
start = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
end = float(sys.argv[5]) if len(sys.argv) > 5 else 1e9

rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=md + "turbo-encoder.int8.onnx", decoder=md + "turbo-decoder.int8.onnx",
    tokens=md + "turbo-tokens.txt", language=lang, task="transcribe", num_threads=8)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.float32)
sr = 16000
total = len(a) / sr

hop = sr // 100
n = len(a) // hop
rms = np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)

t = start
while t < min(total, end) - 0.5:
    target = t + 22
    lo, hi = int((target - 4) * 100), int(min(target + 4, total) * 100)
    cut = target if hi <= lo else (lo + int(np.argmin(rms[lo:hi]))) / 100
    cut = min(cut, total, end)
    st = rec.create_stream()
    st.accept_waveform(sr, a[int(t * sr): int(cut * sr)])
    rec.decode_stream(st)
    print(f"[{t:6.1f}-{cut:6.1f}] {st.result.text.strip()}", flush=True)
    t = cut
