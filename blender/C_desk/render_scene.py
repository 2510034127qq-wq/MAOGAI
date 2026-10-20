"""Render an existing scene, recording real wall times and refreshing owned GPU lock."""
import bpy, sys, time, json, os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index("--")+1:]
shot=args[0];mode=args[1]
scene=bpy.data.scenes[shot];bpy.context.window.scene=scene
prefs=bpy.context.preferences.addons["cycles"].preferences
try:prefs.compute_device_type="OPTIX";prefs.get_devices()
except Exception:prefs.compute_device_type="CUDA";prefs.get_devices()
for d in prefs.devices:d.use=d.type in ("OPTIX","CUDA")
scene.cycles.device="GPU"
if mode.startswith("review"):
    scene.render.resolution_percentage=50;scene.cycles.samples=40
    frames=[1,(scene.frame_end+1)//2,scene.frame_end]
    out=ROOT/mode/shot
elif mode=="still":
    scene.render.resolution_percentage=200;scene.cycles.samples=144;scene.cycles.adaptive_threshold=.009
    frames=[scene.frame_end];out=ROOT.parent.parent/"assets"/"renders"/shot
else:
    frames=range(int(args[2]) if len(args)>2 else 1,scene.frame_end+1)
    out=ROOT.parent.parent/"assets"/"renders"/shot/"frames"
out.mkdir(parents=True,exist_ok=True)
log=ROOT/(shot+"_"+mode+"_timings.jsonl")
lock=ROOT.parent.parent/"assets"/"renders"/".gpu.lock"
for fr in frames:
    scene.frame_set(fr)
    dst=out/("still_4k.png" if mode=="still" else f"{fr:04}.png")
    if mode=="final" and dst.exists():continue
    scene.render.filepath=str(dst)
    start=time.perf_counter()
    bpy.ops.render.render(write_still=True)
    elapsed=time.perf_counter()-start
    with log.open("a",encoding="utf-8") as f:f.write(json.dumps({"frame":fr,"seconds":elapsed,"file":str(dst)})+"\n")
    print("FRAME_COMPLETE",shot,mode,fr,round(elapsed,3),flush=True)
    if mode in ("final","still") and lock.exists():
        try:
            if json.loads(lock.read_text(encoding="utf-8")).get("task")=="C_desk":os.utime(lock,None)
        except (OSError,ValueError):pass
print("RENDER_COMPLETE",shot,mode,flush=True)
