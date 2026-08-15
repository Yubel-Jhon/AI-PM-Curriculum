# -*- coding: utf-8 -*-
"""用 WPS COM 把 PPTX 每页导出 PNG，便于逐页检查排版。"""
import os
import pythoncom
import win32com.client

PPTX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AI-Agent行业现状报告.pptx")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_preview")
os.makedirs(OUT_DIR, exist_ok=True)

pythoncom.CoInitialize()
app = win32com.client.Dispatch("KWPP.Application")
try:
    pres = app.Presentations.Open(PPTX, ReadOnly=True)
    n = pres.Slides.Count
    for i in range(1, n + 1):
        out = os.path.join(OUT_DIR, "slide_%02d.png" % i)
        pres.Slides(i).Export(out, "PNG", 1600, 900)
    pres.Close()
    print("EXPORTED", n, "slides ->", OUT_DIR)
finally:
    try:
        app.Quit()
    except Exception:
        pass
    pythoncom.CoUninitialize()
