"""Create H.264 previews/contact sheets, then audit every PNG and video frame."""
from pathlib import Path
import subprocess,json,hashlib,time
import numpy as np
import cv2
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent.parent/"assets"/"renders"
FFMPEG=r"C:\Users\Admin\AppData\Local\Programs\Python\Python312\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
FONT=ImageFont.truetype(r"C:\Windows\Fonts\STSONG.TTF",25)
def run(cmd,log):
    p=subprocess.run(cmd,capture_output=True,text=True,encoding="utf-8",errors="replace")
    log.write_text(p.stdout+"\n"+p.stderr,encoding="utf-8")
    if p.returncode:raise RuntimeError(str(log))
    return p

report={"shots":{},"created":time.strftime("%Y-%m-%d %H:%M:%S")}
for shot,count in [("desk_open",180),("desk_close",330)]:
    out=BASE/shot;frames=out/"frames"
    paths=sorted(frames.glob("*.png"))
    assert [p.name for p in paths]==[f"{i:04}.png" for i in range(1,count+1)],"Sequence has missing or extra frame"
    run([FFMPEG,"-y","-framerate","30","-start_number","1","-i",str(frames/"%04d.png"),
         "-frames:v",str(count),"-c:v","libx264","-preset","slow","-crf","18","-pix_fmt","yuv420p",
         "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709",
         "-movflags","+faststart","-an",str(out/"preview.mp4")],ROOT/(shot+"_encode.log"))
    run([FFMPEG,"-v","error","-i",str(out/"preview.mp4"),"-f","null","-"],ROOT/(shot+"_decode.log"))
    selected=[1]+list(range(30,count+1,30))
    cols=3;tw,th=640,360;label=36;rows=(len(selected)+cols-1)//cols
    contact=Image.new("RGB",(cols*tw,rows*(th+label)),(237,229,212));draw=ImageDraw.Draw(contact)
    for j,fr in enumerate(selected):
        x=(j%cols)*tw;y=(j//cols)*(th+label)
        im=Image.open(frames/f"{fr:04}.png");im.thumbnail((tw,th),Image.Resampling.LANCZOS)
        contact.paste(im,(x,y))
        draw.text((x+12,y+th+5),f"{shot}  |  {fr:04}  |  {(fr-1)/30:.2f} s",font=FONT,fill=(28,26,23))
    contact.save(out/"contact.png")

    records=[];previous=None;hashes=[];diffmeans=[]
    for i,p in enumerate(paths):
        with Image.open(p) as im:
            assert im.size==(1920,1080) and im.mode=="RGB",(p,im.size,im.mode)
            im.load()
            small=np.asarray(im.resize((480,270),Image.Resampling.BOX))
            a=np.asarray(im)
            clipped_white=float(np.mean(np.all(a>=250,axis=2)))
            clipped_black=float(np.mean(np.all(a<=4,axis=2)))
        gray=cv2.cvtColor(small,cv2.COLOR_RGB2GRAY)
        rec={"frame":i+1,"mean_luma":float(gray.mean()),"clipped_white_fraction":clipped_white,"clipped_black_fraction":clipped_black}
        if previous is not None:
            # Optical flow aligns camera motion; flat areas expose shading/noise jumps.
            flow=cv2.calcOpticalFlowFarneback(previous,gray,None,.5,3,19,3,5,1.2,0)
            yy,xx=np.mgrid[:270,:480].astype(np.float32)
            warped=cv2.remap(gray,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_LINEAR)
            diff=np.abs(warped.astype(float)-previous.astype(float))
            grad=cv2.magnitude(cv2.Sobel(previous,cv2.CV_32F,1,0),cv2.Sobel(previous,cv2.CV_32F,0,1))
            valid=(grad<12)&(xx>8)&(xx<472)&(yy>8)&(yy<262)
            rec["motion_compensated_flat_mae_8bit"]=float(diff[valid].mean())
            rec["motion_compensated_flat_p95_8bit"]=float(np.percentile(diff[valid],95))
            diffmeans.append(rec["motion_compensated_flat_mae_8bit"])
        hashes.append(hashlib.sha256(p.read_bytes()).hexdigest())
        records.append(rec);previous=gray
    cap=cv2.VideoCapture(str(out/"preview.mp4"))
    info={"width":int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),"height":int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
          "fps":cap.get(cv2.CAP_PROP_FPS),"declared_frames":int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}
    actual=0
    while True:
        ok,frame=cap.read()
        if not ok:break
        assert frame.shape[:2]==(1080,1920)
        actual+=1
    cap.release()
    assert actual==count and info["fps"]==30,info
    info["decoded_frames"]=actual;info["duration_seconds"]=actual/info["fps"]
    summary={
        "frame_count":count,"all_png_rgb_8bit_1920x1080":True,
        "unique_frame_hashes":len(set(hashes)),"video":info,
        "max_white_clipping_fraction":max(x["clipped_white_fraction"] for x in records),
        "max_black_clipping_fraction":max(x["clipped_black_fraction"] for x in records),
        "flat_motion_compensated_mae_max":max(diffmeans),"flat_motion_compensated_mae_median":float(np.median(diffmeans)),
        "contact_frames":selected,"ffmpeg_full_decode_passed":True,
        "frame_audit":records,
    }
    (ROOT/(shot+"_frame_hashes.json")).write_text(json.dumps(hashes),encoding="utf-8")
    report["shots"][shot]=summary
    print("DELIVERY_VERIFIED",shot,{k:v for k,v in summary.items() if k!="frame_audit"},flush=True)
still=BASE/"desk_close"/"still_4k.png"
with Image.open(still) as im:
    im.load();assert im.size==(3840,2160) and im.mode=="RGB"
report["still_4k"]={"path":str(still),"size":[3840,2160],"mode":"RGB","sha256":hashlib.sha256(still.read_bytes()).hexdigest()}
report["pass"]=True
(ROOT/"delivery_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("ALL_DELIVERY_CHECKS_PASS")
