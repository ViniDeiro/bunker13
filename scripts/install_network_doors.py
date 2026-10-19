"""Reimport architecture without movable leaves; preserve the map and material assignments."""
from pathlib import Path
import json
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
level.load_level('/Game/Bunker/Lvl_Bunker')
mesh_path='/Game/Bunker/Geometry/SM_Bunker_Playtest_Merged'
mesh=u.load_asset(mesh_path)
prior={str(s.material_slot_name):s.material_interface for s in mesh.get_editor_property('static_materials')}
task=u.AssetImportTask()
task.filename=str(ROOT/'exports/Bunker_Playtest_Merged.fbx')
task.destination_path='/Game/Bunker/Geometry'
task.destination_name='SM_Bunker_Playtest_Merged'
task.automated=True;task.replace_existing=True;task.save=True
options=u.FbxImportUI();options.import_mesh=True;options.import_as_skeletal=False
options.import_materials=False;options.import_textures=False
options.static_mesh_import_data.combine_meshes=True
options.static_mesh_import_data.generate_lightmap_u_vs=False
options.static_mesh_import_data.auto_generate_collision=False
task.options=options
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
mesh=u.load_asset(mesh_path)
slots=list(mesh.get_editor_property('static_materials'))
for slot in slots:
    key=str(slot.material_slot_name)
    if key not in prior:raise RuntimeError('Unexpected material slot: '+key)
    slot.set_editor_property('material_interface',prior[key])
mesh.set_editor_property('static_materials',slots)
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
u.EditorAssetLibrary.save_loaded_asset(mesh)
# Repair authored finish elements which the capsule audit found across routes.
for actor in actors.get_all_level_actors():
    label=actor.get_actor_label();loc=actor.get_actor_location()
    if label in ('B2_WhiteModule_2400','B2_WhiteModule_2640'):
        loc.x=2380 if label.endswith('2400') else 2720
        scale=actor.get_actor_scale3d();scale.x=1.4;actor.set_actor_scale3d(scale)
        actor.set_actor_location(loc,False,False)
    if label.startswith('B2_CorridorRib') and label.endswith(('_500','_2500')):
        loc.x=600 if label.endswith('_500') else 2600
        actor.set_actor_location(loc,False,False)
    if label == 'Medical_Trolley':
        loc.x=305;actor.set_actor_location(loc,False,False)
    if label.startswith('Medical_TrolleyWheel_') and '_Clear_' not in label:
        old_x=float(label.split('_')[-2]);loc.x=old_x+40 if old_x in (245,285) else old_x
        actor.set_actor_location(loc,False,False)
        actor.set_actor_label(f'Medical_TrolleyWheel_Clear_{int(loc.x)}_{int(loc.y)}')
    if label == 'Generator_HazardFloor':
        loc.z=1.5;actor.set_actor_location(loc,False,False)
for actor in actors.get_all_level_actors():
    if isinstance(actor,u.BunkerDoor):actors.destroy_actor(actor)
layout=json.loads((ROOT/'logs/doors_layout.json').read_text())
for item in layout:
    pos=u.Vector(*item['hinge_cm'])
    # Two cm clearance between the leaf edge and each jamb.
    yaw=item['closed_yaw']
    if yaw==0:pos.x+=2
    else:pos.y-=2
    door=actors.spawn_actor_from_class(u.BunkerDoor,pos)
    door.set_actor_label('INT_Door_'+item['name'])
    door.set_editor_property('width',item['opening_width_cm']-4)
    door.set_editor_property('height',item['height_cm'])
    door.set_editor_property('closed_yaw',yaw)
    door.set_editor_property('open_angle',item['open_angle'])
    door.set_editor_property('display_name','Porta — '+item['name'].removesuffix('N').removesuffix('S'))
    door.mesh.set_relative_scale3d(u.Vector((item['opening_width_cm']-4)/180,1,item['height_cm']/240))
    collision=door.get_component_by_class(u.BoxComponent)
    collision.set_relative_location(u.Vector((item['opening_width_cm']-4)/2,0,item['height_cm']/2),False,False)
    collision.set_box_extent(u.Vector((item['opening_width_cm']-4)/2,8,item['height_cm']/2),False)
    door.set_actor_rotation(u.Rotator(0,yaw+item['open_angle'],0),False)
level.save_current_level()
report={'movable_doors':len(layout),'sealed_leaves_preserved':3,'source':'logs/doors_layout.json','material_slots_preserved':len(slots),'width_range_cm':[min(d['opening_width_cm'] for d in layout),max(d['opening_width_cm'] for d in layout)]}
(ROOT/'logs/doors_install.json').write_text(json.dumps(report,indent=2))
u.log('C13_DOORS_INSTALLED '+json.dumps(report))
