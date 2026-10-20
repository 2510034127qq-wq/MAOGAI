"""Automated pacing QA: flag near-empty stretches (dead air) and luminance jumps (flashes).
usage: python tools/qa_video.py video.mp4 [fps=2]"""
import subprocess, sys, json, pathlib
import numpy as np
import imageio_ffmpeg

src = sys.argv[1]
fps = float(sys.argv[2]) if len(sys.argv) > 2 else 2
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 192, 108
raw = subprocess.run([FF, "-loglevel", "error", "-i", src, "-vf", f"fps={fps},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
# content = local contrast after removing the paper's low-frequency mottling
detail = np.array([np.abs(np.diff(f, axis=1)).mean() + np.abs(np.diff(f, axis=0)).mean() for f in fr])
mean = fr.mean(axis=(1, 2))
TL = json.loads((pathlib.Path(__file__).resolve().parents[1] / "video/src/data/timeline.json").read_text(encoding="utf8"))


def where(t):
    for s in TL["scenes"]:
        if s["from"] / 30 <= t < (s["from"] + s["dur"]) / 30:
            return f"{s['id']}+{t - s['from'] / 30:.1f}s"
    return "?"


thr = np.percentile(detail, 8) * 1.15
empty = detail < max(thr, 1.6)
print(f"frames={len(fr)} detail p8={np.percentile(detail, 8):.2f} median={np.median(detail):.2f}")
run = 0
for i, e in enumerate(list(empty) + [False]):
    if e:
        run += 1
    elif run:
        if run / fps >= 1.5:
            t0 = (i - run) / fps
            print(f"EMPTY {t0:6.1f}s–{i / fps:6.1f}s ({run / fps:.1f}s) at {where(t0)}")
        run = 0
for i in range(1, len(mean)):
    if abs(mean[i] - mean[i - 1]) > 40:
        print(f"JUMP  {i / fps:6.1f}s  {mean[i - 1]:.0f}->{mean[i]:.0f} at {where(i / fps)}")
