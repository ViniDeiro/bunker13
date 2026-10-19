"""Render the Painter exports on the authored models for offline visual QA."""
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/Bunker_HeroKit_v001.blend'))
for obj in bpy.data.objects:
    if not obj.name.startswith('SM_Hero_'):continue
    for slot in obj.material_slots:
        original=slot.material.name
        folder=ROOT/'assets/painter'/obj.name
        if not (folder/(original+'_BaseColor.png')).exists():raise RuntimeError(str(folder/original))
        mat=bpy.data.materials.new(obj.name+'_'+original+'_Painter');mat.use_nodes=True
        nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF')
        samples={}
        for kind in ('BaseColor','Normal','ORM'):
            n=nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(folder/(original+'_'+kind+'.png')))
            if kind!='BaseColor':n.image.colorspace_settings.name='Non-Color'
            samples[kind]=n
        links.new(samples['BaseColor'].outputs['Color'],bs.inputs['Base Color'])
        sep=nodes.new('ShaderNodeSeparateColor');links.new(samples['ORM'].outputs['Color'],sep.inputs[0])
        links.new(sep.outputs['Green'],bs.inputs['Roughness']);links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
        split=nodes.new('ShaderNodeSeparateColor');links.new(samples['Normal'].outputs['Color'],split.inputs[0])
        inv=nodes.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1
        links.new(split.outputs['Green'],inv.inputs[1])
        combine=nodes.new('ShaderNodeCombineColor');links.new(split.outputs['Red'],combine.inputs['Red']);links.new(inv.outputs[0],combine.inputs['Green']);links.new(split.outputs['Blue'],combine.inputs['Blue'])
        normal=nodes.new('ShaderNodeNormalMap');links.new(combine.outputs[0],normal.inputs['Color']);links.new(normal.outputs[0],bs.inputs['Normal'])
        slot.material=mat
bpy.context.scene.cycles.samples=48
bpy.context.scene.render.filepath=str(ROOT/'screenshots/painter_kit_final.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/Bunker_PainterKit_v001.blend'))
bpy.ops.render.render(write_still=True)
print('PAINTER_RENDER_OK')
