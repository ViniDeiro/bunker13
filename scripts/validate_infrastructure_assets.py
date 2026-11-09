import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'blender/Bunker_Infrastructure_v001.blend'));errors=[];rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 ok=all(math.isfinite(v) for p in o.data.vertices for v in p.co)
 if not ok or len(o.data.uv_layers)<2:errors.append(o.name)
 rows.append({'name':o.name,'finite':ok,'uv_layers':len(o.data.uv_layers),'dimensions_m':list(o.dimensions)})
images=[im for im in bpy.data.images if im.source=='FILE'];missing=[im.name for im in images if not im.packed_file];errors+=missing
result={'passed':not errors and len(rows)==7 and bpy.context.scene.unit_settings.scale_length==1,'reopened':True,'assets':rows,'embedded_textures':len(images),'errors':errors};(R/'logs/infra_asset_validation.json').write_text(json.dumps(result,indent=2));print(result)
if not result['passed']:raise RuntimeError(result)
