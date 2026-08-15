# -*- coding: utf-8 -*-
"""
《AI Agent 行业现状报告》PPT 生成器（数据驱动骨架）
====================================================
基于报告 md 的 10 章结构 → 12 页原生可编辑 PPTX（真文本框 + 形状，无 imagegen）。
- 改内容：只改下方各 slide 函数里的数据，不用动渲染逻辑。
- 换配色：改 COLORS 字典。
- 输出：<repo>/ppt/AI-Agent行业现状报告.pptx
运行：python ppt/build_agent_report_ppt.py
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "ppt", "AI-Agent行业现状报告.pptx")

# ─────────────────────────── 配色 / 版式常量 ───────────────────────────
COLORS = {
    "navy":  RGBColor(0x1B, 0x2A, 0x4A),
    "blue":  RGBColor(0x2D, 0x6C, 0xDF),
    "teal":  RGBColor(0x0F, 0xA3, 0xA3),
    "ink":   RGBColor(0x1F, 0x29, 0x37),
    "muted": RGBColor(0x6B, 0x72, 0x80),
    "bg":    RGBColor(0xF4, 0xF6, 0xFA),
    "card":  RGBColor(0xFF, 0xFF, 0xFF),
    "line":  RGBColor(0xE5, 0xE7, 0xEB),
    "white": RGBColor(0xFF, 0xFF, 0xFF),
    "tint_ai": RGBColor(0xE0, 0xF5, 0xF5),
    "tint_blue": RGBColor(0xE8, 0xF0, 0xFE),
    "danger": RGBColor(0xC0, 0x3A, 0x2B),
}
FONT = "Microsoft YaHei"

EMU_W = Inches(13.333)
EMU_H = Inches(7.5)

TOTAL = 12


# ─────────────────────────── 基础工具 ───────────────────────────
def _set_font(run, size, bold=False, color=None, name=FONT):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {})
        rPr.append(ea)
    ea.set("typeface", name)


def _solid(shape, fill, line=None, line_w=None):
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(line_w or 0.75)
    shape.shadow.inherit = False


def _rect(slide, L, T, W, H, fill, line=None, round_=False, line_w=None):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if round_ else MSO_SHAPE.RECTANGLE
    sp = slide.shapes.add_shape(kind, Inches(L), Inches(T), Inches(W), Inches(H))
    if round_:
        try:
            sp.adjustments[0] = 0.08
        except Exception:
            pass
    _solid(sp, fill, line, line_w)
    return sp


def _text(slide, L, T, W, H, lines, anchor=MSO_ANCHOR.TOP, align=PP_ALIGN.LEFT,
          spacing=1.0):
    tb = slide.shapes.add_textbox(Inches(L), Inches(T), Inches(W), Inches(H))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, para in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        for (t, size, bold, color) in para:
            r = p.add_run()
            r.text = t
            _set_font(r, size, bold, color)
    return tb


def _bg(slide, color=COLORS["bg"]):
    _rect(slide, 0, 0, 13.333, 7.5, color)


def _chip(slide, L, T, W, H, text, fill, text_color, size=12, bold=True):
    _rect(slide, L, T, W, H, fill, round_=True)
    _text(slide, L, T, W, H, [[(text, size, bold, text_color)]],
          anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)


def _footer(slide, idx, total, dark=False):
    fg = RGBColor(0xBF, 0xD0, 0xE8) if dark else COLORS["muted"]
    line_c = RGBColor(0x3A, 0x4A, 0x66) if dark else COLORS["line"]
    _rect(slide, 0.6, 7.14, 12.13, 0.012, line_c)
    _text(slide, 0.6, 7.20, 9.5, 0.26,
          [[("AI Agent 行业现状报告", 9, False, fg)]])
    _text(slide, 10.9, 7.20, 1.83, 0.26,
          [[("%d / %d" % (idx, total), 9, False, fg)]], align=PP_ALIGN.RIGHT)


def _header(slide, num, title, tag, accent, idx):
    """正文页统一头部：序号徽章 + 标题 + 侧重点标签"""
    _bg(slide)
    _rect(slide, 0.6, 0.45, 0.72, 0.72, accent, round_=True)
    _text(slide, 0.6, 0.45, 0.72, 0.72, [[(num, 22, True, COLORS["white"])]],
          anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
    _text(slide, 1.5, 0.48, 9.0, 0.7, [[(title, 26, True, COLORS["ink"])]])
    _chip(slide, 10.7, 0.58, 2.0, 0.5, tag, COLORS["tint_ai"], accent, size=12)
    _rect(slide, 0.6, 1.32, 12.13, 0.03, accent)
    _footer(slide, idx, TOTAL)


def _table(slide, L, T, col_widths, headers, rows, header_fill, header_color,
           font_size=11.5, header_size=12, row_h=0.44, header_h=0.5,
           align_right_cols=(), zebra=(COLORS["card"], RGBColor(0xF0, 0xF3, 0xF8))):
    n_rows = len(rows) + 1
    n_cols = len(headers)
    W = sum(col_widths)
    gfx = slide.shapes.add_table(n_rows, n_cols, Inches(L), Inches(T),
                                 Inches(W), Inches(header_h + row_h * len(rows))).table
    for i, cw in enumerate(col_widths):
        gfx.columns[i].width = Inches(cw)
    gfx.rows[0].height = Inches(header_h)
    for i in range(len(rows)):
        gfx.rows[i + 1].height = Inches(row_h)

    def _cell(cell, text, size, bold, color, fill, align):
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_left = Inches(0.08)
        cell.margin_right = Inches(0.08)
        cell.margin_top = Inches(0.02)
        cell.margin_bottom = Inches(0.02)
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = align
        r = p.add_run()
        r.text = text
        _set_font(r, size, bold, color)

    for c, h in enumerate(headers):
        _cell(gfx.cell(0, c), h, header_size, True, header_color, header_fill, PP_ALIGN.LEFT)
    for ri, row in enumerate(rows):
        fill = zebra[ri % 2]
        for ci, val in enumerate(row):
            align = PP_ALIGN.RIGHT if ci in align_right_cols else PP_ALIGN.LEFT
            _cell(gfx.cell(ri + 1, ci), val, font_size, False, COLORS["ink"], fill, align)
    return gfx


# ─────────────────────────── 页面 ───────────────────────────
def add_cover(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _rect(s, 0, 0, 13.333, 7.5, COLORS["navy"])
    _rect(s, 0, 0, 13.333, 0.14, COLORS["teal"])
    _rect(s, 0.6, 2.0, 1.6, 0.06, COLORS["teal"])
    _text(s, 0.6, 2.25, 12.0, 1.4, [[("AI Agent 行业现状报告", 44, True, COLORS["white"])]])
    _text(s, 0.6, 3.45, 12.0, 0.9,
          [[("从「能不能做」到「算不算得过账」—— 用产品视角看清 Agent 走到哪、卡在哪、往哪走",
             20, False, RGBColor(0xBF, 0xD0, 0xE8))]])
    _text(s, 0.6, 4.5, 12.0, 0.5,
          [[("目标读者：AI 产品经理 · 技术 / 商业决策者　|　2026-08",
             13, False, RGBColor(0x8E, 0xA3, 0xC4))]])
    chips = ["摘要", "定义", "技术", "市场", "应用", "商业化", "安全", "挑战", "趋势", "建议"]
    x = 0.6
    y = 6.35
    for c in chips:
        w = 0.52 + 0.14 * max(0, len(c) - 2)
        _chip(s, x, y, w, 0.5, c, RGBColor(0x2A, 0x3D, 0x60), RGBColor(0xCF, 0xDD, 0xF0), size=12)
        x += w + 0.16


def add_summary(prs, idx):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _header(s, "1", "摘要", "先看结论", COLORS["teal"], idx)
    # 核心结论卡
    _rect(s, 0.6, 1.55, 12.13, 1.05, COLORS["navy"], round_=True)
    _text(s, 0.85, 1.62, 1.4, 0.4, [[("核心结论", 13, True, COLORS["teal"])]])
    _text(s, 0.85, 2.0, 11.7, 0.6,
          [[("Agent 已从「能不能做」的论证期进入「做得好不好、算不算得过账」的验证期；技术能撑起单点场景，"
             "但可靠性、单位经济、责任归属三道坎，让它还卡在「单点工具」而非「可托付的自主劳动力」。",
             13.5, False, COLORS["white"])]])
    # 关键判断（左）+ 数据快照（右）
    _text(s, 0.6, 2.85, 6.2, 0.4, [[("关键判断", 14, True, COLORS["ink"])]])
    judgments = [
        "瓶颈从「模型不够聪明」转向「不够可靠、可控、便宜」。",
        "市场「框架热、应用冷」：能收上钱的仍是客服 / 代码 / 办公。",
        "竞争从「模型之争」转向「工具 + 数据闭环之争」。",
        "商业化「按调用付费」为主，多数通用场景单位经济未打正。",
        "安全合规是「发布门槛」，责任不清是 B 端采购最大隐性阻力。",
    ]
    jlines = [[("▸  " + j, 12.5, False, COLORS["ink"])] for j in judgments]
    _text(s, 0.6, 3.25, 6.2, 3.5, jlines, spacing=1.25)
    # 数据快照表
    _text(s, 7.0, 2.85, 5.7, 0.4, [[("关键数据快照（多为估计）", 14, True, COLORS["ink"])]])
    _table(s, 7.0, 3.25, [2.6, 2.4, 0.9],
           ["指标", "量级判断", "可信度"],
           [["全球市场规模", "数十亿–百亿美元级", "待核实"],
            ["多步任务成功率", "复杂任务多数 < 50%", "待核实"],
            ["单次调用成本", "普通 LLM 的数倍–数十倍", "待核实"],
            ["头部模型推理", "通过多数「慢思考」基准", "共识"],
            ["MCP 生态采纳", "2025 起成事实工具标准", "共识"]],
           COLORS["teal"], COLORS["white"], font_size=11, row_h=0.42)


def add_definition(prs, idx):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _header(s, "2", "定义与边界", "在讨论什么", COLORS["blue"], idx)
    # 定义四要素
    _rect(s, 0.6, 1.55, 12.13, 0.72, COLORS["tint_blue"], round_=True)
    _text(s, 0.85, 1.62, 1.8, 0.4, [[("Agent 定义", 13, True, COLORS["blue"])]])
    _text(s, 0.85, 1.98, 11.6, 0.3,
          [[("规划 Planning ＋ 工具调用 Tool Use ＋ 记忆 Memory ＋ 自主执行 Autonomy —— 不再只是「回答问题」，而是拆解任务、调用工具、循环完成目标。",
             13, False, COLORS["ink"])]])
    # 递进关系表
    _text(s, 0.6, 2.5, 6.0, 0.4, [[("与相邻形态的递进关系", 14, True, COLORS["ink"])]])
    _table(s, 0.6, 2.92, [1.7, 2.6, 1.7, 1.9],
           ["形态", "核心特征", "自主程度", "与 Agent"],
           [["Chatbot", "只输出文本", "无", "交互底座"],
            ["Copilot", "人主导、AI 辅助", "低", "前置形态"],
            ["RPA / 工作流", "规则固定、确定流程", "中（无理解）", "互补"],
            ["AI Agent", "自主规划 + 工具 + 循环", "高（受约束）", "收敛点"]],
           COLORS["blue"], COLORS["white"], font_size=11, row_h=0.46)
    # 分层
    _text(s, 7.0, 2.5, 5.7, 0.4, [[("Agent 分层", 14, True, COLORS["ink"])]])
    layers = [
        ("单 Agent", "一个模型 + 一组工具，自主循环完成单目标。"),
        ("多 Agent", "多个各司其职的 Agent 协作（编排者 + 执行者）。"),
        ("Agentic Workflow", "把「规划—执行—反思」固化成可复用流程。"),
    ]
    y = 2.92
    for name, desc in layers:
        _rect(s, 7.0, y, 5.7, 0.86, COLORS["card"], line=COLORS["line"], round_=True)
        _text(s, 7.2, y + 0.12, 1.6, 0.4, [[(name, 12.5, True, COLORS["blue"])]])
        _text(s, 8.85, y + 0.12, 3.7, 0.62, [[(desc, 11.5, False, COLORS["ink"])]])
        y += 1.0
    # 判断条
    _rect(s, 0.6, 6.05, 12.13, 0.6, COLORS["tint_blue"], round_=True)
    _text(s, 0.85, 6.05, 11.7, 0.6,
          [[("判断：四者非替代，是「自主程度 × 任务确定性」连续谱上的落点；Agent 专攻 RPA 覆盖不了的非确定任务，二者互补而非竞争。",
             12.5, True, COLORS["ink"])]], anchor=MSO_ANCHOR.MIDDLE)


def add_tech(prs, idx):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _header(s, "3", "技术现状", "能不能做 · 透镜⑧", COLORS["teal"], idx)
    # 模型支撑
    _text(s, 0.6, 1.5, 12.0, 0.4, [[("底层模型的三类支撑", 14, True, COLORS["ink"])]])
    supports = [
        ("推理", "「慢思考」路线抬高多步规划与自我修正的天花板"),
        ("长上下文", "百万级 Token 让记忆 + 任务状态多跑几步不丢线"),
        ("多模态", "「看界面、点按钮」，工具调用边界从 API 扩到 GUI"),
    ]
    x = 0.6
    for name, desc in supports:
        _rect(s, x, 1.92, 3.95, 1.0, COLORS["card"], line=COLORS["line"], round_=True)
        _text(s, x + 0.22, 2.04, 1.0, 0.4, [[(name, 14, True, COLORS["teal"])]])
        _text(s, x + 0.22, 2.42, 3.55, 0.5, [[(desc, 11, False, COLORS["ink"])]])
        x += 4.09
    # 能力现状表
    _text(s, 0.6, 3.12, 6.0, 0.4, [[("核心能力现状", 14, True, COLORS["ink"])]])
    _table(s, 0.6, 3.54, [1.5, 3.2, 1.0],
           ["能力", "现状", "成熟度"],
           [["规划", "简单可用，长程易走偏", "中"],
            ["工具调用", "MCP 标准化后改善，参数仍错", "中高"],
            ["记忆", "短期成熟，长期不成熟", "中低"],
            ["反思", "推理模型带来进步，不保证收敛", "中"]],
           COLORS["teal"], COLORS["white"], font_size=11, row_h=0.44)
    # 瓶颈
    _text(s, 7.0, 3.12, 5.7, 0.4, [[("技术瓶颈", 14, True, COLORS["ink"])]])
    bottlenecks = [
        "幻觉：无法根除，执行类场景代价被急剧放大",
        "多步成功率：步骤越多，错误率累积、成功率骤降",
        "上下文与延迟：窗口大 ≠ 什么都塞，决定交互形态",
        "可靠 vs 自主：越自主越不可控，越可控越退化成工作流",
    ]
    blines = [[("▸  " + b, 12, False, COLORS["ink"])] for b in bottlenecks]
    _text(s, 7.0, 3.54, 5.7, 2.3, blines, spacing=1.2)
    _rect(s, 0.6, 6.05, 12.13, 0.6, COLORS["tint_ai"], round_=True)
    _text(s, 0.85, 6.05, 11.7, 0.6,
          [[("判断：单点、封闭、可验证场景「能」；能否规模化取决于评测体系（透镜⑨）能否把「成功率」变成可管理的指标。",
             12.5, True, COLORS["ink"])]], anchor=MSO_ANCHOR.MIDDLE)


def add_market(prs, idx):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _header(s, "4", "市场与格局", "谁在做 · 做到哪", COLORS["blue"], idx)
    _table(s, 0.6, 1.5, [1.5, 3.2, 2.6, 2.6],
           ["生态层", "代表玩家", "做什么", "商业化"],
           [["模型厂商", "OpenAI / Anthropic / Google ＋ DeepSeek / 智谱 / 通义 / 豆包", "底层推理 + 原生 Agent", "API / 订阅已规模变现"],
            ["框架 / 中间件", "LangChain / CrewAI / AutoGen / Dify / Coze", "编排、工具、多智能体", "开源 / 早期，多数引流"],
            ["平台 / 低代码", "Copilot Studio / Coze / 千帆 / n8n", "非开发者搭建分发", "订阅 / 按量，早期"],
            ["垂直应用", "客服 / 代码 / 办公 / 营销 / 金融", "封装成可交付产品", "分化大，少数赚钱"]],
           COLORS["blue"], COLORS["white"], font_size=10.5, row_h=0.66, header_h=0.46)
    _text(s, 0.6, 4.6, 6.0, 0.4, [[("格局判断", 14, True, COLORS["ink"])]])
    judgements = [
        "模型厂商是当前唯一确定赚到钱的一层。",
        "框架层供给过剩、同质化，价值向「模型 + 数据」两端挤压。",
        "协议标准化（MCP / A2A）把「工具调用」变商品，削弱框架差异化。",
    ]
    jlines = [[("▸  " + j, 12.5, False, COLORS["ink"])] for j in judgements]
    _text(s, 0.6, 5.0, 6.2, 1.9, jlines, spacing=1.3)
    _rect(s, 7.0, 4.6, 5.7, 2.1, COLORS["navy"], round_=True)
    _text(s, 7.25, 4.78, 5.2, 0.4, [[("规模判断", 13, True, COLORS["teal"])]])
    _text(s, 7.25, 5.2, 5.2, 1.3,
          [[("AI Agent 是被普遍看好、但口径混乱的赛道：预测差异极大，短期落地收入远小于预测值。",
             12, False, COLORS["white"])],
           [("结论：市场在「叙事规模」上很大，在「可确认付费收入」上还小。", 12, True, COLORS["white"])]],
          spacing=1.2)


def add_application(prs, idx):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _header(s, "5", "应用落地", "做得好不好 · 透镜⑨", COLORS["teal"], idx)
    _table(s, 0.6, 1.5, [1.2, 2.9, 2.9, 2.6],
           ["场景", "落地形态", "为何跑通", "验证方式"],
           [["代码", "Claude Code / Copilot / 通义灵码", "结果可编译、可测试", "通过率 + 采纳率"],
            ["客服", "智能客服 / 工单 Agent", "任务封闭、容错低", "解决率 + 接管率"],
            ["办公", "邮件 / 文档 / RPA+LLM", "流程相对确定", "任务完成率"],
            ["营销", "素材生成 / 投放优化", "ROI 可归因", "转化 / ROI"],
            ["金融", "尽调 / 报告 / 风控", "数据密集、可审计", "准确率 + 复核"]],
           COLORS["teal"], COLORS["white"], font_size=11, row_h=0.5, header_h=0.44)
    _text(s, 0.6, 4.55, 12.0, 0.4, [[("仍未跑通的场景（核心：评不出好）", 14, True, COLORS["ink"])]])
    unmade = [
        ("长程自主任务", "规划易散、成功率低、责任不清"),
        ("高风险决策 / 执行", "容错成本高，不敢放手给自主"),
        ("长记忆 / 跨系统状态", "记忆层不成熟，状态丢失频繁"),
    ]
    x = 0.6
    for name, desc in unmade:
        _rect(s, x, 4.95, 3.95, 1.05, COLORS["card"], line=COLORS["line"], round_=True)
        _text(s, x + 0.2, 5.07, 3.55, 0.4, [[(name, 12.5, True, COLORS["danger"])]])
        _text(s, x + 0.2, 5.45, 3.55, 0.5, [[(desc, 11, False, COLORS["ink"])]])
        x += 4.09
    _rect(s, 0.6, 6.2, 12.13, 0.55, COLORS["tint_ai"], round_=True)
    _text(s, 0.85, 6.2, 11.7, 0.55,
          [[("判断：落地好坏的分水岭不是「有没有 AI 价值」，而是「能不能建评估集 + 在线指标 + 数据闭环」——评测能力决定落地的顺序。",
             12, True, COLORS["ink"])]], anchor=MSO_ANCHOR.MIDDLE)


def add_business(prs, idx):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _header(s, "6", "商业化与经济性", "值不值赚不赚 · 透镜⑪", COLORS["blue"], idx)
    # 成本结构
    _rect(s, 0.6, 1.5, 12.13, 0.72, COLORS["tint_blue"], round_=True)
    _text(s, 0.85, 1.57, 1.6, 0.4, [[("成本结构", 13, True, COLORS["blue"])]])
    _text(s, 0.85, 1.93, 11.6, 0.3,
          [[("一次 Agent 任务 = 规划 + 多轮工具调用 + 反思，Token 消耗是单次回答的数倍–数十倍，且可能失败重试——每次调用都是真实且叠加的成本。",
             13, False, COLORS["ink"])]])
    # 单位经济表
    _text(s, 0.6, 2.4, 6.0, 0.4, [[("单位经济模型", 14, True, COLORS["ink"])]])
    _table(s, 0.6, 2.82, [1.6, 2.9, 2.3],
           ["环节", "现状", "判断"],
           [["推理成本", "持续降但仍是大头", "被多步放大抵消"],
            ["定价建模", "按量订阅为主，按结果探索", "成本+价值+分层"],
            ["付费意愿", "B 端愿付，C 端只要结果", "分化大"],
            ["数据飞轮", "少数闭环有，多数没有", "真正的护城河"]],
           COLORS["blue"], COLORS["white"], font_size=11, row_h=0.46)
    # 核心矛盾
    _rect(s, 7.0, 2.82, 5.7, 3.1, COLORS["navy"], round_=True)
    _text(s, 7.25, 3.0, 5.2, 0.4, [[("核心矛盾", 13, True, COLORS["teal"])]])
    _text(s, 7.25, 3.45, 5.2, 2.3,
          [[("价值越高（越自主）→ 单次成本越高 → 越难定价 → 越难算清账。", 13, True, COLORS["white"])],
           [("通用场景普遍算不过账；只有「高频、可量化、容错低」的场景单位经济才能打正。", 12, False, RGBColor(0xBF, 0xD0, 0xE8))],
           [("→ 选场景即选商业模式，第一性动作是「算账」而非「堆能力」。", 13, True, COLORS["teal"])]],
          spacing=1.3)
    _rect(s, 0.6, 6.15, 12.13, 0.55, COLORS["tint_blue"], round_=True)
    _text(s, 0.85, 6.15, 11.7, 0.55,
          [[("定价公式（术语 68）：成本打底 + 价值锚定 + 版本分层；护城河来自数据飞轮（术语 70），不是算法本身。",
             12, True, COLORS["ink"])]], anchor=MSO_ANCHOR.MIDDLE)


def add_trust(prs, idx):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _header(s, "7", "信任、安全与合规", "守住底线 · 透镜⑩", COLORS["teal"], idx)
    risks = [
        ("越权 / 误操作", "Agent 拿着权限去执行，一次幻觉可能是一次真实损失"),
        ("提示注入", "工具输入面扩大，恶意内容可借网页 / 邮件诱导越权"),
        ("隐私泄露", "为执行读取更多上下文，数据采集面变大"),
    ]
    x = 0.6
    for name, desc in risks:
        _rect(s, x, 1.5, 3.95, 1.05, COLORS["card"], line=COLORS["line"], round_=True)
        _text(s, x + 0.2, 1.62, 3.55, 0.4, [[(name, 13, True, COLORS["danger"])]])
        _text(s, x + 0.2, 2.0, 3.55, 0.5, [[(desc, 11, False, COLORS["ink"])]])
        x += 4.09
    _text(s, 0.6, 2.8, 6.0, 0.4, [[("可解释性与责任归属", 14, True, COLORS["ink"])]])
    _text(s, 0.6, 3.22, 6.2, 1.6,
          [[("「为什么这么做」说不清（术语 61），事故就无法追责，也就无法批量上线。", 12.5, False, COLORS["ink"])],
           [("B 端最头疼的问题：Agent 做错了，是模型商、平台方、集成商还是使用者的责任？", 12.5, False, COLORS["ink"])]],
          spacing=1.25)
    _text(s, 7.0, 2.8, 5.7, 0.4, [[("合规与监管动向", 14, True, COLORS["ink"])]])
    _text(s, 7.0, 3.22, 5.7, 1.6,
          [[("执行类、高风险类 Agent 会被逐步纳入「高风险系统」审查（可审计、可兜底、可问责）。", 12.5, False, COLORS["ink"])],
           [("具体条款与时间线待核实，但方向明确。", 11.5, False, COLORS["muted"])]],
          spacing=1.25)
    _rect(s, 0.6, 5.1, 12.13, 1.35, COLORS["tint_ai"], round_=True)
    _text(s, 0.85, 5.25, 11.7, 0.4, [[("发布门槛（术语 65）", 13, True, COLORS["teal"])]])
    _text(s, 0.85, 5.68, 11.7, 0.7,
          [[("安全 + 兜底 + 指标 + 监控，不过关不发；红队 + 安全检查 + 分层发布。落到 Agent 上会从「最佳实践」变成「合规刚需」。",
             12.5, False, COLORS["ink"])]])
    _text(s, 0.85, 6.15, 11.7, 0.35,
          [[("Agent 产品经理的第一职责：先想清楚怎么不闯祸，再谈功能多强。", 12.5, True, COLORS["ink"])]])


def add_challenges(prs, idx):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _header(s, "8", "关键挑战汇总", "四类收敛", COLORS["blue"], idx)
    _table(s, 0.6, 1.55, [1.1, 3.3, 7.7],
           ["类别", "挑战", "一句话"],
           [["技术", "幻觉与可靠性", "无法根除，执行类场景代价被放大"],
            ["技术", "多步任务成功率", "步骤越多，端到端成功率越差"],
            ["技术", "长程记忆与状态", "跨会话稳定状态不成熟"],
            ["产品", "评测与验收难", "多数场景「评不出好」，落地无依据"],
            ["产品", "交互形态未定", "高延迟 + 高自主，照搬 Chatbot 体验失效"],
            ["商业", "单位经济打不正", "多步放大成本，通用场景算不过账"],
            ["商业", "定价与付费意愿", "按结果付费难落地，付费意愿分化"],
            ["生态", "框架同质化", "供给过剩，差异化消失"],
            ["生态", "责任归属不清", "B 端规模化采购的隐性阻力"]],
           COLORS["blue"], COLORS["white"], font_size=12, row_h=0.5, header_h=0.44)


def add_trends(prs, idx):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _header(s, "9", "趋势判断", "往哪走 · 12–24 个月", COLORS["teal"], idx)
    _rect(s, 0.6, 1.5, 6.0, 0.55, COLORS["teal"], round_=True)
    _text(s, 0.6, 1.5, 6.0, 0.55, [[("高确定性趋势", 14, True, COLORS["white"])]],
          anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
    certain = [
        "推理成本持续下降，单位经济逐步改善（但多步吃掉红利）",
        "工具调用标准化：MCP / A2A 成事实标准",
        "Agent 深度嵌入垂直工作流，从助手走向交付结果",
        "安全合规前置：可审计、可兜底、分层发布成标配",
        "「慢思考 + 反思」成为 Agent 默认架构",
    ]
    clines = [[("▸  " + t, 12, False, COLORS["ink"])] for t in certain]
    _text(s, 0.7, 2.2, 5.8, 4.3, clines, spacing=1.5)
    _rect(s, 6.85, 1.5, 5.9, 0.55, RGBColor(0xC0, 0x3A, 0x2B), round_=True)
    _text(s, 6.85, 1.5, 5.9, 0.55, [[("高分歧 / 不确定点", 14, True, COLORS["white"])]],
          anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
    uncertain = [
        "多智能体是否真的必要，还是单 Agent + 强工具已够用",
        "是否出现「Agent 平台型超级应用」，入口归属未定",
        "通用 Agent（「一个干所有事」）何时可托付",
        "按结果付费能否成为主流商业模式（取决于价值可归因）",
    ]
    ulines = [[("▸  " + t, 12, False, COLORS["ink"])] for t in uncertain]
    _text(s, 6.95, 2.2, 5.7, 4.3, ulines, spacing=1.5)


def add_conclusion(prs, idx):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _header(s, "10", "结论与建议", "带走什么行动", COLORS["blue"], idx)
    _rect(s, 0.6, 1.55, 12.13, 1.0, COLORS["navy"], round_=True)
    _text(s, 0.85, 1.62, 1.4, 0.4, [[("核心结论", 13, True, COLORS["teal"])]])
    _text(s, 0.85, 2.0, 11.7, 0.55,
          [[("「能不能做」已基本有答案，真正的分水岭是「做得好不好」（评测与数据闭环）和「算不算得过账」（单位经济）——谁先跑通，谁拿到先手。",
             13.5, False, COLORS["white"])]])
    advice = [
        ("1", "用「评测」倒逼「落地」",
         "先定义评估集和在线指标（采纳率 / 任务完成率 / 人工接管率），评不出的场景先不做（透镜⑨）。"),
        ("2", "把「单位经济」当第一过滤器",
         "优先「高频、可量化、容错低、有数据飞轮」的场景，别用堆能力掩盖算不过账（透镜⑪）。"),
        ("3", "把安全与责任当「发布门槛」",
         "内建权限边界、兜底与可审计机制，红队 + 分层发布守住底线，从演示推向生产（透镜⑩）。"),
    ]
    y = 2.9
    for num, title, desc in advice:
        _rect(s, 0.6, y, 12.13, 1.15, COLORS["card"], line=COLORS["line"], round_=True)
        _rect(s, 0.6, y, 0.72, 1.15, COLORS["blue"], round_=True)
        _text(s, 0.6, y, 0.72, 1.15, [[(num, 24, True, COLORS["white"])]],
              anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        _text(s, 1.55, y + 0.14, 3.6, 0.5, [[(title, 15, True, COLORS["ink"])]])
        _text(s, 1.55, y + 0.6, 11.0, 0.5, [[(desc, 12.5, False, COLORS["ink"])]])
        y += 1.32


def add_end(prs, idx):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _rect(s, 0, 0, 13.333, 7.5, COLORS["navy"])
    _rect(s, 0, 7.36, 13.333, 0.14, COLORS["teal"])
    _text(s, 0.6, 2.9, 12.0, 1.0, [[("谢谢", 44, True, COLORS["white"])]],
          align=PP_ALIGN.CENTER)
    _text(s, 0.6, 4.0, 12.0, 0.6,
          [[("事实类数据如能提供最新一手来源，建议回填并替换「待核实 / 估计」标注。", 15, False, RGBColor(0xBF, 0xD0, 0xE8))]],
          align=PP_ALIGN.CENTER)
    _footer(s, idx, TOTAL, dark=True)


# ─────────────────────────── 主流程 ───────────────────────────
def build():
    prs = Presentation()
    prs.slide_width = EMU_W
    prs.slide_height = EMU_H
    add_cover(prs)
    add_summary(prs, 2)
    add_definition(prs, 3)
    add_tech(prs, 4)
    add_market(prs, 5)
    add_application(prs, 6)
    add_business(prs, 7)
    add_trust(prs, 8)
    add_challenges(prs, 9)
    add_trends(prs, 10)
    add_conclusion(prs, 11)
    add_end(prs, 12)
    prs.save(OUT)
    print("[OK] generated:", OUT, "(slides:", len(prs.slides._sldIdLst), ")")


if __name__ == "__main__":
    build()
