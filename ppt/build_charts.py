# -*- coding: utf-8 -*-
"""
《AI Agent 行业现状报告》图表数据 + 生成入口
==================================================
按券商标准图型生成 14 张图（图表1–14），统一「图表X：标题 + 资料来源」格式。
图型遵循 5 份券商样本的铁律：规模→柱+同比折线双轴；份额/占比→饼状；横向对比→柱状/水平条形。
运行：python ppt/build_charts.py
输出：ppt/charts/fig*.png
"""
import charts as C

SRC = "AI-PM-Curriculum"  # 报告整理方（非虚构券商，仅作「整理」署名）


def build():
    outs = {}

    # 图表1：全球 AI Agent 市场规模及同比（柱+折线双轴）
    outs["fig01_market"] = C.combo(
        ["2024", "2025", "2026E", "2027E", "2028E", "2029E", "2030E"],
        [52.6, 78.4, 114.7, 167.8, 245.5, 359.1, 526.2],
        [float("nan"), 49.0, 46.3, 46.3, 46.3, 46.3, 46.5],
        "图表1：全球 AI Agent 市场规模及同比增速（亿美元）",
        "fig01_market", bar_label="市场规模（亿美元）", line_label="同比（%）",
        source="资料来源：MarketsandMarkets，2025；2026-2030 为按 CAGR 46.3% 测算")

    # 图表2：Gartner Agentic AI 支出（广义口径）
    outs["fig02_gartner"] = C.combo(
        ["2026", "2027", "2028E", "2029"],
        [2019, 3714, 5287, 7527],
        [float("nan"), 84.0, 42.3, 42.4],
        "图表2：全球 Agentic AI 支出（广义口径，亿美元）",
        "fig02_gartner", bar_label="支出（亿美元）", line_label="同比（%）",
        source="资料来源：Gartner，2025Q4；2028 为两端插值测算")

    # 图表3：区域市场结构（饼状）
    outs["fig03_region"] = C.pie(
        ["北美", "欧洲", "亚太", "中东及非洲", "拉美"],
        [44, 25, 20, 6, 5],
        "图表3：全球 AI Agent 市场区域结构（2025）", "fig03_region",
        donut=True, source="资料来源：MarketsandMarkets，2025")

    # 图表4：垂直 vs 通用 Agent 增速（柱状）
    outs["fig04_vertical"] = C.bar(
        ["垂直/专用 Agent", "通用/整体 Agent"], [62.7, 44.9],
        "图表4：垂直 Agent 与通用 Agent CAGR 对比（%）", "fig04_vertical",
        color=C.BLUE, highlight=[0],
        source="资料来源：Moltbook 综述（100+ 机构），2026",
        value_fmt=lambda x, _: f"{x:.1f}%")

    # 图表5：企业 Agent 平台部署份额（饼状，CR3 73%）
    outs["fig05_platform"] = C.pie(
        ["Microsoft Copilot Studio", "Salesforce Agentforce", "Anthropic Claude API",
         "Google Vertex AI", "ServiceNow", "其他"],
        [31, 24, 18, 14, 7, 6],
        "图表5：企业 Agent 平台部署份额（2026，CR3 73%）", "fig05_platform",
        donut=True, source="资料来源：KGT / Digital Applied，2026")

    # 图表6：模型层企业工作负载份额（饼状）
    outs["fig06_model_share"] = C.pie(
        ["Anthropic", "OpenAI", "Google", "其他"], [40, 27, 21, 12],
        "图表6：模型层企业工作负载份额（2026）", "fig06_model_share",
        donut=True, source="资料来源：Menlo Ventures，2026")

    # 图表7：价值链收入分布（饼状，[估计]）
    outs["fig07_valuechain"] = C.pie(
        ["上游·算力/云", "下游·应用/软件", "上游·基础模型 API", "中游·框架/平台"],
        [55, 23, 18, 4],
        "图表7：全球 Agentic AI 价值链收入分布（2026E，测算）", "fig07_valuechain",
        donut=True, source="资料来源：基于 Gartner/公开财报重构测算，标 [估计]")

    # 图表8：纯 Agent 产品 ARR 对比（水平条形）
    outs["fig08_arr"] = C.hbar(
        ["Cursor (编码)", "Salesforce Agentforce", "ServiceNow Now Assist",
         "Sierra (客服)", "Intercom Fin (客服)"],
        [40, 12, 10, 2.0, 1.0],
        "图表8：头部纯 Agent 产品年化收入对比（亿美元）", "fig08_arr",
        color=C.TEAL, highlight=[0],
        source="资料来源：公司财报/媒体披露，2026；口径不一，详见正文",
        value_fmt=lambda x, _: f"${x:g}亿")

    # 图表9：SWE-bench Verified（水平条形）
    outs["fig09_swebench"] = C.hbar(
        ["GPT-4o", "DeepSeek-V3", "DeepSeek-R1", "Gemini 2.5 Flash",
         "Gemini 2.5 Pro", "DeepSeek-V3.1", "DeepSeek-V3.2", "Claude Opus 4.5"],
        [33.2, 42.0, 49.2, 48.9, 59.6, 66.0, 73.1, 80.9],
        "图表9：SWE-bench Verified 代码修复成功率（%）", "fig09_swebench",
        color=C.BLUE, highlight=[7],
        source="资料来源：Papers with Code，2025",
        value_fmt=lambda x, _: f"{x:.1f}%")

    # 图表10：OSWorld GUI 操作成功率（水平条形）
    outs["fig10_osworld"] = C.hbar(
        ["GPT-4o（基线，估计）", "Claude 3.7 Sonnet", "OpenAI CUA", "Gemini 2.5",
         "Claude Sonnet 4.5", "人类基线", "Simular Agent S2"],
        [12.0, 34.5, 38.1, 41.4, 61.4, 72.36, 72.6],
        "图表10：OSWorld 计算机操作成功率（%）", "fig10_osworld",
        color=C.BLUE, highlight=[5, 6],
        source="资料来源：OSWorld / Coasty，2025",
        value_fmt=lambda x, _: f"{x:.1f}%")

    # 图表11：METR 长程任务时间线（折线）
    outs["fig11_metr"] = C.line(
        ["Claude 3.7 Sonnet\n(2025-03)", "o3\n(2025)", "GPT-5\n(2025)",
         "Claude Opus 4.5\n(2025-12)"],
        [("50% 时间线", [50, 90, 137, 289], C.TEAL)],
        "图表11：模型长程任务「50% 时间线」演进（分钟）", "fig11_metr",
        ylabel="分钟", source="资料来源：METR（arXiv 2503.14499），2025")

    # 图表12：旗舰模型推理价格下降（折线，输入/输出双系列）
    outs["fig12_cost"] = C.line(
        ["GPT-4\n(2023-03)", "GPT-4 Turbo\n(2023-11)", "GPT-4o\n(2024-05)", "GPT-4o\n(2024-08)"],
        [("输入价", [30, 10, 5, 2.5], C.BLUE),
         ("输出价", [60, 30, 15, 10], C.TEAL)],
        "图表12：OpenAI 旗舰模型推理价格下降（$/1M tokens）", "fig12_cost",
        ylabel="$/1M tokens",
        source="资料来源：OpenAI 官方定价，Deploybase 汇总",
        y_fmt=lambda x, _: f"${x:g}")

    # 图表13：多步任务成功率衰减（折线）
    outs["fig13_decay"] = C.line(
        [1, 5, 10, 15, 20, 40],
        [("端到端成功率", [90, 59, 35, 20, 12, 1.5], C.DANGER)],
        "图表13：多步任务端到端成功率衰减（单步 90%）", "fig13_decay",
        xlabel="步数", ylabel="成功率",
        source="资料来源：Lusser 定律推导（单步 90%），2025",
        y_fmt=lambda x, _: f"{x:.0f}%")

    # 图表14：分场景落地渗透率（柱状）
    outs["fig14_penetration"] = C.bar(
        ["客服", "营销", "代码/开发", "金融"],
        [49, 46, 35, 24],
        "图表14：各场景 AI Agent 部署渗透率（2025，%）", "fig14_penetration",
        color=C.BLUE, source="资料来源：Google Cloud / Zapier 调查，2025",
        value_fmt=lambda x, _: f"{x:.0f}%")

    print("[OK] 生成", len(outs), "张图 ->", C.CHART_DIR)
    for k, v in outs.items():
        print("  ", k, "->", v)
    return outs


if __name__ == "__main__":
    build()
