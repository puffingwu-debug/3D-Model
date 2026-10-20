import bpy
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.get_devices()
for device in prefs.devices:
    device.use=device.type=='METAL'
scene.cycles.device='GPU'
print('RENDER_DEVICE',[(device.name,device.type,device.use) for device in prefs.devices],flush=True)
preview='--preview' in sys.argv
shots=[('02 | REAR • three recessed exhausts','Rear'),
       ('03 | PLAN • true orthographic','Top'),
       ('04 | FRONT • wide canopy','Front'),
       ('05 | DETAIL • canopy and intakes','Detail'),
       ('06 | PROFILE • true orthographic','Side'),
       ('07 | VENTRAL • underside inspection','Ventral'),
       ('08 | EXHAUST • hot tail detail','Exhaust')]
if not preview:
    shots=[('01 | HERO • front three-quarter','Hero')]+shots
scene.cycles.samples=48 if preview else 96
scene.cycles.adaptive_threshold=.02
scene.cycles.volume_bounces=0
scene.cycles.volume_step_rate=4.0
scene.render.resolution_x=1600 if preview else 3840
scene.render.resolution_y=1000 if preview else 2160
scene.render.resolution_percentage=100
if '--check' in sys.argv:
    shots=[shot for shot in shots if shot[1] in ('Rear','Side','Ventral','Exhaust','Detail')]
if '--resume' in sys.argv:
    shots=[shot for shot in shots if not (ROOT/'renders'/('J36_36011_'+shot[1]+'_4K.png')).exists()
           or (ROOT/'renders'/('J36_36011_'+shot[1]+'_4K.png')).stat().st_mtime<(ROOT/'J36_36011_Master.blend').stat().st_mtime]
base_exposure=scene.view_settings.exposure
for camera,name in shots:
    print('RENDERING',name,flush=True)
    scene.camera=bpy.data.objects[camera]
    if name=='Top':
        scene.camera.data.ortho_scale=53
    if name=='Side':
        scene.camera.data.ortho_scale=32
    airborne=name in ('Ventral','Exhaust')
    scene.view_settings.exposure=base_exposure+(1.0 if name=='Ventral' else 0)
    for stage in ('Seamless studio ground','Infinite circular cyclorama'):
        bpy.data.objects[stage].hide_render=airborne
    scene.render.filepath=str(ROOT/'renders'/('preview_'+name.lower()+'.png' if preview else 'J36_36011_'+name+'_4K.png'))
    bpy.ops.render.render(write_still=True)
