from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).parent
S=2
INK='#15191C'; MUTED='#656B6F'; WHITE='#FFFFFF'; LINE='#DCE0E2'
FONT='/System/Library/Fonts/HelveticaNeue.ttc'
def f(size,bold=False): return ImageFont.truetype(FONT,size*S,index=1 if bold else 0)
def tx(d,x,y,value,size=14,bold=False,color=INK): d.text((x*S,y*S),value,font=f(size,bold),fill=color)
def rr(d,box,fill,outline=None,width=1): d.rectangle(tuple(v*S for v in box),fill=fill,outline=outline,width=width*S)
def arrow(d,x,y,color):
 d.line((x*S,(y+12)*S,(x+12)*S,y*S),fill=color,width=2*S)
 d.line(((x+4)*S,y*S,(x+12)*S,y*S,(x+12)*S,(y+8)*S),fill=color,width=2*S)
def avatar():
 a=Image.new('RGB',(1024,1024),WHITE); d=ImageDraw.Draw(a)
 mark="[ 'draft ]"; face=ImageFont.truetype(FONT,126,index=1); tracking=3
 mark_width=sum(d.textlength(ch,font=face) for ch in mark)+tracking*(len(mark)-1)
 x=(1024-mark_width)/2
 for ch in mark:
  d.text((x,344),ch,fill=INK,font=face,stroke_width=2,stroke_fill=INK)
  x+=d.textlength(ch,font=face)+tracking
 d.text((198,475),'banket',fill=INK,font=ImageFont.truetype(FONT,91,index=0))
 a.save(OUT/'logo-avatar.png',optimize=True)
 return a
A=avatar()
PHOTO=ImageOps.exif_transpose(Image.open(ROOT/'site/assets/hero-snacks-yellow-v7.png')).convert('RGB')
COLORS={'sunny-yellow':'#F3CA52','fresh-lime':'#D8F060','warm-coral':'#FF7564'}
def screen(accent):
 im=Image.new('RGB',(390*S,850*S),WHITE); d=ImageDraw.Draw(im)
 # header: repeat the bracketed name from the existing Instagram identity
 d.text((22*S,20*S),"[ 'draft ]",font=f(23,True),fill=INK,stroke_width=1*S,stroke_fill=INK)
 tx(d,133,24,'banket',17,False)
 d.ellipse((342*S,14*S,380*S,52*S),outline=INK,width=S)
 d.rectangle((352*S,27*S,369*S,41*S),outline=INK,width=S)
 d.arc((356*S,21*S,365*S,32*S),180,360,fill=INK,width=S)
 d.line((0,68*S,390*S,68*S),fill=LINE,width=S)
 tx(d,22,85,'КЕЙТЕРИНГ В МИНСКЕ',9,True)
 # assertive, tightly set headline
 tx(d,22,115,'Боксы и',45,True)
 rr(d,(22,203,206,213),accent)
 tx(d,22,161,'закуски для',43,True)
 tx(d,22,210,'ваших событий.',40,True)
 tx(d,22,281,'Выберите готовый бокс или соберите свой набор',14,False,MUTED)
 tx(d,22,303,'из закусок. Оставьте заявку — мы свяжемся',14,False,MUTED)
 tx(d,22,325,'с вами и согласуем детали.',14,False,MUTED)
 rr(d,(22,371,368,427),accent)
 tx(d,38,389,'01',10,False)
 tx(d,81,383,'Готовые боксы',16,True)
 arrow(d,338,390,INK)
 rr(d,(22,435,368,491),WHITE,INK)
 tx(d,38,453,'02',10,False)
 tx(d,81,447,'Собрать свой набор',16,True)
 arrow(d,338,454,INK)
 crop=ImageOps.fit(PHOTO,(390*S,334*S),Image.Resampling.LANCZOS,centering=(.5,.45))
 im.paste(crop,(0,516*S))
 return im
screens=[]
for name,color in COLORS.items():
 im=screen(color); dest=OUT/f'mobile-home-{name}.png'; im.save(dest,optimize=True); screens.append((name,im))
# Default picture is the live site's yellow direction.
screens[0][1].save(OUT/'mobile-home-mockup.png',optimize=True)
labels={'sunny-yellow':'ЖЁЛТЫЙ','fresh-lime':'ЛАЙМ','warm-coral':'КОРАЛЛ'}
board=Image.new('RGB',(3*390*S+4*24*S,920*S),WHITE); bd=ImageDraw.Draw(board)
for i,(name,im) in enumerate(screens):
 x=(24+i*(390+24))*S
 bd.text((x,17*S),labels[name],font=f(17,True),fill=INK)
 bd.rectangle((x+260*S,19*S,x+282*S,41*S),fill=COLORS[name])
 board.paste(im,(x,56*S))
board.save(OUT/'accent-options.png',optimize=True)
print('Created three mobile variants, comparison, and draft banket avatar.')
