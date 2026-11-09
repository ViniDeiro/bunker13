import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'blender/Bunker_OpenPlan_v001.blend'))
report=json.loads((R/'logs/open_plan_source.json').read_text());errors=[]
for name in report['removed_partition_objects']:
 if name in bpy.data.objects:errors.append('Retained partition: '+name)
for collection in ('ARCH_Walls','ARCH_Floors','ARCH_Ceilings','ARCH_Doors','REFERENCE_ROOM_ASSEMBLY'):
 if collection not in bpy.data.collections:errors.append('Missing collection: '+collection)
for o in bpy.data.objects:
 if o.type=='MESH' and any(not math.isfinite(x) for v in o.data.vertices for x in v.co):errors.append('Nonfinite: '+o.name)
for room in ('Dormitorio','Sanitario','Antecamara','Gerador'):
 if not any(o.name.startswith('SM_'+room) for o in bpy.data.collections['ARCH_Walls'].objects):errors.append('Enclosure missing: '+room)
if not (R/'exports/Bunker_OpenPlanShell.fbx').is_file():errors.append('Export missing')
result={'passed':not errors,'blend_reopened':True,'errors':errors,'removed_partition_objects':len(report['removed_partition_objects']),'unit_scale':bpy.context.scene.unit_settings.scale_length,'limits':['Geometry/collection audit; circulation is tested separately in the cooked Unreal world.']}
(R/'logs/open_plan_editable_validation.json').write_text(json.dumps(result,indent=2));print('OPEN_PLAN_EDITABLE',result)
if errors:raise RuntimeError(errors)
