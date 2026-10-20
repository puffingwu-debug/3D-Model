import bpy
import math
import json
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in list(bpy.data.materials):
    bpy.data.materials.remove(block)

COL = None
def collection(name):
    global COL
    COL = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(COL)
    return COL

def finish(obj, name, mat=None):
    obj.name = name
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    COL.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj

def mesh(name, vs, fs, mat, smooth=False):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vs, [], fs)
    data.update()
    obj = bpy.data.objects.new(name, data)
    COL.objects.link(obj)
    if mat:
        data.materials.append(mat)
    for p in data.polygons:
        p.use_smooth = smooth
    return obj

def bevel(obj, width=.015, segments=3):
    mod = obj.modifiers.new('Machined edge radius', 'BEVEL')
    mod.width = width
    mod.segments = segments
    return obj

def box(name, loc, dims, mat, radius=.015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=finish(bpy.context.object,name,mat)
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if radius: bevel(o,radius)
    return o

def uv(name, loc, scale, mat, segments=48, rings=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
    o=finish(bpy.context.object,name,mat); o.scale=scale
    for p in o.data.polygons: p.use_smooth=True
    return o

def curve(name, pts, radius, mat, closed=False):
    d=bpy.data.curves.new(name,'CURVE'); d.dimensions='3D'
    d.resolution_u=2; d.bevel_depth=radius; d.bevel_resolution=2
    s=d.splines.new('POLY'); s.points.add(len(pts)-1)
    for p,v in zip(s.points,pts): p.co=(*v,1)
    s.use_cyclic_u=closed
    o=bpy.data.objects.new(name,d); COL.objects.link(o); d.materials.append(mat)
    return o

def rod(name,a,b,r,mat,vertices=32):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2)
    o=finish(bpy.context.object,name,mat); o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    bevel(o,min(.006,r*.12),2)
    for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
    return o

def material(name,color,rough=.4,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal
    return m

paint=material('01 | Graphite grey • satin prototype coating',(.225,.258,.279),.38,.28)
edge=material('02 | Leading edge & RAM tape',(.18,.208,.226),.47,.18)
panel=material('03 | Access panels • subtle tonal variation',(.242,.274,.291),.42,.25)
dark=material('04 | Recesses & elastomer seals',(.013,.019,.024),.55,.04)
rubber=material('05 | Tire rubber',(.018,.022,.026),.63,.02)
steel=material('06 | Oleo polished steel',(.51,.56,.61),.2,.88)
titanium=material('07 | Nozzle titanium',(.17,.158,.135),.33,.78)
red=material('08 | Navigation red',(.35,.009,.005),.25,.2)
glass=material('09 | Smoked canopy • faint amber coating',(.28,.34,.36),.09,.05)
g=glass.node_tree.nodes.get('Principled BSDF')
g.inputs['Transmission Weight'].default_value=.94
g.inputs['IOR'].default_value=1.47
g.inputs['Coat Weight'].default_value=.5
white=material('10 | Faded prototype markings',(.56,.59,.59),.5,.05)
gearpaint=material('11 | Warm grey struts',(.56,.58,.57),.3,.35)
ceramic=material('12 | Exhaust heat shield • carbon ceramic',(.072,.081,.085),.56,.35)
nozzle_lip=material('16 | Oxidized nozzle titanium',(.08,.060,.045),.60,.52)
sensor=material('13 | Optical aperture • amber interference',(.145,.068,.016),.12,.68)
for m in (paint,panel,edge):
    ns=m.node_tree.nodes; ls=m.node_tree.links; p=ns.get('Principled BSDF')
    tc=ns.new('ShaderNodeTexCoord'); noise=ns.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=170; noise.inputs['Detail'].default_value=2
    ls.new(tc.outputs['Object'],noise.inputs['Vector'])
    bump=ns.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.1
    bump.inputs['Distance'].default_value=.0008
    ls.new(noise.outputs['Fac'],bump.inputs['Height']); ls.new(bump.outputs['Normal'],p.inputs['Normal'])
    ramp=ns.new('ShaderNodeMapRange'); ramp.inputs['To Min'].default_value=.34; ramp.inputs['To Max'].default_value=.44
    ls.new(noise.outputs['Fac'],ramp.inputs['Value']); ls.new(ramp.outputs[0],p.inputs['Roughness'])

import camouflage
camouflage.apply_camouflage([paint,panel])

def interp(x, points):
    if x<=points[0][0]: return points[0][1]
    for (a,b),(c,d) in zip(points,points[1:]):
        if x<=c: return b+(d-b)*(x-a)/(c-a)
    return points[-1][1]

def leading(x):
    return interp(abs(x),[(0,-12),(4.0,-2.65),(10.6,6.86)])
def trailing(x):
    return interp(abs(x),[(0,10.05),(1.45,10.65),(10.6,6.91)])
def control_chord(x):
    return min(1.12,(trailing(x)-leading(x))*.8)

def top(x,y):
    le,te=leading(x),trailing(x)
    q=max(0,min(1,(y-le)/(te-le)))
    foil=math.sin(math.pi*q)**.65
    width=interp(y,[(-12,.05),(-10,.65),(-8,1.35),(-5,1.9),(-1,2.6),(5,3.0),(9,3.0),(10.7,3.0)])
    core=math.exp(-(abs(x)/max(width,.01))**3.3)
    height=interp(y,[(-12,0),(-10,.28),(-8,.65),(-5,.84),(-1,.95),(4,.88),(7,.64),(10.7,.08)])
    z=2.7+(.13+height*core)*foil
    # Three gently blended engine shoulders taper into recessed first-prototype troughs.
    if y>1:
        blend=math.sin(math.pi*max(0,min(1,(y-1)/10)))**.8
        for xc in (-1.95,0,1.95):
            z+=.19*math.exp(-((x-xc)/.72)**4)*blend
    if y>6.5:
        for xc in (-1.95,0,1.95):
            cut=math.exp(-((x-xc)/.64)**8)
            z-=.055*cut*min(1,max(0,(y-8.0)/1.1))
    if abs(x)<3.0 and y>7.5:
        u=max(0,min(1,(y-7.5)/(trailing(x)-7.5)));blend=u*u*(3-2*u)
        weight=max(math.exp(-((x-xc)/.75)**8) for xc in (-1.95,0,1.95))
        z=z*(1-blend)+(2.7+.20*weight)*blend
    return z

def bottom(x,y):
    le,te=leading(x),trailing(x)
    q=max(0,min(1,(y-le)/(te-le))); foil=math.sin(math.pi*q)**.68
    w=interp(y,[(-12,.1),(-8,1.1),(-4,1.9),(1,2.8),(7,3.2),(10.7,2.8)])
    depth=interp(y,[(-12,0),(-10,.40),(-8,.63),(-4,.70),(2,.72),(6,.63),(9,.40),(10.7,.18)])
    keel=math.exp(-(abs(x)/max(w,.1))**6)
    z=2.7-(.09+depth*keel)*foil
    if y>1:
        blend=math.sin(math.pi*max(0,min(1,(y-1)/10)))**1.2
        for xc in (-1.95,0,1.95):
            z-=.13*math.exp(-((x-xc)/.78)**4)*blend
    if abs(x)<3.0 and y>7.5:
        u=max(0,min(1,(y-7.5)/(trailing(x)-7.5)));blend=u*u*(3-2*u)
        weight=max(math.exp(-((x-xc)/.75)**8) for xc in (-1.95,0,1.95))
        z=z*(1-blend)+(2.7-.37*weight)*blend
    return z

CANOPY_PROFILE=[(-8.55,.07,.01),(-8.36,.45,.19),(-8.02,.82,.45),(-7.55,1.05,.63),
                (-6.9,1.13,.73),(-6.2,1.12,.73),(-5.65,1.0,.61),(-5.1,.77,.38),(-4.75,.35,.13),(-4.63,.03,.01)]
CANOPY_PROFILE=[((y+6.65)*.74-7.3,w*.84,h*.56) for y,w,h in CANOPY_PROFILE]
def cockpit_hole(x,y):
    if not CANOPY_PROFILE[0][0]<y<CANOPY_PROFILE[-1][0]: return False
    return abs(x)<interp(y,[(v[0],v[1]) for v in CANOPY_PROFILE])-.18

collection('01 • Continuous airframe')
xs=sorted(set([-10.6+21.2*i/300 for i in range(301)]+[-2.55,-1.35,-.6,.6,1.35,2.55,-8.2,8.2]))
NX,NY=len(xs)-1,260
vs=[]
for side in (1,-1):
    for i in range(NX+1):
        x=xs[i]
        for j in range(NY+1):
            y=leading(x)+(trailing(x)-leading(x))*j/NY
            vs.append((x,y,top(x,y) if side==1 else bottom(x,y)))
N=(NX+1)*(NY+1); fs=[]
for side in (0,1):
    off=side*N
    for i in range(NX):
        for j in range(NY):
            a=off+i*(NY+1)+j; b=a+NY+1
            if side==0:
                c=(Vector(vs[a])+Vector(vs[b+1]))/2
                if cockpit_hole(c.x,c.y): continue
            else:
                c=(Vector(vs[a])+Vector(vs[b+1]))/2
                main_bay=1.8<abs(c.x)<2.95 and 2.0<c.y<5.15
                nose_bay=abs(c.x)<.54 and -7.95<c.y<-6.3
                lower_inlet=1.62<abs(c.x)<3.16 and -4.7+.54*(abs(c.x)-1.68)<c.y<-1.4
                if main_bay or nose_bay or lower_inlet: continue
            if abs(c.x)>8.2 and c.y>trailing(c.x)-control_chord(c.x): continue
            fs.append((a,b,b+1,a+1) if side==0 else (a+1,b+1,b,a))
for i in range(NX):
    for j in (0,NY):
        a=i*(NY+1)+j; b=a+NY+1
        if j==NY and any(abs((vs[a][0]+vs[b][0])*.5-xc)<.60 for xc in (-1.95,0,1.95)): continue
        fs.append((a,a+N,b+N,b) if j==0 else (b,b+N,a+N,a))
for i in (0,NX):
    for j in range(NY):
        a=i*(NY+1)+j
        fs.append((a,a+1,a+1+N,a+N))
skin=mesh('J-36 • Blended double-delta monocoque',vs,fs,paint,True)
skin['reference_airframe']='36011 • first public prototype configuration'
skin['accuracy']='Photo-based exterior reconstruction. No surveyed dimensions. Not engineering geometry.'
skin['working_scale']='Working mesh length 22.65 m, span 21.20 m. Clean nose without projecting probe; official dimensions unverified.'

def path_surface(name,xy,mat=dark,r=.004,lower=False,closed=False,offset=.004):
    pts=[]
    for a,b in zip(xy,xy[1:]+([xy[0]] if closed else [])):
        steps=max(2,int(math.dist(a,b)/.045))
        for i in range(steps):
            u=i/steps; x=a[0]*(1-u)+b[0]*u; y=a[1]*(1-u)+b[1]*u
            z=(bottom(x,y)-offset) if lower else (top(x,y)+offset)
            pts.append((x,y,z))
    if not closed:
        x,y=xy[-1]; pts.append((x,y,(bottom(x,y)-offset) if lower else top(x,y)+offset))
    return curve(name,pts,r,mat,closed)

def patch(name,xy,mat,lower=False,offset=.006):
    # Tesselated decal follows the compound skin, including its subtle curvature.
    from mathutils.geometry import tessellate_polygon
    coords=[Vector((x,y,0)) for x,y in xy]
    tris=tessellate_polygon([coords]); verts=[]; faces=[]
    for tri in tris:
        a,b,c=[coords[v] if isinstance(v,int) else v for v in tri]
        n=max(3,int(max((a-b).length,(b-c).length,(c-a).length)/.12))
        ids={}
        for i in range(n+1):
            for j in range(n+1-i):
                v=a+(b-a)*(i/n)+(c-a)*(j/n); x,y=v.x,v.y
                ids[i,j]=len(verts)
                verts.append((x,y,bottom(x,y)-offset if lower else top(x,y)+offset))
        for i in range(n):
            for j in range(n-i):
                faces.append((ids[i,j],ids[i+1,j],ids[i,j+1]))
                if j<n-i-1: faces.append((ids[i+1,j],ids[i+1,j+1],ids[i,j+1]))
    return mesh(name,verts,faces,mat,True)

collection('02 • RAM edges, panels & control seams')
for s in (-1,1):
    path_surface('Continuous leading edge seal',[(s*x,leading(x)+.045) for x in [i*10.55/130 for i in range(131)]],edge,.014)
    # Long leading-edge coating strip with an intentionally restrained contrast.
    xy=[(s*x,leading(x)+.05) for x in (2.8,4.0,10.56)]
    xy += [(s*x,leading(x)+.22) for x in (10.5,4.0,2.8)]
    patch('Leading edge coating',xy,edge)
    for idx,(a,b) in enumerate([(3.38,4.8),(4.82,6.35),(6.37,8.18),(8.2,9.32),(9.34,10.55)]):
        points=[(s*a,trailing(a)-control_chord(a)),(s*b,trailing(b)-control_chord(b)),(s*b,trailing(b)-.035),(s*a,trailing(a)-.035)]
        if idx<3:
            patch('Elevon %s %02d • surface'%(s,idx+1),points,panel if idx%2==0 else paint)
        else:
            for direction in (-1,1):
                flapv=[];flapf=[];angle=math.radians(23)*direction
                for ix in range(25):
                    x=s*(a+(b-a)*ix/24)
                    hinge=trailing(x)-control_chord(x)
                    for iy in range(17):
                        d=max(.01,control_chord(x)-.04)*iy/16; y=hinge+d*math.cos(angle)
                        z0=top(x,hinge) if direction>0 else bottom(x,hinge)
                        flapv.append((x,y,z0+d*math.sin(angle)))
                for ix in range(24):
                    for iy in range(16):
                        k=ix*17+iy;flapf.append((k,k+17,k+18,k+1))
                flap=mesh('Outer split rudder • '+str(s)+' / '+str(idx)+' / '+str(direction),flapv,flapf,paint,True)
                solid=flap.modifiers.new('Thin control shell','SOLIDIFY');solid.thickness=.026
                bevel(flap,.007,2)
        for lower in (False,True):
            if idx<3:
                path_surface('Elevon hinge & split rudder outline',points,dark,.007,lower,True)
            else:
                path_surface('Split rudder hinge seal',points[:2],dark,.005,lower)
        for x in (a+.13,b-.13):
            y=trailing(x)-control_chord(x)+.02
            path_surface('Hinge titanium knuckle',[(s*x,y-.02),(s*x,y+.08)],steel,.014)
    # A narrow continuous hinge cuff closes the skin-to-split-panel root neatly.
    for lower in (False,True):
        hv=[];hf=[]
        for j in range(121):
            x=s*(8.195+(10.55-8.195)*j/120)
            hinge=trailing(x)-control_chord(x);w=min(.075,control_chord(x)*.28)
            for dy in (-w,.025):
                y=hinge+dy;z=bottom(x,y)-.006 if lower else top(x,y)+.006
                hv.append((x,y,z))
        for j in range(120):
            a=j*2;hf.append((a,a+1,a+3,a+2))
        mesh('Split rudder • continuous hinge cuff',hv,hf,paint,True)
    # Angular upper maintenance panels, visually derived layout; fasteners kept flush.
    layouts=[[(2.9,-.9),(3.48,-.1),(5.6,3.0),(4.55,4.0),(2.94,2.2)],
             [(3.5,4.5),(4.8,4.5),(6.6,7.8),(4.5,8.15)],
             [(1.15,-3.3),(1.88,-2.8),(2.3,.4),(1.3,.15)],
             [(2.85,4.7),(3.43,5.0),(3.48,8.35),(2.83,8.75)]]
    for j,poly in enumerate(layouts):
        poly=[(s*x,y) for x,y in poly]
        path_surface('Upper service panel %d'%j,poly,dark,.003,closed=True)
    for y in (-9.45,-3.3,1.0,5.25):
        w=min(1.95, max(.1,(y+12)/3.4))
        path_surface('Fuselage transverse skin join',[(s*.06,y),(s*w,y+.1)],edge,.003)
    # Lower sealed bay doors; no speculative internal equipment.
    bay=[(.12,-3.75),(1.08,-3.1),(1.17,4.65),(.18,5.0)]
    path_surface('Closed ventral main bay perimeter',[(s*x,y) for x,y in bay],dark,.005,True,True)
    sidebay=[(1.25,-2.0),(2.12,-1.6),(2.18,1.6),(1.28,2.1)]
    path_surface('Ventral secondary door outline',[(s*x,y) for x,y in sidebay],edge,.004,True,True)
    # Subtle nose radome transition follows the chine.
    path_surface('Radome seam',[(s*x,-9.35+x*.09) for x in [i*.94/25 for i in range(26)]],dark,.005)

collection('03 • Cockpit & glazing')
# The canopy is a purpose-built closed dome with longitudinally tapered section rings.
canopy_rings=CANOPY_PROFILE
cv=[]; cf=[]; NTH=64
for y,w,h in canopy_rings:
    for k in range(NTH+1):
        t=math.pi*k/NTH; x=w*math.cos(t)
        cv.append((x,y,top(x,y)+.045+h*math.sin(t)**.8))
for j in range(len(canopy_rings)-1):
    for k in range(NTH):
        a=j*(NTH+1)+k; b=a+NTH+1; cf.append((a,b,b+1,a+1))
can=mesh('Wide low bubble canopy • optical shell',cv,cf,glass,True)
sol=can.modifiers.new('Laminated glazing thickness','SOLIDIFY'); sol.thickness=.018
sub=can.modifiers.new('Optical continuity','SUBSURF'); sub.levels=2
for s in (-1,1):
    pts=[(s*w,y,top(s*w,y)+.04) for y,w,h in canopy_rings]
    curve('Canopy perimeter structural rail',pts,.027,edge)
    curve('Canopy edge gasket',[(x,y,z+.014) for x,y,z in pts],.008,dark)
uv('Cockpit dark tub',(0,-7.3,3.02),(.83,1.22,.24),dark)
for s in (-1,1):
    o=box('Seat silhouette • unverified interior',(s*.36,-6.94,3.28),(.44,.50,.35),dark,.08)
    o.rotation_euler.x=math.radians(-12)
    box('Seat headrest',(s*.36,-6.80,3.48),(.24,.19,.15),dark,.05)
    # Only broad silhouettes are suggested through the tinted canopy.
    box('Instrument coaming',(s*.34,-7.83,3.25),(.45,.42,.10),dark,.04)
    hu=mesh('HUD combiner',[(s*.34-.11,-7.88,3.30),(s*.34+.11,-7.88,3.30),(s*.34+.11,-7.78,3.46),(s*.34-.11,-7.78,3.46)],[(0,1,2,3)],glass)
    hu['basis']='Interior silhouettes are illustrative, not verified cockpit equipment.'

collection('04 • Three intakes & recessed exhausts')
def duct(name,outer,back,mat=paint):
    # Open inlet: thin closed lip ring around an actual dark duct, never a painted rectangle.
    ctr=sum((Vector(p) for p in outer),Vector())/len(outer)
    inner=[tuple(ctr+(Vector(p)-ctr)*.93) for p in outer]
    v=outer+inner+back; n=len(outer)
    f=[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    lip=mesh(name+' • inlet rim',v[:n*2],f,mat); bevel(lip,.018,3)
    tunnel=mesh(name+' • duct walls',inner+back,[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)],edge)
    tunnel.data.materials.append(dark)
    mesh(name+' • optical depth',back,[tuple(range(n-1,-1,-1))],dark)
    return lip

# Dorsal DSI inlet. Its trapezoidal mouth is well above the blended central body.
front=[(-1.02,-3.75,3.70),(1.02,-3.75,3.70),(.82,-3.48,4.68),(-.82,-3.48,4.68)]
rear=[(-.85,-1.4,3.78),(.85,-1.4,3.78),(.68,-1.3,4.37),(-.68,-1.3,4.37)]
duct('Dorsal trapezoidal intake',front,rear,paint)
# Closed outer cowl with softly chamfered trapezoidal cross-sections.
sections=[(-3.48,1.02,4.68),(-3.1,1.08,4.67),(-2.2,1.16,4.46),(-.9,1.25,4.15),(.6,1.22,3.93),(2.2,.85,3.75),(3.1,.3,3.65)]
vv=[];ff=[];COWL=24
for y,w,h in sections:
    for k in range(COWL+1):
        t=k/COWL;x=-w+2*w*t
        profile=min(1, max(0,1-(abs(2*t-1)**6)))**.36
        base=top(x,y+1.35)+.008
        vv.append((x,y,base+max(0,h-base)*profile))
for j in range(len(sections)-1):
    for k in range(COWL):
        a=j*(COWL+1)+k;b=a+COWL+1;ff.append((a,a+1,b+1,b))
mesh('Dorsal inlet cowl • blended shoulders',vv,ff,paint,True)
for s in (-1,1):
    cheek=[(s*1.02,-3.75,3.70),(s*.82,-3.48,4.68),
           (s*1.02,-3.48,top(s*1.02,-2.13)+.008),
           (s*1.06,-3.75,top(s*1.06,-2.40)+.008)]
    mesh('Dorsal inlet cheek closure',cheek,[(0,1,2),(0,2,3)],paint)
# The DSI bump rises directly from the skin rather than floating above it.
vv=[];ff=[]
for j in range(35):
    y=-4.65+1.2*j/34
    for k in range(35):
        x=-.85+1.7*k/34
        bump=.18*math.sin(math.pi*j/34)**.9*max(0,1-(x/.85)**2)**1.5
        vv.append((x,y,top(x,y+1.35)+.006+bump))
for j in range(34):
    for k in range(34):
        a=j*35+k;ff.append((a,a+1,a+36,a+35))
mesh('Dorsal inlet DSI ramp',vv,ff,paint,True)
for ob in list(COL.objects):
    if ob.name.startswith('Dorsal'):
        ob.location.y+=1.35
for s in (-1,1):
    out=[(s*1.68,-4.5,1.98),(s*3.12,-3.72,2.05),
         (s*2.98,-3.60,top(s*2.98,-3.60)-.015),(s*1.86,-4.36,top(s*1.86,-4.36)-.015)]
    back=[(s*1.83,-2.0,2.10),(s*2.90,-1.6,2.14),(s*2.80,-1.6,2.97),(s*1.94,-2.0,2.98)]
    duct(('Port' if s<0 else 'Starboard')+' lower caret intake',out,back,paint)
    # Lower intake gondola blends rearwards into the ventral engine volume.
    v=out+[(s*1.72,2.2,2.18),(s*3.0,2.4,2.39),(s*2.75,2.3,3.14),(s*1.8,2.2,3.32)]
    mesh('Caret inlet nacelle transition',v,[(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],paint,True)
    path_surface('Nacelle skin seam',[(s*3.04,-1.1),(s*3.08,3.0),(s*2.8,4.4)],edge,.006,True)

for idx,xc in enumerate((-1.95,0,1.95)):
    # Apertures terminate the continuous blended skin; there are no layered shrouds.
    outer=[]
    for lower in (False,True):
        offsets=[-.60+1.20*k/12 for k in range(13)]
        if lower: offsets.reverse()
        for dx in offsets:
            x=xc+dx;y=trailing(x)
            outer.append((x,y+.002,bottom(x,y) if lower else top(x,y)))
    count=len(outer);inside=[];back=[]
    for x,y,z in outer:
        ix=xc+(x-xc)*.92;iz=2.61+(z-2.61)*.82
        inside.append((ix,y-.02,iz));back.append((ix,y-.80,iz))
    lip=mesh('Exhaust %d • rear nozzle lip'%(idx+1),outer+inside,
             [(k,(k+1)%count,count+(k+1)%count,count+k) for k in range(count)],nozzle_lip)
    bevel(lip,.008,3)
    mesh('Exhaust %d • recessed hot duct'%(idx+1),inside+back,
         [(k,count+k,count+(k+1)%count,(k+1)%count) for k in range(count)],ceramic,True)
    mesh('Exhaust %d • dark interior depth'%(idx+1),back,[tuple(range(count-1,-1,-1))],dark)
    # Short flush thermal shingles follow the top shoulder, without raised stacks.
    for k in range(9):
        a=xc-.54+1.08*k/9;b=a+.108
        te=min(trailing(a),trailing(b))-.035
        pts=[(x,y,top(x,y)+.007) for x,y in [(a,te-.26),(b,te-.26),(b,te),(a,te)]]
        shingle=mesh('Exhaust %d • flush thermal petal %02d'%(idx+1,k),pts,[(0,1,2,3)],titanium)
        sol=shingle.modifiers.new('Thin thermal skin','SOLIDIFY');sol.thickness=.009

collection('06 • Flush sensors & prototype markings')
for s in (-1,1):
    # Angular nose apertures seen in multiple public views; no functional claim.
    xy=[(s*.97,-8.88),(s*1.23,-8.15),(s*1.04,-7.72),(s*.80,-8.44)]
    patch('Nose amber optical window',xy,sensor)
    path_surface('Optical aperture seal',xy,dark,.009,closed=True)
    xy=[(s*1.63,-6.9),(s*1.86,-6.15),(s*1.95,-5.55),(s*1.63,-5.9)]
    patch('Flush side cheek panel',xy,edge)
    # Serial is aligned with the nose centreline and conformed to the compound surface.
    d=bpy.data.curves.new('36011 marking','FONT');d.body='36011';d.size=.25;d.align_x='CENTER';d.extrude=0
    ob=bpy.data.objects.new('36011 • prototype identification',d);COL.objects.link(ob);d.materials.append(white)
    ob.location=(s*.64,-8.45,2.3);ob.rotation_euler.z=math.radians(90 if s<0 else -90)
    bpy.context.view_layer.objects.active=ob;ob.select_set(True)
    bpy.ops.object.convert(target='MESH');ob=bpy.context.object;ob.select_set(False)
    for vert in ob.data.vertices:
        p=ob.matrix_world@vert.co;p.z=bottom(p.x,p.y)-.012;vert.co=ob.matrix_world.inverted()@p
    # Navigation fixtures are unobtrusive within the outer wing.
    x=s*9.93;y=leading(x)+.15;z=top(x,y)
    uv('Wingtip navigation housing',(x,y,z+.018),(.09,.11,.035),dark,32,12)
    nm=material('Port ruby lens' if s<0 else 'Starboard green lens',(.42,.003,.002) if s<0 else (.003,.23,.1),.15,.25)
    uv('Wingtip navigation lens',(x,y-.045,z+.039),(.055,.075,.023),nm,24,12)

marking=material('14 | Low-visibility stencil grey',(.32,.36,.39),.51,.1)
for s in (-1,1):
    # Thin outline wing insignia, interpreted from the supplied three-view image.
    cx=s*7.05;cy=5.1
    star=[]
    for k in range(10):
        t=math.pi/2+2*math.pi*k/10;r=.40 if k%2==0 else .17
        star.append((cx+r*math.cos(t),cy+r*math.sin(t)))
    path_surface('Low-visibility wing star',star,marking,.005,closed=True)
    for a,b in [(-.86,-.4),(.4,.86)]:
        poly=[(cx+a,cy-.065),(cx+b,cy-.065),(cx+b,cy+.065),(cx+a,cy+.065)]
        path_surface('Wing insignia bar',poly,marking,.005,closed=True)
    d=bpy.data.curves.new('Nose serial stencil','FONT');d.body='36011';d.size=.17;d.align_x='CENTER'
    ob=bpy.data.objects.new('36011 • upper nose stencil',d);COL.objects.link(ob);d.materials.append(marking)
    ob.location=(s*.78,-9.17,3.0);ob.rotation_euler.z=math.radians(-90 if s<0 else 90)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.object.convert(target='MESH');ob=bpy.context.object;ob.select_set(False)
    for vert in ob.data.vertices:
        p=ob.matrix_world@vert.co;p.z=top(p.x,p.y)+.008;vert.co=ob.matrix_world.inverted()@p

# Individual flush fasteners are restricted to selected access panels.
for s in (-1,1):
    for x0,y0 in [(2.87,5.0),(2.9,8.4),(3.35,5.2),(3.4,8.2),(1.36,-2.8),(1.72,-2.7)]:
        x=s*x0;z=top(x,y0)
        o=rod('Flush access fastener',(x,y0,z+.001),(x,y0,z+.004),.014,edge,16)
        curve('Fastener recess',[(x-.006,y0,z+.005),(x+.006,y0,z+.005)],.0015,dark)

# Clean pointed nose, without a projecting probe, per the latest user reference.

import gear
gear.build_gear(dict(paint=gearpaint,edge=edge,dark=dark,rubber=rubber,steel=steel,titanium=titanium,red=red,glass=glass))
import ventral_detail
ventral_detail.build_ventral_detail(dict(collection=collection,mesh=mesh,curve=curve,
    path_surface=path_surface,patch=patch,bottom=bottom,trailing=trailing,leading=leading,
    materials=dict(paint=paint,edge=edge,panel=panel,dark=dark,steel=steel,titanium=titanium,ceramic=ceramic)))

collection('00 • Aircraft transform')
aircraft_root=bpy.data.objects.new('J-36 / 36011 • move entire aircraft',None)
COL.objects.link(aircraft_root);aircraft_root.empty_display_type='PLAIN_AXES'
for coll in bpy.data.collections:
    if coll.name[:2] in ('01','02','03','04','05','06','08'):
        for ob in coll.objects:
            ob.parent=aircraft_root
for mat in (paint,panel):
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    tc=nodes.new('ShaderNodeTexCoord');tc.object=aircraft_root;tc.label='Coating coordinates follow aircraft root'
    for link in list(links):
        if link.from_node.type=='NEW_GEOMETRY' and link.from_socket.name=='Position':
            links.new(tc.outputs['Object'],link.to_socket)
        elif link.from_node.type=='NEW_GEOMETRY' and link.from_socket.name=='Normal':
            tr=nodes.new('ShaderNodeVectorTransform');tr.vector_type='NORMAL';tr.convert_from='WORLD';tr.convert_to='OBJECT'
            links.new(link.from_socket,tr.inputs['Vector']);links.new(tr.outputs['Vector'],link.to_socket)
coat=paint.copy();coat.name='15 | Dorsal inlet wraparound coating'
for node in coat.node_tree.nodes:
    if node.type=='MIX_RGB' and node.label=='Charcoal underside / patterned upper skin':
        for link in list(node.inputs[0].links): coat.node_tree.links.remove(link)
        node.inputs[0].default_value=1
for ob in aircraft_root.children:
    if ob.type=='MESH' and ob.name.startswith('Dorsal'):
        for slot in ob.material_slots:
            if slot.material==paint: slot.material=coat
for ob in aircraft_root.children:
    if ob.name.startswith(('Upper service panel','Fuselage transverse skin join','Nacelle skin seam',
                           'Closed ventral main bay perimeter','Ventral secondary door outline')):
        ob.hide_render=True;ob.hide_viewport=True
import exhaust_fx
exhaust_fx.build_exhaust_fx(dict(collection=collection,mesh=mesh,curve=curve,top=top,trailing=trailing,
    aircraft_root=aircraft_root,
    exhaust_centers=[(xc,trailing(xc)+.02,2.61,1.16,.40,4.6 if xc==0 else 4.2) for xc in (-1.95,0,1.95)]))
if (ROOT/'references'/'User_Three_View.png').exists():
    user_reference=bpy.data.images.load(str(ROOT/'references'/'User_Three_View.png'),check_existing=True)
    user_reference.name='USER • Three-view exterior reference';user_reference.use_fake_user=True;user_reference.pack()
for number in (1,3,4,5):
    p=ROOT/'references'/('Revision_Ref_%d.png'%number)
    if p.exists():
        im=bpy.data.images.load(str(p),check_existing=True);im.use_fake_user=True;im.pack()

collection('90 • Studio')
floor=material('Studio | blue graphite floor',(.065,.079,.095),.33,.25)
box('Seamless studio ground',(0,0,-.13),(200,200,.2),floor,.02)
# A circular cyclorama gives all inspection cameras a continuous studio backdrop.
vv=[];ff=[];rings=[(70+10*math.sin(math.pi*j/40),-.03+10*(1-math.cos(math.pi*j/40))) for j in range(21)]
rings.append((80,65))
for r,z in rings:
    for k in range(256):
        t=2*math.pi*k/256;vv.append((r*math.cos(t),r*math.sin(t),z))
for j in range(len(rings)-1):
    for k in range(256):
        a=j*256+k;b=j*256+(k+1)%256;ff.append((a,a+256,b+256,b))
mesh('Infinite circular cyclorama',vv,ff,floor,True)

def light(name,loc,target,power,color,size,shape='DISK',size_y=None):
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.color=color;d.shape=shape;d.size=size
    if size_y is not None:d.size_y=size_y
    ob=bpy.data.objects.new(name,d);COL.objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    return ob

light('Key | broad silk',(-12,-6,19),(0,0,2),6200,(.86,.92,1),12,'RECTANGLE',18)
light('Rim | warm strip',(8,8,15),(0,2,2),7800,(1,.84,.66),7,'RECTANGLE',16)
light('Fill | forward softbox',(5,-14,10),(0,-5,3),3400,(.78,.87,1),10)
light('Edge | far wing strip',(-9,11,8),(0,4,2),4000,(.64,.78,1),5,'RECTANGLE',13)
light('Canopy | reflection strip',(0,-2,14),(0,-6,3),1900,(1,.96,.89),2,'RECTANGLE',9)
light('Ventral | broad inspection fill',(-7,-2,-11),(0,1,2.3),14000,(.67,.80,1),10,'RECTANGLE',15)
light('Ventral | opposite shoulder fill',(9,5,-9),(0,2,2.3),5200,(1,.85,.69),8)
world=bpy.data.worlds.new('Quiet blue-grey studio');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.17,.23,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.32
bpy.context.scene.world=world

collection('91 • Cameras')
def camera(name,loc,target,lens=50,ortho=None):
    d=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,d);COL.objects.link(ob)
    ob.location=loc; ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    d.lens=lens;d.clip_end=1000
    if ortho: d.type='ORTHO';d.ortho_scale=ortho
    return ob
cams={}
cams['hero']=camera('01 | HERO • front three-quarter',(-27,-33,23),(0,1,2.4),46)
cams['rear']=camera('02 | REAR • three recessed exhausts',(23,33,19),(0,3.5,2.5),50)
cams['top']=camera('03 | PLAN • true orthographic',(0,.9,45),(0,.9,0),50,53)
cams['front']=camera('04 | FRONT • wide canopy',(0,-35,6.8),(0,-1,2.5),53)
cams['detail']=camera('05 | DETAIL • canopy and intakes',(-10,-15,11),(0,-5.4,3.2),63)
cams['side']=camera('06 | PROFILE • true orthographic',(-38,.8,3.8),(0,.8,3),50,32)
cams['ventral']=camera('07 | VENTRAL • underside inspection',(-22,-27,-15),(0,.7,2.3),45)
cams['exhaust']=camera('08 | EXHAUST • hot tail detail',(9,25,7.5),(0,10,2.6),55)

scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=256;scene.cycles.use_denoising=True
scene.cycles.adaptive_threshold=.012
scene.cycles.max_bounces=10;scene.cycles.transmission_bounces=8
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='METAL';prefs.get_devices()
    for device in prefs.devices: device.use=device.type=='METAL'
    scene.cycles.device='GPU'
except Exception as exc: print('GPU preference:',exc)
scene.render.resolution_x=3840;scene.render.resolution_y=2160;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='16'
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=-.5
for ob in bpy.data.objects:
    if ob.type=='LIGHT': ob.data.energy*=.5
scene.render.film_transparent=False
scene.camera=cams['hero']
scene.unit_settings.system='METRIC'
scene['project']='J-36 / 36011 • photographic exterior study'
scene['scope']='ONE editable exterior aircraft, studio stage, eight inspection cameras.'
scene['revision']='Tail & ventral refinement; reduced low canopy; switchable red-orange exhaust and shock cells.'
scene['exhaust_effects']='Toggle collection 07 • Exhaust effects. Artistic visualization; not a measured prototype plume.'
scene['limitations']='Not an exact replica. Official dimension drawings, hidden geometry, paint formulation and fine fastener patterns unavailable. Interior and small gear fittings inferred.'
scene['user_reference']='references/User_Three_View.png supplied by user. Planform and angular camouflage reconstructed from this illustration; not a surveyed blueprint.'

text=bpy.data.texts.new('READ ME • Reference & limitations')
text.write("""J-36 / 36011 — EXTERIOR VISUAL RECONSTRUCTION

ONE aircraft, eight cameras, editable materials and meshes.
Latest revision: continuous blended aft body with three recessed rear-facing openings;
refined ventral keel, sealed bay outlines and six small actuator fairings;
smaller, flatter cockpit glazing; clean pointed nose WITHOUT projecting probe.

Collection 07: optional red-orange exhaust with shock-cell and Mach-ring motifs.
The plume is an artistic visual effect, not verified prototype exhaust data or CFD.
Collection 08: ventral exterior refinements. Collection 90: removable studio.
Move the root object in Collection 00 to transform the complete aircraft.
For underside rendering, hide the studio ground and cyclorama; retain the lights.
The included render_views.py configures these switches for each view.

References: user's three-view illustration plus Revision_Ref_1,3,4,5 and Revision_No_Probe.
The original public photo source links are listed in DELIVERY.md.
Official dimensioned drawings are unavailable in this reference set.
Scale, hidden surfaces, cockpit interior and small mechanical fittings are interpretations.
This is a visual model, not surveyed engineering geometry or a 100 percent verified replica.
Cycles / Metal / 256 adaptive samples / AgX / 3840 x 2160 PNG.
""")

# Open directly to a carefully framed material preview without studio wire clutter.
bpy.ops.object.select_all(action='DESELECT')
skin.select_set(True);bpy.context.view_layer.objects.active=skin
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.overlay.show_overlays=False
            area.spaces.active.shading.type='MATERIAL'
            area.spaces.active.clip_end=1000
scene.render.filepath=str(ROOT/'renders'/'J36_36011_Hero_4K.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'J36_36011_Master.blend'))
stats=dict(objects=len(bpy.data.objects),mesh_objects=sum(o.type=='MESH' for o in bpy.data.objects),
           polygons=sum(len(o.data.polygons) for o in bpy.data.objects if o.type=='MESH'),
           vertices=sum(len(o.data.vertices) for o in bpy.data.objects if o.type=='MESH'),
           cameras=len(cams),blender=bpy.app.version_string)
(ROOT/'model_stats.json').write_text(json.dumps(stats,indent=2))
print('MODEL_STATS',json.dumps(stats))
if '--preview' in sys.argv:
    scene.render.resolution_percentage=35;scene.cycles.samples=40
    scene.render.filepath=str(ROOT/'renders'/'preview_hero.png')
    bpy.ops.render.render(write_still=True)
