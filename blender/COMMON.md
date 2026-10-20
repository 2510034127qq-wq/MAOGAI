# 执行通用规范（所有 codex 任务必读）

你是这部研读微视频的 3D/美术执行。导演阐述见 `D:\MAOGAI\docs\导演阐述.md`（必须先读“视觉体系”一节）。
你的产出会被导演逐帧审核，不合格会被退回返工，所以请自己先严格审核。

## 环境
- 工作根目录：`D:\MAOGAI`。只在你的任务目录（`blender\<任务名>\`）和 `assets\renders\<镜头名>\`（或 `assets\img\`）里写文件。
- Blender：`D:\UE\Tools\blender.exe`（5.2.1 LTS）。用 bpy 脚本**程序化**建模、布光、动画，脚本保存在任务目录，保证可复现；最后另存 `.blend`。
- GPU：RTX 5060 Laptop 8GB。渲染用 Cycles + OptiX（若 OptiX 不可用则 CUDA），开启 OptiX/OIDN 降噪，自适应采样。
- ffmpeg：`C:\Users\Admin\AppData\Local\Programs\Python\Python312\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe`
- Python 3.12（有 numpy、Pillow、opencv）。
- 字体（中文必须用这些）：`C:\Windows\Fonts\STSONG.TTF`（华文宋体，铅字首选）、`C:\Windows\Fonts\Source Han Serif SC Heavy (TrueType).ttf`、`C:\Windows\Fonts\STKAITI.TTF`。
- 1976 年版扫描：`D:\MAOGAI\assets\scans\cover.png`（彩色封面，右侧和底部有黑色扫描边，需要裁掉）、`pXX.png`（正文页灰度，1474×2240）。

## GPU 锁（必须遵守，多个任务共用一块 GPU）
任何超过 20 帧的渲染，开始前必须获取锁：以独占方式创建 `D:\MAOGAI\assets\renders\.gpu.lock`（内容写任务名和时间）。
若文件已存在，每 60 秒检查一次，直到它被删除；若它超过 90 分钟没有更新修改时间，视为失效可以删除。
渲染过程中每完成约 20 帧 touch 一次锁文件；渲染结束（含失败）立即删除。低分辨率测试静帧（≤ 960×540、≤ 5 帧）不需要锁。

## 输出规格
- 1920×1080，30fps，PNG 8-bit RGB，帧序列存 `D:\MAOGAI\assets\renders\<镜头名>\frames\0001.png` 起。
- 每个镜头另出：`preview.mp4`（H.264 CRF 18）和 `contact.png`（每 30 帧取一张拼成的联系表）。
- 色彩管理用 AgX（或 Filmic），整体偏暖、低饱和；画面颜色必须落在导演阐述的调色板内。

## 自审流程（至少 3 轮）
1. 先出低分辨率关键帧（首、中、尾），用看图工具亲自查看。
2. 对照下面清单逐条自查并修改：
   - 结构真实：比例、厚度、倒角、磨损符合真实物件；没有穿插、悬浮、法线翻转、贴图拉伸。
   - 质感：金属/木材/纸张有微观粗糙度变化和细小瑕疵，不是“塑料感 CG”。
   - 光影：有明确主光方向，阴影柔和可信；无过曝死白、无死黑。
   - 镜头：构图稳定、运动缓慢顺滑（缓入缓出），景深自然，焦点落在叙事重点上。
   - 噪点与闪烁：成片序列逐帧无噪点闪烁、无降噪涂抹斑块。
   - 文字：所有汉字字形正确、无缺笔乱码；铅字必须是镜像（反字）。
3. 记录每轮发现的问题和修改，写进任务目录的 `REVIEW.md`，附最终关键帧路径。

## 禁止
- 不要调用 tripo。如果你确信某个物件靠 Blender 程序化建模达不到精美程度，停下来，在 `REPORT.md` 里写明原因和你需要的模型描述，由导演决定。
- 不要 git commit（导演负责版本管理）。
- 不要修改任务目录以外的已有文件。

## 收尾
在任务目录写 `REPORT.md`：产出清单（路径、帧数）、渲染参数、每帧耗时、已知不足。
