"""Dedicated A2 paper maps; unchanged A1 resources remain reproducible."""
from pathlib import Path
import json, math
import numpy as np

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'textures'/'poli_side'
W,H=4096,4096
PW,PH=14.0,16.0
CY=1.0
ANGLE=-10.0
STAMP_Y=-1.3

def main():
    from PIL import Image, ImageDraw, ImageFilter
    OUT.mkdir(exist_ok=True,parents=True)
    rng=np.random.default_rng(1976)
    def noise(scale):
        a=rng.random((max(2,H//scale),max(2,W//scale)))
        return np.asarray(Image.fromarray(np.uint8(a*255)).resize((W,H),Image.Resampling.BICUBIC),dtype=np.float32)/255
    coarse=noise(180);medium=noise(22);fine=noise(3)
    grain=rng.random((H,W),dtype=np.float32)
    fibre=Image.new('L',(W,H),128);d=ImageDraw.Draw(fibre)
    for _ in range(52000):
        x,y=rng.integers(0,W),rng.integers(0,H)
        length=rng.uniform(3,25);slope=rng.uniform(-.5,.5)
        d.line((x,y,x+length,y+slope*length),fill=int(rng.integers(70,180)),width=1)
    fibres=np.asarray(fibre.filter(ImageFilter.GaussianBlur(.35)),dtype=np.float32)/255
    texture=.35*coarse+.22*medium+.13*fine+.10*grain+.20*fibres
    Image.fromarray(np.uint8(texture*255)).save(OUT/'paper_fibre.png')
    outlines=json.loads((ROOT/'textures'/'glyph_meshes.json').read_text(encoding='utf8'))
    mask=Image.new('L',(W,H),0);d=ImageDraw.Draw(mask)
    angle=math.radians(ANGLE);c,s=math.cos(angle),math.sin(angle)
    centres=[]
    for ch,x in [('破',-1.0),('立',1.0)]:
        points=[]
        for mx,my in outlines[ch]['points']:
            # One reflection reverses the mirrored printing face into normal text.
            gx=x-mx;gy=STAMP_Y+my
            xx=gx*c-gy*s;yy=gx*s+gy*c
            points.append(((xx/PW+.5)*W,(.5-(yy-CY)/PH)*H))
        for tri in outlines[ch]['triangles']:d.polygon([points[i] for i in tri],fill=255)
        centres.append([x*c-STAMP_Y*s,x*s+STAMP_Y*c])
    mask.save(OUT/'stamp_height.png')
    crisp=np.asarray(mask,dtype=np.float32)/255
    bleed=np.asarray(mask.filter(ImageFilter.GaussianBlur(.65)),dtype=np.float32)/255
    spread=np.asarray(mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(.8)),dtype=np.float32)/255
    # Dense vermilion with slight pressure variation and fibre-sized voids.
    pressure=.988+.010*noise(34)+.002*fine
    pinhole=np.clip((grain-.989)*25,0,.28)
    alpha=np.maximum(crisp*(pressure-pinhole),spread*.22+bleed*.18)
    Image.fromarray(np.uint8(np.clip(alpha,0,1)*255)).save(OUT/'stamp_alpha.png')
    (OUT/'manifest.json').write_text(json.dumps({'font':'STSONG.TTF','seed':1976,
        'resolution':[W,H],'paper_size_units':[PW,PH],'paper_centre':[0,CY],
        'stamp_centres':centres,'stamp_local_y':STAMP_Y,'rotation_degrees':ANGLE,
        'source':'../glyph_meshes.json','ink_srgb':'#B5302A','paper_srgb':'#EDE5D4',
        'physical_unit_metres':.004},ensure_ascii=False,indent=2),encoding='utf8')

if __name__=='__main__':main()
