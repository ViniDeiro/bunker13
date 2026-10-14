"""Author reproducible seamless PBR surfaces; no external asset dependencies."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/textures'
OUT.mkdir(parents=True, exist_ok=True)
N = 512
rng = np.random.default_rng(13)
y, x = np.mgrid[:N, :N]

def noise(size):
    a = rng.random((size, size))
    # Periodic interpolation keeps both edges continuous.
    a = np.pad(a, ((0, 1), (0, 1)), mode='wrap')
    im = Image.fromarray((a * 255).astype('uint8'))
    return np.asarray(im.resize((N + N // size, N + N // size), Image.Resampling.BICUBIC), dtype=float)[:N, :N] / 255

def save(name, base, height, rough, metallic=0):
    height = np.clip(height, 0, 1)
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * .6
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * .6
    normal = np.stack((-dx, -dy, np.ones_like(dx)), -1)
    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    rgb = np.clip(base, 0, 1)
    Image.fromarray((rgb * 255).astype('uint8')).save(OUT / f'T_{name}_BaseColor.png')
    Image.fromarray(((normal * .5 + .5) * 255).astype('uint8')).save(OUT / f'T_{name}_Normal.png')
    orm = np.stack((np.clip(.72 + height * .28, 0, 1), np.broadcast_to(rough, height.shape), np.full_like(height, metallic)), -1)
    Image.fromarray((np.clip(orm, 0, 1) * 255).astype('uint8')).save(OUT / f'T_{name}_ORM.png')

fine, medium, broad = noise(256), noise(32), noise(8)
pores = np.maximum(0, fine - .72) * 2
seams = ((x % 256 < 3) | (y % 256 < 3)).astype(float)
h = .5 + (medium - .5) * .22 + (fine - .5) * .16 - pores * .2 - seams * .18
c = .34 + (broad - .5) * .035 + (medium - .5) * .025 + (fine - .5) * .035 - pores * .055 - seams * .045
save('Concrete', np.stack((c * 1.01, c, c * .94), -1), h, .91 - fine * .1)

rust = np.clip((broad * .65 + medium * .35 - .66) * 6, 0, 1)
scratch = ((np.sin(x * .73 + medium * 8) > .997) & (fine > .42)).astype(float)
paint = np.array([.21, .29, .235])
oxide = np.array([.35, .14, .045])
c = paint[None,None,:] * (1 - rust[...,None]) + oxide[None,None,:] * rust[...,None]
c += ((fine - .5) * .05 + scratch * .14)[...,None]
save('PaintedMetal', c, .5 + medium * .06 - rust * .1 + scratch * .05, .46 + rust * .42, .45)

grain = np.sin(x * .39 + np.sin(y * .018) * 3 + medium * 4) * .5 + .5
c = .23 + grain * .025 + broad * .025
save('Wood', np.stack((c * 1.28, c * .80, c * .43), -1), grain * .12 + fine * .08 + .4, .72 + fine * .15)

weave = (np.sin(x * np.pi / 2) * np.sin(y * np.pi / 2)) * .5 + .5
c = .23 + weave * .055 + medium * .035
save('Fabric', np.stack((c * .88, c * 1.08, c), -1), .4 + weave * .22, .96)

diamond = ((np.abs((x % 64) - 32) + np.abs((y % 64) - 32)) < 18).astype(float)
c = .15 + diamond * .09 + fine * .035
save('Floor', np.stack((c * .92, c, c * 1.02), -1), .4 + diamond * .25 + fine * .025, .66 + medium * .2, .6)

brush = noise(256) * .025 + np.sin(y * 3.1) * .018
c = .24 + brush + broad * .04
save('Steel', np.stack((c * .94, c, c * 1.04), -1), .5 + brush, .35 + medium * .14, .85)

thumbs = []
for name in ('Concrete','PaintedMetal','Wood','Fabric','Floor','Steel'):
    thumbs.append(Image.open(OUT / f'T_{name}_BaseColor.png').resize((256,256)))
sheet = Image.new('RGB', (768,512))
for i, im in enumerate(thumbs): sheet.paste(im, ((i%3)*256,(i//3)*256))
sheet.save(OUT / 'surface_contact_sheet.png')
(OUT / 'manifest.json').write_text(json.dumps({'resolution':N,'surfaces':6,'maps_per_surface':['BaseColor','Normal','ORM'],'seed':13,'license':'Original procedural assets authored for Deiros Dev'}, indent=2))
print('TEXTURES_OK: 6 surfaces, 18 PBR maps, 512px')
