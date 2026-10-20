"""Rename/compress final renders to their Chinese delivery names."""
import os, subprocess, pathlib
import imageio_ffmpeg

OUT = pathlib.Path(__file__).resolve().parents[1] / "video/out"
FF = imageio_ffmpeg.get_ffmpeg_exe()
jobs = [("main_subs.mp4", "论十大关系_研读_字幕版.mp4"), ("main_clean.mp4", "论十大关系_研读_无字幕版.mp4")]
for src, dst in jobs:
    s = OUT / src
    if not s.exists():
        continue
    tmp = OUT / ("_tmp_" + dst)
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(s), "-c:v", "libx264", "-crf", "19", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(tmp)], check=True)
    if s.name != dst:
        s.unlink()
    os.replace(tmp, OUT / dst)
    print(dst, (OUT / dst).stat().st_size // 1048576, "MB")
