from PIL import Image, ImageDraw, ImageFont
import math, sys
BASE='/home/claude/sem-narrativa-blog'
OUT=BASE+'/src/assets/capa-espectro-politico-bolsonaro-lula-12-eixos.jpg'
PREV=sys.argv[1] if len(sys.argv)>1 else None
ref=Image.open(BASE+'/src/assets/capa-voto-nulo-e-em-branco.jpg').convert('RGB')
W,H=1200,600
top=ref.getpixel((10,8)); mid=ref.getpixel((10,300)); bot=ref.getpixel((10,592))
box=ref.getpixel((66,300))
im=Image.new('RGB',(W,H)); px=im.load()
def lerp(a,b,t): return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
for y in range(H):
    t=y/(H-1)
    c=lerp(top,mid,t/0.6) if t<0.6 else lerp(mid,bot,(t-0.6)/0.4)
    for x in range(W): px[x,y]=c
im.paste(ref.crop((62,50,380,100)),(62,50))
d=ImageDraw.Draw(im,'RGBA')
X0=606
for y in range(H):
    t=y/H
    d.line([(X0,y),(W,y)],fill=(int(18+30*t),int(14+8*t),int(46+60*t),255))
F='/usr/share/fonts/opentype/inter/'
bold=lambda s: ImageFont.truetype(F+'Inter-Bold.otf',s)
med=lambda s: ImageFont.truetype(F+'Inter-Medium.otf',s)
white=(255,255,255); gray=(170,170,200); amber=(246,184,72); cyan=(110,200,255)
d.text((632,34),'PERFIL NO TESTE 12 AXES',font=med(17),fill=(200,200,225))
lx=632; ly=64
d.ellipse([lx,ly+4,lx+14,ly+18],fill=amber+(255,)); d.text((lx+22,ly),'Bolsonaro',font=bold(17),fill=white)
lx2=lx+140
d.ellipse([lx2,ly+4,lx2+14,ly+18],fill=cyan+(255,)); d.text((lx2+22,ly),'Lula',font=bold(17),fill=white)
axes=[('Estrutura','federal','unitário',31.9,30),
      ('Representação','democracia','autocracia',51.3,77.5),
      ('Poder','segurança','liberdade',49.6,43.8),
      ('Imigração','assimilação','multicultura',76.5,23.8),
      ('Diplomacia','militarista','pacifista',76.7,25),
      ('Intervenção','não interv.','nacionalista',28.1,61.3),
      ('Economia','público','privado',28.0,78.8),
      ('Controle','planejamento','livre mercado',27.8,78.8),
      ('Comércio','protecionismo','globalismo',36.3,63.7),
      ('Religião','irreligioso','religioso',11.7,50),
      ('Moral','progressista','tradicionalista',7.7,68.8),
      ('Tecnologia','tecnologia','biologia',70.1,45)]
L0,L1=792,1158
y=100; step=33
for name,lp,rp,b,l in axes:
    d.text((632,y),name,font=bold(16),fill=white)
    yl=y+10
    d.line([(L0,yl),(L1,yl)],fill=(95,90,150,255),width=2)
    d.line([((L0+L1)/2,yl-4),((L0+L1)/2,yl+4)],fill=(95,90,150,255),width=1)
    sf=med(11)
    d.text((L0,yl+5),lp,font=sf,fill=gray)
    tb=d.textbbox((0,0),rp,font=sf); d.text((L1-(tb[2]-tb[0]),yl+5),rp,font=sf,fill=gray)
    for val,col in ((l,cyan),(b,amber)):
        xx=L0+(100-val)/100*(L1-L0)
        d.ellipse([xx-7,yl-7,xx+7,yl+7],fill=col+(240,),outline=(20,16,50,255),width=2)
    y+=step
d.text((632,500),'Posição de cada um entre os dois polos, segundo o site.',font=med(14),fill=(150,150,175))
d.text((632,519),'O artigo confere eixo por eixo com votos e atos.',font=med(14),fill=(150,150,175))
d.text((72,150),'Bolsonaro e Lula',font=bold(46),fill=white)
f=bold(40); t='no espectro político'
bb=d.textbbox((0,0),t,font=f)
bx0,by0=62,222; bx1,by1=bx0+bb[2]-bb[0]+34,by0+78
d.rectangle([bx0,by0,bx1,by1],fill=box)
d.text((bx0+17,by0+4-bb[1]+8),t,font=f,fill=white)
for i,s2 in enumerate(['O que diz o teste dos 12 eixos','e o que mostram os votos e','os atos de cada um.']):
    d.text((72,340+i*42),s2,font=med(31),fill=(235,235,245))
ov=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
pts=[(x,560+14*math.sin(x/190.0)+7*math.sin(x/70.0)) for x in range(0,W+1,4)]
od.polygon(pts+[(W,H),(0,H)],fill=(124,76,214,235))
im=Image.alpha_composite(im.convert('RGBA'),ov).convert('RGB')
im.save(OUT,quality=92)
if PREV: im.save(PREV)
print(im.size,bx1)
