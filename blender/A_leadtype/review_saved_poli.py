"""Render exactly the three low-resolution review frames from the saved A2 scene."""
from pathlib import Path
import bpy, sys, time
ROOT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['round7']
out=ROOT/'review'/args[0];out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
scene.cycles.device='GPU';scene.render.resolution_percentage=50
scene.cycles.samples=64;scene.cycles.adaptive_min_samples=24
for frame in [1,90,180]:
    scene.frame_set(frame);scene.render.filepath=str(out/f'poli_{frame:04d}.png')
    start=time.monotonic();bpy.ops.render.render(write_still=True)
    print('REVIEW_FRAME',frame,round(time.monotonic()-start,3),flush=True)
