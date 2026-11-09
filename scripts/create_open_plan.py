"""Alternative architectural layout; never overwrites the approved reference source."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
# Reuse the exact reference-shell export, with an independent destination and filters.
s=(R/'scripts/export_reference_shell.py').read_text()
s=s.replace('Bunker_ReferenceShell.fbx','Bunker_OpenPlanShell.fbx').replace('reference_shell_export.json','open_plan_shell_export.json')
s=s.replace("        source_objects.append(obj.name)","""        if obj.name in removed_names: continue
        source_objects.append(obj.name)""")
s=s.replace('vertices = []', '''open_rooms=('Convivencia','Cozinha','Despensa','Enfermaria','Radio_Comando','Oficina')
retained_sides={'Convivencia':'S','Cozinha':'S','Despensa':'E'}
removed_names=set()
for obj in bpy.data.objects:
    for room in open_rooms:
        if obj.name.startswith('SM_'+room):
            side=obj.name[len('SM_'+room):len('SM_'+room)+1]
            if side in 'NSWE' and side!=retained_sides.get(room):removed_names.add(obj.name)
        if obj.name.startswith(('SM_Frame_'+room,'SM_FrameTop_'+room)):
            removed_names.add(obj.name)
    if obj.name.startswith('SM_ServiceShaft_'):removed_names.add(obj.name)
vertices = []''',1)
# The legacy door manifest must remain untouched.
s=s.replace("(ROOT/'logs/doors_layout.json').write_text(json.dumps(door_layout,indent=2))",'')
exec(compile(s,str(R/'scripts/export_reference_shell.py'),'exec'))
for n in removed_names:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
for o in list(bpy.data.collections['COLLISION'].objects):
 if any(o.name.startswith('UCX_'+n+'_') for n in removed_names) or any(o.name.startswith('UCX_SM_Door_'+r) for r in open_rooms):bpy.data.objects.remove(o,do_unlink=True)
for t in list(bpy.data.texts):
 if t.name=='walk_bunker.py':bpy.data.texts.remove(t)
readme=bpy.data.texts.new('LEIA_PLANTA_ABERTA');readme.write('Planta alternativa de 29/10/2026. Navegacao validada no executavel Unreal, nao pelo antigo inspector B1. Mapa Lvl_Bunker_OpenPlan; avaliacao sem salvamento de campanha. Ver docs/OPEN_PLAN_REPORT.md. Demais moveis em proxy fora da convivência. Fontes anteriores preservadas.')
for o in list(bpy.data.objects):
 if o.name.startswith('SM_Door_') and any(o.name.startswith('SM_Door_'+r) for r in open_rooms):bpy.data.objects.remove(o,do_unlink=True)
# Hide the temporary joined export; architecture remains modular in this source.
merged.hide_render=True;merged.hide_set(True)
for o in bpy.data.objects:
 if o.name.startswith(('LABEL_','TITLE','DIM_','CORRIDOR')):o.hide_render=True
# Replace social blockout masses with the existing editable reference assembly.
for o in list(bpy.data.collections['PROPS_Blockout'].objects):
 if any(o.name.startswith('SM_'+p) for p in ('Mesa_Social','Cadeira_','Sofa','TV_Antiga','Mesa_Cartas','Radio_Social','Estante_Social','Quadro_Avisos')):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(R/'blender/Convivencia_Reference_v001.blend'),link=False) as (src,dst):dst.collections=['REFERENCE_ROOM_ASSEMBLY']
assembly=dst.collections[0];bpy.context.scene.collection.children.link(assembly)
removed_ref=[]
for o in list(assembly.objects):
 if o.name.startswith(('REF_Panel_East','REF_Panel_West','REF_Panel_South','REF_CoveFixture','Practical_')):
  removed_ref.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
for o in assembly.objects:
 if o.name in ('REF_Floor','REF_Ceiling'):
  o.location=(14,10,.026 if o.name=='REF_Floor' else 2.86);o.scale=(27.4,19.4,1 if o.name=='REF_Floor' else 2)
# A freestanding dart backing preserves the playable target location without a room.
bpy.ops.mesh.primitive_cube_add(size=1,location=(15.15,7.05,1.73));screen=bpy.context.object;screen.name='SM_OP_DartScreen';screen.dimensions=(.6,.08,.6);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);screen.data.materials.append(bpy.data.materials['M_Concrete'])
for n,loc,dim in [('Post',(15.15,7.05,.86),(.06,.06,1.7)),('Base',(15.15,7.05,.041),(.5,.5,.03))]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='SM_OP_DartStand'+n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(bpy.data.materials['M_Steel'])
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
cam=bpy.data.objects['CAM_Top'];cam.location=(14,10,40);cam.rotation_euler=(0,0,0);cam.rotation_euler=(Vector((14,10,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=31;scene.camera=cam
for o in bpy.data.collections['ARCH_Ceilings'].objects:o.hide_render=True
for o in assembly.objects:
 if o.name.startswith('REF_Ceiling'):o.hide_render=True
for o in bpy.data.collections['PROPS_Blockout'].objects:
 if o.name.startswith('SM_Duto_'):o.hide_render=True
scene.render.filepath=str(R/'screenshots/open_plan_blender_top.png');bpy.ops.render.render(write_still=True)
for o in bpy.data.collections['PROPS_Blockout'].objects:
 if o.name.startswith('SM_Duto_'):o.hide_render=False
for o in bpy.data.collections['ARCH_Ceilings'].objects:o.hide_render=False
for o in assembly.objects:
 if o.name.startswith('REF_Ceiling'):o.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Bunker_OpenPlan_v001.blend'))
(R/'logs/open_plan_source.json').write_text(json.dumps({'removed_partition_objects':sorted(removed_names),'removed_reference_objects':removed_ref,'enclosed':['Dormitorio','Sanitario','Antecamara','Gerador'],'integrated':list(open_rooms),'source_preserved':True},indent=2))
print('OPEN_PLAN_SOURCE_OK')
