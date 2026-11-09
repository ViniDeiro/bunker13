"""Independent reopen and geometry/packing check, not a visual-approval assertion."""
import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'blender/Convivencia_Reference_v001.blend'))
manifest=json.loads((R/'exports/reference_room/manifest.json').read_text());errors=[];assets=[]
if bpy.context.scene.unit_settings.system!='METRIC' or bpy.context.scene.unit_settings.scale_length!=1:errors.append('Source is not meter scale')
for name,expected in manifest.items():
 o=bpy.data.objects.get(name)
 if not o or o.type!='MESH':errors.append('Missing mesh '+name);continue
 if not o.data.uv_layers:errors.append('Missing UV '+name)
 if not all(math.isfinite(v) for p in o.data.vertices for v in p.co):errors.append('Nonfinite vertex '+name)
 if any(len(p.vertices)<3 or p.area<1e-12 for p in o.data.polygons):errors.append('Degenerate polygon '+name)
 if any(abs(a-b)>.0005 for a,b in zip(o.dimensions,expected['dimensions_m'])):errors.append('Bounds mismatch '+name)
 if not (R/'exports/reference_room'/(name+'.fbx')).is_file():errors.append('Missing FBX '+name)
 assets.append({'mesh':name,'dimensions_m':list(o.dimensions),'polygons':len(o.data.polygons),'materials':len(o.data.materials)})
imgs=[]
for im in bpy.data.images:
 if 'reference_room' in im.filepath and im.users:
  if not im.packed_file:errors.append('Unpacked image '+im.name)
  if list(im.size)!=[1024,1024]:errors.append('Unexpected map resolution '+im.name)
  imgs.append(im.name)
# Confirm that the final assembly matches the actual final Unreal placement file.
for row in json.loads((R/'exports/reference_room/scene_placements.json').read_text()):
 if not row['mesh']:continue
 o=bpy.data.objects.get(row['label'])
 if not o:errors.append('Missing assembly object '+row['label']);continue
 expected=(row['position'][0]/100,-row['position'][1]/100,row['position'][2]/100)
 if any(abs(a-b)>.0001 for a,b in zip(o.location,expected)):errors.append('Assembly position differs '+row['label'])
res={'passed':not errors,'blend_reopened':True,'mesh_count':len(assets),'packed_maps':len(imgs),'assets':assets,'errors':errors,'limits':['Checks topology, bounds, units, exports, packed maps and scene placements; visual approval is a separate human decision.']};(R/'logs/reference_art_validation.json').write_text(json.dumps(res,indent=2));print('REFERENCE_ART_VALIDATION',json.dumps(res));
if errors:raise RuntimeError(str(errors))
