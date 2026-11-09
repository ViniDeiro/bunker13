"""Match the final Unreal placements in the editable Blender source and pack maps."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'blender/Convivencia_Reference_v001.blend'))
s=bpy.context.scene
old=bpy.data.collections.get('REFERENCE_ROOM_ASSEMBLY')
if old:
 for o in list(old.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.collections.remove(old)
c=bpy.data.collections.new('REFERENCE_ROOM_ASSEMBLY');s.collection.children.link(c)
rows=json.loads((R/'exports/reference_room/scene_placements.json').read_text())
for r in rows:
 if not r['mesh'] or r['mesh'] not in bpy.data.objects:continue
 src=bpy.data.objects[r['mesh']];o=src.copy();o.data=src.data;c.objects.link(o);o.name=r['label'];o.location=(r['position'][0]/100,-r['position'][1]/100,r['position'][2]/100);o.rotation_euler=(math.radians(r['rotation'][0]),-math.radians(r['rotation'][1]),-math.radians(r['rotation'][2]));o.scale=r['scale'];o.hide_set(False);o.hide_render=False
 if r['class']=='BunkerReferenceCabinet':
  leaf=bpy.data.objects['SM_Ref_CabinetLeaf'].copy();leaf.data=bpy.data.objects['SM_Ref_CabinetLeaf'].data;c.objects.link(leaf);leaf.name='REF_CabinetLeaf_Editable';leaf.location=o.location+o.rotation_euler.to_matrix()@Vector((-.576,-.27,0));leaf.rotation_euler=o.rotation_euler;leaf.hide_set(False);leaf.hide_render=False
for name in ('Concrete','Paint','Steel','Rubber','Fabric','Wood','Ivory','Paper','Amber','Light'):
 if 'M_Ref_'+name not in bpy.data.materials:continue
 m=bpy.data.materials['M_Ref_'+name];p=m.node_tree.nodes.get('Principled BSDF')
 for old_node in list(m.node_tree.nodes):
  if old_node.type in ('TEX_IMAGE','SEPARATE_COLOR','NEW_GEOMETRY'):m.node_tree.nodes.remove(old_node)
 geo=m.node_tree.nodes.new('ShaderNodeNewGeometry')
 for kind in ('BaseColor','Normal','ORM'):
  im=bpy.data.images.load(str(R/'assets/reference_room'/f'T_Ref_{name}_{kind}.png'),check_existing=True)
  if im.packed_file:im.unpack(method='REMOVE')
  im.reload();im.pack()
  if kind!='BaseColor':im.colorspace_settings.name='Non-Color'
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;tex.projection='BOX';tex.projection_blend=.2;m.node_tree.links.new(geo.outputs['Position'],tex.inputs['Vector'])
  if kind=='BaseColor':m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
  if kind=='ORM':
   sep=m.node_tree.nodes.new('ShaderNodeSeparateColor');m.node_tree.links.new(tex.outputs['Color'],sep.inputs['Color']);m.node_tree.links.new(sep.outputs['Green'],p.inputs['Roughness']);m.node_tree.links.new(sep.outputs['Blue'],p.inputs['Metallic'])
 if name=='Light':p.inputs['Emission Color'].default_value=(1,.6,.22,1);p.inputs['Emission Strength'].default_value=3
for i,r in enumerate(rows):
 if r['class'] not in ('PointLight','SpotLight'):continue
 d=bpy.data.lights.new('Practical_'+str(i),'SPOT' if r['class']=='SpotLight' else 'POINT');
 if r['class']=='SpotLight':d.spot_size=math.radians(160);d.spot_blend=.35
 d.energy=100;d.color=(1,.67,.36);d.shadow_soft_size=.12;o=bpy.data.objects.new(d.name,d);c.objects.link(o);o.location=(r['position'][0]/100,-r['position'][1]/100,r['position'][2]/100)
s.world.color=(.015,.02,.025);s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
for name,pos,target,ortho in [('Top',(11.5,3.8,15),(11.5,3.8,0),True),('Perspective',(14.6,6.5,1.65),(10,2.85,1.25),False)]:
 d=bpy.data.cameras.new('CAM_Ref_'+name);o=bpy.data.objects.new(d.name,d);c.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 if ortho:d.type='ORTHO';d.ortho_scale=10.5
 s.camera=o;s.render.resolution_y=960 if ortho else 720
 if ortho:
  ceiling=bpy.data.objects.get('REF_Ceiling');ceiling.hide_render=True if ceiling else False
 s.render.filepath=str(R/'screenshots'/f'reference_blender_{name.lower()}.png');bpy.ops.render.render(write_still=True)
 if ortho and ceiling:ceiling.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Convivencia_Reference_v001.blend'))
print('REFERENCE_ASSEMBLED_BLEND_OK')
