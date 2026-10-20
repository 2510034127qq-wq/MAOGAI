"""A2 FEEDBACK_2: parallel type on its side, macro rack-focus and caption space.

Blender --background --python build_poli_side.py [-- --test round7]
Uses the approved shared casting/material functions without changing A1.
"""
import bpy, math, json, sys, subprocess, time
from pathlib import Path
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import build_leadtype as base
import prepare_poli_textures as tex
U=base.U
R=Matrix.Rotation(math.radians(tex.ANGLE),4,'Z')

def world(v):return R@Vector(v)

def paper_height(x,y):
    ex=max(0,(abs(x)-12.4)/1.6)
    ey=max(0,(abs(y-2)-11.5)/1.5)
    return .0225+.15*ex**3+.10*ey**3

def make_paper():
    import numpy as np
    im=bpy.data.images.load(str(tex.OUT/'stamp_height.png'),check_existing=True)
    px=np.asarray(im.pixels[:],dtype=np.float32).reshape(im.size[1],im.size[0],4)[:,:,0]
    nx,ny=448,416
    verts=[];uvs=[]
    for j in range(ny+1):
        y=2+(j/ny-.5)*26
        v=(y-tex.CY)/tex.PH+.5
        for i in range(nx+1):
            x=(i/nx-.5)*28
            u=x/tex.PW+.5
            mask=float(px[max(0,min(im.size[1]-1,int(v*im.size[1]))),max(0,min(im.size[0]-1,int(u*im.size[0])))])
            verts.append((x*U,y*U,(paper_height(x,y)-mask*.004)*U));uvs.append((u,v))
    faces=[]
    for j in range(ny):
        for i in range(nx):
            k=j*(nx+1)+i;faces.append((k,k+1,k+nx+2,k+nx+1))
    me=bpy.data.meshes.new('A2旧纸微卷网格');me.from_pydata(verts,[],faces);me.update()
    uv=me.uv_layers.new(name='纸面')
    for poly in me.polygons:
        poly.use_smooth=True
        for idx in poly.loop_indices:uv.data[idx].uv=uvs[me.loops[idx].vertex_index]
    obj=bpy.data.objects.new('旧纸｜侧卧铅字与同源压印',me);bpy.context.collection.objects.link(obj)
    obj.data.materials.append(base.MATS['stamped_paper'])
    sol=obj.modifiers.new('纸张厚度90微米','SOLIDIFY');sol.thickness=.0225*U;sol.offset=-1
    return obj

def animate(scene):
    cam,focus=base.camera()
    manifest=[]
    for frame in range(1,181):
        t=base.smoother((frame-1)/179)
        distance=base.lerp(23.5,23.2,t)
        target=Vector((0,-.7,.15))
        azimuth=math.radians(-20)
        pos=target+Vector((math.sin(azimuth)*distance*math.cos(math.pi/6)+base.lerp(-.10,.10,t),
                          -math.cos(azimuth)*distance*math.cos(math.pi/6),distance*.5))
        rack=base.smoother((frame-60)/78)
        focal=Vector((0,base.lerp(-1/6,tex.STAMP_Y,rack),base.lerp(.5225,.0225,rack)))
        cam.location=world(pos)*U
        cam.rotation_euler=(world(target-pos)).to_track_quat('-Z','Y').to_euler()
        focus.location=world(focal)*U
        cam.data.dof.aperture_fstop=6.3
        cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_euler',frame=frame)
        focus.keyframe_insert('location',frame=frame)
        manifest.append({'frame':frame,'camera':list(world(pos)),'target':list(world(target)),
            'focus':list(world(focal)),'fstop':6.3,'rack_fraction':rack,'depression_degrees':30.0})
    for obj in (cam,focus):
        for layer in obj.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for k in fc.keyframe_points:k.interpolation='LINEAR'
    (ROOT/'poli_camera.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')

def audit(scene,heroes):
    records=[]
    for frame in [1,60,90,138,180]:
        scene.frame_set(frame);bpy.context.view_layer.update()
        entry={'frame':frame,'glyphs':[],'bodies':[],'stamps':[]}
        for parent in heroes:
            for prefix,key in [('反字','glyphs'),('字身_','bodies')]:
                ob=next(o for o in parent.children if o.name.startswith(prefix))
                pts=[world_to_camera_view(scene,scene.camera,ob.matrix_world@Vector(p)) for p in ob.bound_box]
                entry[key].append({'name':ob.name,'screen_bbox':[min(p.x for p in pts),1-max(p.y for p in pts),max(p.x for p in pts),1-min(p.y for p in pts)],
                    'world_z_min_mm':min((ob.matrix_world@Vector(p)).z for p in ob.bound_box)*1000})
        for x in [-1,1]:
            pts=[world_to_camera_view(scene,scene.camera,world((x+dx,tex.STAMP_Y+dy,.0225))*U) for dx in [-.43,.43] for dy in [-.43,.43]]
            entry['stamps'].append({'screen_bbox':[min(p.x for p in pts),1-max(p.y for p in pts),max(p.x for p in pts),1-min(p.y for p in pts)]})
        entry['caption_safe_top']=2/3
        records.append(entry)
    (ROOT/'poli_side_composition.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')

def main():
    if '--camera-only' in sys.argv:
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'leadtype_poli.blend'))
        scene=bpy.context.scene
        for ob in [scene.camera,scene.camera.data.dof.focus_object]:bpy.data.objects.remove(ob,do_unlink=True)
        animate(scene)
        audit(scene,[o for o in bpy.data.objects if o.type=='EMPTY' and '_主体' in o.name])
        scene.frame_set(1)
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'leadtype_poli.blend'))
        return
    bpy.ops.wm.read_factory_settings(use_empty=True)
    base.MATS.clear();base.TEMPLATE.clear()
    base.FONT=bpy.data.fonts.load('C:/Windows/Fonts/STSONG.TTF')
    base.create_materials()
    outlines={}
    for ch in '破立':
        mesh,n=base.glyph_mesh(ch)
        outlines[ch]={'points':[(v.co.x/U,v.co.y/U) for v in mesh.vertices[:len(mesh.vertices)//4]],
                      'triangles':[list(p.vertices) for p in mesh.polygons[:n]]}
    (ROOT/'textures'/'glyph_meshes.json').write_text(json.dumps(outlines,ensure_ascii=False),encoding='utf8')
    subprocess.run([r'C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe',str(ROOT/'prepare_poli_textures.py')],check=True)
    for material in [base.MATS['paper'],base.MATS['stamped_paper']]:
        for node in material.node_tree.nodes:
            if node.type=='TEX_IMAGE' and node.image:
                node.image=bpy.data.images.load(str(tex.OUT/Path(node.image.filepath).name),check_existing=True)
                node.extension='REPEAT' if 'paper_fibre' in node.image.filepath else 'EXTEND'
    stamp=base.MATS['stamped_paper']
    pigment=base.node(stamp,'ShaderNodeMixRGB','朱砂实墨吸收｜避免纸面反射发粉')
    pigment.blend_type='MULTIPLY';pigment.inputs[0].default_value=1
    pigment.inputs[1].default_value=base.sRGB('#B5302A')
    pigment.inputs[2].default_value=(.72,.72,.72,1)
    base.connect(stamp,pigment,'Color',stamp.node_tree.nodes['墨色不匀与纸纤维透出'],2)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC';scene.render.engine='CYCLES';scene.cycles.device='GPU'
    prefs=bpy.context.preferences.addons['cycles'].preferences
    try:prefs.compute_device_type='OPTIX';prefs.get_devices()
    except Exception:prefs.compute_device_type='CUDA';prefs.get_devices()
    for d in prefs.devices:d.use=d.type==prefs.compute_device_type
    scene.cycles.samples=128;scene.cycles.use_adaptive_sampling=True
    scene.cycles.adaptive_threshold=.012;scene.cycles.adaptive_min_samples=32
    scene.cycles.use_denoising=True;scene.cycles.denoiser='OPTIX'
    scene.cycles.use_animated_seed=False;scene.cycles.seed=1976
    scene.cycles.max_bounces=7;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=4
    scene.cycles.sample_clamp_indirect=3
    scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
    scene.render.fps=30;scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
    scene.render.image_settings.compression=20;scene.render.use_persistent_data=True
    scene.render.threads_mode='FIXED';scene.render.threads=12
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=-.85
    scene.world=bpy.data.worlds.new('暖灰环境');scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=base.sRGB('#B9A68B');bg.inputs['Strength'].default_value=.22
    base.cube('桌面',(0,0,-.4),(40,34,.8),base.MATS['wood'],.06)
    heroes=[]
    for ch,x in [('破',-1.),('立',1.)]:
        p=base.type_piece(ch,0,0,0,ink='red')
        p.rotation_euler=(math.pi/2,0,math.radians(tex.ANGLE))
        p.location=world((x,base.BODY_HEIGHT,.5225))*U
        p['pose']='side lying; face toward front-left; parallel 4mm gap'
        heroes.append(p)
    make_paper()
    base.area('左侧柔窗光',(-6,-7,10),(0,0,.5),.055,8,(1,.94,.86),6)
    base.area('右侧弱纸面反光',(7,-1,8),(0,0,.5),.012,7,(1,.96,.89),5)
    base.area('后侧窗缘',(0,7,10),(0,2,.5),.020,6,(1,.91,.80),3)
    animate(scene);scene.frame_start=1;scene.frame_end=180
    scene['brief']='FEEDBACK_2.md supersedes BRIEF upright pose';scene['source_font']='STSONG.TTF'
    scene['geometry_scale']='4mm face; 23.5mm body; 0.667mm relief; 90-degree side pose'
    scene['caption_safe_region']='bottom third, y >= 720 at 1080p'
    audit(scene,heroes);scene.frame_set(1)
    scene.render.filepath=str(base.ASSETS/'leadtype_poli'/'frames')+'/'
    for im in bpy.data.images:
        if im.source=='FILE' and im.users:im.pack()
    base.FONT.pack()
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'leadtype_poli.blend'))
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    if '--test' in args:
        out=ROOT/'review'/args[args.index('--test')+1];out.mkdir(parents=True,exist_ok=True)
        scene.render.resolution_percentage=50;scene.cycles.samples=64;scene.cycles.adaptive_min_samples=24
        for f in [1,90,180]:
            scene.frame_set(f);scene.render.filepath=str(out/f'poli_{f:04d}.png')
            start=time.monotonic();bpy.ops.render.render(write_still=True)
            print('TEST_FRAME',f,round(time.monotonic()-start,3),flush=True)

if __name__=='__main__':main()
