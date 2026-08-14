# AI-PM-Curriculum

产品经理就业知识体系 · AI 增补版课程仓库。

## 目录结构（以内容为主）

```
product/   产品经理相关 —— 通用底座（板块①–⑦ + 全景 + 附录）
skill/     skill 相关  —— AI 增补层（板块⑧–⑪）
xmind/     全书总结导图 —— 思维导图成品 + 源文件（.md）
```

## 分支规范（git flow）

- `main`：主干 / 发布分支。只接受 `develop` 的 merge，发布后打 tag。
- `develop`：开发分支。基于 `main` 拉取，开发增量特性。

流程：`develop` 基于 `main` 拉取 → 开发增量特性 → merge 回 `main` → `main` 发布 → 基于 `main` 打 tag。

> 内容以目录划分，`main` / `develop` 的区分以 branch 划分，二者不互相迁移。

## 全景

```
通用底座（product/）：
  ① 需求  ② 规划设计  ③ 项目管理  ④ 数据分析  ⑤ 商业战略
  翻译     落地         交付         验证         方向
  ⑥ 沟通协作（放大器）→ 让 ①–⑤ 推得动
  ⑦ 学习与自我修养（底色）→ 决定天花板

AI 增补层（skill/）：
  ⑧ AI 技术认知          → 判断「能不能做」
  ⑨ 模型评估与数据闭环    → 验证「做得好不好」
  ⑩ 信任安全与伦理合规    → 守住「底线」
  ⑪ AI 产品经济学        → 算清「值不值、赚不赚」
```

## 目录导航

- [product/](product/README.md) — 通用底座（产品经理相关）
  - [00 全景与使用说明](product/00-全景与使用说明/README.md)
  - [01 需求能力](product/01-需求能力/README.md)
  - [02 规划设计](product/02-规划设计/README.md)
  - [03 项目管理](product/03-项目管理/README.md)
  - [04 数据分析](product/04-数据分析/README.md)
  - [05 商业战略](product/05-商业战略/README.md)
  - [06 沟通协作](product/06-沟通协作/README.md)
  - [07 学习与自我修养](product/07-学习与自我修养/README.md)
  - [附录](product/附录/README.md)
- [skill/](skill/README.md) — AI 增补层（skill 相关）
  - [08 AI 技术认知](skill/08-AI技术认知/README.md)
  - [09 模型评估与数据闭环](skill/09-模型评估与数据闭环/README.md)
  - [10 信任安全与伦理合规](skill/10-信任安全与伦理合规/README.md)
  - [11 AI 产品经济学](skill/11-AI产品经济学/README.md)
- [xmind/](xmind/README.md) — 全书总结导图（3 张 sheet：板块式 / 大表 / 阶段式）
