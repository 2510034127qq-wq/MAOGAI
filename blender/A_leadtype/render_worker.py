"""Render one packed .blend under the queue controller's exclusive GPU lease."""
import bpy
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent
RENDERS=ROOT.parents[1]/"assets"/"renders"
LOCK=RENDERS/".gpu.lock"
args=sys.argv[sys.argv.index("--")+1:]
shot,token=args[:2]
scene=bpy.context.scene
out=RENDERS/("leadtype_"+shot)
frames=out/"frames";frames.mkdir(parents=True,exist_ok=True)
statsfile=ROOT/(shot+"_render_stats.json")
stats=json.loads(statsfile.read_text(encoding="utf8")) if statsfile.exists() else {"shot":shot,"frames":[]}
done={x["frame"]:x for x in stats["frames"]}


def heartbeat():
    owner=json.loads(LOCK.read_text(encoding="utf8"))
    if owner.get("owner")!=token:
        raise RuntimeError("GPU lock owner changed; stop rather than overlap another task.")
    os.utime(LOCK,None)


prefs=bpy.context.preferences.addons["cycles"].preferences
try:
    prefs.compute_device_type="OPTIX";prefs.get_devices()
    if not any(d.type=="OPTIX" for d in prefs.devices):raise RuntimeError("No OptiX device")
except Exception:
    prefs.compute_device_type="CUDA";prefs.get_devices()
for d in prefs.devices:d.use=d.type==prefs.compute_device_type
scene.cycles.device="GPU"
scene.cycles.samples=128;scene.cycles.adaptive_min_samples=32
scene.cycles.adaptive_threshold=.012
scene.cycles.use_denoising=True;scene.cycles.denoiser="OPTIX"
scene.cycles.use_animated_seed=False;scene.cycles.seed=1976
scene.render.resolution_x=1920;scene.render.resolution_y=1080
scene.render.resolution_percentage=100;scene.render.fps=30
scene.render.image_settings.file_format="PNG";scene.render.image_settings.color_mode="RGB"
scene.render.image_settings.color_depth="8"
scene.render.use_persistent_data=True
scene.render.filepath=str(frames)+os.sep
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/f"leadtype_{shot}.blend"))
stats["settings"]={"engine":"Cycles","compute_device":prefs.compute_device_type,"samples":128,
                   "adaptive_min_samples":32,"adaptive_threshold":.012,"denoiser":"OptiX",
                   "animated_seed":False,"seed":1976,"resolution":[1920,1080],"fps":30,
                   "color":"AgX - Medium High Contrast","png":"8-bit RGB"}
heartbeat()
for frame in range(1,scene.frame_end+1):
    p=frames/f"{frame:04d}.png"
    if p.exists() and frame in done:continue
    scene.frame_set(frame);scene.render.filepath=str(p)
    start=time.monotonic()
    bpy.ops.render.render(write_still=True)
    entry={"frame":frame,"seconds":round(time.monotonic()-start,4),"bytes":p.stat().st_size}
    done[frame]=entry;stats["frames"]=[done[f] for f in sorted(done)]
    statsfile.write_text(json.dumps(stats,indent=2),encoding="utf8")
    (ROOT/"render_progress.json").write_text(json.dumps({"shot":shot,"frame":frame,"total":scene.frame_end,
        "seconds":entry["seconds"],"updated_utc":datetime.now(timezone.utc).isoformat()}),encoding="utf8")
    print("FRAME_DONE",shot,frame,entry["seconds"],flush=True)
    if frame%20==0:heartbeat()
if shot=="title":
    heartbeat()
    scene.frame_set(210)
    scene.render.resolution_x=3840;scene.render.resolution_y=2160
    scene.cycles.samples=256;scene.cycles.adaptive_threshold=.008
    scene.render.filepath=str(out/"still_4k.png")
    start=time.monotonic();bpy.ops.render.render(write_still=True)
    stats["still_4k_seconds"]=round(time.monotonic()-start,4)
    stats["still_4k_samples"]=256
    statsfile.write_text(json.dumps(stats,indent=2),encoding="utf8")
heartbeat()
reopen_start=time.monotonic()
bpy.ops.wm.open_mainfile(filepath=str(ROOT/f"leadtype_{shot}.blend"))
scene=bpy.context.scene
scene.frame_set(1)
reopen_dir=ROOT/"review"/"reopened_blend"
reopen_dir.mkdir(parents=True,exist_ok=True)
scene.render.filepath=str(reopen_dir/f"{shot}_0001.png")
bpy.ops.render.render(write_still=True)
stats["reopened_blend_seconds"]=round(time.monotonic()-reopen_start,4)
stats["reopened_frame"]=str(reopen_dir/f"{shot}_0001.png")
statsfile.write_text(json.dumps(stats,indent=2),encoding="utf8")
heartbeat()
print("SHOT_COMPLETE",shot,flush=True)
