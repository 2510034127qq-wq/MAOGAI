"""Copy assets into video/public and write video/src/data/renders.json.

- scans/*.png              -> public/scans/
- img/<name>_paper.png     -> public/img/
- renders/<shot>/frames/   -> public/renders/<shot>.mp4 (x264 CRF 10, re-encoded only when frames change)
"""
import json, pathlib, shutil, subprocess

import imageio_ffmpeg

ROOT = pathlib.Path(__file__).resolve().parents[1]
PUB = ROOT / "video/public"
FF = imageio_ffmpeg.get_ffmpeg_exe()


def copy_newer(src: pathlib.Path, dst: pathlib.Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
        shutil.copy2(src, dst)


import numpy as np
from PIL import Image


def ink_scan(src: pathlib.Path, dst: pathlib.Path):
    """grey page scan -> RGBA ink layer (#1C1A17, alpha from darkness), so pages sit on our paper"""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        return
    L = np.asarray(Image.open(src).convert("L")).astype(np.float32)
    a = np.clip((232 - L) / (232 - 45), 0, 1) ** 0.85
    rgba = np.zeros(L.shape + (4,), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 0x1C, 0x1A, 0x17
    rgba[..., 3] = (a * 245).astype(np.uint8)
    Image.fromarray(rgba).save(dst)


for p in (ROOT / "assets/scans").glob("p*.png"):
    ink_scan(p, PUB / "scans" / p.name)
copy_newer(ROOT / "assets/scans/cover.png", PUB / "scans/cover.png")

m = {}
for p in sorted((ROOT / "assets/img").glob("*_paper.png")):
    copy_newer(p, PUB / "img" / p.name)
    m["img:" + p.name[: -len("_paper.png")]] = 1

for d in sorted((ROOT / "assets/renders").glob("*/frames")):
    frames = sorted(d.glob("*.png"))
    if not frames:
        continue
    shot = d.parent.name
    out = PUB / "renders" / f"{shot}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    newest = max(f.stat().st_mtime for f in frames)
    if not out.exists() or out.stat().st_mtime < newest:
        subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", "30", "-i", str(d / "%04d.png"), "-c:v", "libx264", "-crf", "10", "-preset", "slow", "-pix_fmt", "yuv420p", str(out)], check=True)
    m[shot] = len(frames)

(ROOT / "video/src/data/renders.json").write_text(json.dumps(m, indent=1), encoding="utf8")
print(m)
