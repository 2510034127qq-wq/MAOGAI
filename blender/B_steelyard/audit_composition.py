import bpy
import json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parent
s=bpy.data.scenes["B1 · steelyard_balance"]
bpy.context.window.scene=s
beam=bpy.data.objects["01 力矩驱动秤杆"]
pan=bpy.data.objects["手工锤打黄铜浅盘 · 实体厚度"]
weight=bpy.data.objects["实心梨形铸铁秤砣"]


def project(v):
    p=world_to_camera_view(s,s.camera,v)
    return (p.x,1-p.y)


def bounds(ob):
    xy=[project(ob.matrix_world @ v.co) for v in ob.data.vertices]
    return [min(p[0] for p in xy),min(p[1] for p in xy),
            max(p[0] for p in xy),max(p[1] for p in xy)]


rows=[]
for f in (1,130,300):
    s.frame_set(f)
    a=project(beam.matrix_world @ Vector((-.13,0,-.023)))
    b=project(beam.matrix_world @ Vector((.62,0,-.023)))
    rows.append({"frame":f,"rod_endpoints":[a,b],"rod_width_fraction":b[0]-a[0],
                 "rod_mid_height_from_top":(a[1]+b[1])/2,"pan_bounds":bounds(pan),"weight_bounds":bounds(weight)})
(ROOT/"composition_audit.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
print("COMPOSITION",json.dumps(rows))
