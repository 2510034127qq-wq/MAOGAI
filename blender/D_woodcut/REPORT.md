# 任务 D：新兴木刻插图交付报告

日期：2026-10-20  
状态：**发现新增 FEEDBACK_1.md、FEEDBACK_2.md，正在依最新导演意见返工。本文件下文为上一轮记录，最终交付后更新。**

已完整阅读本目录的任务书及《导演阐述》，按“铅字与朱砂”的视觉规范制作。本次使用内置 image_gen 工具实际生成18张原图，六个题材各三版；经过比较与提示词改写，各题最终采用第三版。全部原图、完整提示词、取舍记录及可复现后期脚本均已保存。

## 交付文件

每组均有两个正式成品，路径为项目根目录下的 `assets/img/`。

| 题材 | 透明墨层 | 旧纸成品 |
|---|---|---|
| 农轻重 | [nongqingzhong_ink.png](../../assets/img/nongqingzhong_ink.png) | [nongqingzhong_paper.png](../../assets/img/nongqingzhong_paper.png) |
| 沿海港口 | [yanhai_ink.png](../../assets/img/yanhai_ink.png) | [yanhai_paper.png](../../assets/img/yanhai_paper.png) |
| 内地建设 | [neidi_ink.png](../../assets/img/neidi_ink.png) | [neidi_paper.png](../../assets/img/neidi_paper.png) |
| 母鸡与马 | [muji_maer_ink.png](../../assets/img/muji_maer_ink.png) | [muji_maer_paper.png](../../assets/img/muji_maer_paper.png) |
| 阿Q | [aq_ink.png](../../assets/img/aq_ink.png) | [aq_paper.png](../../assets/img/aq_paper.png) |
| 空气、森林、宝藏 | [kongqi_senlin_baozang_ink.png](../../assets/img/kongqi_senlin_baozang_ink.png) | [kongqi_senlin_baozang_paper.png](../../assets/img/kongqi_senlin_baozang_paper.png) |

透明墨层统一为 **2560×1440、RGBA**，墨色严格为 `#1C1A17`，Alpha只有0和255。原图白色区域完全透明，透明像素的隐藏RGB也设为墨色，减少合成时出现白边的风险。

旧纸成品统一为 **1920×1080、RGB**，纸底基色为 `#EDE5D4`；墨色有极轻微不均及少量漏白，纸纹非常淡。纸版的色差属于任务书要求的印刷后期，原始造型没有灰阶渐变。

各图采用一致的纸页式版心，约占画布宽高的74%，四周各留约13%的余量。没有添加边框、题签、字样或印章。另行查看中央70%裁切图，关键人物、动物和叙事物件仍完整。

![六张纸底成品总览](qa/contact_sheet.jpg)

## 自审结果

| 检查项 | 结果与证据 |
|---|---|
| 生成版本 | 六题各3版，共18张；原图完整保留于 `assets/img/raw/` |
| 内容完整性 | 麦田—厂房—高炉、港口、山谷建设、两个空食具、阿Q阻拦场景及三层资源剖面均可辨 |
| 画面文字 | 逐张全图与局部检查，未发现文字、数字、签名、印章或伪文字 |
| 人物与动物 | 放大查看手脚、发式、持棒姿态、马腿和套车，未见明显畸形或错接 |
| 木刻风格 | 第三轮减少细碎线描，采用大黑块、宽窄不齐的刀口；无柔光、景深模糊和照片式渐变 |
| 构图 | 六图均非镜像对称；全图与中央70%裁切预览通过 |
| 墨层像素 | 六张均只有指定墨色，Alpha唯一值为0/255，中间透明度像素为0 |
| 纸版像素 | 颜色仅在纸色及墨色的轻微浮动范围内，无两者之间的灰色混合边 |
| 文件读取 | 12张正式PNG均实际解码成功，尺寸、模式符合要求 |
| 后期复现 | 独立执行两次；12张PNG的SHA-256逐一相同，详见复现记录 |

完整的逐题版本比较、发现的问题、选用理由及18条实际提示词见 [REVIEW.md](REVIEW.md)。风格与形体结论来自本次目视自审，未以数值校验替代视觉判断。

## 后期复现

在项目根目录 `D:\MAOGAI` 运行：

```powershell
python blender/D_woodcut/post.py
```

依赖版本记录在 [requirements.txt](requirements.txt)，本次运行环境为 Python 3.12，Pillow 12.2.0、NumPy 2.5.3、SciPy 1.18.1。脚本从自身位置解析项目根目录，也可用绝对路径从其他目录运行；审核预览图默认使用 Windows Consolas 字体。

处理步骤：

1. 从保留原图读取，转换灰度，归一化到16:9版心。
2. Lanczos缩放，适度锐化；固定阈值155进行二值化。
3. 去除小于4像素的孤立黑色连通分量；保留刀口、毛边及白色刻痕，不进行轮廓平滑。
4. 导出指定墨色与二值Alpha的透明PNG。
5. 缩至1920×1080后再次二值化，按固定随机种子生成纸纹、轻微墨色起伏和厚墨内部漏白，导出纸底PNG。
6. 自动校验文件，并输出审核图及JSON记录。

纸色各通道变化为±2，墨色各通道变化为−2至+3。每张仅有约400—600个厚墨内部像素做新增漏白，细线处不随机打孔。

生成原图实测为1672×941左右，后期经过常规缩放再二值化得到2560×1440交付画布；这不等于原生2560细节，也没有使用生成式超分。固定原图、脚本和依赖后，后期输出可复现；重新调用图像生成工具不能保证得到相同原图。

## 文件索引

- [post.py](post.py)：后期与数值校验脚本。
- [generation.json](generation.json)：18次生成的完整提示词及原始生成文件路径。
- [REVIEW.md](REVIEW.md)：中文逐题自审，包含全部实际提示词。
- [qa/validation.json](qa/validation.json)：每张尺寸、模式、颜色、清噪数量、漏白数量、裁切框与SHA-256。
- [qa/reproducibility.json](qa/reproducibility.json)：两次独立运行的12个文件哈希比较。
- [qa/contact_sheet.jpg](qa/contact_sheet.jpg)：六图总览。
- [qa/crop70_contact_sheet.jpg](qa/crop70_contact_sheet.jpg)：中央70%裁切总览。
- `qa/<题材>_versions.jpg`：每题三版对比。
- `qa/<题材>_detail.png`：墨层关键局部放大。
- `qa/<题材>_crop70.png`：各图中央70%纸底裁切。

正式成品不含审核图上的英文文件名标签。视频合成可直接使用纸底版；如需沿用整片统一的纸纹动画，应使用透明墨层。
