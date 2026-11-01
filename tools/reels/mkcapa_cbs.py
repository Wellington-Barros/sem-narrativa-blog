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
d.text((x0,60),'CBS NA REFORMA TRIBUTÁRIA, 2027',font=med(20),fill=(200,200,225,255))
d.line([(x0+14,118),(x0+14,500)],fill=(90,86,150,255),width=3)
PU=(70,60,160); AM=(120,84,20); BL=(40,80,120)
rows=[('Alíquota de referência','11,3% para 2027, aprovada pelo TCU','CONFIRMADO',white,PU),
      ('Redutor em compras públicas','44,2% (algumas fontes: 44,16%)','DADO',(170,205,240),BL),
      ('Estimativas anteriores','9,21% (Comitê do IBS) e 8,8% (Fazenda)','DADO',(170,205,240),BL),
      ('Quem decide agora','Senado, por resolução, até 15/12','PENDENTE',amber,AM),
      ('Preço final de cada produto','Não dá para afirmar com esses dados','NÃO SE SABE',amber,AM),
      ('Alíquota do IBS','Ainda sem número oficial','NÃO SE SABE',amber,AM)]
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
d.text((x0,500),'Conferido no TCU e na imprensa, com fontes no artigo.',font=med(15),fill=(150,150,175))
d.text((72,150),'Alíquota da CBS',font=bold(40),fill=white)
f=bold(42)
t='de 11,3% em 2027'
bb=d.textbbox((0,0),t,font=f)
bx0,by0=62,214
bx1,by1=bx0+bb[2]-bb[0]+34,by0+82
d.rectangle([bx0,by0,bx1,by1],fill=box)
d.text((bx0+17,by0+4-bb[1]+8),t,font=f,fill=white)
for i,s2 in enumerate(['O que o TCU decidiu, como o','número foi calculado e o que','o Senado ainda precisa definir.']):
    d.text((72,340+i*42),s2,font=med(33),fill=(235,235,245))
ov=Image.new('RGBA',(W,H),(0,0,0,0))
od=ImageDraw.Draw(ov)
pts=[(x,548+16*math.sin(x/190.0)+8*math.sin(x/70.0)) for x in range(0,W+1,4)]
od.polygon(pts+[(W,H),(0,H)],fill=(124,76,214,235))
im=Image.alpha_composite(im.convert('RGBA'),ov).convert('RGB')
im.save('/home/claude/sem-narrativa-blog/src/assets/capa-cbs-aliquota-11-3-tcu-2027.jpg',quality=92)
im.save('/tmp/capa-cbs-preview.png')
print(im.size, bx1)
