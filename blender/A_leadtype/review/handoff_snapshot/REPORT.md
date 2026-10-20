# 铅字镜头制作状态

当前状态：**定稿低清审核通过，正式渲染等待共享 GPU 锁。任务尚未完成，以下不是最终交付报告。**

已完整阅读 BRIEF、COMMON、导演阐述与 FEEDBACK_1，并落实导演七项意见。完成六轮低清修订与逐字对焦检查。详见 [REVIEW.md](REVIEW.md)。

已就绪：

- `leadtype_title.blend`、`leadtype_poli.blend`：可编辑场景。
- `review/round6/`：两个镜头的首、中、尾定稿测试帧。
- `review/readability/`：五字焦点经过位置的测试帧。
- `title_scene_audit.json`、`poli_scene_audit.json`：几何、字形、尺寸和构图检查。
- `build_leadtype.py`、`make_textures.py`：可复现建模与纹理生成。
- `render_delivery.py`、`render_worker.py`：遵守独占 GPU 锁的正式渲染与续渲。
- `finish_delivery.py`：视频编码、完整解码、逐帧校验、联系表、工程复开比对和校验和。

几何定稿为 4×4×23.5 mm 铅字字身，凸字高约 0.667 mm，带斜坡根部与微倒角。使用 STSONG 字体；铅字镜像、纸面正向，印迹与凸字共用同一字形网格。

等待完成：

1. A1 210 帧、A2 180 帧，1920×1080 / 30 fps / PNG 8-bit RGB。
2. 两段 H.264 CRF 18 预览、两张每 30 帧取样的联系表。
3. A1 第 210 帧的 3840×2160 静帧。
4. 全序列人工审核、严格视频解码和保存工程复开验证。
5. 用实测帧数、耗时与最终验证结果替换本状态报告。

等待期间不绕过其他任务的有效 GPU 锁；最终提交仍以全部交付物完成并通过终审为准。
