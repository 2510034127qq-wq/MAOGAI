import bpy,sys,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
s=bpy.context.scene
out=[]
for o in bpy.data.objects:
    if o.name.startswith("反字"):
        out.append({"name":o.name,"verts":len(o.data.vertices),"faces":len(o.data.polygons),
                    "materials":[m.name for m in o.data.materials],
                    "top_faces":sum(p.material_index==1 for p in o.data.polygons),
                    "area_top":sum(p.area for p in o.data.polygons if p.material_index==1),
                    "z":sorted(set(round(v.co.z,7) for v in o.data.vertices))})
(ROOT/"geometry_inspection.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf8")
s.frame_set(210)
c=s.camera;c.animation_data_clear();c.data.animation_data_clear()
c.location=(0,0,.08);c.rotation_euler=(0,0,0)
c.data.type="ORTHO";c.data.ortho_scale=.025;c.data.dof.use_dof=False
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
s.render.filepath=str(ROOT/"review"/"round2"/"title_top.png")
bpy.ops.render.render(write_still=True)
