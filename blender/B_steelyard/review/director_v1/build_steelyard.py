"""B 杆秤：完全程序化的模型、材质、镜头及可复现的力矩动画。

运行：
  blender --background --factory-startup --python build_steelyard.py
所有长度以米计。动画烘焙为普通关键帧，无需安装插件或保留 handler。
"""
import bpy
import math
import json
import sys
import bmesh
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
RENDERS = ROOT.parents[1] / "assets" / "renders"
PI = math.pi
FPS = 30
G = 9.80665
PIVOT = Vector((0, 0, 0.405))
ROD_Z = -0.023
X_LOAD = -0.112
X_MIN, X_MAX = -0.13, 0.62
PAN_R = 0.119
M_LOAD, M_WEIGHT, M_BEAM = 0.86, 0.18, 0.135
BEAM_COM = X_MIN + .75 * (.012**2+2*.012*.0065+3*.0065**2)/(4*(.012**2+.012*.0065+.0065**2))
X_BALANCE = (M_LOAD * -X_LOAD - M_BEAM * BEAM_COM) / M_WEIGHT
X_START = 0.105
COLLECTIONS = {}
MOTION = []


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in c) + (1,)


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    COLLECTIONS[name] = c
    return c


def put(obj, coll, parent=None):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    if parent:
        obj.parent = parent
    return obj


def empty(name, coll, parent=None):
    o = bpy.data.objects.new(name, None)
    coll.objects.link(o)
    o.parent = parent
    o.empty_display_size = .015
    return o


def mesh(name, verts, faces, material, coll, parent=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.parent = parent
    if material:
        ob.data.materials.append(material)
    for p in me.polygons:
        p.use_smooth = True
    return ob


def bevel(ob, width, segments=3):
    m = ob.modifiers.new("手工磨圆边缘", "BEVEL")
    m.width = width
    m.segments = segments
    return m


def material(name, color, metal=0, rough=.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = srgb(color)
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    return m, p, m.node_tree.nodes, m.node_tree.links


def noise(nodes, links, scale, detail=3, vector=None):
    n = nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    if vector:
        links.new(vector, n.inputs["Vector"])
    return n


def ramp(nodes, links, source, colors):
    n = nodes.new("ShaderNodeValToRGB")
    r = n.color_ramp
    for pos, color in colors[:2]:
        e = r.elements[0 if pos == colors[0][0] else 1]
        e.position, e.color = pos, srgb(color)
    for pos, color in colors[2:]:
        e = r.elements.new(pos)
        e.color = srgb(color)
    links.new(source, n.inputs[0])
    return n


def make_materials():
    result = {}
    m,p,n,l = material("红褐硬木 · 顺纹油润包浆", "382017", rough=.39)
    tc = n.new("ShaderNodeTexCoord")
    v = n.new("ShaderNodeVectorMath")
    v.operation = "MULTIPLY"
    v.inputs[1].default_value = (90, 1500, 1500)
    l.new(tc.outputs["Object"], v.inputs[0])
    grain = noise(n,l,1,3,v.outputs[0])
    grain.inputs["Roughness"].default_value = .68
    col = ramp(n,l,grain.outputs["Fac"],[(.22,"160C09"),(.78,"583723"),(.46,"30180F")])
    l.new(col.outputs[0],p.inputs["Base Color"])
    micro = noise(n,l,6800,2,tc.outputs["Object"])
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = .32
    bump.inputs["Distance"].default_value = .00011
    l.new(grain.outputs["Fac"],bump.inputs["Height"])
    fine = n.new("ShaderNodeBump")
    fine.inputs["Strength"].default_value = .2
    fine.inputs["Distance"].default_value = .000038
    l.new(micro.outputs["Fac"],fine.inputs["Height"])
    l.new(bump.outputs[0],fine.inputs["Normal"])
    l.new(fine.outputs[0],p.inputs["Normal"])
    rough=n.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value=.32
    rough.inputs["To Max"].default_value=.48
    l.new(grain.outputs["Fac"],rough.inputs[0])
    l.new(rough.outputs[0],p.inputs["Roughness"])
    p.inputs["Coat Weight"].default_value = .1
    p.inputs["Coat Roughness"].default_value = .36
    result["wood"] = m
    for key, color, rough in [("brass","8A6A3B",.43),("bright","A58A56",.3),
                               ("iron","33312D",.63),("edge","67655C",.4)]:
        m,p,n,l = material({"brass":"旧铜 · 锤痕与氧化", "bright":"磨亮黄铜",
                            "iron":"铸铁 · 砂型肌理", "edge":"铁器磨亮棱边"}[key],
                           color, .86 if "iron" not in key else .76,rough)
        tc = n.new("ShaderNodeTexCoord")
        fine = noise(n,l,3600 if key in ("iron","edge") else 2300,2,tc.outputs["Object"])
        broad = noise(n,l,185,4,tc.outputs["Object"])
        if key == "brass":
            c = ramp(n,l,broad.outputs["Fac"],[(.15,"665536"),(.85,"998253"),(.5,"826B43")])
        elif key == "iron":
            c = ramp(n,l,broad.outputs["Fac"],[(.15,"24221E"),(.85,"484237"),(.51,"34312A")])
        else:
            c = None
        if c:
            l.new(c.outputs[0],p.inputs["Base Color"])
        b = n.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = .25 if key == "iron" else .15
        b.inputs["Distance"].default_value = .00015 if key == "iron" else .000045
        l.new(fine.outputs["Fac"],b.inputs["Height"])
        l.new(b.outputs[0],p.inputs["Normal"])
        mr = n.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value=0
        mr.inputs["From Max"].default_value=1
        mr.inputs["To Min"].default_value=max(.18,rough-.13)
        mr.inputs["To Max"].default_value=min(.85,rough+.15)
        l.new(broad.outputs["Fac"],mr.inputs[0])
        l.new(mr.outputs[0],p.inputs["Roughness"])
        result[key] = m
    for key,color in [("hemp","786A50"),("hemp_light","958468"),("hemp_dark","5B503D")]:
        m,p,n,l = material("旧麻绳 · "+key,color,rough=.91)
        p.inputs["Sheen Weight"].default_value=.22
        tc=n.new("ShaderNodeTexCoord")
        tex=noise(n,l,8500,2,tc.outputs["Object"])
        stains=noise(n,l,700,2,tc.outputs["Object"])
        staincol=ramp(n,l,stains.outputs["Fac"],[(.18,"4B4232"),(.82,color)])
        l.new(staincol.outputs[0],p.inputs["Base Color"])
        b=n.new("ShaderNodeBump")
        b.inputs["Strength"].default_value=.24
        b.inputs["Distance"].default_value=.000035
        l.new(tex.outputs["Fac"],b.inputs["Height"])
        l.new(b.outputs[0],p.inputs["Normal"])
        result[key]=m
    m,p,n,l=material("旧纸背景 #EDE5D4", "EDE5D4",rough=.95)
    tc=n.new("ShaderNodeTexCoord")
    tex=noise(n,l,1800,2,tc.outputs["Object"])
    b=n.new("ShaderNodeBump")
    b.inputs["Strength"].default_value=.11
    b.inputs["Distance"].default_value=.000045
    l.new(tex.outputs["Fac"],b.inputs["Height"])
    l.new(b.outputs[0],p.inputs["Normal"])
    result["paper"]=m
    return result


def lathe(name, profile, mat, coll, parent=None, center=(0,0,0), segments=96, distress=0):
    verts, faces = [], []
    for j,(r,z) in enumerate(profile):
        for i in range(segments):
            a=2*PI*i/segments
            variation = distress*(.6*math.sin(7*a+z*113)+.4*math.sin(11*a+z*41))
            rr=max(0,r+variation)
            verts.append((center[0]+rr*math.cos(a),center[1]+rr*math.sin(a),center[2]+z))
    for j in range(len(profile)-1):
        for i in range(segments):
            a=j*segments+i; b=j*segments+(i+1)%segments
            faces.append((a,b,b+segments,a+segments))
    return mesh(name,verts,faces,mat,coll,parent)


def tube(name, pts, radius, mat, coll, parent=None, sides=8):
    pts=[Vector(p) for p in pts]
    vs,fs=[],[]
    prev=None
    for i,p in enumerate(pts):
        t=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized()
        if prev is None:
            ref=Vector((0,1,0)) if abs(t.y)<.85 else Vector((1,0,0))
            u=t.cross(ref).normalized()
        else:
            u=(prev-t*prev.dot(t)).normalized()
        prev=u
        v=t.cross(u).normalized()
        for k in range(sides):
            a=2*PI*k/sides
            q=p+radius*(u*math.cos(a)+v*math.sin(a))
            vs.append(tuple(q))
    for i in range(len(pts)-1):
        for k in range(sides):
            a=i*sides+k;b=i*sides+(k+1)%sides
            fs.append((a,b,b+sides,a+sides))
    fs.append(tuple(range(sides-1,-1,-1)))
    fs.append(tuple((len(pts)-1)*sides+k for k in range(sides)))
    return mesh(name,vs,fs,mat,coll,parent)


def resample(pts, step=.00065):
    pts=[Vector(p) for p in pts]
    out=[pts[0]]
    for a,b in zip(pts,pts[1:]):
        n=max(1,math.ceil((b-a).length/step))
        out.extend(a.lerp(b,i/n) for i in range(1,n+1))
    return out


def rope(name, pts, radius, coll, parent, mats, pitch=.005, fibers=True):
    pts=resample(pts)
    dist=0
    paths=[[],[],[]]
    fiber_paths=[[] for _ in range(6)]
    prev=None
    for i,p in enumerate(pts):
        if i: dist+=(p-pts[i-1]).length
        t=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized()
        if prev is None:
            ref=Vector((0,1,0)) if abs(t.y)<.85 else Vector((1,0,0))
            u=t.cross(ref).normalized()
        else:
            u=(prev-t*prev.dot(t)).normalized()
        prev=u
        v=t.cross(u).normalized()
        for k in range(3):
            a=2*PI*(dist/pitch+k/3)
            q=p+radius*.48*(u*math.cos(a)+v*math.sin(a))
            paths[k].append(q)
            if fibers:
                for j in range(2):
                    b=a+2*PI*dist/.0018+j*PI
                    fiber_paths[k*2+j].append(q+radius*.49*(u*math.cos(b)+v*math.sin(b)))
    obs=[]
    for k in range(3):
        obs.append(tube(name+f" · 捻股{k+1}",paths[k],radius*.54,mats["hemp"],coll,parent))
    if fibers:
        for k,fp in enumerate(fiber_paths):
            obs.append(tube(name+f" · 细纤维{k+1}",fp,radius*.065,
                            mats["hemp_light" if k%2 else "hemp_dark"],coll,parent,sides=5))
    return obs


def torus(name,center,major,minor,mat,coll,parent=None,rotation=(PI/2,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,
                                    major_segments=64,minor_segments=12,
                                    location=(0,0,0))
    ob=bpy.context.object
    ob.name=name
    put(ob,coll,parent)
    ob.location=center
    ob.rotation_euler=rotation
    ob.data.materials.append(mat)
    for p in ob.data.polygons:p.use_smooth=True
    return ob


def cylinder_between(name,a,b,r,mat,coll,parent=None,vertices=64):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=(b-a).length)
    ob=bpy.context.object;ob.name=name
    put(ob,coll,parent)
    ob.location=(a+b)/2
    ob.rotation_euler=(b-a).to_track_quat("Z","Y").to_euler()
    ob.data.materials.append(mat)
    for p in ob.data.polygons:p.use_smooth=True
    bevel(ob,min(.0005,r*.1),3)
    return ob


def beam_radius(x):
    return .012-(x-X_MIN)/(X_MAX-X_MIN)*.0055


def build_rod(mats, coll):
    root=empty("01 力矩驱动秤杆",coll)
    root.location=PIVOT
    verts,faces=[],[]
    seg,rows=96,64
    for j in range(rows+1):
        x=X_MIN+(X_MAX-X_MIN)*j/rows
        rad=beam_radius(x)
        for i in range(seg):
            a=2*PI*i/seg
            r=rad*(1+.002*math.sin(3*a+x*17))
            verts.append((x,r*math.cos(a),ROD_Z+r*math.sin(a)))
    for j in range(rows):
        for i in range(seg):
            a=j*seg+i;b=j*seg+(i+1)%seg
            # Longitudinal surface with outward winding.
            faces.append((a,b,b+seg,a+seg))
    faces.extend([tuple(range(seg-1,-1,-1)),tuple(rows*seg+i for i in range(seg))])
    rod=mesh("75cm 渐细硬木秤杆",verts,faces,mats["wood"],coll,root)
    bevel(rod,.00045,3)
    for x,l in [(X_MIN+.009,.019),(X_MAX-.007,.015)]:
        r=beam_radius(x)+.0006
        cylinder_between("铜帽", (x-l/2,0,ROD_Z),(x+l/2,0,ROD_Z),r,mats["brass"],coll,root)
        for xx in (x-l/2+.0015,x+l/2-.0015):
            torus("铜帽边缘卷线",(xx,0,ROD_Z),r,.00065,mats["bright"],coll,root,(0,PI/2,0))
    # Fixed rod eyelets. These are rigid with the beam; hung assemblies are not.
    for name,x in [("提纽",0),("秤盘挂耳",X_LOAD)]:
        if name=="提纽":
            center=(x,0,-.008)
            torus(name+"铜环",center,.008,.0017,mats["brass"],coll,root)
            cylinder_between(name+"铆钉",(x,.012,ROD_Z),(x,-.012,ROD_Z),.0022,mats["brass"],coll,root)
            tube("提纽短柄",[(0,0,ROD_Z+.007),(0,0,-.014)],.0022,mats["brass"],coll,root)
        else:
            torus(name+"铜环",(x,0,ROD_Z-.014),.006,.00145,mats["brass"],coll,root)
            tube("盘环嵌杆铆钉",[(x,0,ROD_Z-.007),(x,0,ROD_Z-.011)],.002,mats["brass"],coll,root)
    # 12 groups of five inlaid dots; triple origin. Diameter exactly 1.2 mm.
    dot_positions=[]
    for g in range(12):
        for k in range(5):
            dot_positions.append((.052+g*.043+k*.0061,0))
    for x,dz in [(.032,0),(.025,.0021),(.025,-.0021)]:
        dot_positions.append((x,dz))
    for i,(x,dz) in enumerate(dot_positions):
        r=beam_radius(x)
        y=-math.sqrt(max(0,r*r-dz*dz))
        ob=lathe(f"黄铜秤星 {i+1:02}",[(0,-.00015),(.00055,-.00015),
                   (.0006,0),(.00052,.0002),(0,.00028)],mats["bright"],coll,root,segments=16)
        ob.rotation_euler=(PI/2,0,0)
        ob.location=(x,y,ROD_Z+dz)
    # Visible knots connect the support rope to the eye, without stretching.
    knots=[]
    for i in range(121):
        a=2*PI*i/120
        knots.append((.0033*math.cos(a),-.0002+.0033*math.sin(a),.006+.001*i/120))
    rope("提绳收结",knots,.0012,coll,None,mats,pitch=.004)
    for ob in list(coll.objects):
        if ob.name.startswith("提绳收结"):
            ob.location=PIVOT
    support_loop=[]
    for i in range(121):
        a=2*PI*i/120
        support_loop.append((0,.0032*math.sin(a),PIVOT.z+.002+.0062*math.cos(a)))
    rope("提绳穿环闭合结",support_loop,.0012,coll,None,mats,pitch=.004)
    rope("向上出画的提绳",[(0,0,PIVOT.z+.005),(0,0,1.15)],.0017,coll,None,mats,pitch=.006)
    return root


def build_pan(mats, coll):
    root=empty("02 重力竖直 · 秤盘与齿轮",coll)
    # Open S hook, physically interlinked with beam's closed ring.
    pts=[]
    for i in range(65):
        a=math.radians(45)+math.radians(275)*i/64
        pts.append((.0056*math.cos(a),0,-.004+.0056*math.sin(a)))
    for i in range(49):
        a=math.radians(140)-math.radians(265)*i/48
        pts.append((-.004+.0058*math.cos(a),0,-.013+.0058*math.sin(a)))
    tube("锻铜 S 钩",pts,.0015,mats["brass"],coll,root,12)
    apex=Vector((-.003,0,-.024))
    hook_loop=[]
    for i in range(97):
        a=2*PI*i/96
        hook_loop.append((-.004,.0031*math.sin(a),-.020+.0045*math.cos(a)))
    rope("三绳汇聚穿钩结",hook_loop,.00115,coll,root,mats,pitch=.004)
    pan_z=-.253
    profile=[(0,pan_z-.008),(.025,pan_z-.0078),(.055,pan_z-.005),
             (.087,pan_z+.0008),(.107,pan_z+.008),(.119,pan_z+.016),
             (.1202,pan_z+.018),(.1195,pan_z+.020),(.1175,pan_z+.020),
             (.1165,pan_z+.017),(.105,pan_z+.0095),(.086,pan_z+.0025),
             (.054,pan_z-.0034),(.025,pan_z-.0063),(0,pan_z-.0065)]
    pan=lathe("手工锤打黄铜浅盘 · 实体厚度",profile,mats["brass"],coll,root,segments=160,distress=.0003)
    torus("盘沿卷口",(0,0,pan_z+.0184),PAN_R,.0015,mats["bright"],coll,root,(0,0,0))
    for i,a in enumerate([math.radians(30),math.radians(150),math.radians(270)]):
        x,y=.113*math.cos(a),.113*math.sin(a)
        ring=(x,y,pan_z+.024)
        torus(f"盘沿系绳铜耳 {i+1}",ring,.0033,.00085,mats["brass"],coll,root,(PI/2,0,a))
        end=Vector((x,y,pan_z+.028))
        rope(f"三点吊绳 {i+1}",[apex,end],.00115,coll,root,mats,pitch=.0044)
        # Short tidy whipping at each load-bearing end.
        pts=[(x+.0018*math.cos(j*PI/12),y+.0018*math.sin(j*PI/12),
              pan_z+.032+j/72*.005) for j in range(73)]
        rope(f"吊绳末结 {i+1}",pts,.00048,coll,root,mats,pitch=.002,fibers=False)
    # Annular 24-tooth cast gear, flat on pan. One consistent watertight tooth mesh.
    N=24*8
    verts,faces=[],[]
    r_inner=.024
    profile_r=[.069,.069,.075,.0785,.0785,.075,.069,.069]
    z0,z1=pan_z+.002,pan_z+.017
    # Outer bottom, outer top, inner bottom, inner top.
    for ring in range(4):
        for i in range(N):
            a=2*PI*i/N
            r=profile_r[i%8] if ring<2 else r_inner
            z=z0 if ring%2==0 else z1
            verts.append((r*math.cos(a),r*math.sin(a),z))
    for i in range(N):
        j=(i+1)%N
        faces.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),
                      (N+i,N+j,3*N+j,3*N+i),(i,2*N+i,2*N+j,j)])
    gear=mesh("24齿铸铁齿轮 · 盘径三分之二",verts,faces,mats["iron"],coll,root)
    gear.data.materials.append(mats["edge"])
    bv=bevel(gear,.00065,3);bv.affect="EDGES";bv.material=1
    for p in gear.data.polygons:
        p.use_smooth=False
    # Hub boss and concentric casting edge, open through the center.
    lathe("齿轮凸缘",list(reversed([(.024,z1),(.024,z1+.004),(.025,z1+.005),
                     (.036,z1+.005),(.037,z1+.004),(.037,z1),(.024,z1)])),
          mats["iron"],coll,root,segments=96)
    torus("齿轮孔口磨亮",(0,0,z1+.0048),.0247,.00055,mats["edge"],coll,root,(0,0,0))
    return root


def build_weight(mats,coll):
    saddle=empty("03 可沿杆滑动 · 麻绳套",coll)
    root=empty("04 重力竖直 · 铸铁秤砣",coll)
    # Constant-length loop with a top tangent contact. As the rod tapers the
    # entire undeformed loop hangs fractionally lower, preserving rope length.
    # Rope loop rigidly follows the rod. Lower weight pivots independently.
    pts=[]
    loop_radius=beam_radius(X_START)+.00115
    for i in range(81):
        a=PI*i/80
        pts.append((.0015*math.sin(2*a),-loop_radius*math.cos(a),ROD_Z+loop_radius*math.sin(a)))
    pts.extend([(0,.009,ROD_Z-.009),(0,.005,ROD_Z-.03),
                (0,.0025,ROD_Z-.049),(0,0,ROD_Z-.051),
                (0,-.0025,ROD_Z-.049),(0,-.005,ROD_Z-.03),(0,-.009,ROD_Z-.009),
                (0,-loop_radius,ROD_Z)])
    rope("可滑动闭合麻绳套",pts,.00115,coll,saddle,mats,pitch=.0043)
    torus("秤砣铁提环",(0,0,-.006),.0084,.0021,mats["iron"],coll,root)
    torus("秤砣提环磨亮",(0,0,-.006),.0084,.00035,mats["edge"],coll,root)
    profile=[(0,-.016),(.006,-.016),(.007,-.020),(.0075,-.026),
             (.0105,-.031),(.0155,-.037),(.019,-.046),(.021,-.055),
             (.022,-.062),(.025,-.067),(.027,-.069),(.0275,-.072),
             (.027,-.075),(.024,-.078),(0,-.078)]
    lathe("葫芦钟形铸铁秤砣",list(reversed(profile)),mats["iron"],coll,root,segments=112,distress=.00016)
    torus("秤砣底沿磨耗",(0,0,-.073),.027,.00055,mats["edge"],coll,root,(0,0,0))
    return saddle,root


def aim(ob,target):
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat("-Z","Y").to_euler()


def build_stage(mats,coll):
    # Continuous cyclorama: floor, quarter-circle sweep, vertical backdrop.
    section=[(-2,-.28),(-.05,-.28)]
    r=.28
    for i in range(1,33):
        a=(PI/2)*i/32
        section.append((-.05+r*math.sin(a),-.28+r*(1-math.cos(a))))
    section.extend([(.23,1.0),(.23,2.5)])
    verts=[]
    for y,z in section:verts.extend([(-3,y,z),(3,y,z)])
    faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(section)-1)]
    mesh("无缝旧纸摄影背景",verts,faces,mats["paper"],coll)
    world=bpy.data.worlds.new("暖色摄影棚环境")
    world.use_nodes=True
    world.node_tree.nodes["Background"].inputs[0].default_value=srgb("EDE5D4")
    world.node_tree.nodes["Background"].inputs[1].default_value=.2
    bpy.context.scene.world=world
    for name,loc,power,size,color in [
        ("左上大柔光",(-.55,-.7,1.35),72,.6,"FFF0D9"),
        ("右侧弱补光",(.95,-.12,.7),19,.65,"F5EFDE"),
        ("上方窄柔光反射",(.1,.16,1.45),24,.5,"FFF2DF")]:
        data=bpy.data.lights.new(name,"AREA")
        data.energy=power;data.shape="DISK";data.size=size
        data.color=srgb(color)[:3]
        ob=bpy.data.objects.new(name,data);coll.objects.link(ob)
        ob.location=loc;aim(ob,(.2,0,.22))


def smooth(t):
    t=max(0,min(1,t))
    return t*t*t*(t*(t*6-15)+10)


def slide_ease(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)


def derive_masses():
    global M_LOAD,M_WEIGHT,M_BEAM,X_BALANCE
    volumes={}
    for name in ("75cm 渐细硬木秤杆","手工锤打黄铜浅盘 · 实体厚度",
                 "24齿铸铁齿轮 · 盘径三分之二","齿轮凸缘","葫芦钟形铸铁秤砣"):
        ob=bpy.data.objects[name]
        bm=bmesh.new();bm.from_mesh(ob.data)
        volumes[name]=bm.calc_volume(signed=True)
        bm.free()
        if volumes[name]<=0:
            raise RuntimeError("外法线/体积检查失败："+name)
    M_BEAM=volumes["75cm 渐细硬木秤杆"]*850
    M_LOAD=volumes["手工锤打黄铜浅盘 · 实体厚度"]*8500+(
        volumes["24齿铸铁齿轮 · 盘径三分之二"]+volumes["齿轮凸缘"])*7200
    M_WEIGHT=volumes["葫芦钟形铸铁秤砣"]*7200
    X_BALANCE=(M_LOAD*-X_LOAD-M_BEAM*BEAM_COM)/M_WEIGHT
    if not .25<X_BALANCE<.56:
        raise RuntimeError(f"平衡点超出可用秤星范围：{X_BALANCE}")
    (ROOT/"geometry_audit.json").write_text(json.dumps({
        "signed_volumes_m3":volumes,"density_kg_m3":{"wood":850,"brass":8500,"cast_iron":7200},
        "mass_load_kg":M_LOAD,"mass_weight_kg":M_WEIGHT,"mass_wood_beam_kg":M_BEAM,
        "note":"质量据主要物件净体积估计；小铜环、绳结和铜帽不单独计入等效质量。"
    },ensure_ascii=False,indent=2),encoding="utf-8")


def model_motion():
    """Reduced, torque-driven, actively steadied weighing demonstration.

    An unseen holder supplies the steadying moment implied by the requested
    12-degree static unbalanced opening. A completely free ideal pivot cannot
    remain static at that prescribed angle. The effective compliance represents
    that hand/cord support, rather than pretending that unequal torque is static.
    T = g[(Mload*a-Mbeam*c-Mweight*x)cos(theta)-Mtotal*h*sin(theta)]
    I*theta'' = T - K_hold*theta - C_hold*theta'.
    """
    theta0=math.radians(12)
    total=M_LOAD+M_WEIGHT+M_BEAM
    initial_delta=M_LOAD*-X_LOAD-M_BEAM*BEAM_COM-M_WEIGHT*X_START
    h=-ROD_Z
    k=G*(initial_delta*math.cos(theta0)-total*h*math.sin(theta0))/theta0
    inertia=.25
    damping=1.6
    dt=1/(FPS*16)
    theta,omega=theta0,0
    states={}
    for frame in range(0,301):
        for sub in range(16):
            t=frame+(sub-15)/16
            x=X_START+(X_BALANCE-X_START)*slide_ease((t-30)/170)
            delta=M_LOAD*-X_LOAD-M_BEAM*BEAM_COM-M_WEIGHT*x
            torque=G*(delta*math.cos(theta)-total*h*math.sin(theta))
            if frame>30:
                # At the endpoint the operator relaxes grip; small residual
                # angular velocity produces the single damped settling lobe.
                release=smooth((t-180)/20)
                c=damping*(1-release)+1.3*release
                acc=(torque-k*theta-c*omega)/inertia
                omega+=acc*dt
                theta+=omega*dt
        if frame>=250:
            theta=omega=0
        states[frame]={"frame":frame,"weight_x_m":x,"beam_angle_rad":theta,
                       "beam_angle_deg":math.degrees(theta),"angular_velocity":omega,
                       "load_moment_kg_m":M_LOAD*-X_LOAD,
                       "beam_moment_kg_m":M_BEAM*BEAM_COM,
                       "weight_moment_kg_m":M_WEIGHT*x,
                       "torque_residual_horizontal_Nm":G*delta}
    meta={"mass_load_kg":M_LOAD,"mass_weight_kg":M_WEIGHT,"mass_beam_kg":M_BEAM,
          "load_arm_m":-X_LOAD,"beam_center_m":BEAM_COM,
          "balance_x_m":X_BALANCE,"inertia_kg_m2":inertia,
          "support_compliance_Nm_rad":k,"description_zh":
          "含画外持秤者稳定作用的受控准静态演示。起始12度静止需要支承反力矩；"
          "不是无外力矩的自由杆秤刚体模拟。重物、秤砣、杆自重力矩共同驱动积分。",
          "states":list(states.values())}
    (ROOT/"motion_audit.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    return states


def transform_point(x,z,theta):
    return PIVOT+Vector((x*math.cos(theta)-z*math.sin(theta),0,x*math.sin(theta)+z*math.cos(theta)))


def key_transform(ob,frame):
    ob.keyframe_insert(data_path="location",frame=frame)
    ob.keyframe_insert(data_path="rotation_euler",frame=frame)


def animate(beam,pan,saddle,weight,states):
    # Driven pendulum response to horizontal acceleration; rods never stretch.
    pan_phi=pan_vel=weight_phi=weight_vel=0
    last_pan_x=last_weight_x=None
    last_pan_v=last_weight_v=0
    for f in range(0,301):
        st=states[f];theta=st["beam_angle_rad"];x=st["weight_x_m"]
        beam.rotation_euler=(0,-theta,0)
        anchor=transform_point(X_LOAD,ROD_Z-.018,theta)
        sag=beam_radius(x)-beam_radius(X_START)
        saddle.location=transform_point(x,sag,theta)
        saddle.rotation_euler=(0,-theta,0)
        # top of the weight ring intersects only the rope's empty loop aperture
        wp=transform_point(x,ROD_Z-.052+sag,theta)
        if last_pan_x is not None:
            pv=(anchor.x-last_pan_x)*FPS;wv=(wp.x-last_weight_x)*FPS
            pa=(pv-last_pan_v)*FPS;wa=(wv-last_weight_v)*FPS
            for _ in range(8):
                dt=1/(FPS*8)
                pan_vel+=(-G/.24*pan_phi-2.8*pan_vel-pa/.24)*dt
                pan_phi+=pan_vel*dt
                weight_vel+=(-G/.1*weight_phi-6*weight_vel-wa/.1)*dt
                weight_phi+=weight_vel*dt
            last_pan_v,last_weight_v=pv,wv
        last_pan_x,last_weight_x=anchor.x,wp.x
        if f>=250: pan_phi=weight_phi=pan_vel=weight_vel=0
        pan.location=anchor;pan.rotation_euler=(0,pan_phi,0)
        weight.location=wp;weight.rotation_euler=(0,weight_phi,0)
        for ob in (beam,pan,saddle,weight):key_transform(ob,f)
        st["pan_swing_deg"]=math.degrees(pan_phi)
        st["weight_swing_deg"]=math.degrees(weight_phi)
    data=json.loads((ROOT/"motion_audit.json").read_text(encoding="utf-8"))
    data["states"]=list(states.values())
    (ROOT/"motion_audit.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")


def camera(coll,name):
    d=bpy.data.cameras.new(name)
    ob=bpy.data.objects.new(name,d);coll.objects.link(ob)
    d.type="PERSP";d.sensor_width=36
    d.dof.use_dof=True
    d.dof.aperture_blades=9
    d.clip_start=.005;d.clip_end=50
    return ob


def configure(scene,frames):
    scene.render.engine="CYCLES"
    scene.cycles.device="GPU"
    scene.cycles.samples=128
    scene.cycles.use_adaptive_sampling=True
    scene.cycles.adaptive_threshold=.008
    scene.cycles.adaptive_min_samples=48
    scene.cycles.use_denoising=True
    scene.cycles.denoiser="OPENIMAGEDENOISE"
    scene.cycles.denoising_use_gpu=True
    scene.cycles.seed=2718
    scene.cycles.use_animated_seed=False
    scene.cycles.max_bounces=7
    scene.cycles.diffuse_bounces=3
    scene.cycles.glossy_bounces=4
    scene.cycles.transmission_bounces=3
    scene.cycles.transparent_max_bounces=4
    scene.cycles.sample_clamp_indirect=3
    scene.render.resolution_x=1920
    scene.render.resolution_y=1080
    scene.render.resolution_percentage=100
    scene.render.fps=30
    scene.render.film_transparent=False
    scene.render.image_settings.file_format="PNG"
    scene.render.image_settings.color_mode="RGB"
    scene.render.image_settings.color_depth="8"
    scene.render.image_settings.compression=20
    scene.render.use_persistent_data=True
    scene.view_settings.view_transform="AgX"
    scene.view_settings.look="AgX - Medium High Contrast"
    scene.view_settings.exposure=.05
    scene.view_settings.gamma=1
    scene.frame_start=1;scene.frame_end=frames
    scene.unit_settings.system="METRIC"


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for d in list(bpy.data.collections):
        if not d.objects:bpy.data.collections.remove(d)
    scene=bpy.context.scene
    scene.name="B1 · steelyard_balance"
    modelcoll=collection("01 · 杆秤 | 实际米制尺寸")
    pancoll=collection("02 · 黄铜盘与铸铁齿轮")
    weightcoll=collection("03 · 麻绳套与钟形秤砣")
    stagecoll=collection("04 · 旧纸摄影棚")
    camcoll=collection("05 · 镜头与焦点")
    mats=make_materials()
    beam=build_rod(mats,modelcoll)
    pan=build_pan(mats,pancoll)
    saddle,weight=build_weight(mats,weightcoll)
    derive_masses()
    build_stage(mats,stagecoll)
    states=model_motion()
    animate(beam,pan,saddle,weight,states)
    focus=empty("B1 焦点 · 提纽附近",camcoll)
    focus.location=(.035,0,.37)
    cam=camera(camcoll,"B1 62mm · 缓推6%")
    cam.data.lens=62
    cam.data.dof.focus_object=focus
    cam.data.dof.aperture_fstop=7.1
    target=Vector((.182,0,.245))
    start=Vector((.182,-1.85,.83))
    for f in range(1,301):
        t=smooth((f-1)/299)
        cam.location=target+(start-target)*(1-.06*t)
        aim(cam,target)
        key_transform(cam,f)
    scene.camera=cam
    configure(scene,300)
    scene.render.filepath=str(RENDERS/"steelyard_balance"/"frames"/"")
    scene["说明"]="B1：力矩驱动、画外持秤者稳定；0–30保持，30–200移砣，200–250回稳，250–300保持。"
    scene["质量说明"]="传统杆秤三股真几何麻绳、63颗1.2mm黄铜秤星、24齿铸铁齿轮、旧铜浅盘。"
    # Detail reuses the final rig pose, with independently frozen object transforms.
    detail=bpy.data.scenes.new("B2 · steelyard_detail")
    detail.world=scene.world
    configure(detail,150)
    detail.cycles.samples=160
    detail.cycles.adaptive_threshold=.007
    scene.frame_set(300)
    dcoll=bpy.data.collections.new("B2 · 同一杆秤最终平衡姿态")
    detail.collection.children.link(dcoll)
    mapping={}
    for coll in (modelcoll,pancoll,weightcoll,stagecoll):
        for original in coll.objects:
            copy=original.copy()
            copy.animation_data_clear()
            dcoll.objects.link(copy)
            mapping[original]=copy
    for orig,copy in mapping.items():
        copy.parent=mapping.get(orig.parent)
    dcamcoll=bpy.data.collections.new("B2 · 平行微距镜头")
    detail.collection.children.link(dcamcoll)
    dcam=camera(dcamcoll,"B2 85mm · 平行扫过秤星")
    dcam.data.lens=85
    dcam.data.dof.aperture_fstop=9
    dfocus=empty("B2 焦点随秤星滑移",dcamcoll)
    dcam.data.dof.focus_object=dfocus
    for f in range(1,151):
        t=smooth(min(1,(f-1)/133))
        x=.108+(X_BALANCE-.108)*t
        target=Vector((x,-.009,PIVOT.z+ROD_Z-.001))
        dcam.location=target+Vector((0,-.335,.077))
        aim(dcam,target)
        dfocus.location=target
        key_transform(dcam,f)
        dfocus.keyframe_insert(data_path="location",frame=f)
    detail.camera=dcam
    detail.render.filepath=str(RENDERS/"steelyard_detail"/"frames"/"")
    detail["说明"]="B1第300帧姿态的独立冻结副本；沿杆平行移动，结尾停留麻绳套。"
    # Linear interpolation between dense physically integrated keys prevents spline overshoot.
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    bag=strip.channelbag(slot,ensure=False)
                    if bag:
                        for fc in bag.fcurves:
                            for k in fc.keyframe_points:k.interpolation="LINEAR"
    prefs=bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type="OPTIX"
    prefs.get_devices()
    for d in prefs.devices:d.use=d.type=="OPTIX"
    scene.frame_set(300)
    detail.frame_set(150)
    bpy.context.window.scene=scene
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/"steelyard.blend"))
    manifest={"blend":str(ROOT/"steelyard.blend"),"scenes":[s.name for s in (scene,detail)],
              "rod_length_m":.75,"rod_diameters_m":[.024,.013],"star_diameter_m":.0012,
              "star_count":63,"gear_teeth":24,"gear_diameter_m":.157,
              "pan_diameter_m":.238,"weight_final_x_m":X_BALANCE,
              "render_engine":"Cycles","device":"OPTIX","samples":[128,160],
              "denoiser":"OPENIMAGEDENOISE","color":"AgX - Medium High Contrast",
              "objects":len(bpy.data.objects),"mesh_vertices":sum(len(m.vertices) for m in bpy.data.meshes)}
    (ROOT/"scene_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print("BUILD_COMPLETE",json.dumps(manifest,ensure_ascii=False))


if __name__=="__main__":
    main()
