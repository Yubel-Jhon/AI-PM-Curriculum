# -*- coding: utf-8 -*-
"""
小红书 AI-PM 面经 → 图谱生成器（一次生成两个产物）

    1) 小红书面试经验图谱.html        —— 双击用浏览器打开（推荐）
        单页滚动：上半「数据流程」(5 步竖向时间线) + 下半「知识图谱」(左→右分层树)
    2) 小红书面试经验知识图谱.gexf     —— 给 Gephi 用

数据来源：interview/面试方法论.md 第 5.7 节（小红书 39 笔记 + 194 评论提炼成品，
原始文件 xhs_notes_full.txt 已丢失，重抓步骤见 5.7 节开头的「数据流程」）。

用法：
    python build_xhs_graph.py
"""

import os
import json

# ---------------------------------------------------------------
# 知识图谱节点: (id, label, type, module, layer, desc, file)
#   type: root / source / category / company / topic / qtype
#   layer 用于给 category 上色：方法论(绿) / 面经(灰)
# ---------------------------------------------------------------
NODES = [
    ("root", "小红书 AI-PM 面经", "root", "总纲", "总纲",
     "小红书「AI产品经理面经」39 笔记 + 194 评论提炼成品：面试官视角 + 字节两面 + 2026 新考点", ""),

    # 数据来源 + 6 个小节
    ("cat-source", "数据来源 · 小红书", "source", "来源", "来源",
     "MediaCrawler 抓「AI产品经理面经」39 笔记 + 194 评论（原始文件 xhs_notes_full.txt 已丢，重抓见 5.7 开头）", ""),
    ("cat-interviewer", "面试官视角红黑榜", "category", "5.7.1", "方法论",
     "❌ 新手 vs ✅ 专业答法对照：AI 产品 5 问 + 通用 PM 5 问，可直接背", "interview/面试方法论.md"),
    ("cat-project", "讲项目三层法", "category", "5.7.2", "方法论",
     "功能层 → 设计层 → 工程交付层；模型选型正确讲法（多数人停第一层）", "interview/面试方法论.md"),
    ("cat-agent", "Agent 四层设计", "category", "5.7.3", "方法论",
     "规划 / 工具 / 记忆 / 状态评估四层 + 不确定性管理", "interview/面试方法论.md"),
    ("cat-byte", "字节两面全录", "category", "5.7.4", "面经",
     "面 A 智能客服 13 题（已 oc）+ 面 B Agent/Skills 11 题", "interview/面试方法论.md"),
    ("cat-2026", "2026 新考点", "category", "5.7.5", "面经",
     "27 届连面 9 场：Skills / vibe coding / Agent vs Workflow / AI 工具认知", "interview/面试方法论.md"),
    ("cat-others", "其他公司速览", "category", "5.7.6", "面经",
     "AI 独角兽 / 追觅 / 百度文心 + 5 天速成清单 + 简历包装", "interview/面试方法论.md"),

    # 来源人 / 公司
    ("co-interviewer", "面试官", "company", "通用", "来源人",
     "上午面 6 人复盘 +「听到这几句话基本都 pass」——视角最值钱", "interview/面试方法论.md"),
    ("co-byte", "字节", "company", "字节", "公司",
     "抖音电商智能客服（已 oc）+ 大模型产品实习（Agent/Skills 方向）", "interview/面试方法论.md"),
    ("co-27", "27 届转 AI-PM", "company", "通用", "来源人",
     "连面 9 场心得，2026 新考点一手拷打实录", "interview/面试方法论.md"),
    ("co-aiuc", "AI 独角兽", "company", "AI独角兽", "公司",
     "大模型 PM：一面 mentor + 二面 leader，伦理 + 数据质量二面标配", "interview/面试方法论.md"),
    ("co-dreame", "追觅科技", "company", "追觅", "公司",
     "智能硬件 AI-PM：家庭/商用场景落地 + 具身智能壁垒", "interview/面试方法论.md"),
    ("co-baidu", "百度文心一言", "company", "百度", "公司",
     "已 offer，0 互联网实习靠真实使用体验 + 横向对比上岸", "interview/面试方法论.md"),

    # 考点概念
    ("t-rag", "RAG / 微调选型", "topic", "选型", "考点",
     "FAQ vs 向量库分工、为什么大模型不微调、RAG+Rerank 三步", "interview/面试方法论.md"),
    ("t-faq", "FAQ vs 向量库", "topic", "RAG", "考点",
     "FAQ 管高频标准问（确定/快/可控），向量库管长尾模糊问，互补兜底", "interview/面试方法论.md"),
    ("t-evalset", "评测集构建", "topic", "评估", "考点",
     "定范围 → 定标准 → 交叉校验；技术指标必须绑业务价值", "interview/面试方法论.md"),
    ("t-mock", "转人工率 mock 防护", "topic", "智能客服", "考点",
     "解决率/满意度/一次解决率交叉校验，别只看单一转人工率", "interview/面试方法论.md"),
    ("t-fresh", "知识时效性", "topic", "智能客服", "考点",
     "知识库更新策略，保证智能客服答到最新的", "interview/面试方法论.md"),
    ("t-agent", "Agent 设计 / 不确定性管理", "topic", "Agent", "考点",
     "规划/工具/记忆/状态评估四层；核心=对不确定性的管理", "interview/面试方法论.md"),
    ("t-workflow", "Workflow vs Agent", "topic", "Agent", "考点",
     "确定性（预设流程）vs 自主性（自主规划），2026 必问", "interview/面试方法论.md"),
    ("t-skills", "Skills", "topic", "Agent", "考点",
     "可复用能力封装（指令+工具+示例），每场必问", "interview/面试方法论.md"),
    ("t-vibe", "vibe coding", "topic", "工具", "考点",
     "自然语言让 AI 写代码，适合 demo 不适合生产", "interview/面试方法论.md"),
    ("t-aitools", "AI 工具认知", "topic", "工具", "考点",
     "coze / 龙虾小龙虾，追当下最火工具，常备一个万能答案", "interview/面试方法论.md"),
    ("t-cot", "思维链 CoT", "topic", "技术", "考点",
     "什么场景做 CoT、预设关键步骤", "interview/面试方法论.md"),
    ("t-badcase", "badcase 分析", "topic", "评估", "考点",
     "举例到用户原输入 vs 误理解；带问题定位+归因+建议再找算法", "interview/面试方法论.md"),
    ("t-ethics", "伦理隐私 + 数据质量", "topic", "安全", "考点",
     "AI 独角兽二面标配：伦理隐私处理 + 数据质量处理", "interview/面试方法论.md"),
    ("t-dataloop", "数据闭环", "topic", "数据", "考点",
     "采集→清洗→标注→评估→迭代，真实数据喂飞轮", "interview/面试方法论.md"),

    # 题型
    ("qt-concept", "概念题", "qtype", "题型", "题型",
     "RAG / Agent / Skills / Workflow：类比+定义+选型理由+边界", "interview/面试方法论.md"),
    ("qt-project", "项目题", "qtype", "题型", "题型",
     "介绍项目 + 难点 + 为什么这么决策 + 数据怎么看", "interview/面试方法论.md"),
    ("qt-plan", "方案/业务题", "qtype", "题型", "题型",
     "设计 Agent / 付费权益 / 判断该不该做", "interview/面试方法论.md"),
]

EDGES = [
    # 根 → 小节/来源
    ("root", "cat-source", "属于"),
    ("root", "cat-interviewer", "属于"),
    ("root", "cat-project", "属于"),
    ("root", "cat-agent", "属于"),
    ("root", "cat-byte", "属于"),
    ("root", "cat-2026", "属于"),
    ("root", "cat-others", "属于"),

    # 来源 → 公司
    ("cat-source", "co-interviewer", "来源"),
    ("cat-source", "co-byte", "来源"),
    ("cat-source", "co-27", "来源"),
    ("cat-source", "co-aiuc", "来源"),
    ("cat-source", "co-dreame", "来源"),
    ("cat-source", "co-baidu", "来源"),

    # 小节 → 公司（涉及）
    ("cat-interviewer", "co-interviewer", "涉及"),
    ("cat-project", "co-interviewer", "涉及"),
    ("cat-agent", "co-interviewer", "涉及"),
    ("cat-byte", "co-byte", "涉及"),
    ("cat-2026", "co-27", "涉及"),
    ("cat-others", "co-aiuc", "涉及"),
    ("cat-others", "co-dreame", "涉及"),
    ("cat-others", "co-baidu", "涉及"),

    # 公司 → 考点（考察）
    ("co-interviewer", "t-rag", "考察"),
    ("co-interviewer", "t-evalset", "考察"),
    ("co-interviewer", "t-badcase", "考察"),
    ("co-interviewer", "t-dataloop", "考察"),
    ("co-byte", "t-rag", "考察"),
    ("co-byte", "t-faq", "考察"),
    ("co-byte", "t-evalset", "考察"),
    ("co-byte", "t-mock", "考察"),
    ("co-byte", "t-fresh", "考察"),
    ("co-byte", "t-agent", "考察"),
    ("co-byte", "t-cot", "考察"),
    ("co-byte", "t-badcase", "考察"),
    ("co-byte", "t-skills", "考察"),
    ("co-byte", "t-dataloop", "考察"),
    ("co-27", "t-workflow", "考察"),
    ("co-27", "t-skills", "考察"),
    ("co-27", "t-vibe", "考察"),
    ("co-27", "t-aitools", "考察"),
    ("co-27", "t-agent", "考察"),
    ("co-aiuc", "t-rag", "考察"),
    ("co-aiuc", "t-ethics", "考察"),
    ("co-aiuc", "t-dataloop", "考察"),
    ("co-dreame", "t-agent", "考察"),
    ("co-baidu", "t-aitools", "考察"),

    # 方法论小节 → 考点（提炼）
    ("cat-interviewer", "t-rag", "提炼"),
    ("cat-interviewer", "t-evalset", "提炼"),
    ("cat-interviewer", "t-badcase", "提炼"),
    ("cat-interviewer", "t-dataloop", "提炼"),
    ("cat-project", "t-rag", "提炼"),
    ("cat-project", "t-evalset", "提炼"),
    ("cat-project", "t-badcase", "提炼"),
    ("cat-agent", "t-agent", "提炼"),
    ("cat-agent", "t-workflow", "提炼"),
    ("cat-agent", "t-cot", "提炼"),
    ("cat-agent", "t-skills", "提炼"),

    # 考点 → 题型
    ("t-rag", "qt-concept", "题型"),
    ("t-faq", "qt-concept", "题型"),
    ("t-agent", "qt-concept", "题型"),
    ("t-agent", "qt-plan", "题型"),
    ("t-workflow", "qt-concept", "题型"),
    ("t-skills", "qt-concept", "题型"),
    ("t-cot", "qt-concept", "题型"),
    ("t-ethics", "qt-concept", "题型"),
    ("t-vibe", "qt-plan", "题型"),
    ("t-aitools", "qt-plan", "题型"),
    ("t-mock", "qt-plan", "题型"),
    ("t-fresh", "qt-plan", "题型"),
    ("t-dataloop", "qt-plan", "题型"),
    ("t-badcase", "qt-project", "题型"),
    ("t-evalset", "qt-concept", "题型"),
]

# ---------------------------------------------------------------
# 数据流程（取数据 → 分析 → 展示），渲染为竖向时间线
# ---------------------------------------------------------------
PIPELINE = [
    {"num": "①", "title": "取数据", "color": "#22d3ee",
     "actions": [
         "数据源：小红书，搜「AI产品经理面经」",
         "工具：MediaCrawler + 登录 cookie（Scrapling 静态抓不动小红书）",
         "抓取：39 条笔记 + 194 条评论",
     ],
     "output": "xhs_notes_full.txt（原始笔记 + 评论）"},
    {"num": "②", "title": "清洗", "color": "#f97316",
     "actions": [
         "去广告 / 去重复 / 去无关",
         "按三类打标：面试官视角 / 附答案 / 真实挂点，其余丢弃",
     ],
     "output": "高价值帖子子集"},
    {"num": "③", "title": "抽取", "color": "#f59e0b",
     "actions": [
         "抽 ❌✅ 红黑榜话术（新手答 vs 专业答）",
         "抽题目清单 + 追问链 + 雷区",
     ],
     "output": "结构化题目 / 话术表"},
    {"num": "④", "title": "归类", "color": "#16a34a",
     "actions": [
         "归纳 6 块：红黑榜 / 三层法 / Agent四层 / 字节两面 / 2026新考点 / 公司速览",
         "与牛客面经、刷题卡交叉验证，标证据强度（一手口述 > 二手转述）",
     ],
     "output": "分类体系 5.7.1–5.7.6"},
    {"num": "⑤", "title": "落地", "color": "#2dd4bf",
     "actions": [
         "文字 → 面试方法论.md 5.7",
         "结构化 → 高频题刷题卡.json（来源=小红书）",
         "可视化 → 小红书面试经验图谱.html",
     ],
     "output": "3 个交付物"},
]

RESCRAPE_NOTE = (
    "⚠️ 原始文件 xhs_notes_full.txt 已丢失。重抓：① pip install MediaCrawler；"
    "② 浏览器登录小红书 → F12 拿 cookie 填进 config；③ 搜「AI产品经理面经」批量抓 note + comment；"
    "④ 落盘后按上面 ②→⑤ 处理。"
)

_ROOT = os.path.dirname(os.path.abspath(__file__))


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def build_gexf():
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">')
    lines.append('  <meta lastmodifieddate="2026-08-22">')
    lines.append('    <creator>AI-PM-Curriculum build_xhs_graph.py</creator>')
    lines.append('    <description>小红书 AI 产品经理面经知识图谱</description>')
    lines.append('  </meta>')
    lines.append('  <graph mode="static" defaultedgetype="directed">')
    lines.append('    <attributes class="node">')
    lines.append('      <attribute id="0" title="type" type="string"/>')
    lines.append('      <attribute id="1" title="module" type="string"/>')
    lines.append('      <attribute id="2" title="layer" type="string"/>')
    lines.append('      <attribute id="3" title="desc" type="string"/>')
    lines.append('      <attribute id="4" title="file" type="string"/>')
    lines.append('    </attributes>')
    lines.append('    <attributes class="edge">')
    lines.append('      <attribute id="0" title="rel" type="string"/>')
    lines.append('    </attributes>')
    lines.append('    <nodes>')
    for nid, label, ntype, module, layer, desc, fpath in NODES:
        lines.append(f'      <node id="{nid}" label="{esc(label)}">')
        lines.append('        <attvalues>')
        lines.append(f'          <attvalue for="0" value="{esc(ntype)}"/>')
        lines.append(f'          <attvalue for="1" value="{esc(module)}"/>')
        lines.append(f'          <attvalue for="2" value="{esc(layer)}"/>')
        lines.append(f'          <attvalue for="3" value="{esc(desc)}"/>')
        lines.append(f'          <attvalue for="4" value="{esc(fpath)}"/>')
        lines.append('        </attvalues>')
        lines.append('      </node>')
    lines.append('    </nodes>')
    lines.append('    <edges>')
    for i, (src, tgt, rel) in enumerate(EDGES):
        lines.append(f'      <edge id="{i}" source="{src}" target="{tgt}" label="{esc(rel)}">')
        lines.append('        <attvalues>')
        lines.append(f'          <attvalue for="0" value="{esc(rel)}"/>')
        lines.append('        </attvalues>')
        lines.append('      </edge>')
    lines.append('    </edges>')
    lines.append('  </graph>')
    lines.append('</gexf>')
    return "\n".join(lines)


def build_html():
    data = []
    for nid, label, ntype, module, layer, desc, fpath in NODES:
        absfile = os.path.join(_ROOT, fpath).replace("\\", "/") if fpath else ""
        data.append({
            "id": nid, "label": label, "type": ntype, "module": module,
            "layer": layer, "desc": desc, "file": fpath, "absfile": absfile,
        })
    edges = [{"source": s, "target": t, "rel": r} for (s, t, r) in EDGES]
    payload = {"nodes": data, "edges": edges}
    json_str = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    pipeline_str = json.dumps(PIPELINE, ensure_ascii=False)
    note_str = json.dumps(RESCRAPE_NOTE, ensure_ascii=False)

    html = HTML_TEMPLATE.replace("__DATA__", json_str)
    html = html.replace("__PIPELINE__", pipeline_str)
    html = html.replace("__RESCRAPE_NOTE__", note_str)
    return html


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>小红书 AI-PM 面经图谱</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; background: #0f172a; color: #e2e8f0; }

  header { position: sticky; top: 0; z-index: 10; padding: 12px 20px; background: #1e293b; border-bottom: 1px solid #334155; display: flex; align-items: center; gap: 16px; }
  header h1 { font-size: 16px; font-weight: 600; }
  header .sub { font-size: 12px; color: #94a3b8; }
  header nav { margin-left: auto; display: flex; gap: 6px; }
  header nav a { color: #cbd5e1; text-decoration: none; font-size: 13px; padding: 6px 12px; border-radius: 6px; border: 1px solid #475569; }
  header nav a:hover { background: #334155; }

  section { max-width: 1180px; margin: 0 auto; padding: 32px 20px; }
  .sec-title { font-size: 18px; font-weight: 600; margin-bottom: 4px; }
  .sec-desc { font-size: 13px; color: #94a3b8; margin-bottom: 24px; }

  /* ---------- 数据流程：竖向时间线 ---------- */
  .timeline { position: relative; padding-left: 36px; max-width: 880px; }
  .timeline::before { content: ""; position: absolute; left: 9px; top: 8px; bottom: 8px; width: 2px; background: #334155; }
  .step { position: relative; margin-bottom: 22px; }
  .step .dot { position: absolute; left: -33px; top: 4px; width: 14px; height: 14px; border-radius: 50%; border: 2px solid #0f172a; }
  .step .card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 14px 18px; }
  .step h3 { font-size: 15px; margin-bottom: 8px; }
  .step ul { list-style: none; }
  .step li { font-size: 13px; color: #cbd5e1; line-height: 1.75; padding-left: 14px; position: relative; }
  .step li::before { content: "·"; position: absolute; left: 2px; color: #64748b; }
  .step .out { margin-top: 10px; font-size: 13px; color: #e2e8f0; background: #0f172a; border-radius: 6px; padding: 7px 12px; }
  .rescrape { max-width: 880px; margin-left: 36px; margin-top: 6px; background: #422006; border: 1px solid #92400e; border-radius: 10px; padding: 12px 16px; font-size: 13px; color: #fdba74; line-height: 1.7; }

  /* ---------- 知识图谱：分层树 ---------- */
  .graph-shell { display: flex; gap: 16px; align-items: stretch; }
  .graph-box { flex: 1; min-width: 0; height: 620px; border: 1px solid #334155; border-radius: 10px; background: #0b1220; overflow: hidden; position: relative; }
  .graph-box svg { width: 100%; height: 100%; display: block; }
  .legend { position: absolute; top: 10px; left: 10px; background: rgba(15,23,42,.92); border: 1px solid #334155; border-radius: 8px; padding: 8px 12px; font-size: 11px; color: #cbd5e1; }
  .legend .row { display: flex; align-items: center; gap: 6px; margin: 3px 0; }
  .legend .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
  .hint { position: absolute; bottom: 10px; right: 12px; font-size: 11px; color: #64748b; }
  .panel { width: 330px; height: 620px; background: #1e293b; border: 1px solid #334155; border-radius: 10px; overflow-y: auto; padding: 16px; }
  .panel .empty { color: #64748b; font-size: 13px; margin-top: 12px; }
  .panel h2 { font-size: 17px; margin-bottom: 6px; line-height: 1.4; }
  .badges { margin: 8px 0; }
  .badge { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 10px; margin-right: 6px; margin-bottom: 4px; background: #334155; color: #cbd5e1; }
  .panel .desc { font-size: 13.5px; line-height: 1.7; color: #cbd5e1; background: #0f172a; border-radius: 8px; padding: 12px; margin: 10px 0; }
  .panel .sec-title { font-size: 12px; color: #94a3b8; letter-spacing: 1px; margin: 14px 0 6px; }
  .rel-list { list-style: none; }
  .rel-list li { font-size: 13px; padding: 5px 8px; border-radius: 6px; cursor: pointer; margin-bottom: 2px; display: flex; align-items: center; gap: 6px; }
  .rel-list li:hover { background: #334155; }
  .rel-tag { font-size: 11px; padding: 1px 6px; border-radius: 8px; flex-shrink: 0; }
  .file-row { font-size: 12px; color: #94a3b8; word-break: break-all; margin-top: 8px; }
  .tooltip { position: fixed; pointer-events: none; background: #0f172a; border: 1px solid #334155; border-radius: 6px; padding: 6px 9px; font-size: 12px; max-width: 260px; display: none; z-index: 20; }
</style>
</head>
<body>
<header>
  <h1>小红书 AI-PM 面经图谱</h1>
  <span class="sub">39 笔记 + 194 评论 → 面试官视角 / 字节两面 / 2026 新考点</span>
  <nav><a href="#flow">① 数据流程</a><a href="#graph">② 知识图谱</a></nav>
</header>

<section id="flow">
  <div class="sec-title">从取数据到分析展示</div>
  <div class="sec-desc">小红书面经怎么从一堆帖子，变成可背的弹药 + 可交互的图谱</div>
  <div class="timeline" id="timeline"></div>
  <div class="rescrape" id="rescrapeNote"></div>
</section>

<section id="graph">
  <div class="sec-title">知识图谱</div>
  <div class="sec-desc">左→右：小节 → 公司/来源人 → 考点 → 题型。点任意节点看详情，滚轮缩放、拖拽平移。</div>
  <div class="graph-shell">
    <div class="graph-box" id="graphBox">
      <div class="legend" id="legend"></div>
      <div class="hint">滚轮缩放 · 拖拽平移</div>
    </div>
    <div class="panel" id="panel">
      <div class="empty">👈 点图上的任意一个节点，这里显示它的考点/详情。</div>
    </div>
  </div>
</section>

<div class="tooltip" id="tooltip"></div>

<script>
const PIPELINE = __PIPELINE__;
const RESCRAPE_NOTE = __RESCRAPE_NOTE__;
const DATA = __DATA__;
const nodes = DATA.nodes;
const edges = DATA.edges;
const byId = {};
nodes.forEach(n => byId[n.id] = n);

/* ---------- 数据流程时间线 ---------- */
(function renderFlow() {
  document.getElementById('timeline').innerHTML = PIPELINE.map(s => `
    <div class="step">
      <div class="dot" style="background:${s.color}"></div>
      <div class="card" style="border-left:3px solid ${s.color}">
        <h3 style="color:${s.color}">${s.num} ${s.title}</h3>
        <ul>${s.actions.map(a => `<li>${a}</li>`).join('')}</ul>
        <div class="out">→ 产出：<b style="color:${s.color}">${s.output}</b></div>
      </div>
    </div>`).join('');
  document.getElementById('rescrapeNote').textContent = RESCRAPE_NOTE;
})();

/* ---------- 知识图谱：分层树布局 ---------- */
const adj = {};
nodes.forEach(n => adj[n.id] = []);
edges.forEach(e => {
  adj[e.source].push({other: e.target, rel: e.rel, dir: 'out'});
  adj[e.target].push({other: e.source, rel: e.rel, dir: 'in'});
});

const TYPE_RANK = {root: 0, source: 1, category: 1, company: 2, topic: 3, qtype: 4};
function colorOf(n) {
  if (n.type === 'root') return '#f8fafc';
  if (n.type === 'source') return '#22d3ee';
  if (n.type === 'category') return n.layer === '方法论' ? '#16a34a' : '#64748b';
  if (n.type === 'company') return '#a855f7';
  if (n.type === 'topic') return '#f97316';
  if (n.type === 'qtype') return '#eab308';
  return '#94a3b8';
}
function sizeOf(n) {
  const s = {root: 15, source: 13, category: 12, company: 11, topic: 9, qtype: 10};
  return s[n.type] || 9;
}

const COL = 235, ROW = 46;

function layout() {
  nodes.forEach(n => n.rank = TYPE_RANK[n.type]);
  const byRank = {};
  nodes.forEach(n => (byRank[n.rank] = byRank[n.rank] || []).push(n));
  const inN = {}, outN = {};
  nodes.forEach(n => { inN[n.id] = []; outN[n.id] = []; });
  edges.forEach(e => { outN[e.source].push(e.target); inN[e.target].push(e.source); });
  const ranks = Object.keys(byRank).map(Number).sort((a, b) => a - b);

  ranks.forEach(r => byRank[r].forEach((n, i) => n._y = i));
  // 重心法减少交叉：左→右按入边，右→左按出边
  for (let p = 0; p < 4; p++) {
    for (let ri = 1; ri < ranks.length; ri++) {
      const r = ranks[ri];
      byRank[r].forEach(n => {
        const nb = inN[n.id].filter(x => byId[x].rank < r);
        if (nb.length) n._y = nb.reduce((s, x) => s + byId[x]._y, 0) / nb.length;
      });
      byRank[r].sort((a, b) => a._y - b._y);
    }
    for (let ri = ranks.length - 2; ri >= 0; ri--) {
      const r = ranks[ri];
      byRank[r].forEach(n => {
        const nb = outN[n.id].filter(x => byId[x].rank > r);
        if (nb.length) n._y = nb.reduce((s, x) => s + byId[x]._y, 0) / nb.length;
      });
      byRank[r].sort((a, b) => a._y - b._y);
    }
  }

  const maxRows = Math.max.apply(null, ranks.map(r => byRank[r].length));
  const totalH = (maxRows - 1) * ROW;
  ranks.forEach(r => {
    const off = (totalH - (byRank[r].length - 1) * ROW) / 2;
    byRank[r].forEach((n, i) => { n.x = r * COL; n.y = off + i * ROW; });
  });
  return { w: (ranks.length - 1) * COL, h: totalH, maxRows };
}

/* ---------- 渲染 ---------- */
const svgNS = 'http://www.w3.org/2000/svg';
const graphBox = document.getElementById('graphBox');
const PAD_L = 24, PAD_R = 190, PAD_T = 40, PAD_B = 40;
let svg, g, zoom = 1, tx = 0, ty = 0, selected = null;

const REL_COLOR = {属于: '#475569', 来源: '#22d3ee', 涉及: '#94a3b8', 考察: '#f97316', 提炼: '#16a34a', 题型: '#eab308'};

function buildLegend() {
  const items = [
    ['#f8fafc', '根'],
    ['#22d3ee', '数据来源'],
    ['#64748b', '面经小节'],
    ['#16a34a', '方法论小节'],
    ['#a855f7', '公司/来源人'],
    ['#f97316', '考点'],
    ['#eab308', '题型']
  ];
  document.getElementById('legend').innerHTML = items.map(i =>
    `<div class="row"><span class="dot" style="background:${i[0]}"></span>${i[1]}</div>`).join('');
}

function edgePath(a, b) {
  const mx = (a.x + b.x) / 2;
  return `M ${a.x} ${a.y} C ${mx} ${a.y}, ${mx} ${b.y}, ${b.x} ${b.y}`;
}

function render() {
  if (!svg) {
    const dim = layout();
    const W = dim.w + PAD_L + PAD_R, H = dim.h + PAD_T + PAD_B;
    svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');
    g = document.createElementNS(svgNS, 'g');
    svg.appendChild(g);
    graphBox.appendChild(svg);
  }
  g.innerHTML = '';
  g.setAttribute('transform', `translate(${PAD_L + tx},${PAD_T + ty}) scale(${zoom})`);

  // 边
  edges.forEach(e => {
    const a = byId[e.source], b = byId[e.target];
    const path = document.createElementNS(svgNS, 'path');
    path.setAttribute('d', edgePath(a, b));
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', REL_COLOR[e.rel] || '#475569');
    path.setAttribute('stroke-width', (e.rel === '考察' || e.rel === '提炼') ? 1.5 : 0.8);
    path.setAttribute('stroke-opacity', '0.5');
    g.appendChild(path);
  });

  // 节点 + 右侧标签
  nodes.forEach(n => {
    const gn = document.createElementNS(svgNS, 'g');
    gn.setAttribute('transform', `translate(${n.x},${n.y})`);
    gn.style.cursor = 'pointer';
    const c = document.createElementNS(svgNS, 'circle');
    const r = sizeOf(n);
    c.setAttribute('r', r);
    c.setAttribute('fill', colorOf(n));
    c.setAttribute('stroke', '#0b1220');
    c.setAttribute('stroke-width', '2');
    if (selected === n.id) { c.setAttribute('stroke', '#f8fafc'); c.setAttribute('stroke-width', '3'); }
    gn.appendChild(c);
    const t = document.createElementNS(svgNS, 'text');
    t.setAttribute('x', r + 7);
    t.setAttribute('y', 4);
    t.setAttribute('text-anchor', 'start');
    t.setAttribute('font-size', n.type === 'topic' ? '10' : '12');
    t.setAttribute('fill', '#e2e8f0');
    t.textContent = n.label;
    gn.appendChild(t);
    gn.addEventListener('click', e => { e.stopPropagation(); selectNode(n.id); });
    gn.addEventListener('mouseenter', e => showTooltip(e, n));
    gn.addEventListener('mousemove', e => moveTooltip(e));
    gn.addEventListener('mouseleave', hideTooltip);
    g.appendChild(gn);
  });
}

/* 平移缩放 */
let panning = false, sx = 0, sy = 0;
graphBox.addEventListener('mousedown', e => { panning = true; sx = e.clientX - tx; sy = e.clientY - ty; });
window.addEventListener('mousemove', e => { if (panning) { tx = e.clientX - sx; ty = e.clientY - sy; render(); } });
window.addEventListener('mouseup', () => panning = false);
graphBox.addEventListener('wheel', e => {
  e.preventDefault();
  const f = e.deltaY < 0 ? 1.1 : 0.9;
  zoom = Math.min(3, Math.max(0.35, zoom * f));
  render();
}, {passive: false});

function selectNode(id) {
  selected = id;
  render();
  const p = document.getElementById('panel');
  if (!id) { p.innerHTML = '<div class="empty">👈 点图上的任意一个节点，这里显示它的考点/详情。</div>'; return; }
  const n = byId[id];
  const typeName = {root:'总纲', source:'数据来源', category:'小节', company:'公司/来源人', topic:'考点', qtype:'题型'}[n.type] || n.type;
  let relHtml = '';
  if (adj[id].length) {
    const items = adj[id].map(a => {
      const rc = REL_COLOR[a.rel] || '#475569';
      const other = byId[a.other];
      return `<li onclick="selectNode('${a.other}')">
        <span class="rel-tag" style="background:${rc}22;color:${rc}">${a.rel}</span>
        ${a.dir === 'out' ? '→' : '←'} ${other.label}</li>`;
    }).join('');
    relHtml = `<div class="sec-title">相关连接（点可跳转）</div><ul class="rel-list">${items}</ul>`;
  }
  const fileHtml = n.file ? `<div class="file-row">📄 来源：${n.absfile}</div>` : '';
  p.innerHTML = `
    <h2>${n.label}</h2>
    <div class="badges"><span class="badge">${typeName}</span><span class="badge">${n.module}</span><span class="badge">${n.layer}</span></div>
    <div class="desc">${n.desc}</div>
    ${relHtml}${fileHtml}`;
}

const tooltip = document.getElementById('tooltip');
function showTooltip(e, n) { tooltip.style.display = 'block'; tooltip.innerHTML = `<b>${n.label}</b><br><span style="color:#94a3b8">${n.desc}</span>`; moveTooltip(e); }
function moveTooltip(e) { tooltip.style.left = (e.clientX + 12) + 'px'; tooltip.style.top = (e.clientY + 12) + 'px'; }
function hideTooltip() { tooltip.style.display = 'none'; }

buildLegend();
render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    gexf_path = os.path.join(_ROOT, "小红书面试经验知识图谱.gexf")
    html_path = os.path.join(_ROOT, "小红书面试经验图谱.html")
    with open(gexf_path, "w", encoding="utf-8") as f:
        f.write(build_gexf())
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html())
    print(f"nodes={len(NODES)} edges={len(EDGES)}")
    print("GEXF ->", gexf_path)
    print("HTML ->", html_path)
