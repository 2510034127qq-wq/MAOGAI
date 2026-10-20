"""Read-only geometry, camera, source-crop, packing and contact audit."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent
result={"blender":bpy.app.version_string,"scenes":{}}
ocr=json.loads((ROOT.parent.parent/"assets"/"scans"/"ocr_boxes.json").read_text(encoding="utf-8"))
result["scan_text_inside_crop"]={}
for p in ("p06","p07"):
    result["scan_text_inside_crop"][p]=all(22<=x<=1452 and 45<=y<=2069 for l in ocr[p]["lines"] for x,y in l["box"])
result["packed_images"]={i.name:bool(i.packed_file) for i in bpy.data.images if i.source=="FILE"}
for scene in bpy.data.scenes:
    bpy.context.window.scene=scene
    scene.frame_set(1)
    dg=bpy.context.evaluated_depsgraph_get()
    meshes=[o for o in scene.objects if o.type=="MESH"]
    pages=[o for o in meshes if ("leaf" in o.name or "paper sheet" in o.name or "front cover" in o.name)]
    finite=all(math.isfinite(v) for o in meshes for vert in o.data.vertices for v in vert.co)
    normals_ok=all(p.normal.z>.5 for o in pages for p in o.data.polygons)
    # BVH of table and paper surfaces, in world coordinates, for pencil clearance.
    surfaces=[o for o in meshes if o in pages or o.name.startswith("Elm grain top surface")]
    trees=[]
    for o in surfaces:
        ev=o.evaluated_get(dg);me=ev.to_mesh()
        trees.append(BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]))
        ev.to_mesh_clear()
    pencil=next(o for o in meshes if o.name.startswith("Six-sided red lacquer pencil"))
    gaps=[];gap_samples=[]
    # Include interpolated axial samples on each of the six face ridges.
    for k in range(6):
        a=k*math.pi/3
        for z in sorted(set([.019+(.137-.019)*j/472 for j in range(473)]+[.019,.025,.04,.06,.08,.10,.12,.137])):
            pos=pencil.matrix_world@Vector((.00345*math.cos(a),.00345*math.sin(a),z))
            hitz=[]
            for tree in trees:
                hit,*_=tree.ray_cast(Vector((pos.x,pos.y,.15)),Vector((0,0,-1)))
                if hit is not None:hitz.append(hit.z)
            if hitz:
                clearance=pos.z-max(hitz)
                gaps.append(clearance);gap_samples.append([z*1000,k,clearance*1000])
    positions=[]
    for fr in range(1,scene.frame_end+1):
        scene.frame_set(fr);positions.append(list(scene.camera.location))
    speeds=[(Vector(b)-Vector(a)).length for a,b in zip(positions,positions[1:])]
    entry={
        "frames":scene.frame_end,"fps":scene.render.fps,
        "resolution":[scene.render.resolution_x,scene.render.resolution_y],
        "engine":scene.render.engine,"samples":scene.cycles.samples,"adaptive_threshold":scene.cycles.adaptive_threshold,
        "denoiser":scene.cycles.denoiser,"view_transform":scene.view_settings.view_transform,
        "finite_geometry":finite,"paper_front_normals_up":normals_ok,
        "pencil_min_ridge_clearance_mm":min(gaps)*1000,
        "pencil_bottom_clearance_by_axial_mm":{str(z):min(g[2] for g in gap_samples if abs(g[0]-z)<.001) for z in (19,25,40,60,80,100,120,137)},
        "camera_max_step_mm":max(speeds)*1000,
        "camera_last_step_mm":speeds[-1]*1000,
    }
    if scene.name=="desk_open":
        sheet=next(o for o in pages if o.name=="Open right leaf 07")
        def world_at(sx,sy):
            u=(sx-22)/1430;v=1-(sy-45)/2024
            z=.00035+6*.00014+.0046*math.exp(-((u-.12)/.19)**2)+.00045*math.sin(v*math.pi)*math.sin(u*math.pi)+.00028*math.sin(v*7+6*.2)*u*u
            return Vector((-.035+u*.13,.015+(v-.5)*.184,z))
        screen={}
        for key,line in [("title",ocr["p07"]["lines"][0]),("date",ocr["p07"]["lines"][1])]:
            ps=[world_to_camera_view(scene,scene.camera,world_at(x,y)) for x,y in line["box"]]
            screen[key]={"bounds_px":[min(p.x for p in ps)*1920,(1-max(p.y for p in ps))*1080,max(p.x for p in ps)*1920,(1-min(p.y for p in ps))*1080],
                         "height_px":(max(p.y for p in ps)-min(p.y for p in ps))*1080,
                         "within_frame":all(0<=p.x<=1 and 0<=p.y<=1 for p in ps)}
        entry["final_text_projection"]=screen
    result["scenes"][scene.name]=entry
result["pass_basic"]=all(result["scan_text_inside_crop"].values()) and all(result["packed_images"].values()) and all(v["finite_geometry"] and v["paper_front_normals_up"] and v["pencil_min_ridge_clearance_mm"]>=-.05 for v in result["scenes"].values())
(ROOT/"geometry_audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))
