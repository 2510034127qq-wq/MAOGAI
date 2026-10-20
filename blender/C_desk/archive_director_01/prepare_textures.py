"""Reproducible scan treatment and physically scaled desk textures; no source edits."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
import cv2

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent.parent / "assets" / "scans"
OUT = ROOT / "textures"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(1976)

def save(a, name):
    Image.fromarray(np.uint8(np.clip(a, 0, 255))).save(OUT / name)

def noise(w, h, small, amp=1):
    x = rng.random((max(2, h//small), max(2, w//small))).astype(np.float32)
    return (cv2.resize(x, (w,h), interpolation=cv2.INTER_CUBIC)-.5)*amp

# Paper rectangle excludes the scanner bed at right/bottom. The final rectangle
# is EXACTLY 975:1380 = 130:184, without nonuniform scaling of the original ink.
cover = np.array(Image.open(SRC/"cover.png").convert("RGB"))
cover = cover[20:1400, 0:975].copy()
# Repair only the narrow scanner seam and damaged/outside edges, never the text.
mask = np.zeros(cover.shape[:2], np.uint8)
mask[:, 399:404] = 255
gray = cv2.cvtColor(cover, cv2.COLOR_RGB2GRAY)
mask[:, 965:] = np.where(gray[:,965:] < 75, 255, mask[:,965:])
cover = cv2.inpaint(cover, mask, 4, cv2.INPAINT_TELEA).astype(np.float32)
lum = .25*cover[:,:,0]+.6*cover[:,:,1]+.15*cover[:,:,2]
red = np.clip((cover[:,:,0]-cover[:,:,1]-18)/90,0,1)
# Compress saturated scan reds to the director's cinnabar; keep all ink edges.
paper = np.array([237,229,212], np.float32)
ink = np.array([28,26,23], np.float32)
base = ink[None,None,:]+(paper-ink)[None,None,:]*(lum/255)[:,:,None]
redcolor = np.array([181,48,42],np.float32)[None,None,:]*(.85+.15*lum/255)[:,:,None]
cover = base*(1-red[:,:,None])+redcolor*red[:,:,None]
save(cover,"cover_clean.png")

for page in ("p06","p07"):
    # Uniform crop 1430x2024: exactly the 130:184 physical aspect ratio.
    # Remove outer scanner noise with whitespace intact around all printed glyphs.
    a = np.array(Image.open(SRC/(page+".png")).convert("L"))[45:2069,22:1452]
    h,w = a.shape
    yy,xx = np.mgrid[0:h,0:w]
    edge = np.minimum.reduce([xx/w,(w-1-xx)/w,yy/h,(h-1-yy)/h])
    aging = 1-.034*np.exp(-edge*55)+noise(w,h,160,.009)+noise(w,h,3,.008)
    tone = np.array([237,229,212])[None,None,:]*aging[:,:,None]
    black = np.array([28,26,23])[None,None,:]
    result = black+(tone-black)*(a/255)[:,:,None]
    save(result,page+"_aged.png")

# Blank ruled sheets, no pseudo-writing.
w,h=1300,1840
a = np.ones((h,w,3))*np.array([228,217,195])
a += noise(w,h,3,2)[:,:,None]
im=Image.fromarray(np.uint8(np.clip(a,0,255)))
d=ImageDraw.Draw(im)
for y in range(160,1730,75):
    d.line((70,y,1230,y), fill=(167,158,141), width=2)
d.line((145,100,145,1760),fill=(164,125,111),width=2)
im.save(OUT/"ruled.png")

# Old elm: multi-scale, mostly longitudinal fibres with local knot distortion.
w=h=2048
yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
x=xx/w;y=yy/h
warp = .003*np.sin(x*19)+.007*np.sin(x*4.1+y*8)+noise(w,h,240,.008)
for kx,ky,s in [(.22,.31,.045),(.73,.68,.03),(.54,.88,.024)]:
    dx=(x-kx)*.40
    dy=y-ky
    warp += .015*np.exp(-((dx/s)**2+(dy/(s*1.8))**2))*np.sin(np.arctan2(dy,dx))
v=y+warp
long_fibres = cv2.resize(rng.random((950,28)).astype(np.float32),(w,h),interpolation=cv2.INTER_CUBIC)
mapx=xx.astype(np.float32)
mapy=np.clip(v*h,0,h-1).astype(np.float32)
grain=cv2.remap(long_fibres,mapx,mapy,cv2.INTER_LINEAR)
wide_fibres=cv2.resize(rng.random((85,13)).astype(np.float32),(w,h),interpolation=cv2.INTER_CUBIC)
wide_fibres=cv2.remap(wide_fibres,mapx,mapy,cv2.INTER_LINEAR)
fine=noise(w,h,2,1)+.5
large=noise(w,h,230,.22)+noise(w,h,60,.08)
shade=.92+large-.19*grain**3+.15*(wide_fibres-.5)-.025*fine
for kx,ky,s in [(.22,.31,.045),(.73,.68,.03),(.54,.88,.024)]:
    radius=np.sqrt(((x-kx)*.38)**2+(y-ky)**2)
    envelope=np.exp(-(radius/(s*1.6))**2)
    shade-=envelope*(.065+.045*np.sin(radius*650+wide_fibres*5))
    shade-=.10*np.exp(-(radius/(s*.24))**2)
plank=(y*5).astype(int)
shade*=np.array([.94,1.01,.95,1.06,.97,1.0])[np.minimum(plank,5)]
seams=(np.abs(np.sin(y*5*np.pi))<.003)
shade[seams]*=.52
wood=np.array([87,63,44])[None,None,:]*shade[:,:,None]
wear=noise(w,h,160,1)
wood+=np.maximum(wear-.19,0)[:,:,None]*np.array([38,33,25])
woodim=Image.fromarray(np.uint8(np.clip(wood,0,255)))
wd=ImageDraw.Draw(woodim)
for _ in range(210):
    px=int(rng.integers(0,w));py=int(rng.integers(0,h))
    ln=int(rng.integers(6,85));dy=int(rng.integers(-14,15))
    wd.line((px,py,px+ln,py+dy),fill=(93,71,51),width=1)
woodim.save(OUT/"elm_color.png")
height = 130+grain*9+fine*3+large*18
height[seams]-=38
hi=Image.fromarray(np.uint8(np.clip(height,0,255)))
d=ImageDraw.Draw(hi)
for _ in range(290):
    px=int(rng.integers(0,w));py=int(rng.integers(0,h))
    ln=int(rng.integers(8,160))
    d.line((px,py,px+ln,py+int(rng.integers(-3,4))),fill=int(rng.integers(111,128)),width=1)
hi.save(OUT/"elm_height.png")
rough = 155+noise(w,h,60,40)+noise(w,h,7,9)+grain*12
save(rough,"elm_roughness.png")
manifest = {
    "source_files": ["assets/scans/cover.png","assets/scans/p06.png","assets/scans/p07.png"],
    "cover_crop_xyxy":[0,20,975,1400],
    "cover_aspect_ratio":975/1380,
    "physical_aspect_ratio":130/184,
    "page_crop_xyxy":[22,45,1452,2069],
    "operations":"Original scan glyphs retained. Uniform crops, scanner seam repair, paper tint and cinnabar mapping. No re-typesetting.",
    "seed":1976
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(manifest,ensure_ascii=False))
