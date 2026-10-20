"""受共享GPU锁保护的渲染入口，含断点续渲、计时与锁心跳。"""
import bpy
import os
import json
import time
import sys
import uuid
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parent
RENDERS=ROOT.parents[1]/"assets"/"renders"
LOCK=RENDERS/".gpu.lock"
args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
mode=args[0] if args else "tests"
owner=str(uuid.uuid4())
owned=False


def acquire():
    global owned
    while True:
        try:
            with LOCK.open("x",encoding="utf-8") as f:
                json.dump({"task":"B_steelyard","owner":owner,"pid":os.getpid(),
                           "started_utc":datetime.now(timezone.utc).isoformat()},f)
            owned=True
            print("GPU_LOCK_ACQUIRED",flush=True)
            return
        except FileExistsError:
            try:
                age=time.time()-LOCK.stat().st_mtime
                if age>5400:
                    LOCK.unlink()
                    continue
            except FileNotFoundError:
                continue
            print("WAIT_GPU_LOCK",datetime.now().isoformat(),flush=True)
            time.sleep(60)


def release():
    if owned and LOCK.exists():
        try:
            if json.loads(LOCK.read_text(encoding="utf-8")).get("owner")==owner:
                LOCK.unlink()
        except (OSError,ValueError):
            pass


def render(scene,frame,path,scale=100,samples=None):
    bpy.context.window.scene=scene
    scene.frame_set(frame)
    scene.render.resolution_percentage=scale
    if samples:scene.cycles.samples=samples
    scene.render.filepath=str(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    t=time.perf_counter()
    bpy.ops.render.render(write_still=True)
    elapsed=time.perf_counter()-t
    with (ROOT/"render_times.jsonl").open("a",encoding="utf-8") as f:
        f.write(json.dumps({"scene":scene.name,"frame":frame,"mode":mode,"seconds":elapsed,
                            "path":str(path),"samples":scene.cycles.samples,
                            "resolution":[scene.render.resolution_x*scale//100,
                                          scene.render.resolution_y*scale//100]})+"\n")
    if owned:os.utime(LOCK,None)
    print("FRAME_DONE",scene.name,frame,round(elapsed,3),flush=True)


try:
    prefs=bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type="OPTIX"
    prefs.get_devices()
    for d in prefs.devices:d.use=d.type=="OPTIX"
    b1=bpy.data.scenes["B1 · steelyard_balance"]
    b2=bpy.data.scenes["B2 · steelyard_detail"]
    if mode.startswith("test"):
        # Never more than five <=960x540 test stills per batch.
        folder=ROOT/"review"/mode
        for sc,frame,label in [(b1,1,"B1_0001"),(b1,130,"B1_0130"),(b1,300,"B1_0300"),
                               (b2,1,"B2_0001"),(b2,150,"B2_0150")]:
            render(sc,frame,folder/(label+".png"),50,48)
    elif mode=="final":
        acquire()
        for sc,shot,end,samples in [(b1,"steelyard_balance",300,128),(b2,"steelyard_detail",150,160)]:
            for frame in range(1,end+1):
                path=RENDERS/shot/"frames"/f"{frame:04}.png"
                if path.exists() and path.stat().st_size>10000:
                    print("SKIP_EXISTING",shot,frame,flush=True)
                    continue
                render(sc,frame,path,100,samples)
        b1.render.resolution_x=3840;b1.render.resolution_y=2160
        render(b1,300,RENDERS/"steelyard_balance"/"still_4k.png",100,192)
    elif mode=="still":
        acquire()
        b1.render.resolution_x=3840;b1.render.resolution_y=2160
        render(b1,300,RENDERS/"steelyard_balance"/"still_4k.png",100,192)
    else:
        raise ValueError(mode)
finally:
    release()
