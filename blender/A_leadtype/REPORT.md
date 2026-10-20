# 铅字镜头交付报告

完成时间：2026-10-20 16:05:37（本地时间，Asia/Shanghai）

## 完成内容

已按 `HANDOFF.md`、`BRIEF.md`、`../COMMON.md`、`../../docs/导演阐述.md` 和两次导演反馈完成全部交付。A1 保留导演批准的 round6 / readability 造型、灯光与镜头；A2 以 `FEEDBACK_2.md` 为准改为侧卧，并完成 round7 起的低清复核、正式序列检查、封装与工程复开验证。详细证据见 [REVIEW.md](REVIEW.md)。

| 镜头 | 正式帧序列 | 数量 / 时长 | 预览 | 联系表 |
|---|---|---|---|---|
| A1 片名 | `D:\MAOGAI\assets\renders\leadtype_title\frames\0001.png` 至 `0210.png` | 210 帧 / 7 秒 | `leadtype_title\preview.mp4` | `leadtype_title\contact.png` |
| A2 破立 | `D:\MAOGAI\assets\renders\leadtype_poli\frames\0001.png` 至 `0180.png` | 180 帧 / 6 秒 | `leadtype_poli\preview.mp4` | `leadtype_poli\contact.png` |

表中预览与联系表均位于 `D:\MAOGAI\assets\renders\` 下。另交付片名最后一帧的 **3840×2160 RGB PNG**：

`D:\MAOGAI\assets\renders\leadtype_title\still_4k.png`

预览为 H.264、CRF 18、yuv420p、30 fps、faststart；联系表包含首帧及每 30 帧一次的采样，包含终帧。两个预览均为无声镜头素材。

## 编辑工程与可复现源文件

- [leadtype_title.blend](leadtype_title.blend)：片名镜头，包含相机／焦点动画、手托、主角与背景铅字、材质和灯光。
- [leadtype_poli.blend](leadtype_poli.blend)：破立镜头，包含侧卧铅字、旧纸、实际压痕、印迹、轻微推近／横移和移焦。
- [build_leadtype.py](build_leadtype.py)：程序化建模、材质、布光和逐帧平滑动画。
- [make_textures.py](make_textures.py)：固定随机种子的纤维、实墨、针孔和轻微晕染纹理。
- [build_poli_side.py](build_poli_side.py)、[prepare_poli_textures.py](prepare_poli_textures.py)：A2 最新版重建入口与独立纸张纹理；不要用旧 `build_leadtype.py -- poli` 重建终版 A2。
- [textures/glyph_meshes.json](textures/glyph_meshes.json)：从凸字顶面导出的共用字形，供纸面镜像对应。
- [render_delivery.py](render_delivery.py)、[render_worker.py](render_worker.py)：GPU 锁队列、正式渲染、断点续渲、每帧计时和工程复开。
- [finish_delivery.py](finish_delivery.py)：编码、完整解码、逐帧 PNG 校验、联系表、逐帧审查表、SHA-256 与时域异常筛查。
- [audit_scene.py](audit_scene.py)：尺寸、法线、实体拓扑和字面构图检查。
- [audit_poli_side.py](audit_poli_side.py)：A2 全部 180 帧的完整入画、接触关系、移焦与纸面覆盖检查。
- [review_delivery.html](review_delivery.html)：本地复核页面，可播放预览、逐帧查看 PNG 和显示下三分之一参考线。

主角与陪体汉字均来自 `C:\Windows\Fonts\STSONG.TTF`，已转为真实网格。所需纸纹和印迹图像已打包进 `.blend`；工程复开无需重新生成纹理。独立从脚本重建仍需任务目录的脚本／纹理和 COMMON 指定的 Blender、Python、字体。

## 导演意见落实

1. **结构**：字身 4×4×23.5 mm；凸字高约 0.667 mm，即字面边长的 1/6。斜壁向根部外张并带微倒角，肩部平整，字身有真实凹槽。
2. **合金**：细腻哑光银灰，粗糙度 0.35–0.50；局部细微氧化、细划痕与磨亮边缘。消除了先前的拉伸粗纹和石材感。
3. **油墨**：顶面和极小的笔画顶缘覆墨，保留轻微光泽、磨薄露铅与肩部残墨。片名用铅字黑，破立用朱砂 `#B5302A`。
4. **A1 取景**：开头完整呈现“系”的字面，焦点依次经过五字；后段升起并后拉到导演认可的手托全景。第 210 帧五字排列仍为左至右“系关大十论”，各字左右镜像。
5. **A1 光线**：保留左侧低角度暖光，压低补光与后光，暗部仍有层次。
6. **A2 取景**：两枚铅字平行侧卧，字身间净距约 4 mm，字面朝左前方。约 30° 俯角，只有轻微推近和横移。第 1–60 帧聚焦字面，第 61–138 帧平滑移焦，第 139–180 帧停在正向印迹；底部 360 像素为安静纸面，供后期两行释义使用。
7. **A2 印迹**：由同一凸字顶面网格反向投影，保持相同物理尺寸。纸上是正向“破”“立”，实墨、纤维针孔、微晕染和约 16 微米的凹痕共同形成压印感；纸色基准为 `#EDE5D4`。

## 渲染参数与实测耗时

- Blender 5.2.1 LTS，Cycles，NVIDIA GeForce RTX 5060 Laptop GPU，**OPTIX**。
- 1920×1080，30 fps，PNG 8-bit RGB。
- 序列：128 samples，自适应阈值 0.012，最小 32 samples，OptiX 降噪。
- 固定种子 1976，关闭逐帧随机种子变化；AgX / Medium High Contrast。
- 4K 静帧：256 samples，自适应阈值 0.008，耗时 **38.946 秒**。
- 任意正式序列均在独占 GPU 锁内渲染，每 20 帧刷新锁，结束释放；等待其他任务的时间不计入下面的渲染耗时。

| 镜头 | 帧数 | 平均每帧 | 中位每帧 | 最短–最长 | 帧渲染合计 |
|---|---:|---:|---:|---:|---:|
| leadtype_title | 210 | 6.260 秒 | 6.303 秒 | 5.151–7.130 秒 | 21.91 分钟 |
| leadtype_poli | 180 | 4.684 秒 | 4.683 秒 | 3.980–5.210 秒 | 14.05 分钟 |

逐帧原始记录见 `title_render_stats.json` 和 `poli_render_stats.json`。

## 验证结果

| 镜头 | PNG / 视频解码帧数 | 帧率 / 时长 | 最大近黑 / 近白像素占比 | 保存工程复开渲染 |
|---|---:|---:|---:|---|
| leadtype_title | 210 / 210 | 30 fps / 7 秒 | 2.69575% / 0.00000% | MAE 0.00228 |
| leadtype_poli | 180 / 180 | 30 fps / 6 秒 | 0.00000% / 0.00000% | MAE 0.00241 |

两组 PNG 全部成功读取，分辨率、RGB 模式、连续编号符合规格；两段 H.264 通过 FFmpeg 全片严格解码。主角凸字均为封闭实体、非流形边 0、正体积、外法线正确。A2 全 180 帧的完整字身与字面都在画内。工程复开后重渲首帧，与交付首帧比较通过。

A1 交接快照与正式工程的几何、材质、灯光及 210 帧相机动画比对一致，见 `title_preservation_audit.json`。A2 字身底部与纸面高度的最大误差为 0.000001039 mm，属于浮点计算精度。

详尽证据：

- `title_scene_audit.json`、`poli_side_audit.json`、`poli_side_composition.json`（旧 `poli_scene_audit.json` 属于已被退回的站立版，仅留档）
- `leadtype_title_qa.json`、`leadtype_poli_qa.json`
- `leadtype_title_sha256.json`、`leadtype_poli_sha256.json`
- `review/final_all_frames/`：所有 390 帧的分组联系表
- `review/reopened_blend/`：保存工程复开后的重渲帧
- `final_visual_review.json`：本轮人工图像审核与连续播放记录

最终完整图像、时域变化和异常帧的人工结论记录在 REVIEW 的终审部分。技术检查能核验文件、拓扑和时序，并不能替代导演的美术判断。

## 复现方法

在 `D:\MAOGAI\blender\A_leadtype` 目录执行：

```powershell
python make_textures.py
python run_blender.py rebuild_title --factory-startup --python build_leadtype.py -- title
python run_blender.py rebuild_poli --factory-startup --python build_poli_side.py
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
