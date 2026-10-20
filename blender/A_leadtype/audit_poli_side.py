"""All-frame geometry, focus timing and caption-space audit of the saved A2."""
import bpy, bmesh, json, sys, math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import prepare_poli_textures as tex
scene=bpy.context.scene
heroes=sorted([o for o in scene.objects if o.type=='EMPTY' and '_主体' in o.name],key=lambda o:o.location.x)
report={'heroes':[],'frames':[],'external_missing':[]}
for parent in heroes:
    body=next(o for o in parent.children if o.name.startswith('字身_'))
    glyph=next(o for o in parent.children if o.name.startswith('反字'))
    bm=bmesh.new();bm.from_mesh(glyph.data)
    heights=[(body.matrix_world@v.co).z*1000 for v in body.data.vertices]
    report['heroes'].append({'character':glyph['source_character'],'mirrored_x':glyph['mirrored_x'],
        'body_bbox_mm':[round((max(v.co[i] for v in body.data.vertices)-min(v.co[i] for v in body.data.vertices))*1000,5) for i in range(3)],
        'body_bottom_mm':min(heights),'paper_top_mm':.09,'contact_error_mm':abs(min(heights)-.09),
        'relief_mm':glyph['relief_height_mm'],'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
        'positive_volume':bm.calc_volume(signed=True)>0,'type_axis_world':list(parent.matrix_world.to_3x3()@Vector((0,0,1)))})
    bm.free()
for f in range(1,181):
    scene.frame_set(f);bpy.context.view_layer.update();cam=scene.camera
    boundaries={}
    for parent in heroes:
        for ob in [o for o in parent.children if o.name.startswith(('反字','字身_'))]:
            pts=[world_to_camera_view(scene,cam,ob.matrix_world@Vector(v)) for v in ob.bound_box]
            boundaries[ob.name]=[min(p.x for p in pts),1-max(p.y for p in pts),max(p.x for p in pts),1-min(p.y for p in pts)]
    caption_corners=[]
    # Camera-local view-frame gives the four full-image rays. Check their paper intersections.
    for corner in cam.data.view_frame(scene=scene):
        ray=cam.matrix_world.to_3x3()@corner
        point=cam.location+ray*((.00009-cam.location.z)/ray.z)
        caption_corners.append([point.x/.004,point.y/.004])
    direction=cam.matrix_world.to_3x3()@Vector((0,0,-1))
    focus=cam.data.dof.focus_object.location
    report['frames'].append({'frame':f,'objects':boundaries,
        'focus_distance_mm':(focus-cam.location).dot(direction)*1000,
        'depression_degrees':math.degrees(math.asin(-direction.z)),
        'paper_frame_corners_units':caption_corners})
for im in bpy.data.images:
    if im.source=='FILE' and im.users and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists():report['external_missing'].append(im.filepath)
report['all_180_frames_body_and_faces_inside']=all(0<=b[0]<b[2]<=1 and 0<=b[1]<b[3]<=1 for f in report['frames'] for b in f['objects'].values())
report['all_heroes_solid']=all(h['nonmanifold_edges']==0 and h['positive_volume'] for h in report['heroes'])
report['max_contact_error_mm']=max(h['contact_error_mm'] for h in report['heroes'])
report['packed_images']=sum(bool(im.packed_file) for im in bpy.data.images if im.users)
report['paper_covers_full_frame_all_frames']=all(abs(x)<14 and -11<y<15 for f in report['frames'] for x,y in f['paper_frame_corners_units'])
report['depression_range_degrees']=[min(f['depression_degrees'] for f in report['frames']),max(f['depression_degrees'] for f in report['frames'])]
camera=json.loads((ROOT/'poli_camera.json').read_text(encoding='utf8'))
report['focus_timing']={'faces_1_to_60':all(f['rack_fraction']==0 for f in camera[:60]),
    'prints_139_to_180':all(f['rack_fraction']==1 for f in camera[138:]),
    'monotonic_rack':all(a['rack_fraction']<=b['rack_fraction'] for a,b in zip(camera,camera[1:]))}
composition=json.loads((ROOT/'poli_side_composition.json').read_text(encoding='utf8'))
report['stamp_max_bottom_fraction']=max(s['screen_bbox'][3] for f in composition for s in f['stamps'])
report['caption_region_clear_of_subjects']=report['stamp_max_bottom_fraction']<2/3 and all(b[3]<2/3 for f in report['frames'] for b in f['objects'].values())
(ROOT/'poli_side_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='frames'},ensure_ascii=False,indent=2),flush=True)
assert report['all_180_frames_body_and_faces_inside'] and report['all_heroes_solid']
assert report['caption_region_clear_of_subjects'] and report['paper_covers_full_frame_all_frames']
assert not report['external_missing'] and all(report['focus_timing'].values())
