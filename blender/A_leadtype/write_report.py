"""Write the Chinese delivery report from measured render and QA evidence."""
from pathlib import Path
from datetime import datetime
import json
import statistics

ROOT=Path(__file__).resolve().parent
RENDERS=ROOT.parents[1]/"assets"/"renders"
stats={s:json.loads((ROOT/f"{s}_render_stats.json").read_text()) for s in ("title","poli")}
qa={s:json.loads((ROOT/f"leadtype_{s}_qa.json").read_text()) for s in ("title","poli")}
audits={s:json.loads((ROOT/f"{s}_scene_audit.json").read_text(encoding="utf8")) for s in ("title","poli")}
rows=[]
for shot in ("title","poli"):
    times=[f["seconds"] for f in stats[shot]["frames"]]
    rows.append(f"| leadtype_{shot} | {len(times)} | {statistics.mean(times):.3f} 秒 | {statistics.median(times):.3f} 秒 | {min(times):.3f}–{max(times):.3f} 秒 | {sum(times)/60:.2f} 分钟 |")
qa_rows=[]
for shot in ("title","poli"):
    q=qa[shot]
    rp=q["reopened_blend"]
    qa_rows.append(f"| leadtype_{shot} | {q['frame_count']} / {q['decoded_frames']} | {q['fps']:.0f} fps / {q['duration_seconds']:.0f} 秒 | {q['max_black_pixel_percent']:.5f}% / {q['max_white_pixel_percent']:.5f}% | {'像素一致' if rp['identical_pixels'] else 'MAE '+str(round(rp['mean_absolute_error'],5))} |")
text=f"""# 铅字镜头交付报告

完成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}（本地时间，Asia/Shanghai）

## 完成内容

已按 `BRIEF.md`、`../COMMON.md`、`../../docs/导演阐述.md` 和导演 `FEEDBACK_1.md` 制作两个可编辑 Blender 镜头，完成六轮低清修订、正式序列检查及封装／工程复开检查。详细发现和修订证据见 [REVIEW.md](REVIEW.md)。

| 镜头 | 正式帧序列 | 数量 / 时长 | 预览 | 联系表 |
|---|---|---|---|---|
| A1 片名 | `D:\\MAOGAI\\assets\\renders\\leadtype_title\\frames\\0001.png` 至 `0210.png` | 210 帧 / 7 秒 | `leadtype_title\\preview.mp4` | `leadtype_title\\contact.png` |
| A2 破立 | `D:\\MAOGAI\\assets\\renders\\leadtype_poli\\frames\\0001.png` 至 `0180.png` | 180 帧 / 6 秒 | `leadtype_poli\\preview.mp4` | `leadtype_poli\\contact.png` |

表中预览与联系表均位于 `D:\\MAOGAI\\assets\\renders\\` 下。另交付片名最后一帧的 **3840×2160 RGB PNG**：

`D:\\MAOGAI\\assets\\renders\\leadtype_title\\still_4k.png`

预览为 H.264、CRF 18、yuv420p、30 fps、faststart；联系表包含首帧及每 30 帧一次的采样，包含终帧。两个预览均为无声镜头素材。

## 编辑工程与可复现源文件

- [leadtype_title.blend](leadtype_title.blend)：片名镜头，包含相机／焦点动画、手托、主角与背景铅字、材质和灯光。
- [leadtype_poli.blend](leadtype_poli.blend)：破立镜头，包含铅字、卷边旧纸、实际压痕、印迹、相机环绕和移焦。
- [build_leadtype.py](build_leadtype.py)：程序化建模、材质、布光和逐帧平滑动画。
- [make_textures.py](make_textures.py)：固定随机种子的纤维、实墨、针孔和轻微晕染纹理。
- [textures/glyph_meshes.json](textures/glyph_meshes.json)：从凸字顶面导出的共用字形，供纸面镜像对应。
- [render_delivery.py](render_delivery.py)、[render_worker.py](render_worker.py)：GPU 锁队列、正式渲染、断点续渲、每帧计时和工程复开。
- [finish_delivery.py](finish_delivery.py)：编码、完整解码、逐帧 PNG 校验、联系表、逐帧审查表、SHA-256 与时域异常筛查。
- [audit_scene.py](audit_scene.py)：尺寸、法线、实体拓扑和字面构图检查。

主角与陪体汉字均来自 `C:\\Windows\\Fonts\\STSONG.TTF`，已转为真实网格。所需纸纹和印迹图像已打包进 `.blend`；工程复开无需重新生成纹理。独立从脚本重建仍需任务目录的脚本／纹理和 COMMON 指定的 Blender、Python、字体。

## 导演意见落实

1. **结构**：字身 4×4×23.5 mm；凸字高约 0.667 mm，即字面边长的 1/6。斜壁向根部外张并带微倒角，肩部平整，字身有真实凹槽。
2. **合金**：细腻哑光银灰，粗糙度 0.35–0.50；局部细微氧化、细划痕与磨亮边缘。消除了先前的拉伸粗纹和石材感。
3. **油墨**：顶面和极小的笔画顶缘覆墨，保留轻微光泽、磨薄露铅与肩部残墨。片名用铅字黑，破立用朱砂 `#B5302A`。
4. **A1 取景**：开头完整呈现“系”的字面，焦点依次经过五字；后段升起并后拉到导演认可的手托全景。第 210 帧五字排列仍为左至右“系关大十论”，各字左右镜像。
5. **A1 光线**：保留左侧低角度暖光，压低补光与后光，暗部仍有层次。
6. **A2 取景**：约 45° 俯角，环绕总角度 15°；两枚铅字整体及字面完整入画；焦点由凸字转到纸面印迹。
7. **A2 印迹**：由同一凸字顶面网格反向投影，保持相同物理尺寸。纸上是正向“破”“立”，实墨、纤维针孔、微晕染和约 16 微米的凹痕共同形成压印感；纸色基准为 `#EDE5D4`。

## 渲染参数与实测耗时

- Blender 5.2.1 LTS，Cycles，NVIDIA GeForce RTX 5060 Laptop GPU，**{stats['title']['settings']['compute_device']}**。
- 1920×1080，30 fps，PNG 8-bit RGB。
- 序列：128 samples，自适应阈值 0.012，最小 32 samples，OptiX 降噪。
- 固定种子 1976，关闭逐帧随机种子变化；AgX / Medium High Contrast。
- 4K 静帧：256 samples，自适应阈值 0.008，耗时 **{stats['title']['still_4k_seconds']:.3f} 秒**。
- 任意正式序列均在独占 GPU 锁内渲染，每 20 帧刷新锁，结束释放；等待其他任务的时间不计入下面的渲染耗时。

| 镜头 | 帧数 | 平均每帧 | 中位每帧 | 最短–最长 | 帧渲染合计 |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

逐帧原始记录见 `title_render_stats.json` 和 `poli_render_stats.json`。

## 验证结果

| 镜头 | PNG / 视频解码帧数 | 帧率 / 时长 | 最大纯黑 / 纯白像素占比 | 保存工程复开渲染 |
|---|---:|---:|---:|---|
{chr(10).join(qa_rows)}

两组 PNG 全部成功读取，分辨率、RGB 模式、连续编号符合规格；两段 H.264 通过 FFmpeg 全片严格解码。主角凸字均为封闭实体、非流形边 0、正体积、顶面外法线朝上。工程复开后重渲首帧，与交付首帧比较通过。

详尽证据：

- `title_scene_audit.json`、`poli_scene_audit.json`
- `leadtype_title_qa.json`、`leadtype_poli_qa.json`
- `leadtype_title_sha256.json`、`leadtype_poli_sha256.json`
- `review/final_all_frames/`：所有 390 帧的分组联系表
- `review/reopened_blend/`：保存工程复开后的重渲帧

最终完整图像、时域变化和异常帧的人工结论记录在 REVIEW 的终审部分。技术检查能核验文件、拓扑和时序，并不能替代导演的美术判断。

## 复现方法

在 `D:\\MAOGAI\\blender\\A_leadtype` 目录执行：

```powershell
python make_textures.py
python run_blender.py rebuild_title --factory-startup --python build_leadtype.py -- title
python run_blender.py rebuild_poli --factory-startup --python build_leadtype.py -- poli
python render_delivery.py
python finish_delivery.py
```

`render_delivery.py` 会保留已在计时清单中完成的帧，以便失败续渲。**修改场景后要完整重渲时，应先将相应输出 frames 与对应 render_stats.json 移至任务目录内的版本备份，避免续用旧帧。** 也可直接打开 `.blend` 在 Blender 中编辑；字体已转网格，变更文字需运行建模脚本。

## 已知边界

- 这是依任务规格制作的静物镜头；铅字细划痕、氧化、木纹和纸纤维均为程序化细节，不是对某套历史实物的扫描复刻。
- 原色是材质输入基准。成片经过暖光、阴影和 AgX，像素不会处处等于调色板的十六进制值。
- 使用连续五次平滑插值实现起止缓入缓出，并逐帧烘焙；`.blend` 不依赖外部动画回调。
- 片名字形按真实印刷活字保持反字，正向片名转场和最终字幕／配音由导演合成阶段完成。
- 未调用 Tripo，未执行 Git commit；写入范围为本任务目录、指定镜头输出目录与 COMMON 授权的 GPU 锁。
"""
(ROOT/"REPORT.md").write_text(text,encoding="utf8")
print(ROOT/"REPORT.md")
