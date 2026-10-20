# 任务 A 交接（新会话接手）

上一位执行者因模型容量问题中断。请先读：`BRIEF.md`、`..\COMMON.md`、`FEEDBACK_1.md`、`FEEDBACK_2.md`、`REVIEW.md`，以及本目录下的生成脚本（`build_leadtype.py` 等）和 `.blend` 文件，弄清现有工程状态。

当前结论：
1. **A1 `leadtype_title` 已通过**（以 `review/round6/title_*.png` 与 `review/readability/` 的状态为准）。不要再改造型和镜头，直接按 COMMON 的 GPU 锁规范渲染终版 210 帧到 `D:\MAOGAI\assets\renders\leadtype_title\frames\`，并出 `still_4k.png`、`preview.mp4`、`contact.png`。
2. **A2 `leadtype_poli` 未通过**，按 `FEEDBACK_2.md` 重做：两枚铅字侧卧在旧纸上、字面朝镜头，朱红印迹在前方，30° 俯角微距，焦点从字面移到印迹，画面下三分之一保持安静。先出首/中/尾低分辨率三帧自审（存 `review/round7/`），确认后渲终版 180 帧到 `assets\renders\leadtype_poli\frames\`。
3. 先渲 A1 终版，再做 A2（A1 渲染期间可以并行写 A2 的脚本，但 GPU 测试渲染要等 A1 结束或在锁空闲时进行）。
4. 完成后更新 `REVIEW.md` 与 `REPORT.md`。
