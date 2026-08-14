# -*- coding: utf-8 -*-
"""把同目录下 3 个 .md 源文件生成成一份 .xmind（Xmind 2020+ zen 格式）。

用法：python gen.py
输入：板块式全书总结.md / 能力自评清单大表.md / 阶段式学习路径.md
输出：产品经理就业知识体系-全书总结.xmind
"""
import json, zipfile, uuid, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_XMIND = os.path.join(HERE, "产品经理就业知识体系-全书总结.xmind")

SHEETS = [
    ("板块式全书总结.md", "板块式全书总结", "org.xmind.ui.map"),
    ("能力自评清单大表.md", "能力自评清单大表", "org.xmind.ui.spreadsheet"),
    ("阶段式学习路径.md", "阶段式学习路径", "org.xmind.ui.logic.right"),
]


def parse_md(md):
    lines = md.split("\n")
    stack = []  # (level, node)
    roots = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith("- ") or line.startswith("* "):
            if stack:
                stack[-1][1].setdefault("children", []).append({"title": line[2:].strip()})
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = line.lstrip("#").strip()
            node = {"title": text, "children": []}
            while stack and stack[-1][0] >= level:
                stack.pop()
            if stack:
                stack[-1][1]["children"].append(node)
            else:
                roots.append(node)
            stack.append((level, node))
    return roots


def build_topic(node, structure=None, root=False):
    t = {"id": uuid.uuid4().hex, "title": node["title"]}
    if root:
        t["class"] = "topic"
        t["titleUnedited"] = False
        if structure:
            t["structureClass"] = structure
    if node.get("children"):
        t["children"] = {"attached": [build_topic(c) for c in node["children"]]}
    return t


def main():
    content = []
    for fname, title, structure in SHEETS:
        with open(os.path.join(HERE, fname), encoding="utf-8") as f:
            roots = parse_md(f.read())
        root_node = roots[0] if roots else {"title": title, "children": []}
        content.append({
            "id": uuid.uuid4().hex,
            "class": "sheet",
            "title": title,
            "rootTopic": build_topic(root_node, structure=structure, root=True),
        })

    with zipfile.ZipFile(OUT_XMIND, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.json", json.dumps(content, ensure_ascii=False))
        z.writestr("metadata.json", json.dumps({"dataStructureVersion": "2", "layoutEngineVersion": "5"}))
        z.writestr("manifest.json", json.dumps({"file-entries": {"content.json": {}, "metadata.json": {}}}))
    print("OK ->", OUT_XMIND)


if __name__ == "__main__":
    main()
