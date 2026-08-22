# -*- coding: utf-8 -*-
"""
AI-PM-Curriculum → 知识图谱生成器（一次生成两个产物）

    1) AI-PM知识图谱.gexf   —— 给 Gephi 用
    2) 知识图谱.html         —— 双击用浏览器打开，点节点看资料（推荐）

用法：
    python build_knowledge_graph.py
"""

import os
import json

# ---------------------------------------------------------------
# 节点: (id, label, type, module, layer, desc, file)
# ---------------------------------------------------------------
NODES = [
    ("root", "AI-PM 知识体系", "root", "总纲", "总纲",
     "AI 产品经理完整知识 + 面试弹药库：11 能力板块 + 案例 + 面试题", ""),

    ("cat-curriculum", "curriculum · 知识主体", "category", "curriculum", "目录",
     "11 板块深度详解，概念→缓解→落地→面试话术", "curriculum/"),
    ("cat-cases", "cases · 案例与方法", "category", "cases", "目录",
     "PRD 14 章写法 + 微信 AI 打车助手 BRD/MRD/FSD/PRD 全量示例", "cases/"),
    ("cat-interview", "interview · 面试实战", "category", "interview", "目录",
     "面试方法论 + 25 张高频题刷题卡", "interview/"),
    ("cat-ppt", "ppt · 宣讲产物", "category", "ppt", "目录",
     "课程全景 pptx + 行业报告 pptx", "ppt/"),
    ("cat-report", "AI-Agent 行业报告", "category", "report", "目录",
     "独立行业研究：Agent 现状 + 投资建议", "AI-Agent行业报告/"),

    ("b1",  "① 需求能力 · 翻译",   "block", "①", "通用底座", "从现象挖本质：采集→分析→转化→文档化，产出可评审 PRD", "curriculum/01-通用底座-①-⑦.md"),
    ("b2",  "② 规划设计 · 落地",   "block", "②", "通用底座", "把想法变成可交付约定：BRD/MRD/PRD/FSD 文档阶梯", "curriculum/01-通用底座-①-⑦.md"),
    ("b3",  "③ 项目管理 · 交付",   "block", "③", "通用底座", "多快好省的平衡术：范围/时间/品质/资源取舍", "curriculum/01-通用底座-①-⑦.md"),
    ("b4",  "④ 数据分析 · 验证",   "block", "④", "通用底座", "从拍脑袋到用数据说话：漏斗/A-B/北极星指标", "curriculum/01-通用底座-①-⑦.md"),
    ("b5",  "⑤ 商业战略 · 方向",   "block", "⑤", "通用底座", "选对战场：可行性三步曲 + PEST/SWOT + 战略", "curriculum/01-通用底座-①-⑦.md"),
    ("b6",  "⑥ 沟通协作 · 影响力", "block", "⑥", "通用底座", "不靠权力靠魅力：无授权领导 + 分层沟通", "curriculum/01-通用底座-①-⑦.md"),
    ("b7",  "⑦ 学习与自我修养",   "block", "⑦", "通用底座", "底色决定天花板：少做就是多做 + 持续追 AI", "curriculum/01-通用底座-①-⑦.md"),
    ("b8",  "⑧ AI 技术认知",       "block", "⑧", "AI增补层", "判断能不能做：幻觉/RAG/Agent/大模型基础", "curriculum/02-AI技术认知-⑧.md"),
    ("b9",  "⑨ 模型评估与数据闭环","block", "⑨", "AI增补层", "验证做得好不好：评测集 + 离线在线指标 + 数据闭环", "curriculum/03-模型评估与数据闭环-⑨.md"),
    ("b10", "⑩ 信任安全与伦理合规","block", "⑩", "AI增补层", "守住底线：发布门槛 + 公平/隐私 + 红队", "curriculum/04-信任安全与伦理合规-⑩.md"),
    ("b11", "⑪ AI 产品经济学",     "block", "⑪", "AI增补层", "算清值不值：Token 成本 + 单位经济 + 定价", "curriculum/05-AI产品经济学-⑪.md"),

    ("c-req-uvsp",      "用户需求 vs 产品需求", "concept", "①", "通用底座", "用户要『解决方案』，产品要『分析后的真实需求』（福特：更快的马=更快到达）", "curriculum/01-通用底座-①-⑦.md"),
    ("c-req-quadrant",  "需求采集四象限",       "concept", "①", "通用底座", "定性/定量 × 说/做——问用户会骗你，看行为才真实", "curriculum/01-通用底座-①-⑦.md"),
    ("c-req-dna",       "DNA 检测",             "concept", "①", "通用底座", "属性→商业价值→实现难度→性价比，判断值不值得做", "curriculum/01-通用底座-①-⑦.md"),
    ("c-req-ratio",     "性价比",               "concept", "①", "通用底座", "商业价值 ÷ 实现难度(人天)，不是拍脑袋排优先级", "curriculum/01-通用底座-①-⑦.md"),
    ("c-req-funnel",    "需求处理四步漏斗",     "concept", "①", "通用底座", "采集→分析→转化→文档化，产出可评审 PRD", "curriculum/01-通用底座-①-⑦.md"),
    ("c-doc-ladder",    "BRD/MRD/PRD/FSD 阶梯","concept", "②", "通用底座", "四层文档：值不值→给谁→做什么→怎么做，逐层细化", "curriculum/01-通用底座-①-⑦.md"),
    ("c-prd-7",         "PRD 七大板块",         "concept", "②", "通用底座", "文档头/范围角色/场景需求/功能/非功能/验收/版本遗留", "curriculum/01-通用底座-①-⑦.md"),
    ("c-ai-prd",        "AI-native PRD 五要素", "concept", "②", "通用底座", "评估标准+模型约束+数据需求+埋点+防护兜底，多问『模型错了怎么办』", "curriculum/01-通用底座-①-⑦.md"),
    ("c-tradeoff",      "多快好省 TRQ",         "concept", "③", "通用底座", "范围/时间/品质/资源四者不可兼得，要会取舍", "curriculum/01-通用底座-①-⑦.md"),
    ("c-wbs",           "WBS 任务分解",         "concept", "③", "通用底座", "自上而下拆到『可分配、可估算』粒度", "curriculum/01-通用底座-①-⑦.md"),
    ("c-3review",       "三次评审",             "concept", "③", "通用底座", "需求/设计/测试评审，防病优于治病", "curriculum/01-通用底座-①-⑦.md"),
    ("c-ai-delivery",   "AI 交付与运营",        "concept", "③", "通用底座", "分层发布(alpha→beta→GA)+回滚降级+版本控制，AI 上线只是开始", "curriculum/01-通用底座-①-⑦.md"),
    ("c-kpi-northstar", "KPI vs 北极星指标",    "concept", "④", "通用底座", "KPI 是手段，北极星是代表长期价值的核心指标(目的)", "curriculum/01-通用底座-①-⑦.md"),
    ("c-funnel",        "漏斗与转化",           "concept", "④", "通用底座", "每层流失都是优化机会，先查流失最大的一层", "curriculum/01-通用底座-①-⑦.md"),
    ("c-abtest",        "A/B 测试",             "concept", "④", "通用底座", "随机分两组对照，一次只改一个变量", "curriculum/01-通用底座-①-⑦.md"),
    ("c-model-metrics", "模型指标看板",         "concept", "④", "通用底座", "离线(F1/准确率)+在线(采纳率/完成率/接管率)两套都要盯", "curriculum/01-通用底座-①-⑦.md"),
    ("c-feasibility",   "可行性三步曲",         "concept", "⑤", "通用底座", "我们在哪儿→去哪儿→怎么去", "curriculum/01-通用底座-①-⑦.md"),
    ("c-pest-swot",     "PEST / SWOT",          "concept", "⑤", "通用底座", "PEST 看外部环境，SWOT 看自身优劣势→策略组合", "curriculum/01-通用底座-①-⑦.md"),
    ("c-vmv",           "价值观→使命→愿景→战略","concept", "⑤", "通用底座", "层层炼成，先于执行", "curriculum/01-通用底座-①-⑦.md"),
    ("c-no-auth-lead",  "无授权领导",           "concept", "⑥", "通用底座", "不靠职位权力，靠专业话语权+影响力推动别人把事做成", "curriculum/01-通用底座-①-⑦.md"),
    ("c-interface",     "接口人",               "concept", "⑥", "通用底座", "团队间单一对接人，过滤噪音", "curriculum/01-通用底座-①-⑦.md"),
    ("c-matrix-org",    "矩阵型组织",           "concept", "⑥", "通用底座", "职能+项目双线融合，可能有双头领导", "curriculum/01-通用底座-①-⑦.md"),
    ("c-layer-comm",    "分层沟通",             "concept", "⑥", "通用底座", "对技术讲验收、对高管讲单位经济、对合规讲风险", "curriculum/01-通用底座-①-⑦.md"),
    ("c-4pillars",      "自我修养四件套",       "concept", "⑦", "通用底座", "爱生活、有理想、会思考、能沟通", "curriculum/01-通用底座-①-⑦.md"),
    ("c-less-is-more",  "少做就是多做",         "concept", "⑦", "通用底座", "用 100% 质量做 75% 数量", "curriculum/01-通用底座-①-⑦.md"),
    ("c-pm-ism",        "产品经理主义",         "concept", "⑦", "通用底座", "把产品思维抽象成可普适的做事方法", "curriculum/01-通用底座-①-⑦.md"),
    ("c-track-ai",      "持续追踪 AI 进展",     "concept", "⑦", "通用底座", "跟发布节奏+订阅信源+动手做小实验，上个月做不到的这周就能做", "curriculum/01-通用底座-①-⑦.md"),
    ("c-hallucination", "幻觉",                 "concept", "⑧", "AI增补层", "概率生成自带的，分检索层/生成层两类，四层缓解(Prompt→检索→生成→产品兜底)", "curriculum/02-AI技术认知-⑧.md"),
    ("c-rag",           "RAG",                  "concept", "⑧", "AI增补层", "索引→检索→生成，开卷考试；考切片/混合检索/Rerank/时效性等落地细节", "curriculum/02-AI技术认知-⑧.md"),
    ("c-agent",         "Agent",                "concept", "⑧", "AI增补层", "大模型+规划+工具+记忆+反馈，四层架构，核心=管理不确定性", "curriculum/02-AI技术认知-⑧.md"),
    ("c-llm-base",      "大模型基础",           "concept", "⑧", "AI增补层", "Transformer 自注意力/LoRA/GRPO/上下文窗口，能接住追问", "curriculum/02-AI技术认知-⑧.md"),
    ("c-workflow-agent","Workflow vs Agent",    "concept", "⑧", "AI增补层", "确定性(workflow 预设流程) vs 自主性(agent 自主规划)，2026 高频", "curriculum/02-AI技术认知-⑧.md"),
    ("c-mcp-skills",    "MCP / Skills",         "concept", "⑧", "AI增补层", "MCP 统一模型↔工具协议；Skills=可复用能力封装，2026 每场必问", "curriculum/02-AI技术认知-⑧.md"),
    ("c-vibe-coding",   "vibe coding",          "concept", "⑧", "AI增补层", "自然语言描述意图让 AI 写代码，适合 demo 不适合生产", "curriculum/02-AI技术认知-⑧.md"),
    ("c-evalset",       "评估集 / 金标准集",    "concept", "⑨", "AI增补层", "人工标注标准答案，不参与训练；定范围→定标准→交叉校验→分层→回流", "curriculum/03-模型评估与数据闭环-⑨.md"),
    ("c-off-on-metrics","离线 vs 在线指标",     "concept", "⑨", "AI增补层", "离线(准确率/召回/F1)验能力，在线(采纳率/完成率/接管率)验价值", "curriculum/03-模型评估与数据闭环-⑨.md"),
    ("c-data-loop",     "数据闭环",             "concept", "⑨", "AI增补层", "采集→清洗→标注→评估→迭代，真实数据喂模型形成飞轮", "curriculum/03-模型评估与数据闭环-⑨.md"),
    ("c-attribution",   "价值归因",             "concept", "⑨", "AI增补层", "控制变量+A/B+分层拆解，判断效果提升是不是模型的功劳", "curriculum/03-模型评估与数据闭环-⑨.md"),
    ("c-release-gates", "发布门槛 Release Gates","concept", "⑩", "AI增补层", "安全+兜底+指标+监控四道门，不过关不能发", "curriculum/04-信任安全与伦理合规-⑩.md"),
    ("c-fairness",      "公平/可解释/隐私",     "concept", "⑩", "AI增补层", "分人群测偏差/给引用可解释/最小采集+脱敏+授权", "curriculum/04-信任安全与伦理合规-⑩.md"),
    ("c-content-safety","内容安全",             "concept", "⑩", "AI增补层", "前置过滤+后置拦截+人工巡查", "curriculum/04-信任安全与伦理合规-⑩.md"),
    ("c-red-team",      "Red Teaming 红队",     "concept", "⑩", "AI增补层", "对抗性攻击测试，主动找漏洞，专找歪路怎么绕过防线", "curriculum/04-信任安全与伦理合规-⑩.md"),
    ("c-prompt-inject", "Prompt 注入防御",      "concept", "⑩", "AI增补层", "技术层+产品层+运营层三层一起防，单靠技术挡不住", "curriculum/04-信任安全与伦理合规-⑩.md"),
    ("c-token-cost",    "Token / 推理成本",     "concept", "⑪", "AI增补层", "AI 每次请求都有真实成本，降本：缓存/小模型路由/精简/端侧", "curriculum/05-AI产品经济学-⑪.md"),
    ("c-unit-econ",     "单位经济模型",         "concept", "⑪", "AI增补层", "LTV > CAC + 累计推理成本，多一项推理成本", "curriculum/05-AI产品经济学-⑪.md"),
    ("c-pricing",       "定价建模",             "concept", "⑪", "AI增补层", "成本打底+价值锚定+版本分层；API/订阅/私有化分层", "curriculum/05-AI产品经济学-⑪.md"),
    ("c-model-select",  "模型选型成本权衡",     "concept", "⑪", "AI增补层", "成本/延迟/精度/上下文四维，复杂用大模型、高频用小模型", "curriculum/05-AI产品经济学-⑪.md"),
    ("c-data-flywheel", "数据飞轮与防御性",     "concept", "⑪", "AI增补层", "越用数据越多→模型越准→用户越多，护城河不是算法是数据飞轮", "curriculum/05-AI产品经济学-⑪.md"),

    ("case-method", "方法 · PRD 14 章撰写步骤", "case", "cases", "案例", "14 章 B 端 PRD 全流程，第 10 章功能需求最核心", "cases/方法-PRD撰写步骤.md"),
    ("case-brd",    "案例 · BRD 微信AI打车助手", "case", "cases", "案例", "值不值：商业价值论证", "cases/案例-BRD-微信AI打车助手.md"),
    ("case-mrd",    "案例 · MRD 微信AI打车助手", "case", "cases", "案例", "给谁：市场与用户分析", "cases/案例-MRD-微信AI打车助手.md"),
    ("case-prd",    "案例 · PRD 微信AI打车助手", "case", "cases", "案例", "做什么：14 章全量需求文档", "cases/案例-PRD-微信AI打车助手.md"),
    ("case-fsd",    "案例 · FSD 微信AI打车助手", "case", "cases", "案例", "怎么做：功能规格说明", "cases/案例-FSD-微信AI打车助手.md"),

    ("doc-interview-method", "面试方法论",        "doc", "interview", "面试", "6 大题型破题框架+话术模板+面经实录", "interview/面试方法论.md"),
    ("doc-interview-cards",  "高频题刷题卡(25张)","doc", "interview", "面试", "25 张高频题答题要点+追问链+雷区", "interview/高频题刷题卡.json"),

    ("doc-report",      "AI-Agent 行业现状报告", "doc", "report", "报告", "Agent 现状 + 投资建议", "AI-Agent行业报告/AI-Agent行业现状报告.md"),
    ("doc-ppt-cur",     "课程全景 PPT",          "doc", "ppt",    "宣讲", "AI-PM 课程全景 pptx", "ppt/AI-PM-Curriculum.pptx"),
    ("doc-ppt-report",  "行业报告 PPT",          "doc", "ppt",    "宣讲", "AI-Agent 行业报告 pptx", "ppt/AI-Agent行业现状报告.pptx"),
]

EDGES = [
    ("root", "cat-curriculum", "属于"),
    ("root", "cat-cases",      "属于"),
    ("root", "cat-interview",  "属于"),
    ("root", "cat-ppt",        "属于"),
    ("root", "cat-report",     "属于"),

    ("cat-curriculum", "b1", "属于"), ("cat-curriculum", "b2", "属于"),
    ("cat-curriculum", "b3", "属于"), ("cat-curriculum", "b4", "属于"),
    ("cat-curriculum", "b5", "属于"), ("cat-curriculum", "b6", "属于"),
    ("cat-curriculum", "b7", "属于"), ("cat-curriculum", "b8", "属于"),
    ("cat-curriculum", "b9", "属于"), ("cat-curriculum", "b10", "属于"),
    ("cat-curriculum", "b11", "属于"),
    ("cat-cases", "case-method", "属于"), ("cat-cases", "case-brd", "属于"),
    ("cat-cases", "case-mrd", "属于"),    ("cat-cases", "case-prd", "属于"),
    ("cat-cases", "case-fsd", "属于"),
    ("cat-interview", "doc-interview-method", "属于"),
    ("cat-interview", "doc-interview-cards",  "属于"),
    ("cat-ppt",    "doc-ppt-cur",    "属于"),
    ("cat-ppt",    "doc-ppt-report", "属于"),
    ("cat-report", "doc-report",     "属于"),

    ("b1",  "c-req-uvsp", "属于"), ("b1", "c-req-quadrant", "属于"),
    ("b1",  "c-req-dna", "属于"),  ("b1", "c-req-ratio", "属于"),
    ("b1",  "c-req-funnel", "属于"),
    ("b2",  "c-doc-ladder", "属于"), ("b2", "c-prd-7", "属于"),
    ("b2",  "c-ai-prd", "属于"),
    ("b3",  "c-tradeoff", "属于"), ("b3", "c-wbs", "属于"),
    ("b3",  "c-3review", "属于"),  ("b3", "c-ai-delivery", "属于"),
    ("b4",  "c-kpi-northstar", "属于"), ("b4", "c-funnel", "属于"),
    ("b4",  "c-abtest", "属于"), ("b4", "c-model-metrics", "属于"),
    ("b5",  "c-feasibility", "属于"), ("b5", "c-pest-swot", "属于"),
    ("b5",  "c-vmv", "属于"),
    ("b6",  "c-no-auth-lead", "属于"), ("b6", "c-interface", "属于"),
    ("b6",  "c-matrix-org", "属于"), ("b6", "c-layer-comm", "属于"),
    ("b7",  "c-4pillars", "属于"), ("b7", "c-less-is-more", "属于"),
    ("b7",  "c-pm-ism", "属于"), ("b7", "c-track-ai", "属于"),
    ("b8",  "c-hallucination", "属于"), ("b8", "c-rag", "属于"),
    ("b8",  "c-agent", "属于"), ("b8", "c-llm-base", "属于"),
    ("b8",  "c-workflow-agent", "属于"), ("b8", "c-mcp-skills", "属于"),
    ("b8",  "c-vibe-coding", "属于"),
    ("b9",  "c-evalset", "属于"), ("b9", "c-off-on-metrics", "属于"),
    ("b9",  "c-data-loop", "属于"), ("b9", "c-attribution", "属于"),
    ("b10", "c-release-gates", "属于"), ("b10", "c-fairness", "属于"),
    ("b10", "c-content-safety", "属于"), ("b10", "c-red-team", "属于"),
    ("b10", "c-prompt-inject", "属于"),
    ("b11", "c-token-cost", "属于"), ("b11", "c-unit-econ", "属于"),
    ("b11", "c-pricing", "属于"), ("b11", "c-model-select", "属于"),
    ("b11", "c-data-flywheel", "属于"),

    ("b8",  "b1", "升级"),
    ("b9",  "b4", "升级"),
    ("b10", "b2", "升级"),
    ("b10", "b3", "升级"),
    ("b11", "b5", "升级"),

    ("case-brd", "case-mrd", "前置"),
    ("case-mrd", "case-prd", "前置"),
    ("case-prd", "case-fsd", "前置"),
    ("case-method", "case-prd", "前置"),

    ("cat-curriculum", "cat-cases", "前置"),
    ("cat-cases", "cat-interview", "前置"),
    ("cat-curriculum", "cat-interview", "前置"),

    ("c-rag", "c-hallucination", "关联"),
    ("c-data-loop", "c-data-flywheel", "关联"),
    ("c-model-metrics", "c-off-on-metrics", "关联"),
    ("c-model-select", "c-unit-econ", "关联"),
    ("c-release-gates", "c-prompt-inject", "关联"),
    ("c-agent", "c-mcp-skills", "关联"),
    ("c-agent", "c-workflow-agent", "关联"),
    ("c-evalset", "c-data-loop", "关联"),
]

_ROOT = os.path.dirname(os.path.abspath(__file__))


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def build_gexf():
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">')
    lines.append('  <meta lastmodifieddate="2026-08-21">')
    lines.append('    <creator>AI-PM-Curriculum build_knowledge_graph.py</creator>')
    lines.append('    <description>AI 产品经理知识体系知识图谱</description>')
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

    return HTML_TEMPLATE.replace("__DATA__", json_str)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI-PM 知识图谱</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { height: 100%; font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; }
  body { display: flex; flex-direction: column; background: #0f172a; color: #e2e8f0; }
  header { padding: 10px 16px; background: #1e293b; border-bottom: 1px solid #334155; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
  header h1 { font-size: 16px; font-weight: 600; }
  header .tip { font-size: 12px; color: #94a3b8; }
  header button { margin-left: auto; background: #2563eb; color: #fff; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; }
  .wrap { flex: 1; display: flex; min-height: 0; }
  .graph { flex: 1; position: relative; min-width: 0; }
  svg { width: 100%; height: 100%; display: block; }
  .panel { width: 340px; background: #1e293b; border-left: 1px solid #334155; overflow-y: auto; padding: 16px; }
  .panel .empty { color: #64748b; font-size: 13px; margin-top: 20px; }
  .panel h2 { font-size: 18px; margin-bottom: 6px; line-height: 1.4; }
  .badges { margin: 8px 0; }
  .badge { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 10px; margin-right: 6px; margin-bottom: 4px; background: #334155; color: #cbd5e1; }
  .panel .desc { font-size: 14px; line-height: 1.7; color: #cbd5e1; background: #0f172a; border-radius: 8px; padding: 12px; margin: 10px 0; }
  .panel .sec-title { font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin: 14px 0 6px; }
  .rel-list { list-style: none; }
  .rel-list li { font-size: 13px; padding: 5px 8px; border-radius: 6px; cursor: pointer; margin-bottom: 2px; display: flex; align-items: center; gap: 6px; }
  .rel-list li:hover { background: #334155; }
  .rel-tag { font-size: 11px; padding: 1px 6px; border-radius: 8px; flex-shrink: 0; }
  .file-row { font-size: 12px; color: #94a3b8; word-break: break-all; margin-top: 8px; }
  .file-row button { background: #334155; border: none; color: #e2e8f0; padding: 3px 8px; border-radius: 5px; cursor: pointer; font-size: 12px; margin-top: 4px; }
  .legend { position: absolute; top: 10px; left: 10px; background: rgba(15,23,42,.9); border: 1px solid #334155; border-radius: 8px; padding: 8px 10px; font-size: 11px; color: #cbd5e1; }
  .legend .row { display: flex; align-items: center; gap: 6px; margin: 3px 0; }
  .legend .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
  .tooltip { position: fixed; pointer-events: none; background: #0f172a; border: 1px solid #334155; border-radius: 6px; padding: 6px 9px; font-size: 12px; max-width: 260px; display: none; z-index: 10; }
</style>
</head>
<body>
<header>
  <h1>AI-PM 知识图谱</h1>
  <span class="tip">点左边任意一个点 → 右边看资料；点右边「相关」项可跳转；滚轮缩放、拖拽移动</span>
  <button onclick="toggleLabels()">显示/隐藏文字</button>
</header>
<div class="wrap">
  <div class="graph" id="graph">
    <div class="legend" id="legend"></div>
  </div>
  <div class="panel" id="panel">
    <div class="empty">👈 点左边图上的任意一个点，这里会显示它的知识点。</div>
  </div>
</div>
<div class="tooltip" id="tooltip"></div>

<script>
const DATA = __DATA__;

const nodes = DATA.nodes;
const edges = DATA.edges;
const byId = {};
nodes.forEach(n => byId[n.id] = n);

// 邻接表
const adj = {};
nodes.forEach(n => adj[n.id] = []);
edges.forEach(e => {
  adj[e.source].push({other: e.target, rel: e.rel, dir: 'out'});
  adj[e.target].push({other: e.source, rel: e.rel, dir: 'in'});
});

// 颜色
const LAYER_COLOR = {
  '总纲': '#111827', '目录': '#64748b', '通用底座': '#2563eb',
  'AI增补层': '#ea580c', '案例': '#16a34a', '面试': '#a855f7',
  '报告': '#eab308', '宣讲': '#eab308'
};
function colorOf(n) {
  if (n.type === 'root') return '#f8fafc';
  if (n.type === 'category') return '#64748b';
  if (n.type === 'case') return '#16a34a';
  if (n.type === 'doc') return n.module === 'interview' ? '#a855f7' : '#eab308';
  if (n.type === 'block') return n.layer === 'AI增补层' ? '#f97316' : '#3b82f6';
  return n.layer === 'AI增补层' ? '#fdba74' : '#93c5fd';
}
function sizeOf(n) {
  const s = {root: 30, category: 22, block: 19, case: 15, doc: 15, concept: 11};
  return s[n.type] || 10;
}

// 初始位置：按类型分圈
function initPos() {
  const ring = {root: 0, category: 1, block: 2, case: 2, doc: 2, concept: 3};
  const counts = {};
  nodes.forEach(n => { const r = ring[n.type]; counts[r] = (counts[r] || 0) + 1; });
  const radius = {0: 0, 1: 110, 2: 210, 3: 340};
  const idx = {};
  nodes.forEach(n => {
    const r = ring[n.type];
    const i = idx[r] = (idx[r] || 0);
    const total = counts[r];
    const ang = total === 1 ? 0 : (i / total) * Math.PI * 2;
    n.x = Math.cos(ang) * radius[r];
    n.y = Math.sin(ang) * radius[r];
    idx[r] = i + 1;
  });
}

// 力导向迭代
function layout(iter) {
  const W = 900, H = 640;
  const k = 90; // 理想边长
  for (let it = 0; it < iter; it++) {
    // 斥力
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i], b = nodes[j];
        let dx = a.x - b.x, dy = a.y - b.y;
        let d2 = dx * dx + dy * dy;
        if (d2 < 1) { dx = Math.random() - 0.5; dy = Math.random() - 0.5; d2 = 1; }
        const d = Math.sqrt(d2);
        const f = (k * k) / d2;
        const fx = (dx / d) * f * 0.6, fy = (dy / d) * f * 0.6;
        a.x += fx; a.y += fy; b.x -= fx; b.y -= fy;
      }
    }
    // 弹簧力
    edges.forEach(e => {
      const a = byId[e.source], b = byId[e.target];
      let dx = b.x - a.x, dy = b.y - a.y;
      const d = Math.sqrt(dx * dx + dy * dy) || 1;
      const f = (d - k) * 0.05;
      const fx = (dx / d) * f, fy = (dy / d) * f;
      a.x += fx; a.y += fy; b.x -= fx; b.y -= fy;
    });
    // 中心引力
    nodes.forEach(n => {
      n.x += (0 - n.x) * 0.01;
      n.y += (0 - n.y) * 0.01;
    });
  }
  // 归一到画布
  let minX = 1e9, maxX = -1e9, minY = 1e9, maxY = -1e9;
  nodes.forEach(n => { minX = Math.min(minX, n.x); maxX = Math.max(maxX, n.x); minY = Math.min(minY, n.y); maxY = Math.max(maxY, n.y); });
  const scale = Math.min((W - 120) / (maxX - minX), (H - 120) / (maxY - minY));
  nodes.forEach(n => { n.x = (n.x - (minX + maxX) / 2) * scale; n.y = (n.y - (minY + maxY) / 2) * scale; });
}

const graph = document.getElementById('graph');
const svgNS = 'http://www.w3.org/2000/svg';
let svg, g, zoom = 1, tx = 0, ty = 0, showLabels = true, selected = null;
let dragNode = null;

function buildLegend() {
  const items = [
    ['#f8fafc', '根'],
    ['#64748b', '目录'],
    ['#3b82f6', '通用底座 ①–⑦'],
    ['#f97316', 'AI 增补层 ⑧–⑪'],
    ['#93c5fd', '底座概念'],
    ['#fdba74', 'AI 层概念'],
    ['#16a34a', '案例'],
    ['#a855f7', '面试'],
    ['#eab308', '报告/PPT']
  ];
  document.getElementById('legend').innerHTML = items.map(i =>
    `<div class="row"><span class="dot" style="background:${i[0]}"></span>${i[1]}</div>`
  ).join('');
}

const REL_COLOR = {属于: '#475569', 升级: '#f97316', 前置: '#10b981', 关联: '#38bdf8'};

function render() {
  if (!svg) {
    svg = document.createElementNS(svgNS, 'svg');
    g = document.createElementNS(svgNS, 'g');
    svg.appendChild(g);
    graph.appendChild(svg);
  }
  g.innerHTML = '';
  g.setAttribute('transform', `translate(${tx},${ty}) scale(${zoom})`);

  // 边
  edges.forEach(e => {
    const a = byId[e.source], b = byId[e.target];
    const line = document.createElementNS(svgNS, 'line');
    line.setAttribute('x1', a.x); line.setAttribute('y1', a.y);
    line.setAttribute('x2', b.x); line.setAttribute('y2', b.y);
    line.setAttribute('stroke', REL_COLOR[e.rel] || '#475569');
    line.setAttribute('stroke-width', e.rel === '升级' ? 1.6 : 0.8);
    line.setAttribute('stroke-opacity', '0.55');
    if (e.rel === '关联') line.setAttribute('stroke-dasharray', '3,3');
    line.dataset.rel = e.rel;
    g.appendChild(line);
  });

  // 节点
  nodes.forEach(n => {
    const gNode = document.createElementNS(svgNS, 'g');
    gNode.setAttribute('transform', `translate(${n.x},${n.y})`);
    gNode.dataset.id = n.id;
    gNode.style.cursor = 'pointer';
    const c = document.createElementNS(svgNS, 'circle');
    c.setAttribute('r', sizeOf(n));
    c.setAttribute('fill', colorOf(n));
    c.setAttribute('stroke', '#0f172a');
    c.setAttribute('stroke-width', '2');
    if (selected === n.id) { c.setAttribute('stroke', '#f8fafc'); c.setAttribute('stroke-width', '3'); }
    gNode.appendChild(c);
    if (showLabels) {
      const t = document.createElementNS(svgNS, 'text');
      t.setAttribute('y', sizeOf(n) + 12);
      t.setAttribute('text-anchor', 'middle');
      t.setAttribute('font-size', n.type === 'concept' ? '9' : '11');
      t.setAttribute('fill', '#e2e8f0');
      t.textContent = n.label;
      gNode.appendChild(t);
    }
    gNode.addEventListener('mousedown', e => onMouseDown(e, n));
    gNode.addEventListener('click', e => { e.stopPropagation(); selectNode(n.id); });
    gNode.addEventListener('mouseenter', e => showTooltip(e, n));
    gNode.addEventListener('mousemove', e => moveTooltip(e));
    gNode.addEventListener('mouseleave', hideTooltip);
    g.appendChild(gNode);
  });
}

function onMouseDown(e, n) {
  dragNode = n;
  e.preventDefault();
}
function onMouseMove(e) {
  if (dragNode) {
    const rect = svg.getBoundingClientRect();
    dragNode.x = (e.clientX - rect.left - tx) / zoom;
    dragNode.y = (e.clientY - rect.top - ty) / zoom;
    render();
  }
}
function onMouseUp() { dragNode = null; }

svgEl = null;
graph.addEventListener('wheel', e => {
  e.preventDefault();
  const f = e.deltaY < 0 ? 1.1 : 0.9;
  zoom = Math.min(3, Math.max(0.3, zoom * f));
  render();
}, {passive: false});
graph.addEventListener('mousemove', onMouseMove);
graph.addEventListener('mouseup', onMouseUp);
graph.addEventListener('mousedown', e => { if (e.target === svg || e.target === g) { /* 空白拖拽 */ } });
graph.addEventListener('click', e => { if (e.target === svg) selectNode(null); });

function selectNode(id) {
  selected = id;
  render();
  const p = document.getElementById('panel');
  if (!id) { p.innerHTML = '<div class="empty">👈 点左边图上的任意一个点，这里会显示它的知识点。</div>'; return; }
  const n = byId[id];
  const typeName = {root:'总纲', category:'目录', block:'能力板块', concept:'概念', case:'案例', doc:'文档'}[n.type] || n.type;
  let relHtml = '';
  if (adj[id].length) {
    const items = adj[id].map(a => {
      const relColor = REL_COLOR[a.rel] || '#475569';
      const other = byId[a.other];
      return `<li onclick="selectNode('${a.other}')">
        <span class="rel-tag" style="background:${relColor}22;color:${relColor}">${a.rel}</span>
        ${a.dir === 'out' ? '→' : '←'} ${other.label}
      </li>`;
    }).join('');
    relHtml = `<div class="sec-title">相关连接（点可跳转）</div><ul class="rel-list">${items}</ul>`;
  }
  const fileHtml = n.file ? `<div class="file-row">📄 来源：${n.absfile}<br><button onclick="copyPath(this)">复制路径</button></div>` : '';
  p.innerHTML = `
    <h2>${n.label}</h2>
    <div class="badges">
      <span class="badge">${typeName}</span>
      <span class="badge">${n.module}</span>
      <span class="badge">${n.layer}</span>
    </div>
    <div class="desc">${n.desc}</div>
    ${relHtml}
    ${fileHtml}`;
}

function copyPath(btn) {
  const txt = btn.parentElement.textContent.replace('复制路径', '').replace('📄 来源：', '').trim();
  navigator.clipboard.writeText(txt).then(() => { btn.textContent = '已复制'; });
}

function toggleLabels() { showLabels = !showLabels; render(); }

const tooltip = document.getElementById('tooltip');
function showTooltip(e, n) { tooltip.style.display = 'block'; tooltip.innerHTML = `<b>${n.label}</b><br><span style="color:#94a3b8">${n.desc}</span>`; moveTooltip(e); }
function moveTooltip(e) { tooltip.style.left = (e.clientX + 12) + 'px'; tooltip.style.top = (e.clientY + 12) + 'px'; }
function hideTooltip() { tooltip.style.display = 'none'; }

initPos();
layout(300);
buildLegend();
render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    gexf_path = os.path.join(_ROOT, "AI-PM知识图谱.gexf")
    html_path = os.path.join(_ROOT, "知识图谱.html")
    with open(gexf_path, "w", encoding="utf-8") as f:
        f.write(build_gexf())
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html())
    print(f"nodes={len(NODES)} edges={len(EDGES)}")
    print("GEXF ->", gexf_path)
    print("HTML ->", html_path)
