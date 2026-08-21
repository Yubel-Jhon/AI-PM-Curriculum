# 变更记录（CHANGELOG）

## [v0.3.0] - 2026-08-21（develop，未发布）

- 重构目录：`product/` + `skill/` 的 12 个浅层 README 并入 `curriculum/`（深度详解），删除重复骨架
- `deep/` → `curriculum/`，按 ①→⑪ 顺序重排为 6 个文档，折入原 README 独有术语
- 新增 `cases/`（PRD 14 章方法 + 微信 AI 打车助手 BRD/MRD/FSD/PRD 案例）
- 新增 `interview/`（桌面「面试方法论 + 高频题刷题卡」入库）
- `ppt/` 精简：删脚本/图表/预览，只留 2 个 pptx + 内容稿
- 删除 `wechatauto_logs/`、`xmind/` 日志目录

## [v0.2.0] - 2026-08-14（develop，未发布）

- 每个章节文件夹内新增 `思维导图.png`（对应板块导图图片化，嵌入各 README）
- 删除独立 `xmind/` 目录，导图与章节文档合并为一处

## [v0.1.0] - 2026-08-14

- 初始化目录结构：`product/`（通用底座 ①–⑦ + 附录）+ `skill/`（AI 增补层 ⑧–⑪）
- 建立分支规范：`main` = 发布 / `develop` = 开发，tag 基于 main

## 分支规范（git flow）

- `develop`：日常改动都在这，基于 main 拉取
- `main`：只接受 develop 合并，发布后打 tag
- 流程：develop 改 → merge 回 main → main 打 tag
