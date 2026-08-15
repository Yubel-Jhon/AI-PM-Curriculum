# -*- coding: utf-8 -*-
"""
《AI Agent 行业现状报告》图表生成器（matplotlib → PNG）
========================================================
统一配色 + 中文字体 + 无边框，生成可嵌入 PPT 的高清图。
- 折线图 line()：时间序列增长（市场规模、Agentic 支出、推理成本下降）
- 柱状图 bar()：横向对比（各模型 benchmark、细分市场 CAGR、各公司 ARR）
- 水平条形 hbar()：类别多/文字长的横向对比（场景成熟度）
- 饼状图 pie()：结构占比（区域市场、生态层收入结构）

输出目录：<repo>/ppt/charts/*.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "PingFang SC", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 200
plt.rcParams["savefig.facecolor"] = "white"

# 与 PPT 一致的配色
NAVY = "#1B2A4A"
BLUE = "#2D6CDF"
TEAL = "#0FA3A3"
INK = "#1F2937"
MUTED = "#6B7280"
DANGER = "#C03A2B"
LINE = "#D8DEE7"
GRID = "#ECF0F5"

PALETTE = [BLUE, TEAL, "#F59E0B", DANGER, "#8B5CF6", "#10B981", NAVY, MUTED]

CHART_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "charts")
os.makedirs(CHART_DIR, exist_ok=True)


def _base_fig(w=7.2, h=4.0):
    fig, ax = plt.subplots(figsize=(w, h))
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=9)
    return fig, ax


def _title(ax, title, unit_note=""):
    ax.set_title(title, color=INK, fontsize=13, fontweight="bold", pad=12, loc="left")
    if unit_note:
        ax.text(0.0, 1.06, unit_note, transform=ax.transAxes,
                color=MUTED, fontsize=8.5, va="bottom")


def _finish(fig, name, tight=True):
    out = os.path.join(CHART_DIR, name + ".png")
    fig.savefig(out, bbox_inches="tight" if tight else None,
                pad_inches=0.15, facecolor="white")
    plt.close(fig)
    return out


def line(xs, series, title, name, unit="", xlabel="", ylabel="",
         source="", mark_every=1, y_fmt=None):
    """series: list of (label, ys, color). xs: x 轴刻度."""
    fig, ax = _base_fig()
    for label, ys, color in series:
        ax.plot(xs, ys, marker="o", markersize=4.5, linewidth=2.2,
                color=color, label=label, zorder=3)
    ax.grid(axis="y", color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    _title(ax, title, source)
    if xlabel:
        ax.set_xlabel(xlabel, color=MUTED, fontsize=9)
    if ylabel:
        ax.set_ylabel(ylabel, color=MUTED, fontsize=9)
    if y_fmt:
        ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))
    if len(series) > 1:
        ax.legend(frameon=False, fontsize=9, loc="best", ncols=len(series))
    return _finish(fig, name)


def bar(categories, values, title, name, color=BLUE, unit="", source="",
        value_fmt=None, rotate=0, highlight=None):
    """vertical bar. highlight: list of bool 或 int 下标列表标红."""
    fig, ax = _base_fig()
    colors = [color] * len(categories)
    if highlight is not None:
        for i in highlight:
            colors[i] = DANGER
    ax.bar(categories, values, color=colors, width=0.6, zorder=3)
    ax.grid(axis="y", color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    _title(ax, title, source)
    if rotate:
        plt.setp(ax.get_xticklabels(), rotation=rotate, ha="right")
    if value_fmt:
        ax.yaxis.set_major_formatter(FuncFormatter(value_fmt))
        # 柱顶标数值
        for i, v in enumerate(values):
            ax.text(i, v, value_fmt(v, None), ha="center", va="bottom",
                    fontsize=8.5, color=INK)
    return _finish(fig, name)


def hbar(categories, values, title, name, color=TEAL, unit="", source="",
         value_fmt=None, highlight=None):
    """horizontal bar，适合类别文字长的对比."""
    fig, ax = _base_fig(h=0.5 + 0.5 * len(categories))
    y = range(len(categories))
    colors = [color] * len(categories)
    if highlight is not None:
        for i in highlight:
            colors[i] = DANGER
    ax.barh(list(y), values, color=colors, height=0.62, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels(categories, fontsize=10, color=INK)
    ax.invert_yaxis()
    ax.grid(axis="x", color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    _title(ax, title, source)
    for i, v in enumerate(values):
        label = value_fmt(v, None) if value_fmt else str(v)
        ax.text(v, i, "  " + label, va="center", ha="left",
                fontsize=8.5, color=INK)
    ax.set_xlim(0, max(values) * 1.18 if values else 1)
    return _finish(fig, name)


def pie(labels, values, title, name, source="", donut=False, start_angle=90):
    """饼状图 / 环形图，占比结构."""
    fig, ax = _base_fig()
    colors = PALETTE[:len(labels)]
    if donut:
        wedges, _, autotexts = ax.pie(
            values, labels=labels, colors=colors, autopct="%.0f%%",
            startangle=start_angle, pctdistance=0.78,
            wedgeprops=dict(width=0.42, edgecolor="white", linewidth=2))
    else:
        wedges, _, autotexts = ax.pie(
            values, labels=labels, colors=colors, autopct="%.0f%%",
            startangle=start_angle, pctdistance=0.72,
            wedgeprops=dict(edgecolor="white", linewidth=2))
    for t in autotexts:
        t.set_color("white")
        t.set_fontsize(9.5)
        t.set_fontweight("bold")
    ax.set_title(title, color=INK, fontsize=13, fontweight="bold", pad=12, loc="left")
    if source:
        ax.text(0.0, 1.03, source, transform=ax.transAxes,
                color=MUTED, fontsize=8.5, va="bottom")
    return _finish(fig, name)


def combo(categories, bar_vals, line_vals, title, name, bar_label="", line_label="",
          unit="", source="", bar_color=BLUE, line_color=DANGER):
    """柱状 + 同比折线双轴（券商标准图型：左轴规模柱，右轴增速线）。"""
    fig, ax = _base_fig()
    x = list(range(len(categories)))
    ax.bar(x, bar_vals, color=bar_color, width=0.58, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels([str(c) for c in categories], fontsize=9, color=INK)
    ax.set_ylabel(bar_label or unit, color=bar_color, fontsize=9)
    ax.tick_params(axis="y", colors=bar_color, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    for i, v in enumerate(bar_vals):
        ax.text(i, v, f"{v:g}", ha="center", va="bottom", fontsize=8, color=INK)
    ax2 = ax.twinx()
    ax2.plot(x, line_vals, marker="o", markersize=4, linewidth=2,
             color=line_color, zorder=4)
    ax2.set_ylabel(line_label or "同比(%)", color=line_color, fontsize=9)
    ax2.tick_params(axis="y", colors=line_color, labelsize=9)
    ax2.spines["top"].set_visible(False)
    ax2.grid(False)
    _title(ax, title, source)
    return _finish(fig, name)


if __name__ == "__main__":
    # 自测
    line([2024, 2025, 2026, 2027, 2028, 2029, 2030],
         [("市场规模", [52, 70, 95, 130, 180, 250, 470], BLUE)],
         "全球 AI Agent 市场规模（亿美元）", "test_line",
         source="资料来源：MarketsandMarkets，示例数据",
         ylabel="亿美元", y_fmt=lambda x, _: f"{int(x)}")
    bar(["代码", "客服", "办公", "营销", "金融"],
        [62.7, 44.9, 40, 38, 35], "各场景 CAGR（%）", "test_bar",
        color=BLUE, source="资料来源：示例数据", value_fmt=lambda x, _: f"{x:.0f}%")
    pie(["北美", "亚太", "欧洲", "其他"], [45, 30, 18, 7],
        "全球 AI Agent 市场区域结构", "test_pie", donut=True)
    print("charts ok:", CHART_DIR)
