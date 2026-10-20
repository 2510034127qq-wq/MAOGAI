"""对保存的 .blend 做独立检查：逐帧绳长、重力姿态、镜头和最终姿态。"""
import bpy
import json
import math
import bmesh
import numpy as np
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
scene=bpy.data.scenes["B1 · steelyard_balance"]
detail=bpy.data.scenes["B2 · steelyard_detail"]
records=[]
objects={name:bpy.data.objects[name] for name in (
    "01 力矩驱动秤杆","02 重力竖直 · 秤盘与齿轮",
    "03 可沿杆滑动 · 麻绳套","04 重力竖直 · 铸铁秤砣")}
rope_objects=[o for o in scene.objects if o.type=="MESH" and "捻股" in o.name]
baseline={}
for o in rope_objects:
    # Each 8-sided cross section's center recovers the strand centerline.
    centers=[sum((v.co for v in o.data.vertices[i:i+8]),Vector())/8
             for i in range(0,len(o.data.vertices),8)]
    baseline[o.name]=sum((b-a).length for a,b in zip(centers,centers[1:]))
max_scale_error=0
min_loop_clearance=1
loop_meshes=[o for o in rope_objects if o.name.startswith("可滑动闭合麻绳套")]
loop_vertices={o.name:np.array([(*v.co,1) for v in o.data.vertices]) for o in loop_meshes}
for f in range(1,301):
    scene.frame_set(f)
    for o in rope_objects:
        scale=o.matrix_world.to_scale()
        err=max(abs(v-1) for v in scale)
        max_scale_error=max(max_scale_error,err)
        assert err<1e-6,(f,o.name,scale)
        assert len(o.modifiers)==0,(f,o.name,"绳体具有未检查的变形修改器")
    beam_inverse=objects["01 力矩驱动秤杆"].matrix_world.inverted()
    for o in loop_meshes:
        transform=np.array(beam_inverse @ o.matrix_world)
        q=loop_vertices[o.name] @ transform.T
        radius=1.15*(.012-(q[:,0]+.13)/.75*.0055)
        gap=np.sqrt(q[:,1]**2+(q[:,2]+.023)**2)-radius
        min_loop_clearance=min(min_loop_clearance,float(gap.min()))
    records.append({"frame":f,"pan_deg":math.degrees(objects["02 重力竖直 · 秤盘与齿轮"].rotation_euler.y),
                    "weight_deg":math.degrees(objects["04 重力竖直 · 铸铁秤砣"].rotation_euler.y),
                    "beam_deg":-math.degrees(objects["01 力矩驱动秤杆"].rotation_euler.y)})
    # The suspended pan and weight must not inherit the beam's full rotation.
    assert abs(records[-1]["pan_deg"])<1
    assert abs(records[-1]["weight_deg"])<2
    assert max(abs(a) for a in objects["03 可沿杆滑动 · 麻绳套"].rotation_euler)<1e-8
assert min_loop_clearance>-.0002,("绳套穿杆超过接触容差",min_loop_clearance)
solid=bpy.data.objects["实心梨形铸铁秤砣"]
bm=bmesh.new();bm.from_mesh(solid.data)
nonmanifold=sum(not e.is_manifold for e in bm.edges)
solid_volume=bm.calc_volume(signed=True)
bm.free()
assert nonmanifold==0 and solid_volume>0,("秤砣必须闭合实心",nonmanifold,solid_volume)
scene.frame_set(300)
saved_matrices={o.name:o.matrix_world.copy() for o in objects.values()}
bpy.context.window.scene=detail
detail.frame_set(150)
bpy.context.view_layer.update()
frozen=[]
for original in objects.values():
    copy=bpy.data.objects[original.name+".001"]
    difference=max(abs(a-b) for ra,rb in zip(saved_matrices[original.name],copy.matrix_world) for a,b in zip(ra,rb))
    assert difference<1e-6,(original.name,difference)
    frozen.append({"object":original.name,"matrix_error":difference})
bpy.context.window.scene=scene
scene.frame_set(1)
start_cam=scene.camera.location.copy()
scene.frame_set(300)
end_cam=scene.camera.location.copy()
manifest=json.loads((ROOT/"scene_manifest.json").read_text(encoding="utf-8"))
target=Vector(manifest["B1_target"])
initial_target=Vector(manifest["B1_initial_target"])
ratio=(end_cam-target).length/(start_cam-initial_target).length
assert abs(ratio-.94)<1e-6
detail.frame_set(1)
d0=detail.camera.location.copy()
detail.frame_set(150)
d1=detail.camera.location.copy()
assert abs(d0.y-d1.y)<1e-6 and abs(d0.z-d1.z)<1e-6
external=[i.filepath for i in bpy.data.images if i.source=="FILE" and not i.packed_file]
assert not external,external
out={"all_passed":True,"frames_checked":300,"rope_strands_checked":len(rope_objects),
     "constant_strand_lengths_m":baseline,"max_world_scale_error":max_scale_error,
     "max_pan_tilt_deg":max(abs(r["pan_deg"]) for r in records),
     "max_weight_tilt_deg":max(abs(r["weight_deg"]) for r in records),
     "frozen_B2_matches_B1_frame300":frozen,"B1_camera_distance_ratio":ratio,
     "B2_camera_translation_m":list(d1-d0),"missing_external_images":external,
     "weight_rope_loop_vertical_all_frames":True,
     "weight_loop_min_wood_clearance_m":min_loop_clearance,
     "contact_tolerance_m":.0002,
     "solid_weight_nonmanifold_edges":nonmanifold,
     "solid_weight_net_volume_m3":solid_volume,
     "note":"逐帧检查刚性绳体长度、悬挂姿态及相机连续性；不将这些检查冒充通用碰撞求解。"}
(ROOT/"rig_audit.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print("RIG_AUDIT_PASSED",len(rope_objects),ratio)
