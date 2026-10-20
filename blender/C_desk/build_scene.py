"""Blender 5.2: a 1976 saddle-stitched booklet on an old study desk.
Run: blender -b --python build_scene.py
All dimensions in metres. Both animated scenes are saved in one packed .blend.
"""
import bpy, math, random, json, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
from math import sin, cos, pi, exp

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from surface import page_height
TEX=ROOT/"textures"
random.seed(1976)
bpy.ops.wm.read_factory_settings(use_empty=True)

def srgb(h):
    vals=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals)+(1,)

def mat(name,color,rough=.5,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=srgb(color)
    p.inputs["Roughness"].default_value=rough
    p.inputs["Metallic"].default_value=metal
    return m

def noise_bump(m,scale,dist,strength=.2):
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get("Principled BSDF")
    tex=n.new("ShaderNodeTexNoise");tex.inputs["Scale"].default_value=scale
    tex.inputs["Detail"].default_value=2
    b=n.new("ShaderNodeBump");b.inputs["Distance"].default_value=dist;b.inputs["Strength"].default_value=strength
    l.new(tex.outputs["Fac"],b.inputs["Height"]);l.new(b.outputs["Normal"],p.inputs["Normal"])
    return tex

def image_mat(name,file,rough=.75):
    m=mat(name,"EDE5D4",rough)
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get("Principled BSDF")
    p.inputs["Specular IOR Level"].default_value=.16
    t=n.new("ShaderNodeTexImage");t.image=bpy.data.images.load(str(TEX/file),check_existing=True)
    t.interpolation="Linear";t.extension="EXTEND"
    l.new(t.outputs["Color"],p.inputs["Base Color"])
    noise_bump(m,850,.000012,.19)
    return m

paper=mat("Old paper · cut edges","CABB96",.88)
noise_bump(paper,950,.000015,.22)
covermat=image_mat("1976 original cover · preserved printed glyphs","cover_clean.png")
leftmat=image_mat("1976 contents · original scan p06","p06_aged.png")
rightmat=image_mat("1976 opening page · original scan p07","p07_aged.png")
ruled=image_mat("Blank ruled manuscript paper","ruled.png",.83)
backmat=mat("Soft aged cover stock","CFC1A0",.82)
noise_bump(backmat,700,.00002,.22)
metal=mat("Iron staples · oxidised","645445",.53,.78)
noise_bump(metal,140,.000025,.28)
brass=mat("Spectacles · patinated brass","8A6A3B",.4,.84)
noise_bump(brass,190,.00002,.2)
red=mat("Cinnabar pencil lacquer","A33931",.63)
p=red.node_tree.nodes.get("Principled BSDF");p.inputs["Coat Weight"].default_value=.025
p.inputs["Specular IOR Level"].default_value=.24
nt=red.node_tree;n=nt.nodes;l=nt.links
worn=n.new("ShaderNodeTexNoise");worn.inputs["Scale"].default_value=11;worn.inputs["Detail"].default_value=3
ramp=n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=srgb("813536")
ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=srgb("A73C42")
l.new(worn.outputs["Fac"],ramp.inputs["Fac"]);l.new(ramp.outputs["Color"],p.inputs["Base Color"])
rough=n.new("ShaderNodeMapRange");rough.inputs["To Min"].default_value=.50;rough.inputs["To Max"].default_value=.77
l.new(worn.outputs["Fac"],rough.inputs["Value"]);l.new(rough.outputs["Result"],p.inputs["Roughness"])
noise_bump(red,160,.000026,.25)
cedar=mat("Exposed pencil cedar","B98952",.71)
noise_bump(cedar,140,.00006,.3)
graphite=mat("Graphite","24221F",.38,.2)
enamel=mat("Warm white unlettered enamel","EDE9DD",.24)
p=enamel.node_tree.nodes.get("Principled BSDF");p.inputs["Coat Weight"].default_value=.32
noise_bump(enamel,110,.000018,.13)
rim=mat("Black enamel rolled rim","252724",.22,.4)
chip=mat("Small enamel chips · exposed black iron","28231D",.8,.55)
glass=mat("Clear spectacle lenses","E2DED0",.08)
p=glass.node_tree.nodes.get("Principled BSDF");p.inputs["Transmission Weight"].default_value=1;p.inputs["IOR"].default_value=1.5
wood=image_mat("Dark old elm tabletop","elm_color.png",.5)
n=wood.node_tree.nodes;l=wood.node_tree.links;p=n.get("Principled BSDF")
for file,channel in [("elm_height.png","Normal"),("elm_roughness.png","Roughness")]:
    t=n.new("ShaderNodeTexImage");t.image=bpy.data.images.load(str(TEX/file),check_existing=True)
    t.image.colorspace_settings.name="Non-Color"
    if channel=="Normal":
        b=n.new("ShaderNodeBump");b.inputs["Strength"].default_value=.25;b.inputs["Distance"].default_value=.00032
        l.new(t.outputs["Color"],b.inputs["Height"]);l.new(b.outputs["Normal"],p.inputs["Normal"])
    else:l.new(t.outputs["Color"],p.inputs[channel])

def mesh(name,verts,faces,material,uvs=None):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob)
    if material:me.materials.append(material)
    if uvs:
        uv=me.uv_layers.new(name="Original scan UV")
        for poly in me.polygons:
            for li,vi in zip(poly.loop_indices,poly.vertices):uv.data[li].uv=uvs[vi]
    for f in me.polygons:f.use_smooth=True
    return ob

def cube(name,loc,scale,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name
    o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new("Worn softened edges","BEVEL");b.width=bevel;b.segments=3
        o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return o

def curve(name,points,radius,material):
    c=bpy.data.curves.new(name,"CURVE");c.dimensions="3D";c.resolution_u=16;c.bevel_depth=radius;c.bevel_resolution=3
    s=c.splines.new("POLY");s.points.add(len(points)-1)
    for p,co in zip(s.points,points):p.co=(*co,1)
    o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.data.materials.append(material)
    return o

def lathe(name,profile,material,loc=(0,0,0),segments=128):
    verts=[];faces=[]
    for r,z in profile:
        for i in range(segments):
            a=2*pi*i/segments;verts.append((r*cos(a),r*sin(a),z))
    for j in range(len(profile)-1):
        for i in range(segments):
            a=j*segments+i;b=j*segments+(i+1)%segments
            faces.append((a,b,b+segments,a+segments))
    ob=mesh(name,verts,faces,material);ob.location=loc
    return ob

def torus(name,loc,major,minor,material,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=12,location=loc,
        major_radius=major,minor_radius=minor,rotation=rotation)
    o=bpy.context.object;o.name=name;o.data.materials.append(material)
    for p in o.data.polygons:p.use_smooth=True
    return o

def sheet(name,loc,w,h,z,material,opened=0,index=0,angle=0,thick=.00009):
    # Dense parametric surface, rounded silhouette and gentle long wavelength curl.
    nx,ny=64,90;vs=[];uv=[]
    for j in range(ny+1):
        v=j/ny;yy=(v-.5)*h
        for i in range(nx+1):
            u=i/nx;xx=(u-.5)*w
            corner=.0011
            yedge=max(0,abs(yy)-(h/2-corner))
            inset=corner-(max(0,corner*corner-yedge*yedge))**.5 if yedge>0 else 0
            xx*=1-inset/(w/2)
            zz=page_height(u,v,z,opened,index)
            vs.append((xx,yy,zz));uv.append((u,v))
    fs=[]
    for j in range(ny):
        for i in range(nx):
            k=j*(nx+1)+i;fs.append((k,k+1,k+nx+2,k+nx+1))
    o=mesh(name,vs,fs,material,uv);o.location=(*loc,0);o.rotation_euler.z=angle
    sol=o.modifiers.new("Actual paper thickness","SOLIDIFY");sol.thickness=thick;sol.offset=-1
    o.data.materials.append(paper);sol.material_offset=1;sol.material_offset_rim=1
    return o

def book(opened):
    cx,cy=(-.035,.015) if opened else (-.070,.015)
    if opened:
        for side in (-1,1):
            for k in range(7):
                matl=(leftmat if side<0 else rightmat) if k==6 else paper
                sheet(f"Open {'left' if side<0 else 'right'} leaf {k+1:02}",(cx+side*.065,cy),
                      .130,.184,.00035+k*.00014,matl,side,index=k,thick=.00012)
            sheet("Soft cover under open leaves",(cx+side*.065,cy),.131,.185,.00018,backmat,side,index=0,thick=.00015)
        for y in (-.052,.052):
            pts=[]
            for dx,dy in [(-.0009,y-.005),(0,y-.006),(.0006,y+.006),(-.0004,y+.0065)]:
                zz=page_height(abs(dx)/.13,dy/.184+.5,.00119,1,6)+.00016
                pts.append((cx+dx,cy+dy,zz))
            curve("Visible saddle-stitch inside gutter",pts,.00016,metal)
    else:
        sheet("Back soft paper cover",(cx,cy),.130,.184,.00025,backmat,thick=.00015)
        for k in range(14):
            dx=.0001*sin(k*7);dy=.00012*sin(k*3)
            sheet(f"28 page booklet · paper sheet {k+1:02}",(cx+dx,cy+dy),
                  .1295,.1835,.00038+k*.000105,paper,index=k,thick=.00010)
        sheet("1976 front cover · curved 130 x 184 mm",(cx,cy),.130,.184,.0020,covermat,thick=.00015)
        for y in (-.052,.052):
            curve("Two fine iron saddle staples",[(cx-.0642,cy+y-.006,.0017),
                 (cx-.0652,cy+y-.0055,.0013),(cx-.0653,cy+y+.0055,.0013),
                 (cx-.0642,cy+y+.006,.0017)],.00017,metal)
        # A few sparse fibre ends, much smaller than the cover and only at edges.
        for k in range(23):
            yy=cy+random.uniform(-.088,.088);zz=random.uniform(.0006,.0018)
            curve("Cut-paper fibre",[(cx+.0648,yy,zz),(cx+.0651,yy+.00012,zz+.00008)],.000012,paper)
    return cx,cy

def pencil(opened):
    # Tip + cedar + six lacquered faces, total 140 mm.
    p0=Vector((.002,-.057,0) if opened else (-.055,-.035,0))
    # Solve rigid support against the actual curved leaves and desk. The minimum
    # centre-of-mass height gives two supports, rather than an arbitrary Z offset.
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    trees=[]
    for ob in bpy.context.scene.objects:
        if ob.type!="MESH" or not any(n in ob.name for n in ("leaf","paper sheet","front cover","Elm grain top surface")):continue
        ev=ob.evaluated_get(dg);me=ev.to_mesh()
        trees.append(BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]))
        ev.to_mesh_clear()
    baseq=Vector((.94,-.342,0)).normalized().to_track_quat("Z","Y")
    supports=[]
    for j in range(473):
        s=.019+(.137-.019)*j/472
        for k in range(6):
            a=k*pi/3;local=Vector((.00345*cos(a),.00345*sin(a),s))
            pt=p0+baseq@local;heights=[]
            for tree in trees:
                hit,*_=tree.ray_cast(Vector((pt.x,pt.y,.15)),Vector((0,0,-1)))
                if hit is not None:heights.append(hit.z)
            if heights:supports.append((s,k,max(heights)))
    best=None
    for j in range(601):
        slope=-.060+j*.00015
        direction_test=Vector((.94,-.342,slope)).normalized()
        q=direction_test.to_track_quat("Z","Y")
        ridgez=[(q@Vector((.00345*cos(k*pi/3),.00345*sin(k*pi/3),0))).z for k in range(6)]
        height=max(h-s*direction_test.z-ridgez[k] for s,k,h in supports)
        score=height+.078*direction_test.z
        if best is None or score<best[0]:best=(score,height,direction_test)
    p0.z=best[1]+.000025
    direction=best[2]
    # Construct along local Z then turn to lie flat. Apothem 3 mm.
    quat=direction.to_track_quat("Z","Y")
    def orient(o):
        o.rotation_mode="QUATERNION";o.rotation_quaternion=quat;o.location=p0
        return o
    r=.00345
    profile=[(.00005,0),(.0008,.0038),(.00105,.006),(.00345,.019)]
    orient(lathe("Sharpened cedar pencil tip",profile,cedar,segments=6))
    orient(lathe("Exposed graphite writing point",[(.00004,0),(.00078,.0039),(.00084,.0045)],graphite,segments=24))
    orient(lathe("Six-sided red lacquer pencil",[(r,.019),(r,.137),(.0032,.140)],red,segments=6))
    orient(lathe("Unpainted pencil end",[(.0032,.1401),(0,.1401)],cedar,segments=6))
    # Fine irregular paint loss along two ridges, not decorative lettering.
    for k in range(14):
        a=(k%6)*pi/3
        z=.025+random.random()*.10
        points=[(r*cos(a),r*sin(a),z),(r*cos(a+.018),r*sin(a+.018),z+random.uniform(.0007,.0032))]
        o=curve("Small lacquer wear",points,.00005,cedar);orient(o)
    return p0

def mug():
    c=(.153,.105,0)
    profile=[(0,.003),(.031,.003),(.034,.004),(.036,.009),(.038,.071),(.039,.078),
             (.039,.081),(.0377,.082),(.0368,.080),(.0366,.074),(.034,.010),(.030,.007),(0,.007)]
    lathe("Plain white enamel mug · hollow interior",profile,enamel,c)
    torus("Dark rolled enamel lip",(c[0],c[1],.081),.0382,.0015,rim)
    torus("Enamel mug foot",(c[0],c[1],.005),.033,.0009,enamel)
    pts=[]
    for i in range(65):
        a=-pi/2+pi*i/64
        pts.append((c[0]+.035+.027*cos(a),c[1],.044+.028*sin(a)))
    curve("Enamel mug loop handle",pts,.0042,enamel)
    for phi,z,size in [(-1.24,.065,.0020),(-2.13,.016,.0011)]:
        cr=.036+(z-.009)/.062*.002+.00013
        vs=[(c[0]+cr*cos(phi),c[1]+cr*sin(phi),z)]
        for j in range(13):
            a=2*pi*j/12;rad=size*(.8+.2*sin(j*7))
            ph=phi+cos(a)*rad/.038;zz=z+sin(a)*rad
            rr=.036+(zz-.009)/.062*.002+.00013
            vs.append((c[0]+rr*cos(ph),c[1]+rr*sin(ph),zz))
        mesh("Tiny chip in white enamel",vs,[(0,j,j+1) for j in range(1,13)],chip)

def glasses():
    # Round fine wire frames resting on their folded temples.
    cx,cy=.133,-.117
    for dx in (-.028,.028):
        torus("Round patinated spectacle frame",(cx+dx,cy,.008),.023,.00065,brass)
        lathe("Thin clear glass lens",[(0,.008),(.0223,.008),(.0223,.009),(0,.009)],glass,(cx+dx,cy,0),64)
    curve("Spectacle arched bridge",[(cx-.005,cy+.004,.008),(cx,cy+.008,.009),(cx+.005,cy+.004,.008)],.0006,brass)
    for side in (-1,1):
        curve("Folded wire temple",[(cx+side*.052,cy,.008),(cx+side*.049,cy+.046,.005),
             (cx-side*.025,cy+.057,.002),(cx-side*.034,cy+.052,.002)],.0007,brass)

def set_camera(scene,opened):
    d=bpy.data.cameras.new("Study camera");o=bpy.data.objects.new("Study camera",d);scene.collection.objects.link(o);scene.camera=o
    d.lens=50;d.sensor_width=36;d.clip_start=.005;d.clip_end=20
    d.dof.use_dof=True;d.dof.aperture_fstop=8
    f=bpy.data.objects.new("Narrative focus",None);scene.collection.objects.link(f);d.dof.focus_object=f
    total=180 if opened else 330
    # Sample the director's easing curve exactly, then bake transforms every frame.
    def easing(t):
        lo=0;hi=1
        for _ in range(28):
            u=(lo+hi)/2
            x=3*(1-u)**2*u*.16+3*(1-u)*u*u*.3+u**3
            if x<t:lo=u
            else:hi=u
        return 3*(1-u)**2*u+3*(1-u)*u*u+u**3
    if opened:
        start=Vector((-.004,-.365,.365));end=Vector((.030,-.021,.205))
        ta=Vector((-.015,.016,.003));tb=Vector((.032,.052,.003))
        d.lens=50
    else:
        start=Vector((-.058,-.128,.241));end=Vector((.060,-.395,.660))
        ta=Vector((-.070,.042,.002));tb=Vector((-.013,.015,.0))
    for fr in range(1,total+1):
        t=(fr-1)/(total-1)
        # Mix with linear movement to retain a slow perceptible drift throughout.
        e=.32*easing(t)+.68*(t*t*(3-2*t))
        o.location=start.lerp(end,e)
        target=ta.lerp(tb,e)
        o.rotation_euler=(target-o.location).to_track_quat("-Z","Y").to_euler()
        if opened:
            focus_end=Vector((.030,.067,page_height(.5,(.067-.015)/.184+.5,.00119,1,6)))
            f.location=Vector((-.015,.023,.005)).lerp(focus_end,e)
            d.dof.aperture_fstop=9*(1-e)+7.1*e
        else:
            f.location=Vector((-.070,.030,.002)).lerp(Vector((-.060,.018,.002)),e)
            d.dof.aperture_fstop=8*(1-e)+4.5*e
        d.dof.keyframe_insert("aperture_fstop",frame=fr)
        o.keyframe_insert("location",frame=fr);o.keyframe_insert("rotation_euler",frame=fr);f.keyframe_insert("location",frame=fr)
    return o

def area(name,loc,target,power,color,size,shape="DISK",size_y=None):
    d=bpy.data.lights.new(name,"AREA");d.energy=power;d.color=color;d.shape=shape;d.size=size
    if size_y is not None:d.size_y=size_y
    o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o);o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler();return o

def setup(name,opened):
    s=bpy.data.scenes.new(name);bpy.context.window.scene=s
    s.render.engine="CYCLES";s.cycles.device="GPU";s.cycles.samples=128
    s.unit_settings.system="METRIC"
    s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.012
    s.cycles.use_denoising=True;s.cycles.denoiser="OPTIX"
    s.cycles.seed=1976;s.cycles.use_animated_seed=False
    s.cycles.max_bounces=7;s.cycles.diffuse_bounces=3;s.cycles.glossy_bounces=4
    s.cycles.transmission_bounces=5;s.cycles.transparent_max_bounces=4
    s.cycles.sample_clamp_indirect=3
    s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
    s.render.fps=30;s.render.image_settings.file_format="PNG";s.render.image_settings.color_mode="RGB";s.render.image_settings.color_depth="8"
    s.render.image_settings.compression=25;s.render.film_transparent=False
    s.render.use_persistent_data=True
    s.view_settings.view_transform="AgX";s.view_settings.look="AgX - Medium High Contrast"
    s.view_settings.exposure=.20
    s.world=bpy.data.worlds.new(name+" ambient");s.world.use_nodes=True
    s.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.58,.55,.48,1)
    s.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.15
    s.frame_start=1;s.frame_end=180 if opened else 330
    # Custom UV desk plane over a bevelled solid tabletop.
    cube("Solid old desk edge",(0,0,-.019),(.96,.73,.038),wood,.008)
    mesh("Elm grain top surface",[(-.48,-.365,.00005),(.48,-.365,.00005),(.48,.365,.00005),(-.48,.365,.00005)],
         [(0,1,2,3)],wood,[(0,0),(1,0),(1,1),(0,1)])
    for k in range(3):
        sheet("Blank manuscript sheet "+str(k+1),(-.223+k*.002,-.124-k*.001),.14,.198,
              .00025+k*.00014,ruled if k==2 else paper,index=k,angle=-.14+k*.018,thick=.00012)
    book(opened);pencil(opened)
    if not opened:mug()
    key=area("Low warm left window",(-.34,.06,.22),(-.040,.018,0),.55,(1.0,.88,.69),.11,"RECTANGLE",.22)
    key.data.spread=math.radians(65)
    area("Subtle reflected room fill",(.18,-.24,.28),(-.03,.03,0),.12,(.90,.91,1),.42)
    if not opened:
        key.data.color=(1.0,.89,.72);key.data.keyframe_insert("color",frame=1)
        key.data.color=(1.0,.865,.675);key.data.keyframe_insert("color",frame=330)
    set_camera(s,opened);s.frame_set(1)
    s["specification"]="1976 People's Publishing House original scan booklet, 130x184mm, 28 pages, ~2mm closed thickness."
    s["palette"]="Old paper #EDE5D4 / #E4D9C3, ink #1C1A17, cinnabar #B5302A, sparse brass #8A6A3B"
    return s

prefs=bpy.context.preferences.addons["cycles"].preferences
backend="OPTIX"
try:
    prefs.compute_device_type="OPTIX";prefs.get_devices()
    if not any(d.type=="OPTIX" for d in prefs.devices):raise RuntimeError("No OptiX device")
except Exception:
    backend="CUDA";prefs.compute_device_type="CUDA";prefs.get_devices()
for d in prefs.devices:d.use=d.type==backend
closed=setup("desk_close",False)
opened=setup("desk_open",True)
for s in list(bpy.data.scenes):
    if s.name not in ("desk_close","desk_open"):bpy.data.scenes.remove(s)
bpy.context.window.scene=closed
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/"C_desk.blend"))
(ROOT/"scene_manifest.json").write_text(json.dumps({
    "blender":bpy.app.version_string,"backend":backend,"scenes":["desk_open","desk_close"],
    "objects":len(bpy.data.objects),"images_packed":all(i.packed_file for i in bpy.data.images if i.source=="FILE"),
    "geometry":"14 individual leaves in the 28-page closed booklet; curved paper surfaces, two iron saddle staples; 140mm six-sided pencil; hollow enamel mug"
},indent=2),encoding="utf-8")
print("SCENE_BUILD_OK",backend)
