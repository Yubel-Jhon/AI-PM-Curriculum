# -*- coding: utf-8 -*-
"""Programmatic layout audit: instrument build_agent_report_ppt.py to capture
every text box / card / table / picture, then measure rendered text fit using
real Microsoft YaHei font metrics (at 120 PPI export scale).

Flags:
  OVERFLOW_Y : estimated rendered text height exceeds its box height
  OVERFLOW_X : a single unbreakable run exceeds its box width
  TIGHT      : within 5% of the box height (probable visual cramping)
  PAST_RIGHT : any element's right edge > 12.73" (right margin = left 0.6")
  PAST_FOOTER: any body element's bottom edge crosses the footer line (7.14")
"""
import os, sys, importlib.util
from PIL import ImageFont
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "build_agent_report_ppt.py")

spec = importlib.util.spec_from_file_location("bld", SRC)
m = importlib.util.module_from_spec(spec)
sys.modules["bld"] = m
spec.loader.exec_module(m)

PPI = 120.0
PT2PX = PPI / 72.0

_FONT_CACHE = {}
def _font(size_pt, bold=False):
    key = (round(size_pt, 2), bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    path = "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"
    try:
        f = ImageFont.truetype(path, int(round(size_pt * PT2PX)))
    except Exception:
        f = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", int(round(size_pt * PT2PX)))
    _FONT_CACHE[key] = f
    return f

def _line_h(size_pt, spacing):
    f = _font(size_pt)
    asc, desc = f.getmetrics()
    return (asc + desc) * spacing / PPI  # inches

def _char_breakable(ch):
    o = ord(ch)
    if ch.isspace():
        return True
    if 0x4E00 <= o <= 0x9FFF or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF:
        return True
    if 0x2000 <= o <= 0x206F:
        return True
    return False

def _wrap_lines(text, size_pt, width_in):
    """Return (n_lines, max_line_width_in). Greedy CJK/latin-aware wrap."""
    f = _font(size_pt)
    maxw = width_in * PPI
    n = 1
    cur = 0.0
    max_line = 0.0
    i = 0
    # token = either a latin word or a single breakable char
    while i < len(text):
        ch = text[i]
        if _char_breakable(ch):
            w = f.getlength(ch)
            if cur + w > maxw and cur > 0:
                max_line = max(max_line, cur)
                n += 1
                cur = w
            else:
                cur += w
            i += 1
        else:
            # consume a latin/number word
            j = i
            while j < len(text) and not _char_breakable(text[j]):
                j += 1
            w = f.getlength(text[i:j])
            if cur + w > maxw and cur > 0:
                max_line = max(max_line, cur)
                n += 1
                cur = w
            else:
                cur += w
            i = j
    max_line = max(max_line, cur)
    return n, max_line / PPI

# ---------- capture ----------
records = []  # dicts
SLIDE_IDX = [0]

class _Fake:
    pass

def _slide_for():
    s = _Fake()
    s.shapes = _Fake()
    return s

def rec_rect(slide, L, T, W, H, fill, line=None, round_=False, line_w=None):
    records.append(dict(kind="rect", slide=SLIDE_IDX[0], L=L, T=T, W=W, H=H, fill=fill, round=round_))

def rec_text(slide, L, T, W, H, lines, anchor=None, align=None, spacing=1.0):
    records.append(dict(kind="text", slide=SLIDE_IDX[0], L=L, T=T, W=W, H=H, lines=lines, spacing=spacing))

def rec_table(slide, L, T, col_widths, headers, rows, header_fill=None, header_color=None,
              font_size=11.5, header_size=12, row_h=0.44, header_h=0.5,
              align_right_cols=(), zebra=None):
    records.append(dict(kind="table", slide=SLIDE_IDX[0], L=L, T=T, col_widths=col_widths,
                        headers=headers, rows=rows, font_size=font_size, row_h=row_h, header_h=header_h))

def rec_pic(slide, name, L, T, W, H):
    records.append(dict(kind="pic", slide=SLIDE_IDX[0], name=name, L=L, T=T, W=W, H=H))

m._rect = rec_rect
m._text = rec_text
m._table = rec_table
m._pic = rec_pic

prs = _Fake()
prs.slide_layouts = [_Fake() for _ in range(7)]
class _Slides:
    def add_slide(self, layout):
        SLIDE_IDX[0] += 1
        return _slide_for()
prs.slides = _Slides()

# call all add_* functions in order
m.add_cover(prs)
for fn in ["add_summary","add_toc","add_definition","add_industry_chain",
           "add_market_scale","add_market_segment","add_competition_share",
           "add_competition_matrix","add_companies_table","add_companies_chart",
           "add_tech_bench","add_tech_metr_cost","add_tech_decay","add_application",
           "add_trust","add_business","add_trends","add_investment","add_risk","add_disclaimer"]:
    getattr(m, fn)(prs, 1)

# ---------- analyze ----------
def para_text(lines):
    return "".join(t for p in lines for (t, *_r) in p)

def para_max_size(lines):
    return max((r[1] for p in lines for r in p), default=0)

RIGHT_MARGIN = 0.6
RIGHT_EDGE = 12.76  # 容差到 12.76"（≈0.57" 右边距，2px 以内视为对齐）
FOOTER_Y = 7.14

findings = []
for r in records:
    s = r["slide"]
    if r["kind"] == "text":
        W, H = r["W"], r["H"]
        # estimate wrapped height
        total_h = 0.0
        for p in r["lines"]:
            text = "".join(t for (t, *_r) in p)
            sz = max((run[1] for run in p), default=10)
            if text.strip() == "":
                continue
            n, _mw = _wrap_lines(text, sz, W)
            total_h += _line_h(sz, r["spacing"]) * n
        # horizontal overflow: only truly unbreakable latin/number token wider than box
        hx = False
        for p in r["lines"]:
            for (t, sz, *_r) in p:
                f = _font(sz)
                tok = []
                for ch in t:
                    if _char_breakable(ch):
                        if tok:
                            if f.getlength("".join(tok)) / PPI > W * 1.02:
                                hx = True
                            tok = []
                    else:
                        tok.append(ch)
                if tok and f.getlength("".join(tok)) / PPI > W * 1.02:
                    hx = True
        tag = []
        if total_h > H + 0.03:
            tag.append(f"OVERFLOW_Y text~{total_h:.2f}\" > box {H:.2f}\"")
        elif total_h > H * 0.95:
            tag.append(f"TIGHT text~{total_h:.2f}\" vs box {H:.2f}\"")
        if hx:
            tag.append("OVERFLOW_X unbreakable token wider than box")
        if r["L"] + W > RIGHT_EDGE + 0.01:
            tag.append(f"PAST_RIGHT edge={r['L']+W:.2f}\"")
        if tag:
            snippet = para_text(r["lines"])[:24]
            findings.append((s, "text", f"L={r['L']:.2f} T={r['T']:.2f} W={W:.2f} H={H:.2f} | {snippet}... | {'; '.join(tag)}"))
    elif r["kind"] == "rect":
        # skip full-bleed background (L≈0 and T≈0) and bottom accent bars
        if r["L"] < 0.01 and r["T"] < 0.01:
            continue
        if r["L"] < 0.01 and r["T"] > 7.2 and r["H"] < 0.3:
            continue
        if r["L"] + r["W"] > RIGHT_EDGE + 0.01:
            findings.append((s, "rect", f"L={r['L']:.2f} T={r['T']:.2f} W={r['W']:.2f} H={r['H']:.2f} | PAST_RIGHT edge={r['L']+r['W']:.2f}\""))
        if r["T"] + r["H"] > FOOTER_Y + 0.005 and r["T"] < FOOTER_Y and r["H"] > 0.05:
            findings.append((s, "rect", f"L={r['L']:.2f} T={r['T']:.2f} H={r['H']:.2f} | PAST_FOOTER bottom={r['T']+r['H']:.2f}\""))
    elif r["kind"] == "table":
        W = sum(r["col_widths"])
        right = r["L"] + W
        bot = r["T"] + r["header_h"] + r["row_h"] * len(r["rows"])
        if right > RIGHT_EDGE + 0.01:
            findings.append((s, "table", f"L={r['L']:.2f} W={W:.2f} | PAST_RIGHT edge={right:.2f}\""))
        # cell text fit
        for ci, cw in enumerate(r["col_widths"]):
            inner = cw - 0.16  # margins
            # header cell
            hn, _ = _wrap_lines(r["headers"][ci], 12, inner)
            hh = _line_h(12, 1.0) * hn
            if hh > r["header_h"] - 0.04:
                findings.append((s, "table", f"col{ci} header '{r['headers'][ci]}' ~{hn}ln vs header_h {r['header_h']}\""))
            for ri, row in enumerate(r["rows"]):
                txt = row[ci]
                n, _ = _wrap_lines(txt, r["font_size"], inner)
                th = _line_h(r["font_size"], 1.0) * n
                if th > r["row_h"] - 0.04:
                    findings.append((s, "table", f"col{ci} row{ri} '{txt[:14]}' ~{n}ln vs row_h {r['row_h']}\""))
    elif r["kind"] == "pic":
        if r["L"] + r["W"] > RIGHT_EDGE + 0.01:
            findings.append((s, "pic", f"{r['name']} PAST_RIGHT edge={r['L']+r['W']:.2f}\""))
        if r["T"] + r["H"] > FOOTER_Y + 0.005:
            findings.append((s, "pic", f"{r['name']} PAST_FOOTER bottom={r['T']+r['H']:.2f}\""))

findings.sort(key=lambda x: x[0])

# ---------- text-text overlap (the "UI 重叠" the user sees) ----------
def _overlap_area(a, b):
    x = max(0.0, min(a["L"] + a["W"], b["L"] + b["W"]) - max(a["L"], b["L"]))
    y = max(0.0, min(a["T"] + a["H"], b["T"] + b["H"]) - max(a["T"], b["T"]))
    return x * y

texts_by_slide = {}
for r in records:
    if r["kind"] == "text":
        texts_by_slide.setdefault(r["slide"], []).append(r)

overlap_flags = []
for s, ts in texts_by_slide.items():
    for i in range(len(ts)):
        for j in range(i + 1, len(ts)):
            a, b = ts[i], ts[j]
            ov = _overlap_area(a, b)
            smaller = min(a["W"] * a["H"], b["W"] * b["H"])
            if smaller > 0 and ov / smaller > 0.30:
                ta = para_text(a["lines"])[:18]
                tb = para_text(b["lines"])[:18]
                overlap_flags.append((s, f"TEXT-OVERLAP '{ta}' vs '{tb}' | "
                                        f"a(L{a['L']:.2f},T{a['T']:.2f},W{a['W']:.2f},H{a['H']:.2f}) "
                                        f"b(L{b['L']:.2f},T{b['T']:.2f},W{b['W']:.2f},H{b['H']:.2f}) ov={ov/smaller:.0%}"))

overlap_flags.sort(key=lambda x: x[0])
print("\n--- text-text overlap ---")
for s, msg in overlap_flags:
    print(f"[slide {s:02d}] {msg}")
print("overlap count:", len(overlap_flags))

# ---------- table vs any body element collision (table 是数据块，不应叠任何东西) ----------
def _bbox(r):
    if r["kind"] == "table":
        W = sum(r["col_widths"])
        H = r["header_h"] + r["row_h"] * len(r["rows"])
    else:
        W, H = r["W"], r["H"]
    return (r["L"], r["T"], W, H)

def _is_fullbleed(r):
    return r["kind"] == "rect" and r["L"] < 0.01 and r["T"] < 0.01

collide_flags = []
for r in records:
    if r["kind"] != "table":
        continue
    a = _bbox(r)
    for o in records:
        if o is r or _is_fullbleed(o):
            continue
        if o["slide"] != r["slide"]:
            continue
        b = _bbox(o)
        ox = max(0.0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
        oy = max(0.0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
        if ox > 0.02 and oy > 0.02:
            tname = "·".join(r["headers"])
            collide_flags.append((r["slide"], f"TABLE '{tname}' 与 {o['kind']} 重叠 "
                                f"({ox:.2f}\"x{oy:.2f}\") table(L{r['L']:.2f},T{r['T']:.2f}) "
                                f"other(L{o['L']:.2f},T{o['T']:.2f})"))

collide_flags.sort(key=lambda x: x[0])
print("\n--- table collision ---")
if not collide_flags:
    print("none")
for s, msg in collide_flags:
    print(f"[slide {s:02d}] {msg}")

print("\n--- geometric flags ---")
if not findings:
    print("No programmatic flags.")
for s, kind, msg in findings:
    print(f"[slide {s:02d}] {kind:5s} {msg}")
print("\nTotal flags:", len(findings), "| overlaps:", len(overlap_flags), "| table-collisions:", len(collide_flags))
