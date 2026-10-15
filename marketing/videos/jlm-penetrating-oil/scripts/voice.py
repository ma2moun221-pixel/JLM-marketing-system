"""Arabic voice-over for the JLM Penetrating Oil film — offline Piper (ar_JO kareem, sherpa-onnx).

    python3 scripts/voice.py MODEL_DIR

Writes assets/voice/NN.wav per narrated frame (0.30 s lead-in, 0.45 s tail) and
audio_meta.json `voices` with per-word timings. Each sentence is synthesised on
its own so pauses are real; word starts inside a sentence follow the voiced
energy (same method as the JLM footage edits).
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np
import sherpa_onnx

ROOT = Path(__file__).resolve().parents[1]
SPEED = 1.28
LEAD, TAIL, GAP = 0.25, 0.40, 0.18

# frame → sentences (diacritised for the TTS; display text has no tashkeel)
LINES = {
    2: ["بُرْغِيٌّ عالِقٌ بِسَبَبِ الصَّدَأ؟", "قَبْلَ أَنْ تَكْسِرَهُ... هُناكَ حَلٌّ أَذْكى."],
    3: ["زَيْتُ الاخْتِراقِ مِنْ جِيه إِلْ إِمّ.",
        "بَخّاخُ اخْتِراقٍ عالي الأَداءِ وَمُتَعَدِّدُ الاسْتِخْدامات،",
        "لِمُعالَجَةِ الصَّدَأِ وَالتَّآكُلِ وَالأَجْزاءِ المُلْتَصِقَةِ بِسُهولَة."],
    4: ["تَرْكيبَتُهُ القَوِيَّةُ تَخْتَرِقُ البَراغِيَ وَالصَّوامِيلَ الصَّدِئَةَ بِعُمْق.",
        "تُذيبُ الصَّدَأَ، وَتَطْرُدُ الرُّطوبَة،",
        "وَتَمْنَحُ تَزْييتًا فائِقًا، وَحِمايَةً طَويلَةَ الأَمَد."],
    5: ["أَداةٌ أَساسِيَّةٌ لِلْميكانيكِيّينَ وَالمُهَنْدِسينَ وَهُواةِ الأَعْمالِ اليَدَوِيَّة،",
        "لِصِيانَةِ وَإِصْلاحِ الآلاتِ وَالمَرْكَباتِ وَالمُعَدّاتِ الصِّناعِيَّة."],
    6: ["طَريقَةُ الاسْتِخْدام:", "قُمْ بِرَجِّ العُبْوَةِ جَيِّدًا.",
        "رُشَّ الزَّيْتَ مُباشَرَةً عَلى المِنْطَقَةِ المُسْتَهْدَفَة.",
        "وَاتْرُكْهُ يَتَغَلْغَلُ بِضْعَ دَقائِق."],
    7: ["ثُمَّ اسْتَخْدِمِ الأَدَواتِ المُناسِبَةَ لِفَكِّ الأَجْزاءِ بِعِنايَة،", "وَقُمْ بِمَسْحِ أَيِّ زَوائِدَ مِنَ المُنْتَج."],
    8: ["زَيْتُ الاخْتِراقِ مِنْ جِيه إِلْ إِمّ.",
        "اطْلُبْهُ الآنَ مِنْ مَتْجَرِنا الإِلِكْتْرونِيّ،", "مَعَ تَوَفُّرِ خِدْمَةِ التَّوْصيل."],
}

TASHKEEL = set(chr(c) for c in range(0x064B, 0x0653)) | {"ٰ"}


def plain(s):
    return "".join(ch for ch in s if ch not in TASHKEEL)


def words_in(samples, sr, t0, text):
    """Word starts by cumulative voiced energy (10 ms frames)."""
    hop = sr // 100
    n = len(samples) // hop
    rms = np.sqrt((samples[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
    w = np.clip(rms / (np.percentile(rms, 95) + 1e-9), 0, 1) ** 0.6 + 1e-3
    c = np.concatenate([[0], np.cumsum(w)]) / w.sum()
    toks = [plain(x).strip("،.؟:…") for x in text.split()]
    toks = [x for x in toks if x]
    lens = np.array([len(x) + 1 for x in toks], float)
    acc = np.concatenate([[0], np.cumsum(lens)]) / lens.sum()
    starts = [t0 + np.searchsorted(c, a) / 100 for a in acc]
    return [(toks[i], starts[i], starts[i + 1]) for i in range(len(toks))]


def main():
    md = Path(sys.argv[1])
    cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=str(md / "ar_JO-kareem-medium.onnx"),
                                                   tokens=str(md / "tokens.txt"),
                                                   data_dir=str(md / "espeak-ng-data")),
        num_threads=4))
    tts = sherpa_onnx.OfflineTts(cfg)
    out = ROOT / "assets/voice"
    out.mkdir(parents=True, exist_ok=True)
    voices = []
    for frame, sents in LINES.items():
        sr = None
        pieces = [None]
        words = []
        t = LEAD
        for k, s in enumerate(sents):
            a = tts.generate(s, sid=0, speed=SPEED)
            sr = a.sample_rate
            x = np.array(a.samples, np.float32)
            # trim synthesis silence at both ends
            env = np.abs(x) > 0.01
            i0, i1 = np.argmax(env), len(x) - np.argmax(env[::-1])
            x = x[max(0, i0 - int(0.02 * sr)): min(len(x), i1 + int(0.04 * sr))]
            words += words_in(x, sr, t, s)
            pieces.append(x)
            t += len(x) / sr
            if k < len(sents) - 1:
                pieces.append(np.zeros(int(GAP * sr), np.float32))
                t += GAP
        pieces[0] = np.zeros(int(LEAD * sr), np.float32)
        pieces.append(np.zeros(int((TAIL + (1.4 if frame == max(LINES) else 0)) * sr), np.float32))  # hold the CTA
        y = np.concatenate(pieces)
        y = y / (np.abs(y).max() + 1e-9) * 0.89
        path = out / f"{frame:02d}.wav"
        pcm = (y * 32767).astype(np.int16)
        with wave.open(str(path), "wb") as wv:
            wv.setnchannels(1)
            wv.setsampwidth(2)
            wv.setframerate(sr)
            wv.writeframes(pcm.tobytes())
        dur = round(len(y) / sr, 2)
        voices.append({"frame": frame, "path": f"assets/voice/{frame:02d}.wav", "duration_s": dur,
                       "words": [{"id": f"w{frame}_{i}", "text": w, "start": round(s, 3), "end": round(e, 3)}
                                 for i, (w, s, e) in enumerate(words)]})
        print(f"frame {frame}: {dur:.2f}s  {len(words)} words")
    meta_p = ROOT / "audio_meta.json"
    meta = json.loads(meta_p.read_text()) if meta_p.exists() else {"bgm": None, "sfx": []}
    meta["voices"] = voices
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
