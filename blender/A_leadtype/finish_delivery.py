"""Encode previews, inspect every PNG and decoded movie, produce review sheets."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import subprocess
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
RENDERS=ROOT.parents[1]/"assets"/"renders"
FFMPEG=Path(r"C:\Users\Admin\AppData\Local\Programs\Python\Python312\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe")
FONT=ImageFont.truetype("C:/Windows/Fonts/STSONG.TTF",23)
SMALL=ImageFont.truetype("C:/Windows/Fonts/STSONG.TTF",18)


def sheet(paths, destination, cols=4, width=480):
    height=width*9//16
    cellh=height+30
    rows=math.ceil(len(paths)/cols)
    im=Image.new("RGB",(cols*width,rows*cellh),(237,229,212))
    d=ImageDraw.Draw(im)
    for i,p in enumerate(paths):
        with Image.open(p) as frame:
            thumb=frame.resize((width,height),Image.Resampling.LANCZOS)
        x=(i%cols)*width;y=(i//cols)*cellh
        im.paste(thumb,(x,y))
        d.text((x+10,y+height+3),f"{p.stem}  |  {(int(p.stem)-1)/30:.2f} s",font=SMALL,fill=(28,26,23))
    destination.parent.mkdir(exist_ok=True,parents=True)
    im.save(destination)


def encode(out,count):
    command=[str(FFMPEG),"-hide_banner","-y","-framerate","30","-start_number","1",
             "-i",str(out/"frames"/"%04d.png"),"-frames:v",str(count),
             "-vf","scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p",
             "-c:v","libx264","-preset","slow","-crf","18","-pix_fmt","yuv420p",
             "-movflags","+faststart","-color_primaries","bt709","-color_trc","bt709",
             "-colorspace","bt709",str(out/"preview.mp4")]
    with (ROOT/f"{out.name}_encode.log").open("w",encoding="utf8") as f:
        subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,check=True)
    with (ROOT/f"{out.name}_decode.log").open("w",encoding="utf8") as f:
        subprocess.run([str(FFMPEG),"-hide_banner","-v","error","-xerror","-i",str(out/"preview.mp4"),
                        "-map","0:v:0","-f","null","-"],stdout=f,stderr=subprocess.STDOUT,check=True)


def inspect(out,count):
    frames=out/"frames"
    expected=[frames/f"{i:04d}.png" for i in range(1,count+1)]
    assert all(p.exists() for p in expected),"Missing frame"
    assert len(list(frames.glob("*.png")))==count,"Unexpected frame count"
    metrics=[];last=None;hashes=[]
    for i,p in enumerate(expected,1):
        with p.open("rb") as raw:
            header=raw.read(26)
        assert header[:8]==b"\x89PNG\r\n\x1a\n" and header[24:26]==bytes([8,2]),"PNG is not 8-bit RGB"
        with Image.open(p) as im:
            im.load()
            assert im.size==(1920,1080) and im.mode=="RGB",(p,im.size,im.mode)
            arr=np.asarray(im)
            small=cv2.resize(arr,(480,270),interpolation=cv2.INTER_AREA)
        gray=cv2.cvtColor(small,cv2.COLOR_RGB2GRAY)
        luminance=cv2.cvtColor(arr,cv2.COLOR_RGB2GRAY)
        record={"frame":i,"mean_luma":round(float(luminance.mean()),4),
                "black_pixel_percent":round(float((np.max(arr,axis=2)<=1).mean()*100),5),
                "white_pixel_percent":round(float((np.min(arr,axis=2)>=254).mean()*100),5)}
        if last is not None:
            record["mean_absolute_delta"]=round(float(np.abs(gray.astype(float)-last.astype(float)).mean()),5)
            flow=cv2.calcOpticalFlowFarneback(gray,last,None,.5,3,19,3,5,1.2,0)
            xx,yy=np.meshgrid(np.arange(480,dtype=np.float32),np.arange(270,dtype=np.float32))
            warped=cv2.remap(last,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
            record["flow_compensated_residual"]=round(float(np.abs(warped.astype(float)-gray.astype(float))[12:-12,12:-12].mean()),5)
        metrics.append(record);last=gray
        hashes.append({"path":str(p.relative_to(RENDERS)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
    cap=cv2.VideoCapture(str(out/"preview.mp4"))
    fps=cap.get(cv2.CAP_PROP_FPS);reported=cap.get(cv2.CAP_PROP_FRAME_COUNT)
    decoded=0;minpsnr=100.;maxdiff=0.
    while True:
        ok,frame=cap.read()
        if not ok:break
        decoded+=1
        if decoded in (1,count//2,count):
            original=cv2.imread(str(expected[decoded-1]))
            mse=float(np.mean((frame.astype(np.float32)-original.astype(np.float32))**2))
            psnr=10*math.log10(255**2/max(mse,1e-10))
            minpsnr=min(minpsnr,psnr)
            maxdiff=max(maxdiff,float(np.mean(np.abs(frame.astype(np.float32)-original.astype(np.float32)))))
    cap.release()
    assert decoded==count and fps==30,(decoded,fps)
    vals=np.array([m["flow_compensated_residual"] for m in metrics[1:]])
    med=float(np.median(vals));mad=float(np.median(abs(vals-med)))
    suspects=[metrics[i+1]["frame"] for i,v in enumerate(vals) if v>max(med+8*mad,3)]
    report={"shot":out.name,"frame_count":count,"resolution":[1920,1080],"png_mode":"RGB 8-bit",
            "fps":fps,"duration_seconds":decoded/fps,"video_reported_frames":reported,
            "decoded_frames":decoded,"full_ffmpeg_decode":"passed",
            "sampled_preview_psnr_min_db":round(minpsnr,3),"sampled_preview_abs_delta_max":round(maxdiff,4),
            "max_black_pixel_percent":max(m["black_pixel_percent"] for m in metrics),
            "max_white_pixel_percent":max(m["white_pixel_percent"] for m in metrics),
            "flow_residual_median":med,"flow_residual_max":float(vals.max()),
            "temporal_outlier_frames":suspects,"metrics":metrics}
    reopen_path=ROOT/"review"/"reopened_blend"/(out.name.replace("leadtype_","")+"_0001.png")
    if reopen_path.exists():
        original=cv2.imread(str(expected[0]))
        rerender=cv2.imread(str(reopen_path))
        assert rerender is not None and rerender.shape==original.shape
        difference=np.abs(rerender.astype(np.float32)-original.astype(np.float32))
        error=float(np.mean(difference**2))
        report["reopened_blend"]={"identical_pixels":bool(np.array_equal(original,rerender)),
            "mean_absolute_error":float(difference.mean()),"max_absolute_error":float(difference.max()),
            "psnr_db":round(10*math.log10(255**2/max(error,1e-10)),3)}
        assert report["reopened_blend"]["mean_absolute_error"]<1.0,"Editable project reopen mismatch"
    else:
        raise RuntimeError("Missing reopened .blend render")
    (ROOT/f"{out.name}_qa.json").write_text(json.dumps(report,indent=2),encoding="utf8")
    (ROOT/f"{out.name}_sha256.json").write_text(json.dumps(hashes,indent=2),encoding="utf8")
    contact_frames=[1]+list(range(30,count+1,30))
    sheet([frames/f"{f:04d}.png" for f in contact_frames],out/"contact.png")
    review=ROOT/"review"/"final_all_frames"/out.name
    for start in range(0,count,20):
        sheet(expected[start:start+20],review/f"frames_{start+1:04d}_{min(count,start+20):04d}.png",cols=5,width=384)
    print(json.dumps({k:v for k,v in report.items() if k!="metrics"},ensure_ascii=False,indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--shot",choices=["title","poli","both"],default="both")
    parser.add_argument("--manifest-only",action="store_true",help="Refresh final artifact hashes after reports, without re-encoding verified movies")
    args=parser.parse_args()
    for shot,count in [("title",210),("poli",180)]:
        if args.manifest_only:continue
        if args.shot not in ("both",shot):continue
        out=RENDERS/("leadtype_"+shot)
        encode(out,count);inspect(out,count)
    still=RENDERS/"leadtype_title"/"still_4k.png"
    if still.exists():
        with Image.open(still) as im:
            im.load();assert im.size==(3840,2160) and im.mode=="RGB"
    manifest_files=[ROOT/name for name in (
        "leadtype_title.blend","leadtype_poli.blend","build_leadtype.py","make_textures.py",
        "render_delivery.py","render_worker.py","finish_delivery.py","audit_scene.py",
        "BRIEF.md","FEEDBACK_1.md","FEEDBACK_2.md","HANDOFF.md",
        "build_poli_side.py","prepare_poli_textures.py","review_saved_poli.py",
        "queue_poli_review.py","audit_poli_side.py","write_report.py","review_delivery.html",
        "verify_title_preserved.py","title_preservation_audit.json","poli_side_composition.json",
        "poli_side_audit.json","browser_review.json","final_visual_review.json","REVIEW.md","REPORT.md",
        "title_render_stats.json","poli_render_stats.json","title_scene_audit.json",
        "leadtype_title_qa.json","leadtype_poli_qa.json","leadtype_title_sha256.json","leadtype_poli_sha256.json",
        "textures/glyph_meshes.json","textures/manifest.json","textures/poli_side/manifest.json")]
    manifest_files += [RENDERS/f"leadtype_{s}"/name for s in ("title","poli") for name in ("preview.mp4","contact.png")]
    manifest_files += [still]
    manifest={"blender":"5.2.1 LTS / 9e2066aef7ef","font":"STSONG.TTF",
              "font_sha256":hashlib.sha256(Path("C:/Windows/Fonts/STSONG.TTF").read_bytes()).hexdigest(),
              "artifacts":[{"path":str(p),"bytes":p.stat().st_size,
                            "sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in manifest_files if p.exists()]}
    (ROOT/"delivery_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf8")


if __name__=="__main__":main()
