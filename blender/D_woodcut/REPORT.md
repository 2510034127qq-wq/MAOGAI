# 任务 D：新兴木刻插图交付报告

日期：2026-10-20  
结论：**六组插图全部完成，已按两份新增导演反馈返工，最终目视自审与程序校验通过。**

已完整阅读 [任务书](BRIEF.md) 和 [导演阐述](../../docs/导演阐述.md)。本次使用内置 image_gen 工具，共成功生成并保存 **26张原图**：四个题材各4版，沿海和阿Q各5版。最终采用农轻重、内地、母鸡与马、资源剖面的v4，以及沿海、阿Q的v5。

## 导演反馈的落实

[FEEDBACK_1.md](FEEDBACK_1.md) 要求增加实黑块面、减少精细线稿。六题全部重新生成，最终实黑占**整张交付画布35.36%—39.96%**，统计包含留白纸边。远山、船壳、棚墙与地层改为厚实黑块，以楔形粗刀口表达明暗。

[FEEDBACK_2.md](FEEDBACK_2.md) 修订了原任务书的阿Q服饰设定。最终假洋鬼子**无礼帽、无燕尾服**，穿乌黑洋衣、披散头发，胸前有银桃子，手持哭丧棒；阿Q用竹筷固定顶上盘辫，穿破夹袄，身体畏缩后退。这一项按最新具体考据意见执行。最终结论是本次自审通过，不代表导演已另行签批。

另做两次定点修正：去除沿海v4船首疑似字母的记号；纠正阿Q v4中右侧人物浓须老人的形象与银佩形状。原始版本仍完整保留。

## 正式交付

正式文件均位于 `D:\MAOGAI\assets\img\`，共12张PNG。

| 题材 | 透明墨层 | 旧纸成品 | 最终版 | 实黑比例 |
|---|---|---|---|---:|
| 农、轻、重在同一片土地上 | [nongqingzhong_ink.png](../../assets/img/nongqingzhong_ink.png) | [nongqingzhong_paper.png](../../assets/img/nongqingzhong_paper.png) | v4 | 36.05% |
| 沿海工业港口 | [yanhai_ink.png](../../assets/img/yanhai_ink.png) | [yanhai_paper.png](../../assets/img/yanhai_paper.png) | v5 | 38.04% |
| 内地新建工业 | [neidi_ink.png](../../assets/img/neidi_ink.png) | [neidi_paper.png](../../assets/img/neidi_paper.png) | v4 | 37.12% |
| 母鸡与马 | [muji_maer_ink.png](../../assets/img/muji_maer_ink.png) | [muji_maer_paper.png](../../assets/img/muji_maer_paper.png) | v4 | 39.96% |
| 阿Q：不准革命 | [aq_ink.png](../../assets/img/aq_ink.png) | [aq_paper.png](../../assets/img/aq_paper.png) | v5 | 39.25% |
| 空气、森林与地下宝藏 | [kongqi_senlin_baozang_ink.png](../../assets/img/kongqi_senlin_baozang_ink.png) | [kongqi_senlin_baozang_paper.png](../../assets/img/kongqi_senlin_baozang_paper.png) | v4 | 35.36% |

- **透明墨层：2560×1440、RGBA。** 所有RGB严格为 `#1C1A17`，Alpha仅0或255，白色区域完全透明。透明像素的隐藏RGB也为墨色，避免白边。
- **纸底成品：1920×1080、RGB。** 纸色基值 `#EDE5D4`，极淡纸纹，轻微墨色起伏与少量漏白；不存在照片式灰阶塑形。
- 全景采用约74%的版心，周围约13%留纸；两幅略左移0.8%以保护右侧物件。没有边框、题签、文字或印章。实际检查中央70%裁切，核心人物、动物与物件完整。

![最终六图总览](qa/contact_sheet.jpg)

## 自审与验证

| 项目 | 最终结果 |
|---|---|
| 数量与来源 | 26张成功生成的原图全部保留，原图复制件与工具生成文件逐一校验一致 |
| 题意 | 六题所需主要物件完整；两个空食具、阿Q新考据形象及三层资源关系清楚 |
| 文字 | 逐张全图、局部复核，未发现残留文字、数字、签名、印章或伪文字 |
| 形体 | 放大检查手脚、马腿、套车、持棒和盘辫，未见明显畸形或错接 |
| 风格 | 大黑块、粗细不齐刀口、简化透视；无喷枪渐变、柔光与景深虚化 |
| 实黑比例 | 六张均在导演要求的35%—50%范围内 |
| 裁切 | 六张中央70%裁切预览通过，程序同时检查人工标注的核心内容框 |
| 文件 | 12张正式PNG全部实际解码，尺寸和RGBA/RGB模式正确 |
| 墨层 | 只有指定墨色；中间Alpha像素为0 |
| 纸版 | 像素仅落在纸色和墨色的轻微浮动范围内，无两者之间的灰色混合边 |
| 复现 | 对最终版本独立执行两次后期，12个PNG的SHA-256逐一一致 |

目视自审覆盖六张最终纸底全图、六张墨层关键局部、成品总览及裁切总览。审查中的问题、返工原因、每版取舍及**全部26条实际提示词**见 [REVIEW.md](REVIEW.md)。像素检查用于验证格式和处理流程，未用它代替风格、形体和伪文字判断。

## 复现方法

在项目根目录运行：

```powershell
python blender/D_woodcut/post.py
```

依赖见 [requirements.txt](requirements.txt)。本次使用Python 3.12、Pillow 12.2.0、NumPy 2.5.3、SciPy 1.18.1。脚本从自身位置解析项目根目录，审核预览图使用Windows Consolas字体。

处理顺序为：灰度 → Lanczos缩放 → 适度锐化 → 固定阈值155 → 去除小于4像素的孤立黑点 → 纯墨色及二值Alpha输出。不会磨平相连刀痕的毛边。纸版缩小后再次二值化，然后用固定种子添加印刷质感；纸色每通道变化±2，墨色变化−2至+3，漏白只落在厚墨内部。

生成原图实测约1672×941，后期通过常规缩放得到2560×1440交付画布；**不声称原生2560细节**，也未使用生成式超分。固定原图和依赖后，后期已验证字节级复现；重新调用图像生成工具不能保证得到同一原图。

## 文件索引

- [post.py](post.py)：可复现后期与自动校验。
- [generation.json](generation.json)：全部提示词、生成源路径、编辑输入，以及一次连接失败重试记录。
- [REVIEW.md](REVIEW.md)：中文逐题审核、版本取舍、26条完整实际提示词。
- [qa/validation.json](qa/validation.json)：尺寸、颜色、Alpha、实黑比例、裁切框、处理统计与文件哈希。
- [qa/reproducibility.json](qa/reproducibility.json)：最终版本两次独立运行的哈希比较、26张原图一致性记录。
- [qa/contact_sheet.jpg](qa/contact_sheet.jpg)：最终成品总览。
- [qa/crop70_contact_sheet.jpg](qa/crop70_contact_sheet.jpg)：中央70%裁切总览。
- `qa/<题材>_versions.jpg`：该题全部生成版本对比。
- `qa/<题材>_detail.png`：最终墨层关键局部。
- `qa/<题材>_crop70.png`：最终纸底中央70%裁切。
- `assets/img/raw/<题材>_v*.png`：全部未改动原图。

正式成品不包含审核图的文件名标签。视频合成可直接使用纸底版；需要沿用全片统一纸纹时可用透明墨层。
