"""Geometric and framing audit of the final editable scene."""
import bpy, bmesh, json, sys, math
from mathutils import Vector
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent
s=bpy.context.scene
shot="title" if s.frame_end==210 else "poli"
heroes=[o for o in bpy.data.objects if o.type=="EMPTY" and "_主体" in o.name]
report={"shot":shot,"heroes":[],"frames":[],"external_missing":[]}
for parent in sorted(heroes,key=lambda p:p.location.x):
    body=next(c for c in parent.children if c.name.startswith("字身_"))
    glyph=next(c for c in parent.children if c.name.startswith("反字"))
    bm=bmesh.new();bm.from_mesh(glyph.data)
    report["heroes"].append({"name":parent.name,"character":glyph["source_character"],
        "mirrored_x":glyph["mirrored_x"],"body_bbox_mm":[round((max(v.co[i] for v in body.data.vertices)-min(v.co[i] for v in body.data.vertices))*1000,5) for i in range(3)],
        "relief_mm":round(max(v.co.z for v in glyph.data.vertices)*1000,5),
        "nonmanifold_edges":sum(not e.is_manifold for e in bm.edges),
        "top_normal_min_z":min(p.normal.z for p in glyph.data.polygons if all(abs(glyph.data.vertices[i].co.z-.004/6)<1e-7 for i in p.vertices)),
        "positive_volume":bm.calc_volume(signed=True)>0})
    bm.free()
for frame in ([1,55,76,97,150,180,210] if shot=="title" else [1,45,90,135,180]):
    s.frame_set(frame)
    rec={"frame":frame,"objects":[]}
    for parent in sorted(heroes,key=lambda p:p.location.x):
        glyph=next(c for c in parent.children if c.name.startswith("反字"))
        coords=[world_to_camera_view(s,s.camera,glyph.matrix_world@Vector(v)) for v in glyph.bound_box]
        xmin=min(v.x for v in coords);xmax=max(v.x for v in coords)
        ymin=min(v.y for v in coords);ymax=max(v.y for v in coords)
        rec["objects"].append({"character":glyph["source_character"],"bounds_norm":[xmin,ymin,xmax,ymax],
            "inside":xmin>=0 and xmax<=1 and ymin>=0 and ymax<=1,
            "pixel_width":(xmax-xmin)*1920,"pixel_height":(ymax-ymin)*1080})
    report["frames"].append(rec)
for im in bpy.data.images:
    if im.source=="FILE" and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists():
        report["external_missing"].append(im.filepath)
report["packed_images"]=sum(bool(im.packed_file) for im in bpy.data.images)
report["all_heroes_solid"]=all(h["nonmanifold_edges"]==0 and h["positive_volume"] for h in report["heroes"])
(ROOT/f"{shot}_scene_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
if "--readability" in sys.argv:
    out=ROOT/"review"/"readability";out.mkdir(parents=True,exist_ok=True)
    s.render.resolution_percentage=50;s.cycles.samples=64
    for f in [1,55,76,97,150]:
        s.frame_set(f);s.render.filepath=str(out/f"title_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
