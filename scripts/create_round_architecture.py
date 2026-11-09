"""Editable architectural revision for the stair opening; gameplay lives in Unreal."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'blender/Bunker_OpenPlan_v001.blend'))
col=bpy.data.collections.new('ROUND_Market_Access');bpy.context.scene.collection.children.link(col)
rows=json.loads((R/'logs/round_map_install.json').read_text())['geometry']
for row in rows:
 x,y,z=row['position_cm'];dims=row['dimensions_cm'];bpy.ops.mesh.primitive_cube_add(size=1,location=(x/100,-y/100,z/100));o=bpy.context.object;o.name='SM_'+row['name'];o.dimensions=[d/100 for d in dims];bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.data.materials.append(bpy.data.materials['M_Steel' if 'Rail' in o.name else 'M_Concrete'])
text=bpy.data.texts.new('LEIA_COLETA_MVP');text.write('Revisao arquitetonica da coleta inicial. Novo vao real de escada no piso do supermercado, dividido em quatro pecas. Ver docs/COLLECTION_ROUND_REPORT.md para gameplay e testes Unreal. Fontes anteriores preservadas.')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Bunker_CollectionRound_v001.blend'));print('ROUND_ARCHITECTURE_SAVED',len(rows))
