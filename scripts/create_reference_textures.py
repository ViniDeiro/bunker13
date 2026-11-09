"""Original physical PBR library: 1m tiles; no painted-on seam/rust grids."""
from pathlib import Path
import numpy as np,json,wave
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'assets/reference_room';O.mkdir(parents=True,exist_ok=True)
N=1024; rng=np.random.default_rng(221013);y,x=np.mgrid[:N,:N]/N
spec={'Concrete':((.25,.265,.26),.88,0,.003),'Paint':((.105,.17,.145),.42,0,.0002),'Steel':((.17,.19,.20),.30,1,.0001),'Rubber':((.014,.018,.019),.84,0,.0003),'Fabric':((.12,.17,.155),.9,0,.0007),'Wood':((.26,.14,.065),.48,0,.0004),'Ivory':((.58,.52,.40),.48,0,.00005),'Paper':((.67,.61,.46),.95,0,.00005),'Amber':((.75,.35,.055),.30,0,.0001),'Light':((.9,.66,.35),.22,0,0)}
def field(n):
 a=rng.random((n,n));a=np.pad(a,((0,1),(0,1)),mode='wrap')
 return np.asarray(Image.fromarray(a.astype('float32'),mode='F').resize((N+N//n,N+N//n),Image.Resampling.BICUBIC))[:N,:N]
for name,(rgb,rough,metal,depth) in spec.items():
 fine=field(512)-.5;mid=field(48)-.5;broad=field(8)-.5
 h=.35*fine+.25*mid+.15*broad;v=.035*fine+.025*mid+.025*broad
 if name=='Concrete':
  pores=np.maximum(fine-.31,0);h-=pores*4;v-=pores*.2
 elif name=='Wood':
  grain=np.sin(y*2*np.pi*42+np.sin(x*2*np.pi*3)*1.8+mid*1.5)
  h=grain*.07+fine*.04;v=grain*.07+mid*.03
 elif name=='Fabric':
  weave=np.sin(x*np.pi*800)*np.sin(y*np.pi*800);h=weave*.12+fine*.05;v=weave*.045+mid*.02
 elif name=='Steel':h=fine*.025+np.sin(y*2*np.pi*400)*.02;v=h
 linear=np.clip(np.array(rgb)[None,None,:]*(1+v[...,None]),0,1)
 srgb=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)
 dx=(np.roll(h,-1,1)-np.roll(h,1,1))*depth*N/2;dy=(np.roll(h,-1,0)-np.roll(h,1,0))*depth*N/2
 norm=np.stack((-dx,-dy,np.ones_like(h)),2);norm/=np.linalg.norm(norm,axis=2,keepdims=True)
 orm=np.stack((np.ones_like(h),np.clip(rough+mid*.05,0,1),np.full_like(h,metal)),2)
 for kind,a in [('BaseColor',srgb),('Normal',norm*.5+.5),('ORM',orm)]:Image.fromarray((np.clip(a,0,1)*255).astype('uint8')).save(O/f'T_Ref_{name}_{kind}.png')
# Synthesized original mechanical foley: restrained hinge friction + latch impulse.
rate=44100
for name,closing in [('Open',False),('Close',True)]:
 t=np.arange(int(rate*.85))/rate;n=rng.normal(0,1,len(t));env=np.sin(np.pi*np.clip(t/.85,0,1))**2
 friction=(np.sin(2*np.pi*(170*t+26*t*t))*.15+n*.05)*env
 at=.68 if closing else .04;impact=np.exp(-np.maximum(t-at,0)*65)*(t>=at)*(np.sin(2*np.pi*690*t)+n*.5)*.5
 a=np.clip((friction+impact)*.55,-1,1)
 with wave.open(str(O/f'S_Cabinet_{name}.wav'),'w') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes((a*32767).astype('<i2').tobytes())
(O/'manifest.json').write_text(json.dumps({'resolution':N,'tile_m':1,'materials':spec,'provenance':'Original procedurally authored PBR and synthesized foley, not Painter exports'},indent=2))
print('REFERENCE_TEXTURES_OK')
