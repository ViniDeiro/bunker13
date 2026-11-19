"""Reopen and inspect the saved study, then create lightweight review renders."""
from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[1];S=bpy.context.scene
assert len([o for o in S.objects if o.type=='MESH'])>=178
assert min(len(o.data.uv_layers) for o in S.objects if o.type=='MESH')>=2
assert len([i for i in bpy.data.images if i.packed_file])==2
bpy.data.objects['CAM_Top'].data.ortho_scale=7.8
for p in bpy.data.objects['Blanket'].data.polygons:p.use_smooth=True
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/Bedroom_StyleStudy_v001.blend'))
(R/'logs/bedroom_source_reopened.json').write_text(json.dumps({'passed':True,'meshes':len([o for o in S.objects if o.type=='MESH']),'uv_min':2,'packed_images':2},indent=2))
S.cycles.samples=8;S.cycles.max_bounces=4;S.cycles.diffuse_bounces=2;S.cycles.glossy_bounces=2;S.render.resolution_x=960;S.render.resolution_y=720
S.camera=bpy.data.objects['CAM_Perspective'];S.render.filepath=str(R/'screenshots/bedroom_blender.png');bpy.ops.render.render(write_still=True)
bpy.data.collections['Ceiling'].hide_render=True;S.camera=bpy.data.objects['CAM_Top'];S.render.filepath=str(R/'screenshots/bedroom_top.png');bpy.ops.render.render(write_still=True)
print('C13_BEDROOM_REOPEN_RENDER_OK',flush=True)
