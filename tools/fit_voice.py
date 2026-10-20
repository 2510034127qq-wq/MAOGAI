"""Fit the video to recorded narration.

Put one audio file per line in assets/vo/, named by line id (S0_01.wav, B1_07.mp3, ...; ids are in docs/配音稿.md).
This measures each file, writes its length into docs/script.json as "sec", then re-runs timing and asset sync,
so scene beats, subtitles and the narration track all follow the real voice.
"""
import json, pathlib, re, subprocess, sys

import imageio_ffmpeg

ROOT = pathlib.Path(__file__).resolve().parents[1]
VO = ROOT / "assets/vo"
FF = imageio_ffmpeg.get_ffmpeg_exe()


def duration(p: pathlib.Path) -> float:
    err = subprocess.run([FF, "-hide_banner", "-i", str(p)], capture_output=True, text=True, encoding="utf8", errors="replace").stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    if not m:
        raise SystemExit(f"cannot read duration of {p}")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


files = {p.stem: p for p in VO.glob("*") if p.suffix.lower() in (".wav", ".mp3", ".m4a", ".flac")} if VO.exists() else {}
if not files:
    raise SystemExit(f"no narration files in {VO}")

S = json.loads((ROOT / "docs/script.json").read_text(encoding="utf8"))
hit = 0
for sc in S["scenes"]:
    for i, ln in enumerate(sc["lines"]):
        lid = f"{sc['id']}_{i + 1:02d}"
        if lid in files:
            ln["sec"] = round(duration(files[lid]) + 0.05, 3)
            hit += 1
        else:
            ln.pop("sec", None)
(ROOT / "docs/script.json").write_text(json.dumps(S, ensure_ascii=False, indent=2), encoding="utf8")
print(f"fitted {hit} lines; unmatched files: {sorted(set(files) - {f'{s['id']}_{i + 1:02d}' for s in S['scenes'] for i in range(len(s['lines']))})}")
for tool in ("timing.py", "sync_assets.py"):
    subprocess.run([sys.executable, str(ROOT / "tools" / tool)], check=True)
