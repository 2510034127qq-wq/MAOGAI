"""输出 H.264 CRF18、每30帧联系表；逐张PNG及逐帧视频解码审核。

python finish_delivery.py
仅在全部帧渲染完毕后运行。检查失败时以非零状态退出。
"""
from pathlib import Path
import json
import subprocess
import hashlib
import statistics
import struct
import math
from datetime import datetime
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
RENDERS=ROOT.parents[1]/"assets"/"renders"
FFMPEG=Path(r"C:\Users\Admin\AppData\Local\Programs\Python\Python312\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe")
FONT=Path(r"C:\Windows\Fonts\STSONG.TTF")
SHOTS=[("steelyard_balance",300,"B1 杆秤平衡"),("steelyard_detail",150,"B2 秤星与麻绳微距")]


def png_header(path):
    with path.open("rb") as f:
        h=f.read(33)
    assert h[:8]==b"\x89PNG\r\n\x1a\n",str(path)
    w,hg,depth,color,*_=struct.unpack(">IIBBBBB",h[16:29])
    return {"width":w,"height":hg,"depth":depth,"color_type":color}


def contact(shot,count,title):
    folder=RENDERS/shot
    nums=[1]+list(range(30,count+1,30))
    cols=3;cw=640;ch=390
    rows=math.ceil(len(nums)/cols)
    sheet=Image.new("RGB",(cols*cw,54+rows*ch),"#EDE5D4")
    draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype(str(FONT),22)
    titlefont=ImageFont.truetype(str(FONT),28)
    draw.text((18,12),title+" | 1920×1080 · 30fps",font=titlefont,fill="#1C1A17")
    for i,n in enumerate(nums):
        im=Image.open(folder/"frames"/f"{n:04}.png").convert("RGB")
        im.thumbnail((cw,ch-30),Image.Resampling.LANCZOS)
        x=(i%cols)*cw;y=54+(i//cols)*ch
        sheet.paste(im,(x,y))
        draw.text((x+14,y+361),f"第 {n:04} 帧  ·  {(n-1)/30:.2f} 秒",font=font,fill="#1C1A17")
    sheet.save(folder/"contact.png")
    return nums


def encode(shot,count):
    folder=RENDERS/shot
    cmd=[str(FFMPEG),"-hide_banner","-y","-framerate","30","-start_number","1",
         "-i",str(folder/"frames"/"%04d.png"),"-frames:v",str(count),"-an",
         "-c:v","libx264","-preset","slow","-crf","18","-pix_fmt","yuv420p",
         "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709",
         "-movflags","+faststart",str(folder/"preview.mp4")]
    result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8",errors="replace")
    (ROOT/(shot+"_encode.log")).write_text(result.stdout,encoding="utf-8")
    assert result.returncode==0,result.stdout[-2000:]
    return cmd


def inspect_pngs(shot,count):
    folder=RENDERS/shot/"frames"
    files=sorted(folder.glob("*.png"))
    assert [p.name for p in files]==[f"{f:04}.png" for f in range(1,count+1)],"帧数/命名不连续"
    prev=None
    residuals=[]
    raw_deltas=[]
    background=[]
    hashes=[]
    duplicate_pairs=[]
    last_hash=None
    black=white=total=0
    for n,path in enumerate(files,1):
        h=png_header(path)
        assert h=={"width":1920,"height":1080,"depth":8,"color_type":2},(path,h)
        with Image.open(path) as image:
            image.load()
            a=np.asarray(image)
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        hashes.append({"frame":n,"sha256":digest})
        if digest==last_hash:duplicate_pairs.append(n)
        last_hash=digest
        background.append(a[20:130,20:240].mean(axis=(0,1)).tolist())
        black+=int(np.all(a<=2,axis=2).sum())
        white+=int(np.all(a>=253,axis=2).sum())
        total+=a.shape[0]*a.shape[1]
        small=cv2.resize(a,(480,270),interpolation=cv2.INTER_AREA)
        gray=cv2.cvtColor(small,cv2.COLOR_RGB2GRAY)
        if prev is not None:
            raw_deltas.append(float(np.mean(np.abs(gray.astype(float)-prev.astype(float)))))
            # Reverse flow remaps previous frame into the current frame.
            flow=cv2.calcOpticalFlowFarneback(gray,prev,None,.5,3,19,3,5,1.2,0)
            yy,xx=np.mgrid[:270,:480].astype(np.float32)
            warped=cv2.remap(prev,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_LINEAR)
            residuals.append(float(np.mean(np.abs(gray[8:-8,8:-8].astype(float)-warped[8:-8,8:-8].astype(float)))))
        prev=gray
        if n%30==0:print("PNG_QA",shot,n,flush=True)
    (ROOT/(shot+"_frame_hashes.json")).write_text(json.dumps(hashes,indent=2),encoding="utf-8")
    bg=np.array(background)
    return {
        "frames":len(files),"format":"PNG 8-bit RGB","resolution":[1920,1080],
        "all_decode":True,"continuous_numbering":True,
        "black_clipping_fraction":black/total,"white_clipping_fraction":white/total,
        "background_max_frame_mean_change_8bit":float(np.max(np.abs(np.diff(bg,axis=0)))),
        "raw_adjacent_mae_8bit":{"median":float(np.median(raw_deltas)),"max":max(raw_deltas)},
        "flow_compensated_mae_8bit":{"median":float(np.median(residuals)),"p95":float(np.percentile(residuals,95)),"max":max(residuals)},
        "identical_adjacent_frames":duplicate_pairs,
        "note":"运动补偿残差为辅助筛查，不等价于独立证明所有像素无闪烁；结尾镜头停留允许相同帧。"
    }


def inspect_video(shot,count):
    path=RENDERS/shot/"preview.mp4"
    cap=cv2.VideoCapture(str(path))
    assert cap.isOpened(),str(path)
    fps=cap.get(cv2.CAP_PROP_FPS)
    w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    decoded=0
    while True:
        ok,frame=cap.read()
        if not ok:break
        assert frame.shape[:2]==(1080,1920)
        decoded+=1
    cap.release()
    assert decoded==count and fps==30 and (w,h)==(1920,1080),(decoded,fps,w,h)
    result=subprocess.run([str(FFMPEG),"-v","error","-i",str(path),"-f","null","-"],
                          capture_output=True,text=True)
    assert result.returncode==0 and not result.stderr.strip(),result.stderr
    return {"frames_decoded":decoded,"fps":fps,"duration_seconds":decoded/fps,
            "resolution":[w,h],"codec":"H.264 / libx264","crf":18,
            "pixel_format":"yuv420p","ffmpeg_decode_errors":result.stderr,
            "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size}


def motion_check():
    m=json.loads((ROOT/"motion_audit.json").read_text(encoding="utf-8"))
    s=m["states"]
    angle=np.array([x["beam_angle_deg"] for x in s])
    weight=np.array([x["weight_x_m"] for x in s])
    assert np.max(np.abs(angle[:31]-12))<1e-8
    assert np.min(np.diff(weight))>=-1e-12
    assert np.max(np.abs(angle[250:]))==0
    assert abs(s[-1]["torque_residual_horizontal_Nm"])<1e-10
    assert 0.0>np.min(angle[200:250])>-.5
    return {
        "initial_hold_degrees":float(angle[0]),"hold_0_30":True,
        "monotonic_weight_slide":True,"final_weight_x_m":float(weight[-1]),
        "settling_overshoot_degrees":float(np.min(angle[200:250])),
        "settling_return_degrees":float(np.max(angle[210:250])),
        "final_250_300_horizontal":True,
        "horizontal_torque_residual_Nm":s[-1]["torque_residual_horizontal_Nm"],
        "max_pan_swing_degrees":max(abs(x["pan_swing_deg"]) for x in s),
        "max_weight_swing_degrees":max(abs(x["weight_swing_deg"]) for x in s),
        "load_to_weight_mass_ratio":m["mass_load_kg"]/m["mass_weight_kg"],
        "physical_scope":m["description_zh"]
    }


def main():
    out={"checked_at":datetime.now().isoformat(),"shots":{}}
    current_sources={
        "blend_sha256":hashlib.sha256((ROOT/"steelyard.blend").read_bytes()).hexdigest(),
        "build_sha256":hashlib.sha256((ROOT/"build_steelyard.py").read_bytes()).hexdigest(),
        "renderer_sha256":hashlib.sha256((ROOT/"render_steelyard.py").read_bytes()).hexdigest()}
    for shot,count,title in SHOTS:
        source=json.loads((RENDERS/shot/"render_source.json").read_text(encoding="utf-8"))
        for key,value in current_sources.items():
            assert source[key]==value,("最终帧来源不一致",shot,key)
        stats=inspect_pngs(shot,count)
        cmd=encode(shot,count)
        samples=contact(shot,count,title)
        video=inspect_video(shot,count)
        out["shots"][shot]={"sequence":stats,"video":video,"contact_frames":samples,"encode_command":cmd,"source":source}
    still=RENDERS/"steelyard_balance"/"still_4k.png"
    header=png_header(still)
    assert header=={"width":3840,"height":2160,"depth":8,"color_type":2}
    with Image.open(still) as im:im.load()
    out["still_4k"]={"path":str(still),**header,"sha256":hashlib.sha256(still.read_bytes()).hexdigest()}
    out["motion"]=motion_check()
    times=[json.loads(x) for x in (ROOT/"render_times.jsonl").read_text(encoding="utf-8").splitlines()]
    out["render_times"]={}
    for shot,_,_ in SHOTS:
        filtered=[x["seconds"] for x in times if x["mode"]=="final" and f"\\{shot}\\frames\\" in x["path"]]
        out["render_times"][shot]={"count":len(filtered),"mean_seconds":statistics.mean(filtered),
                                  "median_seconds":statistics.median(filtered),"min_seconds":min(filtered),
                                  "max_seconds":max(filtered),"total_seconds":sum(filtered)}
    stilltimes=[x["seconds"] for x in times if x["path"].endswith("still_4k.png") and x["mode"] in ("final","still")]
    out["render_times"]["still_4k_seconds"]=stilltimes[-1]
    out["all_technical_checks_passed"]=True
    (ROOT/"delivery_audit.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print("DELIVERY_AUDIT_PASSED",json.dumps(out["render_times"],ensure_ascii=False),flush=True)


if __name__=="__main__":
    main()
