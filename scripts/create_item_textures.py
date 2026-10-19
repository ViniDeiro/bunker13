"""Original C13 item atlases: four UV zones, authored labels, PBR surface wear."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/items';OUT.mkdir(parents=True,exist_ok=True)
FONT='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
REG='/System/Library/Fonts/Supplemental/Arial.ttf'
specs={
'Water':((51,86,76),'ÁGUA','POTÁVEL','500 mL','RESERVA / SANTA AURORA'),
'Food':((145,68,33),'AURORA','FEIJÃO COZIDO','400 g','CONSERVA / PRONTO PARA CONSUMO'),
'Medkit':((92,107,83),'PRIMEIROS','SOCORROS','KIT 01','DEFESA CIVIL / SANTA AURORA'),
'Battery':((168,110,30),'AURORA','ENERGIA','1,5 V','PILHA ALCALINA / TIPO D'),
'Tool':((46,65,63),'OFICINA','MANUTENÇÃO','13','PATRIMÔNIO / ABRIGO 13')}
for index,(name,(paint,title,subtitle,amount,footer)) in enumerate(specs.items()):
    rng=random.Random(1300+index)
    base=Image.new('RGB',(1024,1024));orm=Image.new('RGB',(1024,1024));height=Image.new('L',(1024,1024),128)
    # Image coordinates: upper-left painted, upper-right steel, lower-left rubber, lower-right label.
    for zone,(ox,oy),color,rough,metal in [(0,(0,0),paint,160,15),(1,(512,0),(132,139,135),96,245),(2,(0,512),(30,34,32),212,0),(3,(512,512),(213,202,164),185,0)]:
        tile=Image.new('RGB',(512,512));mask=Image.new('RGB',(512,512));hm=Image.new('L',(512,512));p=tile.load();q=mask.load();h=hm.load()
        for y in range(512):
            for x in range(512):
                noise=rng.gauss(0,2.8);grain=3*((y%5)/4-.5) if zone==1 else 0
                p[x,y]=tuple(max(0,min(255,int(c+noise+grain))) for c in color)
                q[x,y]=(255,max(0,min(255,int(rough+noise*2))),metal)
                h[x,y]=max(0,min(255,int(128+noise*.6+grain)))
        d=ImageDraw.Draw(tile);md=ImageDraw.Draw(mask);hd=ImageDraw.Draw(hm)
        for _ in range(90 if zone!=3 else 20):
            x,y=rng.randrange(512),rng.randrange(512);end=(x+rng.randrange(2,28),y+rng.randrange(-3,4))
            d.line((x,y,*end),fill=tuple(int(c*.67) for c in color),width=1);md.line((x,y,*end),fill=(255,195,metal),width=1);hd.line((x,y,*end),fill=108,width=1)
        base.paste(tile,(ox,oy));orm.paste(mask,(ox,oy));height.paste(hm,(ox,oy))
    # A designed, legible label, shared branding without real-world product marks.
    label=Image.new('RGB',(480,480),(216,208,178));d=ImageDraw.Draw(label)
    d.rectangle((0,0,480,62),fill=paint)
    def text(x,y,s,size,color=(36,48,41),bold=True):d.text((x,y),s,font=ImageFont.truetype(FONT if bold else REG,size),fill=color)
    text(18,17,'C13  /  DEFESA CIVIL',27,(239,230,199))
    if name=='Medkit':
        d.rectangle((202,76,268,208),fill=(56,91,76));d.rectangle((169,109,301,175),fill=(56,91,76));top=224
    else:top=94
    text(20,top,title,48 if len(title)<9 else 39);text(20,top+61,subtitle,30)
    d.line((20,top+112,460,top+112),fill=paint,width=4)
    if name!='Medkit':
        text(22,top+133,amount,58)
        text(22,top+211,'LOTE 13  /  ESTOQUE DE EMERGÊNCIA',18)
    text(20,385,footer,17)
    text(20,414,'MANTER SECO  •  INSPECIONAR ANTES DO USO',15,bold=False)
    for i in range(70):
        x=21+i*3;d.line((x,449,x,475),fill=(29,39,34),width=1 if i%3 else 2)
    text(258,449,'SA-13 / 026',22)
    # Mild aged-paper mottling; no fake dirt baked as lighting.
    lp=label.load()
    for _ in range(1800):
        x,y=rng.randrange(480),rng.randrange(480);c=lp[x,y];lp[x,y]=tuple(max(0,v-rng.randrange(3,14)) for v in c)
    base.paste(label,(528,528))
    # Tangent-space micro-normal, DirectX convention for UE.
    normal=Image.new('RGB',(1024,1024));hp=height.filter(ImageFilter.GaussianBlur(.5)).load();np=normal.load()
    for y in range(1024):
        for x in range(1024):
            dx=(hp[min(x+1,1023),y]-hp[max(x-1,0),y])*.8;dy=(hp[x,min(y+1,1023)]-hp[x,max(y-1,0)])*.8
            np[x,y]=(int(max(0,min(255,128-dx))),int(max(0,min(255,128+dy))),255)
    for kind,img in [('BaseColor',base),('ORM',orm),('Normal',normal)]:img.save(OUT/f'T_Item_{name}_{kind}.png')
(ROOT/'logs/item_textures.json').write_text(json.dumps({'resolution':1024,'assets':list(specs),'maps':['BaseColor','Normal DirectX','ORM'],'method':'Original programmatic surface textures and label typography; not a Painter export','seed':1300},indent=2))
print('ITEM_TEXTURES_OK')
