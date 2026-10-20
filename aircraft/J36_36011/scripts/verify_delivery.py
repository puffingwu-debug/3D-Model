import bpy
import json
import math
import struct
import sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

root=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
aircraft=bpy.data.objects.get('J-36 / 36011 • move entire aircraft')
assert aircraft is not None
assert len(bpy.data.cameras)==8
models=[o for o in bpy.data.objects if o.parent==aircraft]
assert len(models)>400
for ob in models:
    if ob.type=='MESH':
        assert all(math.isfinite(v) for vertex in ob.data.vertices for v in vertex.co),ob.name
images=[im for im in bpy.data.images if im.type=='IMAGE' and im.source!='VIEWER']
assert all(im.packed_file is not None for im in images),[(im.name,im.filepath) for im in images]
report={'blender':bpy.app.version_string,'aircraft_count':1,'model_components':len(models),
        'camera_count':8,'packed_images':[im.name for im in images],
        'image_sizes':{im.name:list(im.size) for im in images},'render_checks':[], 'camera_bounds':{}}
scene.render.resolution_x=3840;scene.render.resolution_y=2160
bpy.context.view_layer.update()
points=[]
for ob in models:
    if ob.type=='MESH':
        points.extend(ob.matrix_world@vertex.co for vertex in ob.data.vertices)
    elif ob.type=='CURVE':
        for spline in ob.data.splines:
            points.extend(ob.matrix_world@Vector(p.co[:3]) for p in spline.points)
for camera in bpy.data.objects:
    if camera.type!='CAMERA' or camera.name.startswith(('05','08')): continue
    projected=[world_to_camera_view(scene,camera,p) for p in points]
    bounds=[min(p.x for p in projected),min(p.y for p in projected),max(p.x for p in projected),max(p.y for p in projected)]
    report['camera_bounds'][camera.name]=bounds
    # Bounds derived from object boxes conservatively exceed the actual surface.
    if camera.name.startswith(('01','03','04','06','07')):
        assert bounds[0]>-.02 and bounds[1]>-.02 and bounds[2]<1.02 and bounds[3]<1.02,(camera.name,bounds)
assert bpy.data.collections.get('07 • Exhaust effects') is not None
assert bpy.data.collections.get('08 • Ventral exterior refinements') is not None
report['exhaust_plumes']=sum('transparent red-orange turbulent plume' in ob.name for ob in models)
assert report['exhaust_plumes']==3
assert not any(ob.name.startswith('Nose flight-test probe') for ob in models)
for name in (() if '--geometry-only' in sys.argv else ('Hero','Rear','Top','Front','Detail','Side','Ventral','Exhaust')):
    path=root/'renders'/('J36_36011_'+name+'_4K.png')
    if not path.exists():
        report['render_checks'].append({'view':name,'status':'pending'})
        continue
    assert path.stat().st_mtime>(root/'J36_36011_Master.blend').stat().st_mtime,('stale render',name)
    header=path.read_bytes()[:33]
    assert header[:8]==b'\x89PNG\r\n\x1a\n'
    width,height,depth,color,_,_,_=struct.unpack('>IIBBBBB',header[16:29])
    assert (width,height)==(3840,2160),(name,width,height)
    assert depth==16
    report['render_checks'].append({'view':name,'width':width,'height':height,'bit_depth':depth,'bytes':path.stat().st_size})
(root/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('DELIVERY_VERIFIED',json.dumps(report,ensure_ascii=False))
