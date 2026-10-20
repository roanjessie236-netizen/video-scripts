import numpy as np, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
P='/usr/share/fonts/google-noto-cjk/'
def serif(s,w='Regular'): return ImageFont.truetype(P+f'NotoSerifCJK-{w}.ttc',s,index=2)
def sans(s,w='Regular'): return ImageFont.truetype(P+f'NotoSansSC-{w}.otf',s)
W,H=1920,1080
D='/data/.agent-service/files/10db44ed-4380-4e24-8c2d-f7f46edcf104/tool-output-0.jpg'
def cover(im,w,h):
    r=max(w/im.width,h/im.height); im=im.resize((round(im.width*r),round(im.height*r)),Image.LANCZOS)
    x=(im.width-w)//2; y=(im.height-h)//2; return im.crop((x,y,x+w,y+h))
def vignette(w,h,s):
    y,x=np.mgrid[0:h,0:w]; d=np.sqrt(((x-w/2)/(w/2))**2+((y-h/2)/(h/2))**2)
    return (1-s*np.clip(d-0.55,0,1)**1.6)[...,None]
def grade(im,k):
    a=np.asarray(im.convert('RGB')).astype(np.float32)/255
    lum=(a@np.array([0.299,0.587,0.114],np.float32))[...,None]
    a=lum+(a-lum)*(1-0.5*k)                      # 降饱和
    a=a+((1-lum)**2)*np.array([-0.05,0.004,0.07])*k+(lum**2)*np.array([-0.035,0.0,0.03])*k  # 冷调分离
    a=0.05*k+a*(1-0.09*k)                        # 抬黑、压白（旧胶片褪色）
    a=a*vignette(a.shape[1],a.shape[0],0.35)
    a=a+np.random.default_rng(3).normal(0,0.012+0.012*k,a.shape[:2])[...,None]  # 颗粒
    return Image.fromarray((np.clip(a,0,1)*255).astype(np.uint8))
def shadow_text(img,xy,t,f,fill=(240,240,236),anchor='la',r=3):
    s=Image.new('RGBA',img.size,(0,0,0,0)); ImageDraw.Draw(s).text(xy,t,font=f,fill=(0,0,0,170),anchor=anchor)
    s=s.filter(ImageFilter.GaussianBlur(r)); img.alpha_composite(s); ImageDraw.Draw(img).text(xy,t,font=f,fill=fill,anchor=anchor)
def subtitle(img,t,attr=None):
    shadow_text(img,(W//2,H-92),t,serif(44,'Medium'),anchor='ms')
    if attr: shadow_text(img,(W//2,H-46),attr,serif(26),fill=(205,208,206),anchor='ms')
def tag(img,t):  # 右上角小标签
    d=ImageDraw.Draw(img); f=sans(24); x1=W-56; tw=d.textlength(t,font=f)
    d.rounded_rectangle((x1-tw-28,48,x1,88),6,fill=(20,24,28,150)); d.text((x1-14,68),t,font=f,fill=(225,228,226),anchor='rm')
def info_card(img,kind,title,meta,src,x=72,y=72):
    f1,f2,f3=sans(22,'Medium'),serif(40,'SemiBold'),sans(24)
    d0=ImageDraw.Draw(img); w=max(d0.textlength(title,font=f2),d0.textlength(meta,font=f3),d0.textlength(src,font=f3))+64; h=196
    card=Image.new('RGBA',img.size,(0,0,0,0)); d=ImageDraw.Draw(card)
    d.rectangle((x,y,x+w,y+h),fill=(16,20,24,178)); d.rectangle((x,y,x+5,y+h),fill=(168,58,44,255))
    d.text((x+30,y+22),kind,font=f1,fill=(196,120,104)); d.text((x+30,y+52),title,font=f2,fill=(242,242,238))
    d.text((x+30,y+112),meta,font=f3,fill=(210,213,210)); d.text((x+30,y+150),src,font=f3,fill=(160,166,166))
    img.alpha_composite(card)
# ① 调色强度对比
src=Image.open(D).convert('RGB'); tw,th=960,536
board=Image.new('RGB',(24+2*(tw+24),90+2*(th+70+24)),'#15181b'); bd=ImageDraw.Draw(board)
bd.text((24,26),'冷调旧胶片：强度对比（AI 情景再现与影视剧统一使用）',font=sans(36,'Bold'),fill='#eceeec')
for i,(lab,k) in enumerate([('原图',0),('轻',0.45),('中（推荐）',0.75),('重',1.0)]):
    x=24+(i%2)*(tw+24); y=90+(i//2)*(th+70+24)
    im=cover(src,tw,th) if k==0 else grade(cover(src,tw,th),k)
    board.paste(im,(x,y)); bd.text((x,y+th+12),lab,font=sans(34,'Bold'),fill='#eceeec')
board.save('grade_board.jpg',quality=88)
# ② 历史照片＋统一介绍卡
ph=Image.open('../src/c_hz233.png').convert('L')
bg=cover(ph.convert('RGB'),W,H).filter(ImageFilter.GaussianBlur(28))
bg=grade(Image.blend(bg,Image.new('RGB',(W,H),(22,26,30)),0.6),1.0).convert('RGBA')
ph=ImageOps.contain(ph,(1000,760)); bw,bh=ph.size; b=20
card=Image.new('RGBA',(bw+2*b,bh+2*b),(233,234,230,255)); card.paste(ph.convert('RGBA'),(b,b))
card=card.rotate(-1.6,resample=Image.BICUBIC,expand=True)
sh=Image.new('RGBA',(W,H),(0,0,0,0)); cx=(W-card.width)//2+160; cy=(H-card.height)//2-50
sh.paste((0,0,0,150),(cx+14,cy+18,cx+14+card.width,cy+18+card.height)); bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
bg.alpha_composite(card,(cx,cy))
info_card(bg,'史料 · 照片','参加葬礼的宋庆龄、许广平和周海婴','1936年10月 · 上海','出处：林贤治《鲁迅画传》')
subtitle(bg,'许多素不相识的人，自发走进送葬的队伍'); bg.convert('RGB').save('frame_card.jpg',quality=90)
# ③ AI 情景再现成片效果
f=grade(cover(src,W,H),0.75).convert('RGBA'); tag(f,'AI 情景再现'); subtitle(f,'质铺的是比我高一倍，我从一倍高的柜台外送上衣服或首饰去','——鲁迅《呐喊·自序》')
f.convert('RGB').save('frame_ai.jpg',quality=90); print('ok')
