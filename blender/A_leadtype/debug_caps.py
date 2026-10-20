import bpy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=bpy.context.scene;s.frame_set(1)
o=bpy.data.objects["反字阳文_十"]
data={"raw":[{"id":p.index,"mat":p.material_index,"normal":list(p.normal),"z":[o.data.vertices[i].co.z for i in p.vertices]} for p in list(o.data.polygons)[:5]]}
d=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(d);me=e.to_mesh()
data["evaluated_summary"]={str(i):{"count":sum(p.material_index==i for p in me.polygons),"zmin":min(v.co.z for p in me.polygons if p.material_index==i for v in [me.vertices[j] for j in p.vertices]),"zmax":max(v.co.z for p in me.polygons if p.material_index==i for v in [me.vertices[j] for j in p.vertices])} for i in (0,1)}
(ROOT/"debug_caps.json").write_text(json.dumps(data,indent=2),encoding="utf8")
m=bpy.data.materials.new("DEBUG_TOP");m.use_nodes=True
m.node_tree.nodes.clear()
p=m.node_tree.nodes.new("ShaderNodeEmission");p.inputs["Color"].default_value=(.8,0,0,1)
output=m.node_tree.nodes.new("ShaderNodeOutputMaterial")
output.is_active_output=True
m.node_tree.links.new(p.outputs[0],output.inputs["Surface"])
m.diffuse_color=(1,0,0,1)
for ob in bpy.data.objects:
    if ob.name.startswith("反字"):ob.data.materials[1]=m
c=s.camera;c.animation_data_clear();c.data.dof.use_dof=False
c.location=(0,0,.08);c.rotation_euler=(0,0,0);c.data.type="ORTHO";c.data.ortho_scale=.025
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
s.render.filepath=str(ROOT/"review"/"round3"/"debug_top.png")
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/"debug_caps.blend"))
bpy.ops.render.render(write_still=True)
