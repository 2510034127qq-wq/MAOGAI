"""Compare the approved A1 scene with the production .blend, excluding output settings."""
from pathlib import Path
import bpy, json, hashlib
ROOT=Path(__file__).resolve().parent

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode('utf8')).hexdigest()
def values(v):
    if isinstance(v,(str,int,float,bool)) or v is None:return v
    try:return list(v)
    except TypeError:return str(v)

def fingerprint(path):
    bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.frame_set(1)
    objects={}
    for obj in scene.objects:
        data={'type':obj.type,'parent':obj.parent.name if obj.parent else None,
              'location':list(obj.location),'rotation':list(obj.rotation_euler),'scale':list(obj.scale)}
        if obj.type=='MESH':
            data['vertices']=digest([list(v.co) for v in obj.data.vertices])
            data['polygons']=digest([(list(p.vertices),p.material_index) for p in obj.data.polygons])
            data['materials']=[m.name for m in obj.data.materials]
        if obj.type=='LIGHT':data['light']=[obj.data.type,obj.data.energy,list(obj.data.color),obj.data.size]
        if obj.type=='CAMERA':data['camera']=[obj.data.lens,obj.data.sensor_width,obj.data.dof.use_dof,obj.data.dof.aperture_fstop,obj.data.dof.focus_object.name]
        data['modifiers']=[(m.name,m.type,[(p.identifier,values(getattr(m,p.identifier))) for p in m.bl_rna.properties if p.type in ('FLOAT','INT','BOOLEAN','ENUM') and p.identifier!='rna_type']) for m in obj.modifiers]
        objects[obj.name]=digest(data)
    materials={}
    for mat in bpy.data.materials:
        if not mat.use_nodes:continue
        nodes={}
        for n in mat.node_tree.nodes:
            rec={'type':n.type,'inputs':[(i.identifier,values(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]}
            if hasattr(n,'color_ramp'):rec['ramp']=[(e.position,list(e.color)) for e in n.color_ramp.elements]
            if n.type=='TEX_IMAGE' and n.image:
                rec['image']=hashlib.sha256(n.image.packed_file.data).hexdigest() if n.image.packed_file else n.image.filepath
            nodes[n.name]=rec
        links=[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in mat.node_tree.links]
        materials[mat.name]=digest({'nodes':nodes,'links':sorted(links)})
    animation=[]
    for f in range(1,211):
        scene.frame_set(f);c=scene.camera
        animation.append((f,list(c.location),list(c.rotation_euler),list(c.data.dof.focus_object.location),c.data.dof.aperture_fstop))
    return {'objects':objects,'materials':materials,'camera_animation':digest(animation),
            'color_management':[scene.view_settings.view_transform,scene.view_settings.look,scene.view_settings.exposure,scene.view_settings.gamma]}

approved=fingerprint(ROOT/'review'/'handoff_snapshot'/'leadtype_title.blend')
current=fingerprint(ROOT/'leadtype_title.blend')
report={'approved_file':'review/handoff_snapshot/leadtype_title.blend','production_file':'leadtype_title.blend',
        'geometry_material_light_camera_unchanged':approved==current,'approved_fingerprint':digest(approved),
        'production_fingerprint':digest(current),'differences':{k:{'approved':approved[k],'production':current[k]} for k in approved if approved[k]!=current[k]}}
(ROOT/'title_preservation_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
assert report['geometry_material_light_camera_unchanged'],report['differences']
print('APPROVED_A1_PRESERVED',flush=True)
