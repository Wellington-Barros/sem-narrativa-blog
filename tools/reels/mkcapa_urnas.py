from PIL import Image, ImageDraw, ImageFont
import math
ref=Image.open('/home/claude/sem-narrativa-blog/src/assets/capa-voto-nulo-e-em-branco.jpg').convert('RGB')
W,H=1200,600
top=ref.getpixel((10,8)); mid=ref.getpixel((10,300)); bot=ref.getpixel((10,592))
box=ref.getpixel((66,300))
im=Image.new('RGB',(W,H))
px=im.load()
def lerp(a,b,t): return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
for y in range(H):
    t=y/(H-1)
    c=lerp(top,mid,t/0.6) if t<0.6 else lerp(mid,bot,(t-0.6)/0.4)
    for x in range(W):
        px[x,y]=c
im.paste(ref.crop((62,50,380,100)),(62,50))
d=ImageDraw.Draw(im,'RGBA')
d.rectangle([606,0,W,H],fill=(8,12,28,255))
for y in range(H):
    t=y/H
    d.line([(606,y),(W,y)],fill=(int(18+30*t),int(14+8*t),int(46+60*t),255))
bold=lambda s: ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf',s)
med=lambda s: ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Medium.otf',s)
white=(255,255,255); amber=(246,184,72)
x0=650
d.text((x0,60),'URNAS DO 2º TURNO DE 2026 NOS DADOS DO TSE',font=med(20),fill=(200,200,225,255))
d.line([(x0+14,118),(x0+14,500)],fill=(90,86,150,255),width=3)
PU=(70,60,160); AM=(120,84,20); BL=(40,80,120)
rows=[('Zero voto para Flávio','106 de 499.205 urnas; Lula somou 14.860','CONFIRMADO',white,PU),
      ('Zero voto para Lula','4 urnas; Flávio somou 296 votos','CONFIRMADO',white,PU),
      ('Tamanho das urnas','Mediana de 128 eleitores (país: 263)','DADO',(170,205,240),BL),
      ('Onde ficam','18 estados; 63 com indicação indígena no local','DADO',(170,205,240),BL),
      ('Em 2022','143 com zero para Bolsonaro e 4 para Lula','DADO',(170,205,240),BL),
      ('Por que votaram assim','Os boletins mostram o resultado, não o motivo','NÃO SE SABE',amber,AM)]
y=108
for t,txt,tag,col,bg in rows:
    d.ellipse([x0+6,y+10,x0+22,y+26],fill=col+(255,))
    d.text((x0+44,y),t,font=bold(22),fill=white)
    d.text((x0+44,y+31),txt,font=med(18),fill=(205,205,228))
    tf=bold(13)
    tb=d.textbbox((0,0),tag,font=tf)
    tw=tb[2]-tb[0]+18
    tx=W-48-tw
    d.rounded_rectangle([tx,y+4,tx+tw,y+28],radius=7,fill=bg+(255,))
    d.text((tx+9,y+6-tb[1]+2),tag,font=tf,fill=col)
    y+=62
d.text((x0,500),'Conferido nos boletins de urna do TSE, com fontes no artigo.',font=med(15),fill=(150,150,175))
d.text((72,150),'Urnas sem voto',font=bold(40),fill=white)
f=bold(42)
t='no 2º turno de 2026'
bb=d.textbbox((0,0),t,font=f)
bx0,by0=62,214
bx1,by1=bx0+bb[2]-bb[0]+34,by0+82
d.rectangle([bx0,by0,bx1,by1],fill=box)
d.text((bx0+17,by0+4-bb[1]+8),t,font=f,fill=white)
for i,s2 in enumerate(['O que os boletins do TSE','confirmam, o que já ocorreu','em 2022 e o que não se sabe.']):
    d.text((72,340+i*42),s2,font=med(33),fill=(235,235,245))
ov=Image.new('RGBA',(W,H),(0,0,0,0))
od=ImageDraw.Draw(ov)
pts=[(x,548+16*math.sin(x/190.0)+8*math.sin(x/70.0)) for x in range(0,W+1,4)]
od.polygon(pts+[(W,H),(0,H)],fill=(124,76,214,235))
im=Image.alpha_composite(im.convert('RGBA'),ov).convert('RGB')
im.save('/home/claude/sem-narrativa-blog/src/assets/capa-urnas-zeradas-segundo-turno-2026.jpg',quality=92)
im.save('/tmp/capa-urnas-preview.png')
print(im.size, bx1)
