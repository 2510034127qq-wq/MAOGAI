# B 杆秤：编辑与重现

本目录的 `steelyard.blend` 含两个可直接选择的独立场景：

- `B1 · steelyard_balance`：第 1–300 帧，30fps。
- `B2 · steelyard_detail`：第 1–150 帧，30fps，复用 B1 最终平衡姿态。

全部模型、材质和三股麻绳均由 `build_steelyard.py` 创建。动画已经烘焙为普通关键帧，打开文件即可拖动时间轴，无需插件、外部贴图、Python handler 或联网。

## 重现命令

在 PowerShell 中运行。正式帧输出会自动等待共享 GPU 锁；锁失效时间为 90 分钟，渲染每帧刷新锁，退出时释放。

```powershell
$blenderExe = 'D:\UE\Tools\blender.exe'
$taskDir = 'D:\MAOGAI\blender\B_steelyard'

# 从脚本重新创建场景
& $blenderExe --background --factory-startup --python "$taskDir\build_steelyard.py"

# 低清首、中、尾与微距检查，输出五张 960×540 静帧
& $blenderExe --background "$taskDir\steelyard.blend" --python "$taskDir\render_steelyard.py" -- tests_manual

# 独立场景检查
& $blenderExe --background "$taskDir\steelyard.blend" --python "$taskDir\audit_scene.py"

# 正式渲染：B1、B2、B1最终4K静帧
& $blenderExe --background "$taskDir\steelyard.blend" --python "$taskDir\render_steelyard.py" -- final

# 编码、联系表、逐帧文件与视频解码检查
python "$taskDir\finish_delivery.py"
```

渲染器支持中断后继续，校验镜头目录中的 `render_source.json`，并检查PNG结束标记后跳过已完成帧。**修改模型、灯光或动画后，应先将旧 `frames` 目录及对应 `render_source.json` 一起移至自行指定的备份位置，再渲染，避免新旧帧混用。** 同一场景和同一脚本的中断恢复才可直接续渲。

需要正常停渲时，可在本任务目录创建名为 `STOP_RENDER` 的文件。渲染器会在当前帧结束后退出并释放GPU锁；继续渲染前移走该标记。

本次最终场景与源脚本的 SHA-256 记录在 `render_source_manifest.json`；各帧哈希记录在两个 `*_frame_hashes.json` 中。

## 调整入口

- 秤杆长度、直径、支点位置：脚本头部常量与 `beam_radius()`。
- 木纹与金属旧化：`make_materials()`，均为本地程序纹理。
- 秤盘与齿轮：`build_pan()`。
- 绳套、实心梨形秤砣：`build_weight()`；滑动时绳体不缩放。
- 物件估算质量：`derive_masses()`，以主要物件的净体积乘估算密度。
- 力矩、惯性、阻尼：`model_motion()`；参数与逐帧数据见 `motion_audit.json`。
- 镜头、焦点、光圈：`main()` 中两个相机的关键帧。

## 物理模型边界

这是含画外持秤者稳定作用的受控称量演示。起始状态“秤砣靠近支点、重物侧下沉约12°并静止”需要外部稳定力矩，不能作为理想自由铰接杆秤的静力平衡。本场景明确将这项作用写入力矩积分，没有以线性插值直接指定整段杆角。

按导演审核意见1重制后，盘和齿轮约为秤砣的 4.82 倍重；最终水平时，较远的秤砣力矩与木杆自重力矩共同平衡左侧负载力矩。质量为主要物件体积与估算密度的结果，不是文物实测称量值。

## 审核与交付记录

- `REVIEW.md`：逐轮发现、修改与复审证据。
- `REPORT.md`：中文交付报告、清单、渲染时间及已知不足。
- `geometry_audit.json`：主要实体净体积和估算质量。
- `rig_audit.json`：300 帧绳长、悬挂姿态、相机和 B2 姿态核查。
- `delivery_audit.json`：完整序列、视频、4K静帧及时间统计。
- `review/`：保留每轮低清证据，便于对比修改前后。
