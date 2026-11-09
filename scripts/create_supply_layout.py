"""Editable placement of the six existing production meshes. Coordinates use Unreal's +Y convention, metres."""
from pathlib import Path
import bpy, json, math
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
source=R/'blender/Bunker_Infrastructure_v001.blend'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
names=['SM_Infra_FuelCan','SM_Infra_RepairParts','SM_Infra_Filter']
with bpy.data.libraries.load(str(source),link=False) as (src,dst):
    assert all(name in src.objects for name in names)
    dst.objects=list(names)
templates={obj.name:obj for obj in dst.objects}
collection=bpy.data.collections.new('SUPPLY_Parking_Cache');bpy.context.scene.collection.children.link(collection)
rows=[]
for index in range(6):
    kind=names[index//2];obj=templates[kind].copy();obj.data=templates[kind].data.copy()
    obj.name=f'SupplyV1_{index}';collection.objects.link(obj)
    obj.location=(28+index*.65,32,2.9405);obj['world_key']=obj.name;obj['unreal_mesh']=kind
    obj['coordinate_note']='Unreal +Y in metres; placement reference, reuse existing imported asset'
    rows.append(dict(key=obj.name,mesh=kind,position_cm=[2800+index*65,3200,294.05]))
for obj in templates.values():bpy.data.objects.remove(obj,do_unlink=True)
scene=bpy.context.scene
camera_data=bpy.data.cameras.new('CAM_SupplyCache');camera=bpy.data.objects.new('CAM_SupplyCache',camera_data);scene.collection.objects.link(camera)
camera.location=(29.6,28,5.5);camera.rotation_euler=(Vector((29.6,32,3.1))-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=4.8;scene.camera=camera
bpy.ops.mesh.primitive_cube_add(size=1,location=(27.7,24.5,2.8505))
apron=bpy.context.object;apron.name='ARCH_MarketEntryApron';apron.dimensions=(12.4,3,.18);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
apron['unreal_material']='/Game/Bunker/Materials/M_EXT_Asphalt';apron['purpose']='Repair existing market-parking floor gap; no map expansion'
apron.data.uv_layers.new(name='UV_Meters')
for poly in apron.data.polygons:
 for loop_index in poly.loop_indices:
  v=apron.data.vertices[apron.data.loops[loop_index].vertex_index].co
  apron.data.uv_layers[1].data[loop_index].uv=(v.x+27.7,v.y+24.5)
mat=bpy.data.materials.new('M_ParkingApron_PBR');mat.use_nodes=True
nodes=mat.node_tree.nodes;links=mat.node_tree.links;principled=nodes.get('Principled BSDF')
uv=nodes.new('ShaderNodeUVMap');uv.uv_map='UV_Meters'
scale=nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=1/3;links.new(uv.outputs['UV'],scale.inputs[0])
tex={}
for kind in ('BaseColor','Normal','ORM'):
 node=nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(R/'assets/textures'/f'T_Concrete_{kind}.png'),check_existing=True)
 if kind!='BaseColor':node.image.colorspace_settings.name='Non-Color'
 links.new(scale.outputs['Vector'],node.inputs['Vector']);tex[kind]=node
links.new(tex['BaseColor'].outputs['Color'],principled.inputs['Base Color'])
normal=nodes.new('ShaderNodeNormalMap');links.new(tex['Normal'].outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],principled.inputs['Normal'])
separate=nodes.new('ShaderNodeSeparateColor');links.new(tex['ORM'].outputs['Color'],separate.inputs['Color']);links.new(separate.outputs['Green'],principled.inputs['Roughness']);links.new(separate.outputs['Blue'],principled.inputs['Metallic'])
apron.data.materials.append(mat)
export=R/'exports/expedition' ;export.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='DESELECT');apron.select_set(True);bpy.context.view_layer.objects.active=apron
apron_location=apron.location.copy();apron.location=(0,0,0)
bpy.ops.export_scene.fbx(filepath=str(export/'SM_MarketEntryApron.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False)
apron.location=apron_location
bpy.ops.file.pack_all()
path=R/'blender/Bunker_ExpeditionSupplies_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path))
bpy.ops.wm.open_mainfile(filepath=str(path))
objects=[o for o in bpy.data.objects if o.name.startswith('SupplyV1_')]
assert len(objects)==6
assert all(o.type=='MESH' and len(o.data.uv_layers)>=2 and all(math.isfinite(v) for v in (*o.location,*o.dimensions)) for o in objects)
images=[i for i in bpy.data.images if i.source=='FILE'];assert all(i.packed_file for i in images)
(R/'logs/supply_blender_validation.json').write_text(json.dumps(dict(passed=True,reopened=True,objects=rows,uv_layers_min=min(len(o.data.uv_layers) for o in objects),packed_images=len(images),source_preserved=str(source),apron_dimensions_m=[12.4,3,.18],note='Existing entrance connection repaired; no map expansion. Existing imported item assets reused.'),indent=2))
print('C13_SUPPLY_BLEND_VALIDATED')
