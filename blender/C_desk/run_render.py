"""GPU-lock-aware render coordinator. Run with standard Python, never in Blender."""
from pathlib import Path
import subprocess,sys,json,time,os,datetime
ROOT=Path(__file__).resolve().parent
RENDERS=ROOT.parent.parent/"assets"/"renders"
BLENDER=Path(r"D:\UE\Tools\blender.exe")
LOCK=RENDERS/".gpu.lock"
mode=sys.argv[1] if len(sys.argv)>1 else "review1"
shots=sys.argv[2:] or ["desk_open","desk_close"]
owned=False
RENDERS.mkdir(exist_ok=True,parents=True)
try:
    if mode in ("final","still"):
        while True:
            try:
                with LOCK.open("x",encoding="utf-8") as f:
                    json.dump({"task":"C_desk","time":datetime.datetime.now().isoformat(),"pid":os.getpid()},f)
                owned=True;break
            except FileExistsError:
                if time.time()-LOCK.stat().st_mtime>90*60:
                    LOCK.unlink();continue
                print("GPU_LOCK_WAIT",LOCK.read_text(encoding="utf-8"),flush=True)
                time.sleep(60)
    for shot in shots:
        log=ROOT/(shot+"_"+mode+".log")
        with log.open("w",encoding="utf-8") as out:
            result=subprocess.run([str(BLENDER),"-b",str(ROOT/"C_desk.blend"),"--python",str(ROOT/"render_scene.py"),
                "--",shot,mode],stdout=out,stderr=subprocess.STDOUT)
        if result.returncode:raise RuntimeError(f"Blender failed {result.returncode}; see {log}")
        print("SHOT_COMPLETE",shot,mode,flush=True)
finally:
    if owned and LOCK.exists():
        try:
            if json.loads(LOCK.read_text(encoding="utf-8")).get("pid")==os.getpid():LOCK.unlink()
        except (OSError,ValueError):pass
