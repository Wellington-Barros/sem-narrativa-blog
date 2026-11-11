from PIL import Image, ImageDraw, ImageFont
import math, sys
BASE='/home/claude/sem-narrativa-blog'
OUT=BASE+'/src/assets/capa-eleicoes-estados-unidos-2026.jpg'
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
white=(255,255,255); amber=(246,184,72)
d.text((650,64),'APURAÇÃO DA AP ATÉ 10 DE NOVEMBRO DE 2026',font=med(17),fill=(200,200,225))
rows=[('54','SENADO','ind','Democratas têm pelo menos 54 de 100; republicanos, 44','w'),
      ('255','CÂMARA','ind','Democratas têm pelo menos 255 de 435; maioria: 218','w'),
      ('5','GOVERNADORES','ind','Estados que passaram para os democratas','w'),
      ('2','EM ABERTO','amb','Senado: Mississippi e Alasca, com democratas à frente','a'),
      ('3/1','POSSE','gry','Novo Congresso assume em 2027; Trump segue até 2029','g')]
cols={'ind':((70,60,160),white),'amb':((92,66,22),amber),'gry':((62,60,92),(196,196,214))}
dot={'w':(236,234,248),'a':amber,'g':(120,118,150)}
y0=130; step=84
LX=664
d.line([(LX,y0+10),(LX,y0+step*(len(rows)-1)+10)],fill=(95,90,150,255),width=3)
for i,(when,tag,kind,desc,dk) in enumerate(rows):
    y=y0+i*step
    d.ellipse([LX-8,y+3,LX+8,y+19],fill=dot[dk]+(255,))
    d.text((694,y),when,font=bold(20),fill=white)
    wb=d.textbbox((0,0),when,font=bold(20))
    tx=694+(wb[2]-wb[0])+14
    tf=bold(12)
    tb=d.textbbox((0,0),tag,font=tf)
    tw=tb[2]-tb[0]
    bg,fg=cols[kind]
    d.rounded_rectangle([tx,y+2,tx+tw+18,y+24],radius=5,fill=bg+(255,))
    d.text((tx+9,y+13-(tb[1]+tb[3])/2),tag,font=tf,fill=fg)
    d.text((694,y+27),desc,font=med(17),fill=(205,205,225))
d.text((72,150),'Estados Unidos',font=bold(60),fill=white)
f=bold(35); t='a virada no Congresso'
bb=d.textbbox((0,0),t,font=f)
bx0,by0=62,222; bx1,by1=bx0+bb[2]-bb[0]+34,by0+78
d.rectangle([bx0,by0,bx1,by1],fill=box)
d.text((bx0+17,by0+4-bb[1]+8),t,font=f,fill=white)
for i,s2 in enumerate(['Os números, o que ainda está','em aberto e o que muda','para Trump.']):
    d.text((72,340+i*42),s2,font=med(31),fill=(235,235,245))
ov=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
pts=[(x,560+14*math.sin(x/190.0)+7*math.sin(x/70.0)) for x in range(0,W+1,4)]
od.polygon(pts+[(W,H),(0,H)],fill=(124,76,214,235))
im=Image.alpha_composite(im.convert('RGBA'),ov).convert('RGB')
im.save(OUT,quality=92)
if PREV: im.save(PREV)
print(im.size,bx1)
