"""Write the Chinese delivery report from measured final audit records."""
from pathlib import Path
import json,statistics,hashlib
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent.parent/"assets"/"renders"
a=json.loads((ROOT/"delivery_audit.json").read_text(encoding="utf-8"))
g=json.loads((ROOT/"geometry_audit.json").read_text(encoding="utf-8"))
stats={}
for s in ("desk_open","desk_close"):
    rows=[json.loads(x) for x in (ROOT/(s+"_final_timings.jsonl")).read_text(encoding="utf-8").splitlines()]
    ts=[x["seconds"] for x in rows]
    stats[s]={"count":len(ts),"mean":statistics.mean(ts),"min":min(ts),"max":max(ts),"sum":sum(ts)}
stillrows=[json.loads(x) for x in (ROOT/"desk_close_still_timings.jsonl").read_text(encoding="utf-8").splitlines()]
rows=[]
for s,n in (("desk_open",180),("desk_close",330)):
    q=a["shots"][s];t=stats[s]
    rows.append(f"| `{s}` | {n} | {n/30:.0f} 秒 | {t['mean']:.3f} 秒 | {t['min']:.3f}–{t['max']:.3f} 秒 | {t['sum']/60:.2f} 分钟 |")
text=f"""# 任务 C《书桌上的 1976 年版小册子》交付报告

## 完成情况

已按 `BRIEF.md`、`COMMON.md` 和导演阐述制作展开、合本两个镜头，交付 **510 张正式 PNG 帧、2 个 H.264 预览、2 张联系表、1 张 4K 静帧、1 个内嵌贴图的 Blender 工程和完整复现脚本**。

自审经过八轮；前四轮处理比例、材质、构图和铅笔支撑，导演审核意见 1 退回旧版氛围后，第五至七轮重新审核做旧、页曲、窗光与焦点，第八轮核验新版完整序列、视频和 4K 静帧。详细证据与结论见 `REVIEW.md`。旧版 145 张正式试渲染帧已全部移出交付目录。

## 正式产出

| 交付 | 路径 | 规格 |
|---|---|---|
| C2 展开序列 | `D:\\MAOGAI\\assets\\renders\\desk_open\\frames\\0001.png` 至 `0180.png` | 180 帧；1920×1080；RGB 8-bit；30fps |
| C2 预览 | `D:\\MAOGAI\\assets\\renders\\desk_open\\preview.mp4` | H.264，CRF 18，6 秒，无音轨 |
| C2 联系表 | `D:\\MAOGAI\\assets\\renders\\desk_open\\contact.png` | 首帧及每 30 帧抽样，共 7 张 |
| C1 合本序列 | `D:\\MAOGAI\\assets\\renders\\desk_close\\frames\\0001.png` 至 `0330.png` | 330 帧；1920×1080；RGB 8-bit；30fps |
| C1 预览 | `D:\\MAOGAI\\assets\\renders\\desk_close\\preview.mp4` | H.264，CRF 18，11 秒，无音轨 |
| C1 联系表 | `D:\\MAOGAI\\assets\\renders\\desk_close\\contact.png` | 首帧及每 30 帧抽样，共 12 张 |
| C1 4K 静帧 | `D:\\MAOGAI\\assets\\renders\\desk_close\\still_4k.png` | 第 330 帧；3840×2160；RGB 8-bit |
| 可编辑工程 | `D:\\MAOGAI\\blender\\C_desk\\C_desk.blend` | 两个独立 Scene：`desk_open`、`desk_close`；7 张贴图全部内嵌 |

## 制作细节

- 130×184mm 软封薄册；合本 14 张独立纸叶对应 28 页，约 2mm 厚；页边有微错落，封面微弯曲、圆角及稀疏纸纤维，两枚微锈铁制骑马钉。
- 封面使用原始 `cover.png`，裁切框 `(0,20,975,1400)`，宽高比严格等于 130:184；除去扫描黑边，并局部修补扫描细缝，保留题字、签名与原有印章，不重排字形。内页使用 p06/p07，裁切框 `(22,45,1452,2069)` 同样严格等比；原有印刷文字全部保留。处理参数见 `textures/manifest.json`。
- 书页使用密集曲面与真实纸厚，折缝下沉、两侧隆起，页面略有起伏，右前页角轻翘；旧纸带暖黄底、氧化页边及淡斑。朱砂按导演调色板作暖窗光成像补偿，避免偏成亮橙红。
- 140mm 六棱红漆铅笔，露木削口和黑色石墨芯、细微漆面磨损；基于真实纸页/桌面计算支撑，不靠目测摆放。
- 白色空心搪瓷缸，黑色卷口、两处微小掉瓷；没有添加文字或图案。稿纸只有格线。未使用可选眼镜或尘埃特效。
- 深色木桌包含非周期长纤维、树结、细划痕与不均匀粗糙度；低角度暖窗光来自左方，页脊有柔和阴影，远处桌面自然压暗。合本镜头色温仅轻微变暖。
- C2 从约 45° 俯角推向右页上半部；末帧标题投影高 {g['scenes']['desk_open']['final_text_projection']['title']['height_px']:.2f}px、日期高 {g['scenes']['desk_open']['final_text_projection']['date']['height_px']:.2f}px，焦点落在标题日期区域。
- 供原扫描切换对位：1080p 末帧标题范围约为 {tuple(round(v) for v in g['scenes']['desk_open']['final_text_projection']['title']['bounds_px'])}，日期范围约为 {tuple(round(v) for v in g['scenes']['desk_open']['final_text_projection']['date']['bounds_px'])}，坐标顺序为左、上、右、下；更精确数值见 `geometry_audit.json`。

## 渲染参数与实测耗时

- Blender 5.2.1 LTS；Cycles GPU；RTX 5060 Laptop；OptiX。
- 正式序列：128 最大采样、32 最低采样，自适应阈值 0.012，OptiX 降噪，固定种子 1976；7 次最大反弹，间接光钳制 3，开启 persistent data。
- 4K：144 最大采样，自适应阈值 0.009；直接以 3840×2160 重新渲染，没有放大 1080p。
- AgX / Medium High Contrast，曝光 +0.20EV；展开光圈从 f/9 平滑过渡至 f/7.1，焦点落在真实标题日期表面；合本从 f/8 至 f/4.5；30fps。
- 左窗光位于 (-0.34, 0.06, 0.22)m，0.55W，0.11×0.22m 矩形光源，65° spread；0.12W 极弱室内反射补光，暖灰环境强度 0.15。
- 预览编码：libx264，preset slow，CRF 18，yuv420p，BT.709 标签，faststart。
- 完整渲染按规范独占创建共享 GPU 锁，等待其他任务释放后开始；每帧更新时间，结束和失败均释放。

| 镜头 | 帧数 | 时长 | 平均每帧 | 单帧范围 | 实际渲染累计 |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

4K 静帧耗时 **{stillrows[-1]['seconds']:.3f} 秒**。耗时来自 `*_timings.jsonl`，含单帧渲染与 PNG 写入，不含 GPU 排队、建模、低清审核、废弃试渲染及视频编码。

## 技术核验

- 510 张 PNG 全部解码并检查连续编号、1920×1080、RGB 8-bit；两序列各帧哈希均记录，便于复查。
- 两个 MP4 经 FFmpeg 全片解码和 OpenCV 逐帧读取，均为 30fps，实际解码帧数分别 180/330。
- Edge 中两段视频均完整播放并重播到片尾，媒体尺寸与时长正确；累计呈现丢帧为展开 3/360、合本 2/660，文件解码帧数无缺失，详见 `browser_verification.json`。
- 4K 静帧已完整解码并核对尺寸和色彩通道。
- 几何有限、纸页正面法线正确、贴图内嵌、原件文字裁切框、铅笔无穿插均已检查，见 `geometry_audit.json`。
- 每帧检查黑白端裁切比例，并对相邻帧做光流对齐后的平坦区残差统计；详见 `delivery_audit.json`。时序统计是辅助证据，不能把运动边缘的残差等同于渲染闪烁。

## 已知边界

- 宽景内的原件正文小字是实物细节，部分低于导演通用规范的 28px；为了保留真实版式和完整书册构图，没有扩大或重排扫描文字。负责叙事阅读的 C2 末帧标题和日期均超过 28px。若需要逐字阅读整页，应由导演接入原扫描页。
- 物件按任务给定尺寸程序化复原；并非对实物进行测量扫描。磨损和木纹为程序化材质，封面痕迹来自原件。
- 本交付是供剪辑合成使用的无声 3D 镜头；原文转场、旁白、字幕和全片节拍由导演工程处理。
- 未调用 Tripo，未作 git commit，未修改原扫描及其他任务的已有文件。

## 复现

在 PowerShell 执行：

```powershell
python D:\\MAOGAI\\blender\\C_desk\\prepare_textures.py
& D:\\UE\\Tools\\blender.exe -b --python D:\\MAOGAI\\blender\\C_desk\\build_scene.py
python D:\\MAOGAI\\blender\\C_desk\\run_render.py review7_atmosphere
python D:\\MAOGAI\\blender\\C_desk\\run_render.py final
python D:\\MAOGAI\\blender\\C_desk\\run_render.py still desk_close
python D:\\MAOGAI\\blender\\C_desk\\finish_delivery.py
```

`final` 会跳过已有正式帧，支持中断续渲；修改场景后需先将旧帧移出相应 frames 目录，防止混入旧版本。`.blend` 已内嵌图像，可直接打开编辑或渲染；从头重建则需保留原工作区 `assets/scans`。
"""
(ROOT/"REPORT.md").write_text(text,encoding="utf-8")
(ROOT/"render_statistics.json").write_text(json.dumps(stats,indent=2),encoding="utf-8")
print("REPORT_WRITTEN")
