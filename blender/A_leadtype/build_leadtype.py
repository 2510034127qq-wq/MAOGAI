"""Reproducible physical-scale lead type scenes. Run with Blender --background."""
import bpy
import bmesh
import math
import random
import json
import sys
import time
import subprocess
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT.parents[1] / "assets" / "renders"
U = .004
BODY_HEIGHT = 5.875  # 23.5 mm on a 4 mm square body
random.seed(1956)
FONT = None
MATS = {}
TEMPLATE = {}


def sRGB(hexcode):
    h = hexcode.lstrip("#")
    s = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in s) + (1,)


def node(mat, typ, name=None):
    n = mat.node_tree.nodes.new(typ)
    if name:
        n.name = n.label = name
    return n


def connect(mat, a, output, b, inp):
    mat.node_tree.links.new(a.outputs[output], b.inputs[inp])


def material(name, color, metallic=0, roughness=.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = sRGB(color)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = roughness
    return m, p


def noise(mat, scale, detail=3, rough=.65):
    n = node(mat, "ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    return n


def ramp(mat, source, colors, positions=None):
    n = node(mat, "ShaderNodeValToRGB")
    positions = positions or [i / (len(colors)-1) for i in range(len(colors))]
    for e in list(n.color_ramp.elements)[2:]:
        n.color_ramp.elements.remove(e)
    for i, color in enumerate(colors):
        e = n.color_ramp.elements[i] if i < 2 else n.color_ramp.elements.new(positions[i])
        e.position = positions[i]
        e.color = sRGB(color)
    connect(mat, source, "Fac", n, "Fac")
    return n


def math_node(mat, op, a, b=None):
    n = node(mat, "ShaderNodeMath")
    n.operation = op
    if isinstance(a, (float, int)):
        n.inputs[0].default_value = a
    else:
        connect(mat, a[0], a[1], n, 0)
    if b is not None:
        if isinstance(b, (float, int)):
            n.inputs[1].default_value = b
        else:
            connect(mat, b[0], b[1], n, 1)
    return n


def create_materials():
    m, p = material("铅锑锡｜微氧化银灰", "#898983", .86, .42)
    # Metric object coordinates avoid stretching noise over the long type shank.
    tc = node(m, "ShaderNodeTexCoord")
    coord = node(m, "ShaderNodeVectorMath")
    coord.operation = "SCALE"
    coord.inputs["Scale"].default_value = 1/U
    connect(m, tc, "Object", coord, 0)
    n = noise(m, 4)
    connect(m, coord, "Vector", n, "Vector")
    r = ramp(m, n, ["#80847F", "#898D88", "#92958F"], [.12, .50, .88])
    connect(m, r, "Color", p, "Base Color")
    fine = noise(m, 230, 2)
    connect(m, coord, "Vector", fine, "Vector")
    bump = node(m, "ShaderNodeBump")
    bump.inputs["Strength"].default_value = .10
    bump.inputs["Distance"].default_value = U * .0004
    connect(m, fine, "Fac", bump, "Height")
    connect(m, bump, "Normal", p, "Normal")
    rough = node(m, "ShaderNodeMapRange")
    rough.inputs["To Min"].default_value = .35
    rough.inputs["To Max"].default_value = .50
    connect(m, n, "Fac", rough, "Value")
    connect(m, rough, "Result", p, "Roughness")
    MATS["lead"] = m
    for key, color in [("black", "#1C1A17"), ("red", "#B5302A")]:
        m, p = material("字面薄墨｜" + key, color, 0, .36)
        p.inputs["Specular IOR Level"].default_value=.10
        n = noise(m, 28, 4)
        r = ramp(m, n, ["#0E0D0B", color, "#39362F"] if key == "black" else ["#84201B", color, "#BA3D31"], [.13, .50, .88])
        connect(m, r, "Color", p, "Base Color")
        rgh = node(m, "ShaderNodeMapRange")
        rgh.inputs["To Min"].default_value = .25
        rgh.inputs["To Max"].default_value = .38
        connect(m, n, "Fac", rgh, "Value")
        connect(m, rgh, "Result", p, "Roughness")
        grain = noise(m, 190, 2)
        bump = node(m, "ShaderNodeBump")
        bump.inputs["Distance"].default_value = .0017 * U
        bump.inputs["Strength"].default_value = .18
        connect(m, grain, "Fac", bump, "Height")
        connect(m, bump, "Normal", p, "Normal")
        # Most of the printing face carries opaque ink; occasional worn islands
        # reveal the same lead alloy underneath, without turning the face grey.
        worn = noise(m, 48, 3)
        mask = node(m, "ShaderNodeValToRGB", "薄墨透银｜约百分之三")
        mask.color_ramp.elements[0].position=.21
        mask.color_ramp.elements[0].color=(0,0,0,1)
        mask.color_ramp.elements[1].position=.32
        mask.color_ramp.elements[1].color=(1,1,1,1)
        connect(m,worn,"Fac",mask,"Fac")
        metal = node(m,"ShaderNodeBsdfPrincipled","磨薄处露出的铅")
        metal.inputs["Base Color"].default_value=sRGB("#858983")
        metal.inputs["Metallic"].default_value=.86
        metal.inputs["Roughness"].default_value=.4
        mix=node(m,"ShaderNodeMixShader","覆墨与露铅")
        connect(m,mask,"Color",mix,0)
        connect(m,metal,"BSDF",mix,1);connect(m,p,"BSDF",mix,2)
        connect(m,mix,0,m.node_tree.nodes.get("Material Output"),"Surface")
        MATS[key] = m
    m, p = material("老木｜顺纹磨损", "#58452E", 0, .67)
    tex = node(m, "ShaderNodeTexCoord")
    scale = node(m, "ShaderNodeVectorMath")
    scale.operation = "MULTIPLY"
    scale.inputs[1].default_value = (2, 65, 35)
    connect(m, tex, "Generated", scale, 0)
    n = noise(m, 3, 4)
    connect(m, scale, "Vector", n, "Vector")
    r = ramp(m, n, ["#29231B", "#665239", "#938064"], [.15, .5, .86])
    connect(m, r, "Color", p, "Base Color")
    bump = node(m, "ShaderNodeBump")
    bump.inputs["Distance"].default_value = .012 * U
    bump.inputs["Strength"].default_value = .3
    connect(m, n, "Fac", bump, "Height")
    connect(m, bump, "Normal", p, "Normal")
    MATS["wood"] = m
    m, p = material("手盘钢板｜发暗磨痕", "#585B56", .76, .52)
    n = noise(m, 12)
    r = ramp(m, n, ["#282A25", "#72766D"], [.1, .9])
    connect(m, r, "Color", p, "Base Color")
    MATS["steel"] = m
    m, p = material("纸｜旧纸基色", "#EDE5D4", 0, .86)
    p.inputs["Specular IOR Level"].default_value=.12
    t = node(m, "ShaderNodeTexImage")
    t.image = bpy.data.images.load(str(ROOT / "textures" / "paper_fibre.png"))
    t.image.colorspace_settings.name = "Non-Color"
    r = node(m, "ShaderNodeValToRGB")
    r.color_ramp.elements[0].position = .05
    r.color_ramp.elements[0].color = sRGB("#D9CCB1")
    r.color_ramp.elements[1].position = .92
    r.color_ramp.elements[1].color = sRGB("#F1E9D9")
    connect(m, t, "Color", r, "Fac")
    connect(m, r, "Color", p, "Base Color")
    b = node(m, "ShaderNodeBump")
    b.inputs["Distance"].default_value = .0045 * U
    b.inputs["Strength"].default_value = .30
    connect(m, t, "Color", b, "Height")
    connect(m, b, "Normal", p, "Normal")
    MATS["paper"] = m
    m = m.copy()
    m.name = "旧纸压印｜正向破立｜朱砂晕染"
    p = m.node_tree.nodes.get("Principled BSDF")
    paper_color = p.inputs["Base Color"].links[0].from_socket
    alpha = node(m, "ShaderNodeTexImage")
    alpha.image = bpy.data.images.load(str(ROOT / "textures" / "stamp_alpha.png"))
    alpha.image.colorspace_settings.name = "Non-Color"
    mix = node(m, "ShaderNodeMixRGB", "墨色不匀与纸纤维透出")
    mix.blend_type = "MIX"
    m.node_tree.links.new(paper_color, mix.inputs[1])
    mix.inputs[2].default_value = sRGB("#B5302A")
    connect(m, alpha, "Color", mix, 0)
    connect(m, mix, "Color", p, "Base Color")
    impression=node(m,"ShaderNodeTexImage","压印轮廓｜与凸字共用")
    impression.image=bpy.data.images.load(str(ROOT/"textures"/"stamp_height.png"))
    impression.image.colorspace_settings.name="Non-Color"
    press_bump=node(m,"ShaderNodeBump","压印边缘微凹")
    press_bump.invert=True
    press_bump.inputs["Distance"].default_value=.004*U
    press_bump.inputs["Strength"].default_value=.45
    paper_normal=p.inputs["Normal"].links[0].from_socket
    m.node_tree.links.new(paper_normal,press_bump.inputs["Normal"])
    connect(m,impression,"Color",press_bump,"Height")
    connect(m,press_bump,"Normal",p,"Normal")
    MATS["stamped_paper"] = m


def cube(name, loc, dims, mat, bevel=.015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(v*U for v in loc))
    o = bpy.context.object
    o.name = name
    o.dimensions = tuple(v*U for v in dims)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new("磨圆边缘", "BEVEL")
        mod.width = bevel*U
        mod.segments = 3
        mod = o.modifiers.new("加权法线", "WEIGHTED_NORMAL")
        mod.keep_sharp = True
    return o


def body(name, x, y, base):
    # Front surface has a true concave, horizontal nick, made in the cross-section.
    zc = 4.45
    radius = .085
    profile = [(-.5, 0), (.5, 0), (.5, BODY_HEIGHT), (-.5, BODY_HEIGHT),
               (-.5, zc+radius)]
    for j in range(1, 13):
        a = math.pi*j/12
        profile.append((-.5 + radius * math.sin(a), zc + radius*math.cos(a)))
    nv = len(profile)
    verts = [(sx*.5*U, py*U, pz*U) for sx in [-1,1] for py,pz in profile]
    faces = [tuple(reversed(range(nv))), tuple(range(nv,2*nv))]
    faces += [(i,(i+1)%nv,(i+1)%nv+nv,i+nv) for i in range(nv)]
    me = bpy.data.meshes.new(name+"_mesh")
    me.from_pydata(verts,[],faces)
    me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
    o.location=(x*U,y*U,base*U)
    o.data.materials.append(MATS["lead"])
    b=o.modifiers.new("长期使用磨圆", "BEVEL");b.width=.018*U;b.segments=3
    n=o.modifiers.new("加权法线","WEIGHTED_NORMAL");n.keep_sharp=True
    o["physical_height_mm"]=23.5;o["face_mm"]=4.;o["nick_depth_mm"]=radius*4
    return o


def glyph_mesh(ch):
    if ch in TEMPLATE:
        return TEMPLATE[ch]
    cv = bpy.data.curves.new("STSONG_"+ch, "FONT")
    cv.body=ch;cv.font=FONT;cv.size=1;cv.resolution_u=10
    cv.offset=.0075  # small cast/ink gain, retaining the STSong outlines
    cv.align_x="CENTER";cv.align_y="CENTER";cv.fill_mode="BOTH"
    bpy.ops.object.select_all(action="DESELECT")
    o=bpy.data.objects.new("字形轮廓",cv);bpy.context.collection.objects.link(o)
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    bpy.ops.object.convert(target="MESH")
    me=o.data
    bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(me);bm.free()
    coords=[v.co.copy() for v in me.vertices]
    lo=[min(v[i] for v in coords) for i in (0,1)]
    hi=[max(v[i] for v in coords) for i in (0,1)]
    scale=.82/max(hi[0]-lo[0], hi[1]-lo[1])
    # Mirror X in geometry; corrected topology keeps all surface normals outward.
    pts=[Vector((-(v.x-(lo[0]+hi[0])/2)*scale,(v.y-(lo[1]+hi[1])/2)*scale)) for v in coords]
    triangles=[]
    for p in me.polygons:
        q=list(p.vertices)
        a,b,c=[pts[i] for i in q]
        if (b-a).cross(c-a)<0:q.reverse()
        triangles.append(q)
    edges={}
    for f in triangles:
        for a,b in zip(f, f[1:]+f[:1]):
            key=tuple(sorted((a,b)))
            if key in edges:edges[key]=None
            else:edges[key]=(a,b)
    boundary=[e for e in edges.values() if e is not None]
    offsets=[Vector((0,0)) for p in pts]
    for a,b in boundary:
        d=(pts[b]-pts[a]).normalized()
        n=Vector((d.y,-d.x))
        offsets[a]+=n;offsets[b]+=n
    # A 1/6-face relief with a flared, filleted foot; no vertical extrusion.
    heights=[1/6,.150,.026,0]
    spreads=[0,.003,.018,.032]
    verts=[]
    for height,spread in zip(heights,spreads):
        for p,off in zip(pts,offsets):
            d=off.normalized()*spread if off.length else off
            verts.append(((p.x+d.x)*U,(p.y+d.y)*U,height*U))
    count=len(pts)
    faces=[tuple(t) for t in triangles]
    top_count=len(faces)
    faces += [tuple(i+3*count for i in reversed(t)) for t in triangles]
    for ring in range(3):
        off=ring*count;low=(ring+1)*count
        faces += [(b+off,a+off,a+low,b+low) for a,b in boundary]
    mesh=bpy.data.meshes.new("镜像阳文_"+ch)
    mesh.from_pydata(verts,[],faces);mesh.update()
    mesh.materials.append(MATS["lead"]);mesh.materials.append(MATS["black"])
    for i,p in enumerate(mesh.polygons):
        p.material_index=1 if (i<top_count or 2*top_count<=i<2*top_count+len(boundary)) else 0
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(mesh);bm.free()
    bpy.data.objects.remove(o,do_unlink=True)
    TEMPLATE[ch]=(mesh,top_count)
    return TEMPLATE[ch]


def type_piece(ch, x, y, base=.20, ink="black", angle=0, hero=True):
    parent=bpy.data.objects.new("铅字_"+ch+("_主体" if hero else "_陪体"),None)
    bpy.context.collection.objects.link(parent)
    parent.location=(x*U,y*U,base*U);parent.rotation_euler.z=math.radians(angle)
    b=body("字身_"+ch,0,0,0);b.parent=parent
    me,top_count=glyph_mesh(ch)
    g=bpy.data.objects.new("反字阳文_"+ch,me.copy());bpy.context.collection.objects.link(g)
    g.parent=parent;g.location.z=BODY_HEIGHT*U
    g.data.materials[1]=MATS[ink]
    bevel=g.modifiers.new("笔画顶端微磨损","BEVEL")
    bevel.width=.006*U;bevel.segments=3
    g["source_character"]=ch;g["mirrored_x"]=True;g["relief_height_mm"]=4/6
    g["taper_base_expansion_mm"]=.128
    # Discrete shoulder ink specks; fixed seed, deliberately sparse.
    for j in range(9 if hero else 2):
        xx=random.uniform(-.46,.46);yy=random.choice([-1,1])*random.uniform(.425,.47)
        dot=cube("肩部残墨", (0,0,0), (random.uniform(.01,.045),random.uniform(.006,.02),.0015),MATS[ink],.001)
        dot.parent=parent;dot.location=(xx*U,yy*U,(BODY_HEIGHT+.001)*U)
    # Cast/wear hairlines run down the shank, broken and subpixel at wide framing.
    for j in range(5 if hero else 1):
        xx=random.uniform(-.44,.44);z=random.uniform(.8,3.8)
        scratch=cube("字身细划痕", (0,0,0),(.0018,.0008,random.uniform(.09,.42)),MATS["steel"],0)
        scratch.parent=parent;scratch.location=(xx*U,-.5004*U,z*U)
    return parent


def paper_z(x,y):
    # Quiet curled corners; the central printing surface stays supported.
    ex=max(0,(abs(x)-3.8)/1.45)
    ey=max(0,(abs(y)-2.7)/1.3)
    return .0225 + .18*ex**3 + .09*ey**3 + .018*math.sin(x*.7)*ex*ey


def paper(stamped=True):
    nx,ny=240,184
    img=bpy.data.images.load(str(ROOT/"textures"/"stamp_height.png"),check_existing=True)
    import numpy as np
    px=np.asarray(img.pixels[:],dtype=np.float32).reshape(img.size[1],img.size[0],4)[:,:,0]
    verts=[];uvs=[]
    for j in range(ny+1):
        v=j/ny;y=(v-.5)*8
        for i in range(nx+1):
            u=i/nx;x=(u-.5)*10.5
            mask=float(px[min(img.size[1]-1,int(v*img.size[1])),min(img.size[0]-1,int(u*img.size[0]))]) if stamped else 0
            z=paper_z(x,y)-mask*.004
            verts.append((x*U,y*U,z*U));uvs.append((u,v))
    faces=[]
    for j in range(ny):
        for i in range(nx):
            k=j*(nx+1)+i;faces.append((k,k+1,k+nx+2,k+nx+1))
    me=bpy.data.meshes.new("旧纸微卷网格");me.from_pydata(verts,[],faces);me.update()
    uv=me.uv_layers.new(name="纸面")
    for poly in me.polygons:
        poly.use_smooth=True
        for idx in poly.loop_indices:uv.data[idx].uv=uvs[me.loops[idx].vertex_index]
    o=bpy.data.objects.new("旧纸｜压印微凹16微米",me);bpy.context.collection.objects.link(o)
    o.data.materials.append(MATS["stamped_paper" if stamped else "paper"])
    sol=o.modifiers.new("纸张厚度90微米","SOLIDIFY");sol.thickness=.0225*U;sol.offset=-1
    return o


def area(name, loc, target, energy, size, color, size_y=None):
    d=bpy.data.lights.new(name,"AREA");d.energy=energy;d.color=color
    if size_y:
        d.shape="RECTANGLE";d.size=size*U;d.size_y=size_y*U
    else:d.shape="DISK";d.size=size*U
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
    o.location=Vector(loc)*U;o.rotation_euler=(Vector(target)*U-o.location).to_track_quat("-Z","Y").to_euler()
    return o


def camera():
    d=bpy.data.cameras.new("微距摄影机");d.lens=18;d.sensor_width=10
    d.clip_start=.00005;d.clip_end=10
    d.dof.use_dof=True;d.dof.aperture_blades=9;d.dof.aperture_fstop=8
    o=bpy.data.objects.new("微距摄影机",d);bpy.context.collection.objects.link(o)
    bpy.context.scene.camera=o
    focus=bpy.data.objects.new("焦点｜叙事主体",None);bpy.context.collection.objects.link(focus)
    d.dof.focus_object=focus
    return o,focus


def smoother(t):
    t=max(0,min(1,t))
    return t*t*t*(t*(t*6-15)+10)


def lerp(a,b,t):return a+(b-a)*t


def animate_cam(shot):
    scene=bpy.context.scene;c,f=camera()
    end=210 if shot=="title" else 180
    manifest=[]
    for frame in range(1,end+1):
        if shot=="title":
            t=smoother((frame-1)/149)
            x=lerp(-2.12,2.12,t)
            pull=smoother((frame-150)/60)
            pos=Vector((lerp(x,0,pull),lerp(-6.3,-14.0,pull),lerp(11.25,17.5,pull)))
            target=Vector((lerp(x,0,pull),0,lerp(6.23,3.4,pull)))
            focal=Vector((lerp(x,0,pull),0,6.23))
            aperture=lerp(11,8,pull)
        else:
            t=smoother((frame-1)/(end-1))
            angle=math.radians(lerp(-7.5,7.5,t))
            dist=23.0
            pos=Vector((math.sin(angle)*dist,-math.cos(angle)*dist,25.5))
            target=Vector((0,-.20,2.5))
            rack=smoother((frame-36)/110)
            focal=Vector((0,lerp(.7,-2,rack),lerp(6.064,.0225,rack)))
            aperture=5.6
        c.location=pos*U;c.rotation_euler=(target*U-c.location).to_track_quat("-Z","Y").to_euler()
        f.location=focal*U;c.data.dof.aperture_fstop=aperture
        c.keyframe_insert("location",frame=frame);c.keyframe_insert("rotation_euler",frame=frame)
        f.keyframe_insert("location",frame=frame);c.data.keyframe_insert("dof.aperture_fstop",frame=frame)
        manifest.append({"frame":frame,"camera":list(pos),"target":list(target),"focus":list(focal),"fstop":aperture})
    # Dense, analytic samples: no Bezier overshoot at the two-stage transition.
    for ob in (c,f,c.data):
        if ob.animation_data and ob.animation_data.action:
            for layer in ob.animation_data.action.layers:
                for strip in layer.strips:
                    for bag in strip.channelbags:
                        for fc in bag.fcurves:
                            for k in fc.keyframe_points:k.interpolation="LINEAR"
    (ROOT/f"{shot}_camera.json").write_text(json.dumps(manifest,indent=2),encoding="utf8")
    scene.frame_end=end


def make_scene(shot):
    global FONT
    bpy.ops.wm.read_factory_settings(use_empty=True)
    MATS.clear();TEMPLATE.clear()
    FONT=bpy.data.fonts.load("C:/Windows/Fonts/STSONG.TTF")
    create_materials()
    scene=bpy.context.scene
    scene.unit_settings.system="METRIC";scene.unit_settings.scale_length=1
    scene.render.engine="CYCLES";scene.cycles.device="GPU"
    prefs=bpy.context.preferences.addons["cycles"].preferences
    try:prefs.compute_device_type="OPTIX";prefs.get_devices()
    except Exception:prefs.compute_device_type="CUDA";prefs.get_devices()
    backend=prefs.compute_device_type
    for d in prefs.devices:d.use=d.type==backend
    scene.cycles.samples=96;scene.cycles.use_adaptive_sampling=True
    scene.cycles.adaptive_threshold=.018;scene.cycles.adaptive_min_samples=24
    scene.cycles.use_denoising=True;scene.cycles.denoiser="OPTIX"
    scene.cycles.use_animated_seed=False;scene.cycles.seed=1976
    scene.cycles.max_bounces=7;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=4
    scene.cycles.transmission_bounces=2;scene.cycles.transparent_max_bounces=4
    scene.cycles.sample_clamp_indirect=3
    scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
    scene.render.fps=30;scene.render.fps_base=1
    scene.render.image_settings.file_format="PNG";scene.render.image_settings.color_mode="RGB"
    scene.render.image_settings.color_depth="8";scene.render.image_settings.compression=20
    scene.render.film_transparent=False;scene.render.use_persistent_data=True
    scene.render.threads_mode="FIXED";scene.render.threads=12
    scene.view_settings.view_transform="AgX"
    scene.view_settings.look="AgX - Medium High Contrast"
    scene.view_settings.exposure=-1.05 if shot=="title" else -1.0
    scene.world=bpy.data.worlds.new("暖灰环境")
    scene.world.use_nodes=True
    world=scene.world.node_tree.nodes.get("Background")
    world.inputs["Color"].default_value=sRGB("#B9A68B");world.inputs["Strength"].default_value=.22
    if shot=="title":
        cube("字盘桌面",(0,1,-.4),(40,32,.8),MATS["wood"],.09)
        cube("手盘钢制底板",(0,.3,.09),(7.0,2.1,.18),MATS["steel"],.025)
        cube("木质左挡边",(-3.55,.3,.8),(.45,2.5,1.6),MATS["wood"],.07)
        cube("木质右挡边",(3.55,.3,.8),(.45,2.5,1.6),MATS["wood"],.07)
        cube("手盘后挡", (0,1.21,2.0),(7.2,.23,4),MATS["steel"],.03)
        for ch,x in zip("系关大十论",[-2.12,-1.06,0,1.06,2.12]):type_piece(ch,x,0,.18)
        for j,ch in enumerate("发展人民农业建设实际统筹兼顾"):
            x=(j%7-3)*1.14+random.uniform(-.09,.09);y=3.1+(j//7)*1.7
            type_piece(ch,x,y,0,angle=random.uniform(-5,5),hero=False)
        cube("远处字盘挡边",(0,6.3,2),(14,.28,4),MATS["wood"],.05)
        area("左侧低角度暖光",(-7,-2,8.6),(0,0,6),.035,5.5,(1,.85,.69),2.5)
        area("右侧弱补光",(6,-2,10),(0,0,5),.004,5,(.86,.88,.86),6)
        area("上后方窄柔光",(1,5,12),(0,0,6),.010,6,(1,.89,.73),2)
    else:
        cube("桌面",(0,0,-.4),(40,30,.8),MATS["wood"],.06)
        type_piece("破",-1.0,.7,paper_z(-1,.7),ink="red",angle=-1.4)
        type_piece("立",1.0,.7,paper_z(1,.7),ink="red",angle=.7)
        # Printing masks come from the very same mesh triangles as the raised
        # faces, reflected back to normal reading direction at physical size.
        outlines={}
        for ch in "破立":
            me,n=glyph_mesh(ch)
            pts=[(v.co.x/U,v.co.y/U) for v in me.vertices[:len(me.vertices)//4]]
            outlines[ch]={"points":pts,"triangles":[list(p.vertices) for p in me.polygons[:n]]}
        (ROOT/"textures"/"glyph_meshes.json").write_text(json.dumps(outlines,ensure_ascii=False),encoding="utf8")
        subprocess.run([r"C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe",str(ROOT/"make_textures.py")],check=True)
        for im in bpy.data.images:
            if im.source=="FILE":im.reload()
        paper(True)
        area("左侧窗光",(-6,-4,14),(0,0,1),.055,9,(1,.94,.86),7)
        area("右方纸面反光",(7,0,10),(0,0,3),.018,8,(1,.96,.89),6)
        area("后侧窗缘",(0,6,12),(0,0,4),.035,7,(1,.89,.72),3)
    animate_cam(shot)
    scene.frame_start=1;scene.frame_set(1)
    scene["brief"]="D:/MAOGAI/blender/A_leadtype/BRIEF.md"
    scene["geometry_scale"]="4 mm face; 23.5 mm body; 0.667 mm relief"
    scene["source_font"]="C:/Windows/Fonts/STSONG.TTF"
    scene["backend"]=backend
    output=ASSETS/("leadtype_"+shot);output.mkdir(parents=True,exist_ok=True)
    scene.render.filepath=str(output/"frames")+"/"
    for im in bpy.data.images:
        if im.source=="FILE":im.pack()
    FONT.pack()
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/f"leadtype_{shot}.blend"))
    return scene


def main():
    argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    shot=argv[0] if argv else "title"
    scene=make_scene(shot)
    if "--test" in argv:
        roundname=argv[argv.index("--test")+1]
        scene.render.resolution_percentage=50
        scene.cycles.samples=48;scene.cycles.adaptive_min_samples=16
        frames=[1,105,210] if shot=="title" else [1,90,180]
        out=ROOT/"review"/roundname
        out.mkdir(parents=True,exist_ok=True)
        for f in frames:
            scene.frame_set(f);scene.render.filepath=str(out/f"{shot}_{f:04d}.png")
            t=time.monotonic();bpy.ops.render.render(write_still=True)
            print("TEST_FRAME",shot,f,round(time.monotonic()-t,3),flush=True)


if __name__=="__main__":main()
