# -*- coding: utf-8 -*-
"""
AI-PM 面试词云生成器

读 interview/面试方法论.md + interview/高频题刷题卡.json，统计关键概念词频，
产出自包含 HTML 词云（canvas 螺旋布局 + 悬浮显示词频，深色主题）。

用法：
    python build_wordcloud.py
"""

import os
import re
import json
from collections import Counter

_ROOT = os.path.dirname(os.path.abspath(__file__))

# 关键词 → 类别（用于上色）
KEYWORDS = {
    "tech": ["RAG", "微调", "幻觉", "Agent", "Prompt", "向量库", "评测集", "数据闭环",
             "Function Calling", "模型选型", "GRPO", "LoRA", "Transformer", "CoT",
             "Skills", "MCP", "Workflow", "vibe coding", "badcase", "知识时效性",
             "转人工率", "上下文", "召回", "重排", "数据飞轮", "降级", "兜底", "FAQ",
             "采纳率", "切片"],
    "safety": ["红队", "Prompt注入", "隐私", "伦理", "公平性", "可解释性",
               "内容安全", "发布门槛", "红线", "逃生阀"],
    "biz": ["定价", "商业化", "单位经济", "Token", "竞品", "护城河", "付费", "差异化"],
    "company": ["字节", "抖音", "阿里", "蚂蚁", "百度", "追觅", "文心一言", "豆包", "AI独角兽"],
    "method": ["项目题", "概念题", "方案题", "业务题", "估算题", "追问", "压力题",
               "红黑榜", "三层法", "深挖", "雷区", "数据工具", "复盘"],
}

CAT_LABEL = {"tech": "概念/技术", "safety": "安全/伦理", "biz": "商业化",
             "company": "公司", "method": "题型/方法"}


def load_text():
    parts = []
    md = os.path.join(_ROOT, "interview", "面试方法论.md")
    with open(md, encoding="utf-8") as f:
        parts.append(f.read())
    jf = os.path.join(_ROOT, "interview", "高频题刷题卡.json")
    with open(jf, encoding="utf-8") as f:
        cards = json.load(f)
    for c in cards:
        parts.append(c.get("题目", ""))
        parts.append(c.get("回答要点", ""))
        parts.append(" ".join(c.get("标签", [])))
        parts.append(" ".join(c.get("追问链", [])))
        parts.append(c.get("踩坑", ""))
    return "\n".join(parts)


def count_keywords(text):
    lowered = text.lower()
    words = []
    for cat, terms in KEYWORDS.items():
        for t in terms:
            n = lowered.count(t.lower()) if t.isascii() else text.count(t)
            if n > 0:
                words.append({"text": t, "count": n, "cat": cat})
    # 去重（同词多类别只留 count 最大者），按词频降序
    best = {}
    for w in words:
        k = w["text"]
        if k not in best or w["count"] > best[k]["count"]:
            best[k] = w
    out = sorted(best.values(), key=lambda x: -x["count"])
    # 过滤掉只出现 1 次的词，去掉纯噪声，词云更干净
    return [w for w in out if w["count"] >= 2]


def build_html(words):
    payload = json.dumps({"words": words, "labels": CAT_LABEL}, ensure_ascii=False)
    return HTML_TEMPLATE.replace("__WORDS__", payload)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI-PM 面试词云</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; background: #0f172a; color: #e2e8f0; }
  header { padding: 14px 20px; background: #1e293b; border-bottom: 1px solid #334155; display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap; }
  header h1 { font-size: 16px; font-weight: 600; }
  header .sub { font-size: 12px; color: #94a3b8; }
  .wrap { max-width: 1180px; margin: 0 auto; padding: 20px; }
  #cloud { width: 100%; height: 620px; border: 1px solid #334155; border-radius: 10px; background: #0b1220; position: relative; cursor: default; }
  #cloud canvas { display: block; }
  .legend { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 14px; font-size: 12px; color: #cbd5e1; }
  .legend .row { display: flex; align-items: center; gap: 6px; }
  .legend .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
  .legend .note { color: #64748b; margin-left: auto; }
  .tooltip { position: fixed; pointer-events: none; background: #0f172a; border: 1px solid #334155; border-radius: 6px; padding: 6px 10px; font-size: 12px; display: none; z-index: 20; }
</style>
</head>
<body>
<header>
  <h1>AI-PM 面试词云</h1>
  <span class="sub">字越大 = 面试材料里出现越多（数据源：面试方法论.md + 高频题刷题卡.json）</span>
</header>
<div class="wrap">
  <div id="cloud"></div>
  <div class="legend" id="legend"></div>
</div>
<div class="tooltip" id="tooltip"></div>

<script>
const DATA = __WORDS__;
const words = DATA.words.slice().sort((a, b) => b.count - a.count);
const CAT_COLOR = {tech: '#22d3ee', safety: '#16a34a', biz: '#eab308', company: '#a855f7', method: '#ec4899'};

const cloud = document.getElementById('cloud');
const canvas = document.createElement('canvas');
cloud.appendChild(canvas);
const ctx = canvas.getContext('2d');
const tooltip = document.getElementById('tooltip');

const minC = words[words.length - 1].count;
const maxC = words[0].count;
function sizeOf(c) {
  const t = (c - minC) / (maxC - minC || 1);
  return Math.round(13 + Math.sqrt(t) * 46); // 13..59
}

let placed = [];

function layout() {
  const dpr = window.devicePixelRatio || 1;
  const W = cloud.clientWidth, H = cloud.clientHeight;
  canvas.width = W * dpr; canvas.height = H * dpr;
  canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
  ctx.scale(dpr, dpr);
  ctx.fillStyle = '#0b1220'; ctx.fillRect(0, 0, W, H);
  ctx.textBaseline = 'top'; ctx.textAlign = 'left';

  placed = [];
  const cx = W / 2, cy = H / 2;
  const pad = 3;

  words.forEach(w => {
    const size = sizeOf(w.count);
    ctx.font = `${size}px "Microsoft YaHei", "PingFang SC", sans-serif`;
    const tw = ctx.measureText(w.text).width;
    const th = Math.round(size * 1.25);

    let angle = Math.random() * Math.PI * 2;
    let r = 0, x = 0, y = 0, ok = false;
    while (r < Math.max(W, H) * 1.5) {
      x = cx + Math.cos(angle) * r - tw / 2;
      y = cy + Math.sin(angle) * r - th / 2;
      let hit = false;
      for (const p of placed) {
        if (x < p.x + p.w + pad && x + tw > p.x - pad &&
            y < p.y + p.h + pad && y + th > p.y - pad) { hit = true; break; }
      }
      if (!hit) { ok = true; break; }
      angle += 0.12;
      r += 2.4;
    }
    if (!ok) return;
    placed.push({text: w.text, count: w.count, cat: w.cat, x, y, w: tw, h: th, size});
  });

  placed.forEach(p => {
    ctx.font = `${p.size}px "Microsoft YaHei", "PingFang SC", sans-serif`;
    ctx.fillStyle = CAT_COLOR[p.cat] || '#94a3b8';
    ctx.fillText(p.text, p.x, p.y);
  });
}

// 图例
(function legend() {
  const labels = DATA.labels;
  document.getElementById('legend').innerHTML =
    Object.keys(CAT_COLOR).map(k =>
      `<div class="row"><span class="dot" style="background:${CAT_COLOR[k]}"></span>${labels[k] || k}</div>`
    ).join('') +
    `<span class="note">共 ${words.length} 个词 · 悬浮看词频 · 窗口大小变化自动重排</span>`;
})();

// 悬浮显示词频
canvas.addEventListener('mousemove', e => {
  const rect = canvas.getBoundingClientRect();
  const mx = e.clientX - rect.left, my = e.clientY - rect.top;
  const hit = placed.find(p => mx >= p.x && mx <= p.x + p.w && my >= p.y && my <= p.y + p.h);
  if (hit) {
    tooltip.style.display = 'block';
    tooltip.innerHTML = `<b>${hit.text}</b> · ${hit.count} 次`;
    tooltip.style.left = (e.clientX + 12) + 'px';
    tooltip.style.top = (e.clientY + 12) + 'px';
  } else {
    tooltip.style.display = 'none';
  }
});
canvas.addEventListener('mouseleave', () => tooltip.style.display = 'none');

window.addEventListener('resize', () => { ctx.setTransform(1, 0, 0, 1, 0, 0); layout(); });

ctx.setTransform(1, 0, 0, 1, 0, 0);
layout();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    text = load_text()
    words = count_keywords(text)
    for w in words:
        print(f"{w['count']:>3}  {w['text']:<18} {CAT_LABEL[w['cat']]}")
    print(f"\n共 {len(words)} 个词")
    html_path = os.path.join(_ROOT, "面试词云.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html(words))
    print("HTML ->", html_path)
