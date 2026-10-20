# 任务 D 木刻插图自审记录

当前状态：正在处理新增 FEEDBACK_1.md 与 FEEDBACK_2.md。下文为第三轮审核记录，不能作为第四轮最终放行结论。

审核日期：2026-10-20。依据：本目录 `BRIEF.md` 与 `../../docs/导演阐述.md`，已完整阅读导演阐述，重点遵循“铅字与朱砂”的木刻规范。

使用内置 **image_gen** 图像生成工具，共实际生成 **18 张**：六题各三版。原图未改动，存于 `../../assets/img/raw/`。每题最终采用 v3；不是预先固定选第三版，而是在前两版的细线、人物尺度或边缘问题上继续改写提示词后，逐项比较确定。

## 审核方法与结果

- 原图：每次生成后检查题意、人体/动物结构、伪文字、刀法与构图；所有版本保留。
- 成品：六张纸底全图逐张查看；六张透明墨层以白底合成的关键区域逐张放大查看；比较总览与中央70%裁切预览。
- 数值：`post.py` 校验 PNG 解码、尺寸、RGBA/RGB 模式、墨色、Alpha 唯一值、纸版色值范围、版本数量与人工标注主体框的几何范围。结果见 `qa/validation.json`。
- **自审结论：六组全部通过。** 未发现文字/数字/签名/印章、明显畸形肢体、照片式灰阶塑形、柔光、景深模糊或镜像对称构图。
- 风格判断属于本次目视自审；没有用像素合格冒充艺术判断，也没有声称经过外部专家鉴定。未使用 OCR 结果代替目视。
- “无灰阶”严格落实在 `_ink.png`：所有 RGB 均为 `#1C1A17`，Alpha 仅 `0/255`。纸版按任务要求有轻微印刷色差，不能误称整张纸版只有两种 RGB。
- 各图全景等比例归入约74%的版心，四边约13%留纸；没有额外边框、文字或符号。中央70%仍包含核心叙事物件。环境边缘不是全部需要保存的主体。
- 生成原图实测约1672×941（沿海v1为1672×940），不是原生2560像素。后期采用常规 Lanczos 缩放、轻锐化与再次阈值化，输出2560×1440；不声称增加了原图没有的细节。

总览：![六张纸底成品](qa/contact_sheet.jpg)

裁切审核：![仅保留画面中央70%](qa/crop70_contact_sheet.jpg)

## 农、轻、重在同一片土地上 · `nongqingzhong`

| 版本 | 发现的问题与取舍 |
|---|---|
| v1 | 三层空间与三名收割者明确，但麦田细线过密，人物靠下，重工业部分偏右，未选。 |
| v2 | 改为两名农民，视野稍远；高炉仍靠右，麦田仍有细碎描画，未选。 |
| v3 | 选用。两名农民明显缩小并以背影处理，宽刀麦穗、锯齿厂房、高炉和烟囱形成前中远景，小路与电线杆串起空间。大黑块与粗白刀口更统一。 |

最终检查：放大核对两位收割者、厂房屋顶、烟囱和高炉支架。人物手藏在麦田中，未见多余肢体；厂房的重复竖窗属于建筑结构，未见伪字。二值化后麦穗和烟的刀口仍清楚。中央70%预览保留两人、锯齿厂房和整组高炉。

结论：**通过**。重点放大区域：农民—纺织厂—高炉。

[三版比较](qa/nongqingzhong_versions.jpg) · [墨层局部](qa/nongqingzhong_detail.png) · [中央70%](qa/nongqingzhong_crop70.png) · [纸底成品](../../assets/img/nongqingzhong_paper.png)

生成提示词原文如下，完整保留实际传入的内容。前两版为英文，第三版改为中文强调刀法与构图。

### v1 提示词

```text
Use case: historical-scene. Make one original Chinese New Woodcut Movement black-and-white relief print, landscape 16:9, ideally 2560x1440. This is a 1950s rural industrial book illustration, not a poster. Authentic hand-carved raised black forms on plain white: bold connected ink masses, assertive angular V-gouge marks, irregular U-gouge white hatch cuts, slightly rough cut edges, restrained honest observational composition. No grayscale shading, no gradients, no digital smooth curves, no photographic light, no blur, no speckled distress filter. No writing, lettering, numbers, signs, seals, signatures, borders or frames anywhere.
Subject: agriculture, light industry and heavy industry connected on the SAME land, in three receding spatial planes. In the foreground a wheat field with exactly three small Chinese farmers seen from the back harvesting, simply cut anatomy, hands largely hidden by wheat. Midground a textile mill unmistakably having a row of SAWTOOTH shed roofs, no windows shaped like text. In the distance a blast furnace and two chimneys, smoke made of flat white/black carved curving ribbons. A meandering field path and a few telegraph poles physically link all three planes. Keep the farmers, sawtooth mill, furnace and chimney tops inside the central 70 percent width AND height; outer 15 percent margins are expendable wheat/ground/sky. Modest landscape, asymmetric placement, quiet human labor. Large white sky, substantial black earth and mill silhouettes; tonal feeling only by purposeful carved hatch spacing. Pure BLACK ink and WHITE background only, no cream paper. Complete single scene, not collage.
```

### v2 提示词

```text
Use case: historical-scene. One original horizontal 16:9 Chinese New Woodcut Movement book illustration in the spirit of mid-century 1950s Chinese relief printmaking. Black ink on plain white. Genuine confident hand-cut raised black forms, broad solid ink masses, irregular tapered white V-gouge cuts and rounded U-gouge hatching, blunt economical marks, wood-grain roughness within the carved marks only. Tonality comes exclusively from cut spacing. Humble believable lived-in scene, restrained asymmetric composition, not a poster and not a finely engraved banknote. NO grayscale shading, gradients, stippling, airbrush, photographic light, blur, shiny rendering, calligraphic swirls or smooth vector outlines. No text of any kind, signs, lettering, numbers, signatures, seals, labels, frames or panel divisions. Small simplified people in side/back view only, modest hands hidden where possible, clear natural anatomy. IMPORTANT framing: zoomed-out panorama; all story-essential subjects completely within middle 70% of canvas both horizontally and vertically (15% crop-safe scene margin on EACH side); outer ground/sky/background expendable. Single complete landscape scene, not collage. Aim 2560x1440. Scene: three industries rooted in one continuous Chinese rural landscape. Foreground wheat field with exactly TWO SMALL farmers harvesting, backs toward viewer, full bodies well above lower margin, faces and hands obscured by hats and wheat. Midground textile mill with unequivocal row of sawtooth roofs. Farther away a modest blast furnace and two chimneys (keep chimney tops low enough for cropping), carved ribbon smoke. Winding field path and a few telegraph poles link the farm, mill and ironworks. Make wheat in broad grouped carved clumps, NOT countless fussy marks. Farmer group lies in lower middle-left, mill in center, ironworks behind to right, asymmetrical but visually balanced. Large calm white sky. Stronger and coarser gouge cuts, simpler than fine pen drawing.
```

### v3 提示词

```text
中国1950年代新兴木刻黑白阳刻插图，古元、彦涵、力群的朴素而有力的手工刀法气质。横幅16:9，单幅完整风景。请像木板上真正用三角刀和圆口刀一刀一刀刻成：概括大黑块、宽而短的不规则留白刀痕，少刻细节，绝非照片转素描、精密铜版画或钢笔速写。不加纸纹，不加灰色，只有纯黑纯白。绝无任何汉字、字母、数字、招牌、签名、印章。远景画法：麦田占前景，中间偏左两个小小的农民背影在收割，身体只高约画面12%，手藏在麦穗后；中景中央一排很明确的锯齿形屋顶纺织厂；远景中央偏右是一座高炉和两根烟囱，简练刀刻曲线作烟。小路和电线杆把三者联系在同一土地上。高炉必须放在横向65%处，绝不能挤到右边缘。把两个农民、整个纺织厂、整个高炉和烟囱都放进横向20%-80%、纵向20%-80%的中心区域。四边仅留麦田、远山和白天空作裁切余地。自然不对称，无装饰边框。主题是农轻重相互支持，有生活的质朴力量。
```

## 沿海工业港口 · `yanhai`

| 版本 | 发现的问题与取舍 |
|---|---|
| v1 | 货轮和吊车清楚，但近景船首较大，右边仓库延伸过长，纹理细，未选。 |
| v2 | 船和两台吊车位置更平衡，作为可用对照；海面仍偏细密，后续以第三版更强的黑白块面统一全套。 |
| v3 | 选用。大小不同的两架吊车与中央偏右的货轮形成不对称构图，船壳为大黑块，海面为较宽的水平刀纹；仓库、厂房及极小工人可辨。 |

最终检查：放大检查吊索、桁架、货轮甲板和船尾栏杆。船尾看似短字符的形状经放大为栏杆立柱，并无可识别字母或伪文字；船首白形是船锚。未见船名、编号、印章。细索仍可读，中央70%裁切保留两架主吊车及货轮。

结论：**通过**。重点放大区域：吊车—货轮—码头。

[三版比较](qa/yanhai_versions.jpg) · [墨层局部](qa/yanhai_detail.png) · [中央70%](qa/yanhai_crop70.png) · [纸底成品](../../assets/img/yanhai_paper.png)

生成提示词原文如下，完整保留实际传入的内容。前两版为英文，第三版改为中文强调刀法与构图。

### v1 提示词

```text
Use case: historical-scene. One original horizontal 16:9 Chinese New Woodcut Movement book illustration in the spirit of mid-century 1950s Chinese relief printmaking. Black ink on plain white. Genuine confident hand-cut raised black forms, broad solid ink masses, irregular tapered white V-gouge cuts and rounded U-gouge hatching, blunt economical marks, wood-grain roughness within the carved marks only. Tonality comes exclusively from cut spacing. Humble believable lived-in scene, restrained asymmetric composition, not a poster and not a finely engraved banknote. NO grayscale shading, gradients, stippling, airbrush, photographic light, blur, shiny rendering, calligraphic swirls or smooth vector outlines. No text of any kind, signs, lettering, numbers, signatures, seals, labels, frames or panel divisions. Small simplified people in side/back view only, modest hands hidden where possible, clear natural anatomy. IMPORTANT framing: zoomed-out panorama; all story-essential subjects completely within middle 70% of canvas both horizontally and vertically (15% crop-safe scene margin on EACH side); outer ground/sky/background expendable. Single complete landscape scene, not collage. Aim 2560x1440. 1950s Chinese coastal industrial harbor. One cargo steamship in three-quarter side view at a dock, two characteristic lattice dock cranes with cables reaching their cargo, simple warehouses and sawtooth industrial workshops behind. No modern containers or cruise ships. A few tiny dockworkers. Sea in the foreground is unmistakably carved with broad HORIZONTAL black-and-white gouge strokes, irregular spacing, white wakes. Ship, cranes, warehouses occupy the middle width, all crane tops safely below 15% top margin. Calm documentary observation, broad black ship hull, white water, angular industrial silhouettes, not a dramatic epic scene.
```

### v2 提示词

```text
Use case: historical-scene. One original horizontal 16:9 Chinese New Woodcut Movement book illustration in the spirit of mid-century 1950s Chinese relief printmaking. Black ink on plain white. Genuine confident hand-cut raised black forms, broad solid ink masses, irregular tapered white V-gouge cuts and rounded U-gouge hatching, blunt economical marks, wood-grain roughness within the carved marks only. Tonality comes exclusively from cut spacing. Humble believable lived-in scene, restrained asymmetric composition, not a poster and not a finely engraved banknote. NO grayscale shading, gradients, stippling, airbrush, photographic light, blur, shiny rendering, calligraphic swirls or smooth vector outlines. No text of any kind, signs, lettering, numbers, signatures, seals, labels, frames or panel divisions. Small simplified people in side/back view only, modest hands hidden where possible, clear natural anatomy. IMPORTANT framing: zoomed-out panorama; all story-essential subjects completely within middle 70% of canvas both horizontally and vertically (15% crop-safe scene margin on EACH side); outer ground/sky/background expendable. Single complete landscape scene, not collage. Aim 2560x1440. An unheroic working coastal industrial port in China in the 1950s, seen across a generous stretch of calm water. Cargo steamer with black hull sits diagonally just right of center; two sturdy lattice dockside cranes grouped to the left, low warehouses and plain factory sheds behind. One crane hoists a plain crate above quay, not above people. Tiny laborers are simple cut silhouettes. Thick level horizontal sea cuts, large white sky. Keep the entire vessel, crane tips and all main buildings in the central 70%, allowing sea/blank sky/low land at all edges. Dense black shapes and broad economical rough white gouges, less fine technical detail, human-scale practical industry. No signage on ship or buildings.
```

### v3 提示词

```text
中国1950年代新兴木刻黑白阳刻书籍插图，参照古元、彦涵、李桦、力群、赵延年的质朴刀法气质。横幅16:9，一幅完整画面。像木板用三角刀和圆口刀真正手刻：概括厚实大黑块，宽、短、不规则的留白刀痕，疏密有节制，少刻细节。不是照片转素描、精密铜版、钢笔线描、电脑矢量图。纯黑纯白，不加纸纹，无灰色灰阶渐变、无柔光。画面绝无文字、数字、招牌、签名、印章，建筑只画空白墙面。视野拉远，所有重要物件集中在横向20%-80%、纵向20%-80%的区域，四边只留可裁切的环境。自然不对称，无边框。题材为1950年代沿海工业港口。一艘朴素老式货轮停靠码头，货轮完整位于中央偏右，左边两架大小不同的码头吊车，后方是仓库和厂房。货轮高约画面25%，两台吊车顶部在画面纵向20%以下，船和吊车不可挤出中间70%。船身大块黑，海面使用有力的横向刀纹，宽窄不齐而平静，不刻密密麻麻的小波纹；吊车桁架简练但结构通顺。两三个极小的工人是侧影或背影，手不刻细节。不画现代集装箱，不画轮船名字。大白天空、简洁朴素、工业日常。
```

## 内地新建工业 · `neidi`

| 版本 | 发现的问题与取舍 |
|---|---|
| v1 | 铁路桥与工地关系可读，但厂房过大、偏右，山体细碎，未选。 |
| v2 | 桥的桁架清楚，但额外出现火车，厂房仍贴边，工地较繁杂，未选。 |
| v3 | 选用。拉远到山谷尺度，桥、河、未竣工厂房和抬木料工人同处一个空间；山的黑块更扎实，屋架与脚手架能分辨。 |

最终检查：放大检查桥墩、桁架及两侧延续的轨道线，未见悬空断接；脚手架围绕未完工墙体，工人是小背影/侧影，抬料姿态可读。原图工人仍偏右，统一版心后，主要抬料队伍进入中央70%；不把建筑当成工程结构图使用。

结论：**通过**。重点放大区域：桥—脚手架—工人。

[三版比较](qa/neidi_versions.jpg) · [墨层局部](qa/neidi_detail.png) · [中央70%](qa/neidi_crop70.png) · [纸底成品](../../assets/img/neidi_paper.png)

生成提示词原文如下，完整保留实际传入的内容。前两版为英文，第三版改为中文强调刀法与构图。

### v1 提示词

```text
Use case: historical-scene. One original horizontal 16:9 Chinese New Woodcut Movement book illustration in the spirit of mid-century 1950s Chinese relief printmaking. Black ink on plain white. Genuine confident hand-cut raised black forms, broad solid ink masses, irregular tapered white V-gouge cuts and rounded U-gouge hatching, blunt economical marks, wood-grain roughness within the carved marks only. Tonality comes exclusively from cut spacing. Humble believable lived-in scene, restrained asymmetric composition, not a poster and not a finely engraved banknote. NO grayscale shading, gradients, stippling, airbrush, photographic light, blur, shiny rendering, calligraphic swirls or smooth vector outlines. No text of any kind, signs, lettering, numbers, signatures, seals, labels, frames or panel divisions. Small simplified people in side/back view only, modest hands hidden where possible, clear natural anatomy. IMPORTANT framing: zoomed-out panorama; all story-essential subjects completely within middle 70% of canvas both horizontally and vertically (15% crop-safe scene margin on EACH side); outer ground/sky/background expendable. Single complete landscape scene, not collage. Aim 2560x1440. New inland industry in 1950s China. Within a valley among solid rugged mountains, a convincing RAILWAY BRIDGE with parallel rails crosses a winding river gorge left of center. On the near right bank is ONE new factory building under construction, exposed roof trusses and an orderly but handbuilt timber scaffold attached around its walls, distinct from the bridge. Four tiny workers carry a beam and work at ground level. Mountain planes shown with grouped angular white gouge cuts in large black shapes. River shown by white channel and sparse lateral cuts. Cohesive real landscape, bridge connected to track on BOTH banks, structural clarity, no fantasy architecture. Wide quiet surroundings, all story objects in central 70%.
```

### v2 提示词

```text
Use case: historical-scene. One original horizontal 16:9 Chinese New Woodcut Movement book illustration in the spirit of mid-century 1950s Chinese relief printmaking. Black ink on plain white. Genuine confident hand-cut raised black forms, broad solid ink masses, irregular tapered white V-gouge cuts and rounded U-gouge hatching, blunt economical marks, wood-grain roughness within the carved marks only. Tonality comes exclusively from cut spacing. Humble believable lived-in scene, restrained asymmetric composition, not a poster and not a finely engraved banknote. NO grayscale shading, gradients, stippling, airbrush, photographic light, blur, shiny rendering, calligraphic swirls or smooth vector outlines. No text of any kind, signs, lettering, numbers, signatures, seals, labels, frames or panel divisions. Small simplified people in side/back view only, modest hands hidden where possible, clear natural anatomy. IMPORTANT framing: zoomed-out panorama; all story-essential subjects completely within middle 70% of canvas both horizontally and vertically (15% crop-safe scene margin on EACH side); outer ground/sky/background expendable. Single complete landscape scene, not collage. Aim 2560x1440. Broad distant view of inland Chinese industrial construction in a mountain river valley, 1950s. A short sturdy railway truss bridge crosses the narrow ravine on the middle left, real two rails continue across it and onto both banks. To the right a single rectangular unfinished factory with clearly exposed timber scaffold on its outer wall, simple triangular roof trusses and unglazed window openings. A handful of very small workers carry timber and push one simple wheelbarrow along a site path. No oversized faces or hands. Surrounding dark mountain masses cut with forceful wide diagonal wedges, white river below bridge. All bridge, factory, workers clearly readable but safely away from all 15% crop edges. Very economical hand-carved bold black-and-white shapes, rather than fussy pictorial detail.
```

### v3 提示词

```text
中国1950年代新兴木刻黑白阳刻书籍插图，参照古元、彦涵、李桦、力群、赵延年的质朴刀法气质。横幅16:9，一幅完整画面。像木板用三角刀和圆口刀真正手刻：概括厚实大黑块，宽、短、不规则的留白刀痕，疏密有节制，少刻细节。不是照片转素描、精密铜版、钢笔线描、电脑矢量图。纯黑纯白，不加纸纹，无灰色灰阶渐变、无柔光。画面绝无文字、数字、招牌、签名、印章，建筑只画空白墙面。视野拉远，所有重要物件集中在横向20%-80%、纵向20%-80%的区域，四边只留可裁切的环境。自然不对称，无边框。题材为1950年代中国内地新建工业。群山中一个河谷，中央偏左有一座短而坚实的铁路桁架桥跨过河谷，两根钢轨衔接两岸；中央偏右是一座未完工的新厂房，清楚可辨的木脚手架围着墙壁，屋顶有部分裸露三角屋架。厂房和桥都远远看、小而完整，厂房最右端不得超过画面78%，厂房不超过画面宽28%，桥长约25%。几个小工人高不超过画面7%，背影抬木料，姿态简单自然。山的暗面是一整块黑，用少数大而硬朗的斜刀纹刻山石，河流留白，工地不铺满杂物。不画火车。把桥、厂房、工人安排在同一个有真实路径联系的山谷中。
```

## 母鸡与马 · `muji_maer`

| 版本 | 发现的问题与取舍 |
|---|---|
| v1 | 两个容器的空腔可读，但母鸡羽毛和马身纹理偏细，马车靠右，未选。 |
| v2 | 母鸡较小，仍有繁密墙纹和动物细线，马车依然靠边，未选。 |
| v3 | 选用。母鸡低头对着空碗；后方瘦马套车，空槽置于嘴前。粗刀羽毛和少量肋骨比前两版更概括，空院地支持讽喻。 |

最终检查：逐项确认鸡的头、喙、两腿和空碗；马的四条腿、头、耳、尾以及套具和车辕连接。空槽有深色内壁，但没有草料，碗内没有粮食。未见多腿、粘连或身体穿插。瘦马有肋骨但没有伤口或丑化表情。中央70%预览保留动物、两个容器、车轮和车尾。

结论：**通过**。重点放大区域：鸡与碗—马与槽—套车。

[三版比较](qa/muji_maer_versions.jpg) · [墨层局部](qa/muji_maer_detail.png) · [中央70%](qa/muji_maer_crop70.png) · [纸底成品](../../assets/img/muji_maer_paper.png)

生成提示词原文如下，完整保留实际传入的内容。前两版为英文，第三版改为中文强调刀法与构图。

### v1 提示词

```text
Use case: historical-scene. One original horizontal 16:9 Chinese New Woodcut Movement book illustration in the spirit of mid-century 1950s Chinese relief printmaking. Black ink on plain white. Genuine confident hand-cut raised black forms, broad solid ink masses, irregular tapered white V-gouge cuts and rounded U-gouge hatching, blunt economical marks, wood-grain roughness within the carved marks only. Tonality comes exclusively from cut spacing. Humble believable lived-in scene, restrained asymmetric composition, not a poster and not a finely engraved banknote. NO grayscale shading, gradients, stippling, airbrush, photographic light, blur, shiny rendering, calligraphic swirls or smooth vector outlines. No text of any kind, signs, lettering, numbers, signatures, seals, labels, frames or panel divisions. Small simplified people in side/back view only, modest hands hidden where possible, clear natural anatomy. IMPORTANT framing: zoomed-out panorama; all story-essential subjects completely within middle 70% of canvas both horizontally and vertically (15% crop-safe scene margin on EACH side); outer ground/sky/background expendable. Single complete landscape scene, not collage. Aim 2560x1440. A plain Chinese farm courtyard in the 1950s, quiet gently satirical scene about animals asked to produce without being fed. Foreground center-left ONE hen in natural SIDE view, lowered head and beak looking into a distinctly EMPTY shallow feeding bowl immediately before her. Bowl interior is exposed plain white, no grain. Behind and slightly right ONE lean but dignified horse in SIDE view, four anatomically clear legs, harnessed between two shafts to a plain two-wheeled farm cart behind it. A clearly EMPTY wooden feeding trough is just in front of the horse and does not obscure the horse's legs; clean blank interior, no hay. Horse modestly thin with a few rib cuts, never grotesque or suffering caricature. Hen, bowl, whole horse, cart, trough fully within middle 70% of image. Sparse mud wall and farm gate as background. The two visible empty containers carry the visual argument. Large quiet unmarked courtyard foreground; no extra animals or people.
```

### v2 提示词

```text
Use case: historical-scene. One original horizontal 16:9 Chinese New Woodcut Movement book illustration in the spirit of mid-century 1950s Chinese relief printmaking. Black ink on plain white. Genuine confident hand-cut raised black forms, broad solid ink masses, irregular tapered white V-gouge cuts and rounded U-gouge hatching, blunt economical marks, wood-grain roughness within the carved marks only. Tonality comes exclusively from cut spacing. Humble believable lived-in scene, restrained asymmetric composition, not a poster and not a finely engraved banknote. NO grayscale shading, gradients, stippling, airbrush, photographic light, blur, shiny rendering, calligraphic swirls or smooth vector outlines. No text of any kind, signs, lettering, numbers, signatures, seals, labels, frames or panel divisions. Small simplified people in side/back view only, modest hands hidden where possible, clear natural anatomy. IMPORTANT framing: zoomed-out panorama; all story-essential subjects completely within middle 70% of canvas both horizontally and vertically (15% crop-safe scene margin on EACH side); outer ground/sky/background expendable. Single complete landscape scene, not collage. Aim 2560x1440. A homely rural courtyard, wide unembellished observation. ONE little hen at center-left bows her head toward an EMPTY shallow food bowl; white hollow inside is plainly visible. Farther back, centered across middle of picture, ONE thin farm horse shown in simple clear profile facing left, neatly harnessed to a small two-wheeled wooden cart behind on right. Four coherent horse legs, two ears, one head, one tail; no overlapping second animal. An EMPTY wooden trough sits in front of the horse at the far side of its muzzle, not covering legs, clearly open white cavity, absolutely no hay. Restrained visible ribs made with only a few gouge marks. Mild social irony from both empty vessels, not cruelty or cartoon comedy. Mud wall and low tiled shed loosely cut in background; quiet yard and sky are expendable 15% margins all around. All essential animals, harness, cart and bowls inside middle 70%. Forceful simple black masses, broad irregular carved white cuts, no stippled aged-paper effect.
```

### v3 提示词

```text
中国1950年代新兴木刻黑白阳刻书籍插图，参照古元、彦涵、李桦、力群、赵延年的质朴刀法气质。横幅16:9，一幅完整画面。像木板用三角刀和圆口刀真正手刻：概括厚实大黑块，宽、短、不规则的留白刀痕，疏密有节制，少刻细节。不是照片转素描、精密铜版、钢笔线描、电脑矢量图。纯黑纯白，不加纸纹，无灰色灰阶渐变、无柔光。画面绝无文字、数字、招牌、签名、印章，建筑只画空白墙面。视野拉远，所有重要物件集中在横向20%-80%、纵向20%-80%的区域，四边只留可裁切的环境。自然不对称，无边框。一座朴素农家院子的远景。中间偏左一只小母鸡低头看着前方空空的食碗，母鸡高度只占画面15%，食碗是清楚的白色空腔，没有一粒粮。后面中央一匹瘦而不丑化的马，四条腿、两个耳朵、一个头和一条尾巴都简洁自然，侧面、全身。马套着一辆简单两轮木车，马加车的完整长度不超过画面宽55%，整个车轮和车尾都在横向80%以内。马前方有一个空马槽，开口白、完全无草料，不遮挡马腿。肋骨只刻三四条、不要恐怖。母鸡、空碗、马、空槽、马车都安排在中央区域，四边给充足空院地与白天色。背景只有一段矮院墙和低小瓦棚，不画繁密砖石和树叶。用粗略宽刀表现羽毛和马鬃，动物形象要概括，不画摄影式丝丝毛发。略含讽意但不做滑稽漫画。
```

## 阿Q：不准革命 · `aq`

| 版本 | 发现的问题与取舍 |
|---|---|
| v1 | 阻拦和退缩关系成立，但人物过大、衣褶过细；阿Q发髻位置与顶盘辫特征不够突出，未选。 |
| v2 | 拉远后发式、礼帽和长辫清楚，但阿Q躯干偏向前，退缩动作不如第三版直接，未选。 |
| v3 | 选用。右侧假洋鬼子穿西服戴礼帽，脑后长假辫，扬起细棒；左侧阿Q剃前额、顶上盘辫、短破衣，躯干向后缩退。用门洞黑影与白墙组织画面。 |

最终检查：放大核对持棒手、阿Q胸前的手、两人的腿脚；手以少量刀口概括，无明显多指或错接。棒与假辫方向分离，不混成一条线。门上无匾额、春联或字迹。人物关系靠侧身姿态而非脸部特写传达。中央70%预览两人全身、棒与长辫完整。

结论：**通过**。重点放大区域：两人全身—持棒手—发式。

[三版比较](qa/aq_versions.jpg) · [墨层局部](qa/aq_detail.png) · [中央70%](qa/aq_crop70.png) · [纸底成品](../../assets/img/aq_paper.png)

生成提示词原文如下，完整保留实际传入的内容。前两版为英文，第三版改为中文强调刀法与构图。

### v1 提示词

```text
Use case: historical-scene. One original horizontal 16:9 Chinese New Woodcut Movement book illustration in the spirit of mid-century 1950s Chinese relief printmaking. Black ink on plain white. Genuine confident hand-cut raised black forms, broad solid ink masses, irregular tapered white V-gouge cuts and rounded U-gouge hatching, blunt economical marks, wood-grain roughness within the carved marks only. Tonality comes exclusively from cut spacing. Humble believable lived-in scene, restrained asymmetric composition, not a poster and not a finely engraved banknote. NO grayscale shading, gradients, stippling, airbrush, photographic light, blur, shiny rendering, calligraphic swirls or smooth vector outlines. No text of any kind, signs, lettering, numbers, signatures, seals, labels, frames or panel divisions. Small simplified people in side/back view only, modest hands hidden where possible, clear natural anatomy. IMPORTANT framing: zoomed-out panorama; all story-essential subjects completely within middle 70% of canvas both horizontally and vertically (15% crop-safe scene margin on EACH side); outer ground/sky/background expendable. Single complete landscape scene, not collage. Aim 2560x1440. Illustrate the exclusion scene from Lu Xun's The True Story of Ah Q, early 20th-century China, at the entrance of a prosperous Qian family compound. NO plaque or couplet or writing. Two modest-sized full figures mainly in PROFILE, entire figures in central 70%. On left at doorway, the fake foreign devil wears a WESTERN SUIT with lapels and a TOP HAT; from behind the hat at his NAPE visibly hangs a long thin FALSE QUEUE braid. He blocks the path, leaning forward and raises a plain slender wooden cane diagonally in one hand threateningly, other hand simple and partly obscured. On right, Ah Q recoils backward, shoulders hunched, weight leaning away, one foot retreating, wearing ragged SHORT traditional jacket and loose trousers. Ah Q has a distinctly SHAVED FRONT SCALP and a small BRAID COILED ON THE CROWN of his head, no hat. Fear/exclusion expressed through whole-body stance, not closeup faces. No contact, no injury. Simple empty white gap between the two separates silhouettes. Weathered gate, wall, plain stone threshold; no decorative motifs that look like text. Humble rough woodcut theatre of posture, anatomically simple readable hands and feet.
```

### v2 提示词

```text
Use case: historical-scene. One original horizontal 16:9 Chinese New Woodcut Movement book illustration in the spirit of mid-century 1950s Chinese relief printmaking. Black ink on plain white. Genuine confident hand-cut raised black forms, broad solid ink masses, irregular tapered white V-gouge cuts and rounded U-gouge hatching, blunt economical marks, wood-grain roughness within the carved marks only. Tonality comes exclusively from cut spacing. Humble believable lived-in scene, restrained asymmetric composition, not a poster and not a finely engraved banknote. NO grayscale shading, gradients, stippling, airbrush, photographic light, blur, shiny rendering, calligraphic swirls or smooth vector outlines. No text of any kind, signs, lettering, numbers, signatures, seals, labels, frames or panel divisions. Small simplified people in side/back view only, modest hands hidden where possible, clear natural anatomy. IMPORTANT framing: zoomed-out panorama; all story-essential subjects completely within middle 70% of canvas both horizontally and vertically (15% crop-safe scene margin on EACH side); outer ground/sky/background expendable. Single complete landscape scene, not collage. Aim 2560x1440. A spare 1950s hand-carved book illustration of the 'forbidden to join the revolution' incident in Lu Xun's Ah Q. Early republican Chinese wealthy Qian household gate, blank wall and plain doorway, NO signs or writing. On the right the fake foreign devil guards the doorway in WESTERN SUIT, buttoned coat with lapels, TOP HAT, visible long FALSE BRAID hanging from the NAPE behind his head. He raises one thin wooden cane diagonally above his shoulder, an assertive forbidding posture. Left of him Ah Q recoils a step backward, hunched and shrinking, seen in profile: SHAVED FOREHEAD, his own braid COILED like a small knot on top of his bare crown, ragged SHORT JACKET with uneven hem and loose trousers. Both figures small to medium, fully seen, total group plus doorway safely inside middle 70% of canvas with generous bare courtyard at bottom. Clear separation between hands/cane/braid, no merged limbs. Express relation through asymmetrical poses and the white space between figures. Black clothes and wall shadows contrast with broad white carved cuts. No heroic poster, no cinematic lighting, no ornate architecture.
```

### v3 提示词

```text
中国1950年代新兴木刻黑白阳刻书籍插图，参照古元、彦涵、李桦、力群、赵延年的质朴刀法气质。横幅16:9，一幅完整画面。像木板用三角刀和圆口刀真正手刻：概括厚实大黑块，宽、短、不规则的留白刀痕，疏密有节制，少刻细节。不是照片转素描、精密铜版、钢笔线描、电脑矢量图。纯黑纯白，不加纸纹，无灰色灰阶渐变、无柔光。画面绝无文字、数字、招牌、签名、印章，建筑只画空白墙面。视野拉远，所有重要物件集中在横向20%-80%、纵向20%-80%的区域，四边只留可裁切的环境。自然不对称，无边框。鲁迅《阿Q正传》“不准革命”。钱府朴素的大门前，两个小全身侧面人物在画面中央，人物高度均不超过画面高42%。右边假洋鬼子穿有翻领的西服，戴礼帽，脑后明确垂着一条长假辫子；他一手举起细的哭丧棒斜向上，另一手藏在西服后，拦住门口。左边阿Q剃光前额，自己的辫子盘在头顶，穿破旧短衣和长裤；阿Q身体与头向左后方缩退、脚也往后退，面朝右边的假洋鬼子，一只手缩在胸前，另一手藏在身后，切不可向前进攻。两人姿态不对称，四条腿清楚、手概括、脸只有几个刀口，不细画五官，不刻满细密衣褶。假洋鬼子长辫子和棒子互不重叠。右边门洞的黑影与左边白墙构成黑白对照，地面简洁。门上无匾额、无春联、无文字。
```

## 空气、森林与地下宝藏 · `kongqi_senlin_baozang`

| 版本 | 发现的问题与取舍 |
|---|---|
| v1 | 三层明确，但地下细节过多，马群及晶体偏边缘，未选。 |
| v2 | 煤层较简洁，但左右林带和两簇晶体近似对称，地下仍有细密排线，未选。 |
| v3 | 选用。鹰与流云在上，森林、山、毡房与三匹马居中，煤层、白色矿脉和大小不同的晶体在下。左右不对称，整体是一幅地层剖面的风景而非拼接分格。 |

最终检查：逐张全图检查天空中的鹰，局部检查马群、毡房、矿脉和晶体。三匹马侧身轮廓清楚，未见明显多腿；无地图、国界、地名或数据标注。第三版鹰仍偏高，统一留边后中央70%裁切可保留整只鹰及两簇晶体。地层是服务解说的示意构图，不声称特定地点的真实地质剖面。

结论：**通过**。重点放大区域：鹰—马群和毡房—煤层与晶体。

[三版比较](qa/kongqi_senlin_baozang_versions.jpg) · [墨层局部](qa/kongqi_senlin_baozang_detail.png) · [中央70%](qa/kongqi_senlin_baozang_crop70.png) · [纸底成品](../../assets/img/kongqi_senlin_baozang_paper.png)

生成提示词原文如下，完整保留实际传入的内容。前两版为英文，第三版改为中文强调刀法与构图。

### v1 提示词

```text
Use case: historical-scene. One original horizontal 16:9 Chinese New Woodcut Movement book illustration in the spirit of mid-century 1950s Chinese relief printmaking. Black ink on plain white. Genuine confident hand-cut raised black forms, broad solid ink masses, irregular tapered white V-gouge cuts and rounded U-gouge hatching, blunt economical marks, wood-grain roughness within the carved marks only. Tonality comes exclusively from cut spacing. Humble believable lived-in scene, restrained asymmetric composition, not a poster and not a finely engraved banknote. NO grayscale shading, gradients, stippling, airbrush, photographic light, blur, shiny rendering, calligraphic swirls or smooth vector outlines. No text of any kind, signs, lettering, numbers, signatures, seals, labels, frames or panel divisions. Small simplified people in side/back view only, modest hands hidden where possible, clear natural anatomy. IMPORTANT framing: zoomed-out panorama; all story-essential subjects completely within middle 70% of canvas both horizontally and vertically (15% crop-safe scene margin on EACH side); outer ground/sky/background expendable. Single complete landscape scene, not collage. Aim 2560x1440. One unified landscape with a vertical top-to-bottom spatial cutaway sequence, NOT three separate panels: sky above land above underground. Upper portion: open white sky with a few long blunt carved flowing clouds and ONE small eagle in clear soaring silhouette. Middle: grassland with a stand of dark conifer forest, distant mountain range, one small felt yurt and a small herd of THREE proportionate horses, no riders. Lower: earth is openly cut away in cross-section below a continuous curved ground line, showing broad coal seams, angular mineral veins and a few modest quartz crystal clusters in rough carved geological strata. Underground forms must look like geology rather than waves or machine parts. Important eagle, yurt, horses, forest center, coal and crystal groups in middle 70%; outer terrain/sky/strata expendable. Broad black masses and simple bold white V-gouges; spacious simple composition, balanced but not symmetric. No arrows, keys, labels, borders or scientific typography.
```

### v2 提示词

```text
Use case: historical-scene. One original horizontal 16:9 Chinese New Woodcut Movement book illustration in the spirit of mid-century 1950s Chinese relief printmaking. Black ink on plain white. Genuine confident hand-cut raised black forms, broad solid ink masses, irregular tapered white V-gouge cuts and rounded U-gouge hatching, blunt economical marks, wood-grain roughness within the carved marks only. Tonality comes exclusively from cut spacing. Humble believable lived-in scene, restrained asymmetric composition, not a poster and not a finely engraved banknote. NO grayscale shading, gradients, stippling, airbrush, photographic light, blur, shiny rendering, calligraphic swirls or smooth vector outlines. No text of any kind, signs, lettering, numbers, signatures, seals, labels, frames or panel divisions. Small simplified people in side/back view only, modest hands hidden where possible, clear natural anatomy. IMPORTANT framing: zoomed-out panorama; all story-essential subjects completely within middle 70% of canvas both horizontally and vertically (15% crop-safe scene margin on EACH side); outer ground/sky/background expendable. Single complete landscape scene, not collage. Aim 2560x1440. Show the air in the sky, the forest on the ground, and treasures beneath the earth as ONE coherent wide Chinese woodcut landscape, arranged in three levels from top to bottom, without panel borders. Sky: a few broad white/black hand-gouged cloud ribbons and a single small eagle, generously below top edge. Land: an open stretch of grassland leading to an uneven dark stand of conifers and distant mountains, one plain felt yurt and THREE tiny horses grazing in clean side silhouettes, safely centered. Beneath the ground: a convincing simple cutaway of layered rock, one thick BLACK COAL SEAM, branching thin white mineral veins, two small angular crystal clusters. Keep underground readable and restrained, not fantastical or gem-filled. Use large uneven black shapes and economical angular carved hatching, avoid intricate engraving or constant texture. All meaningful subjects inside central 70% width and height, expendable sky, empty land or rock around perimeter.
```

### v3 提示词

```text
中国1950年代新兴木刻黑白阳刻书籍插图，参照古元、彦涵、李桦、力群、赵延年的质朴刀法气质。横幅16:9，一幅完整画面。像木板用三角刀和圆口刀真正手刻：概括厚实大黑块，宽、短、不规则的留白刀痕，疏密有节制，少刻细节。不是照片转素描、精密铜版、钢笔线描、电脑矢量图。纯黑纯白，不加纸纹，无灰色灰阶渐变、无柔光。画面绝无文字、数字、招牌、签名、印章，建筑只画空白墙面。视野拉远，所有重要物件集中在横向20%-80%、纵向20%-80%的区域，四边只留可裁切的环境。自然不对称，无边框。“天上的空气，地上的森林，地下的宝藏”：同一横幅风景从上到下三层，不是分格漫画。上方是白天、两组简洁的刀刻流云和一只小鹰，小鹰在画面纵向20%-30%位置。中间草原、一片位置不对称的深黑针叶森林、远山，一个小毡房和三匹小小的侧面马；毡房和马群都在横向35%-70%之间，马的四肢简洁合理。下方是地层剖面，几层厚黑煤层、少量曲折矿脉、两个大小不同不对称分布的晶体小簇，晶体在画面横向35%与65%、纵向70%-80%区域。地下岩层用宽刀排线，避免密集细线、不要像珠宝广告。所有主体不贴四边，四周仅作云、山、草原、岩层的延伸。大胆简洁、厚实而朴素，别画成逼真科学渲染图。
```

## 后期与证据

所有版本的生成方式、原始生成文件路径与完整提示词另存 `generation.json`。原图、成品和审核图分别保留，不用审核图覆盖交付图。

后期固定阈值155；UnsharpMask 半径1.0、强度85%、门限3；只去除面积小于4像素的孤立黑色连通分量。没有使用会磨平轮廓的开闭运算，也没有描摹替换人物或动物。

纸色 `#EDE5D4` 的每通道变化限制在±2；墨色围绕 `#1C1A17` 小幅变化（−2至+3）。少量漏白仅放在距边缘大于1.5像素的厚墨内部，尽量保留细线。每题使用固定随机种子20261020加题材序号。

`qa/validation.json` 含每张的实际清噪像素数、漏白数量、SHA-256、尺寸、色值与裁切框。复现校验另见 `qa/reproducibility.json`。这些数字证明的是文件与处理流程的性质，伪文字、肢体和风格由上述目视审核负责。
