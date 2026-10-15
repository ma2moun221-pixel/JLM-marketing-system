"""Arabic voice-over — "expert mechanic" read — for the JLM Penetrating Oil film.
Offline Piper (ar_JO kareem, sherpa-onnx), then a deeper / warmer workshop voice chain.

    python3 scripts/voice.py MODEL_DIR

Every sentence is synthesised on its own and PLACED at the cue time its frame's
animation was built around (so reveals stay in sync), never earlier than the end
of the previous sentence. Each frame's file is exactly that frame's duration.
Writes assets/voice/NN.wav and audio_meta.json `voices` (with word timings).
"""
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
import sherpa_onnx

ROOT = Path(__file__).resolve().parents[1]
SPEED = 1.16          # a calm, confident expert pace
MIN_GAP = 0.14

FRAME_DUR = {1: 3.2, 2: 5.16, 3: 11.95, 4: 12.3, 5: 11.16, 6: 10.18, 7: 7.73, 8: 9.51}

# frame → [(cue_s, diacritised sentence)] — cues match the on-screen reveals
LINES = {
    1: [(0.4, "نَصيحَةٌ مِنْ ميكانيكِيّ...")],
    2: [(0.2, "بُرْغِيٌّ عالِقٌ بِالصَّدَأ؟"), (2.3, "إِيّاكَ أَنْ تَكْسِرَه..."), (3.5, "عِنْدي الحَلّ.")],
    3: [(0.2, "هذا زَيْتُ الاخْتِراقِ مِنْ جِيه إِلْ إِمّ."),
        (2.6, "بَخّاخٌ قَوِيٌّ وَمُتَعَدِّدُ الاسْتِخْدامات،"),
        (6.9, "نَسْتَخْدِمُهُ في الوَرْشَةِ لِلصَّدَأِ وَالتَّآكُلِ وَالقِطَعِ المُلْتَصِقَة.")],
    4: [(0.3, "السِّرُّ في تَرْكيبَتِه:"),
        (1.6, "يَتَغَلْغَلُ بِعُمْقٍ بَيْنَ أَسْنانِ البُرْغِي."),
        (5.15, "يُذيبُ الصَّدَأَ بِسُرْعَة،"), (6.2, "وَيَطْرُدُ الرُّطوبَة،"),
        (7.8, "ثُمَّ يُزَيِّتُ القِطْعَةَ وَيَحْميها طَويلًا.")],
    5: [(0.2, "لِهذا هو أَداةٌ أَساسِيَّة،"),
        (1.5, "لِكُلِّ ميكانيكِيٍّ وَمُهَنْدِسٍ وَهاوٍ،"),
        (6.0, "في صِيانَةِ الآلاتِ وَالسَّيّاراتِ وَالمُعَدّاتِ الصِّناعِيَّة.")],
    6: [(0.2, "وَطَريقَةُ اسْتِخْدامِهِ سَهْلَة:"), (1.8, "قُمْ بِرَجِّ العُبْوَةِ جَيِّدًا،"),
        (3.7, "رُشَّ مُباشَرَةً عَلى مَكانِ الصَّدَأ،"), (7.3, "وَاتْرُكْهُ يَشْتَغِلُ بِضْعَ دَقائِق.")],
    7: [(0.4, "اسْتَخْدِمِ العُدَّةَ المُناسِبَةَ لِفَكِّ القِطْعَةِ بِهُدوء،"),
        (4.6, "وَامْسَحِ الزِّيادَة."), (6.0, "بِهذِهِ البَساطَة.")],
    8: [(0.2, "زَيْتُ الاخْتِراقِ مِنْ جِيه إِلْ إِمّ."),
        (2.6, "اطْلُبْهُ الآنَ مِنْ مَتْجَرِنا الإِلِكْتْرونِيّ،"), (5.5, "وَالتَّوْصيلُ مُتَوَفِّر.")],
}

TASHKEEL = set(chr(c) for c in range(0x064B, 0x0653)) | {"ٰ"}

# deeper + warmer "workshop expert": −1 semitone (formant-ish shift via resample),
# body at 140 Hz, presence at 3 kHz, softened sibilance, gentle compression, a short room.
FX = ("asetrate={sr}*0.944,aresample={sr},atempo=1.0593,"
      "equalizer=f=140:t=q:w=1.0:g=3.5,equalizer=f=3000:t=q:w=1.2:g=2.0,"
      "equalizer=f=6800:t=q:w=1.5:g=-2.5,"
      "acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3dB,"
      "aecho=0.9:0.9:21|37:0.06|0.035")


def plain(s):
    return "".join(ch for ch in s if ch not in TASHKEEL)


def voice_fx(x, sr):
    with tempfile.TemporaryDirectory() as d:
        a, b = Path(d) / "a.wav", Path(d) / "b.wav"
        write_wav(a, x, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a), "-af", FX.format(sr=sr), str(b)], check=True)
        with wave.open(str(b)) as w:
            y = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return y


def write_wav(path, y, sr):
    pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wv:
        wv.setnchannels(1)
        wv.setsampwidth(2)
        wv.setframerate(sr)
        wv.writeframes(pcm.tobytes())


def trim(x, sr):
    env = np.abs(x) > 0.01
    i0, i1 = np.argmax(env), len(x) - np.argmax(env[::-1])
    return x[max(0, i0 - int(0.02 * sr)): min(len(x), i1 + int(0.05 * sr))]


def words_in(samples, sr, t0, text):
    hop = sr // 100
    n = max(1, len(samples) // hop)
    rms = np.sqrt((samples[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
    w = np.clip(rms / (np.percentile(rms, 95) + 1e-9), 0, 1) ** 0.6 + 1e-3
    c = np.concatenate([[0], np.cumsum(w)]) / w.sum()
    toks = [t for t in (plain(x).strip("،.؟:…") for x in text.split()) if t]
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
    for frame, lines in LINES.items():
        dur = FRAME_DUR[frame]
        # place each sentence at its cue (or right after the previous one); if the
        # frame overruns, re-synthesise the frame a little faster until it fits
        speed = SPEED
        for _ in range(6):
            clips = []
            for cue, text in lines:
                a = tts.generate(text, sid=0, speed=speed)
                sr = a.sample_rate
                clips.append((cue, text, trim(np.array(a.samples, np.float32), sr)))
            end = 0.0
            for cue, _, x in clips:
                end = max(cue, end + MIN_GAP) + len(x) / sr
            if end <= dur - 0.35:
                break
            speed *= min(1.12, (end + 0.05) / (dur - 0.35))
        y = np.zeros(int(dur * sr), np.float32)
        words, end = [], 0.0
        for cue, text, x in clips:
            t = max(cue, end + MIN_GAP)
            i = int(t * sr)
            m = min(len(x), len(y) - i)
            y[i:i + m] += x[:m]
            words += words_in(x[:m], sr, t, text)
            end = t + m / sr
        y = voice_fx(y, sr)[: int(dur * sr)]
        if len(y) < int(dur * sr):
            y = np.pad(y, (0, int(dur * sr) - len(y)))
        y = y / (np.abs(y).max() + 1e-9) * 0.89
        path = out / f"{frame:02d}.wav"
        write_wav(path, y, sr)
        voices.append({"frame": frame, "path": f"assets/voice/{frame:02d}.wav", "duration_s": dur,
                       "words": [{"id": f"w{frame}_{i}", "text": w, "start": round(s, 3), "end": round(e, 3)}
                                 for i, (w, s, e) in enumerate(words)]})
        print(f"frame {frame}: {dur:.2f}s  speech ends {end:.2f}s  speed {speed:.2f}")
    meta_p = ROOT / "audio_meta.json"
    meta = json.loads(meta_p.read_text()) if meta_p.exists() else {"bgm": None, "sfx": []}
    meta["voices"] = voices
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
