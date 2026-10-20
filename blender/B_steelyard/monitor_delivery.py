"""监视当前批次并在全部渲染完成后执行编码与技术审核，不获取或修改GPU锁。"""
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
RENDERS=ROOT.parents[1]/"assets"/"renders"
started=time.monotonic()
known_feedback={p.name:p.stat().st_mtime for p in ROOT.glob("FEEDBACK*.md")}

while True:
    counts=[len(list((RENDERS/s/"frames").glob("*.png")))
            for s in ("steelyard_balance","steelyard_detail")]
    data=(ROOT/"render_final.log").read_bytes()
    # PowerShell versions differ in redirection encoding.
    log=data.decode("utf-16" if data.startswith(b"\xff\xfe") else "utf-8-sig",errors="replace")
    still=RENDERS/"steelyard_balance"/"still_4k.png"
    still_complete=False
    if still.exists() and still.stat().st_size>10000:
        with still.open("rb") as f:
            f.seek(-12,2)
            still_complete=f.read()==b"\x00\x00\x00\x00IEND\xaeB`\x82"
    print(f"渲染进度：B1 {counts[0]}/300，B2 {counts[1]}/150，4K静帧 {'完成' if still_complete else '待完成'}。",flush=True)
    for p in ROOT.glob("FEEDBACK*.md"):
        if p.name not in known_feedback or p.stat().st_mtime!=known_feedback[p.name]:
            print("发现更新的导演反馈："+p.name,flush=True)
            known_feedback[p.name]=p.stat().st_mtime
    if counts==[300,150] and still_complete and "Blender quit" in log:
        break
    if "Traceback (most recent call last)" in log or "Error: Cannot read" in log:
        raise RuntimeError("渲染日志记录了错误，请检查 render_final.log。")
    if "Blender quit" in log:
        raise RuntimeError("渲染器已退出，但交付帧尚未齐全。")
    if time.monotonic()-started>10800:
        raise RuntimeError("监视超过3小时，请检查渲染状态；未停止渲染器。")
    time.sleep(30)

print("全部渲染完成，开始联系表、CRF18视频编码和逐帧审核。",flush=True)
subprocess.run([sys.executable,str(ROOT/"finish_delivery.py")],check=True,cwd=ROOT)
print("编码与技术审核完成，等待最终人工看图及播放复核。",flush=True)
