# 变更记录（CHANGELOG）

## [v0.1.0] - 2026-08-14

- 初始化目录结构：`product/`（通用底座 ①–⑦ + 附录）+ `skill/`（AI 增补层 ⑧–⑪）
- 建立分支规范：`main` = 发布 / `develop` = 开发，tag 基于 main

## 分支规范（git flow）

- `develop`：日常改动都在这，基于 main 拉取
- `main`：只接受 develop 合并，发布后打 tag
- 流程：develop 改 → merge 回 main → main 打 tag
