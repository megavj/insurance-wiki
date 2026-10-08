#!/usr/bin/env python3
"""보험위키 정적 사이트 생성기 (디자인 미적용, 내용·구조만).
모든 항목 = 하나의 하위 페이지(폴더/index.html). 클릭 시 하위 페이지로 이동.
"""
import html, json, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from content import TREE, SITE_TITLE

OUT = os.path.join(os.path.dirname(__file__), "site")
pages = []  # (path, title)

def assign(nodes, parent_path):
    for i, n in enumerate(nodes, 1):
        slug = n["slug"] or f"{i:02d}"
        n["path"] = f"{parent_path}{slug}/"
        assign(n["children"], n["path"])

def esc(s): return html.escape(s, quote=True)

def layout(title, crumbs, body):
    nav = " &gt; ".join(f'<a href="{p}">{esc(t)}</a>' for p, t in crumbs)
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - {SITE_TITLE}</title>
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header class="site-header"><a class="site-title" href="/">{SITE_TITLE}</a></header>
<nav class="breadcrumb">{nav}</nav>
<main class="content">
{body}
</main>
<footer class="site-footer">{SITE_TITLE} · 내용 준비 중</footer>
</body>
</html>
"""

def child_list(children):
    if not children: return ""
    items = []
    for c in children:
        href = c["link"] or c["path"]
        items.append(f'<li><a href="{href}">{esc(c["title"])}</a></li>')
    return '<ul class="child-list">\n' + "\n".join(items) + "\n</ul>"

def write(path, doc):
    d = os.path.join(OUT, path.strip("/"))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)

def render(nodes, crumbs):
    for n in nodes:
        if n["link"]:
            continue  # 다른 메뉴로 연결만 하는 항목
        c = crumbs + [(n["path"], n["title"])]
        body = f'<h1>{esc(n["title"])}</h1>\n'
        if n["note"]:
            body += f'<p class="note">{esc(n["note"])}</p>\n'
        if n["children"]:
            body += '<h2>하위 항목</h2>\n' + child_list(n["children"]) + "\n"
        body += '<section class="article"><h2>내용</h2><p>내용 준비 중입니다.</p></section>\n'
        write(n["path"], layout(n["title"], c, body))
        pages.append({"path": n["path"], "title": n["title"], "check": n["check"],
                      "depth": len(c) - 1, "children": len(n["children"])})
        render(n["children"], c)

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "assets"))
    assign(TREE, "/")
    home = [("/", "홈")]
    body = f"<h1>{SITE_TITLE}</h1>\n<p>보험 지식을 분야별로 정리한 위키입니다. 아래 항목을 눌러 들어가세요.</p>\n"
    body += child_list(TREE)
    write("/", layout("홈", home, body))
    pages.append({"path": "/", "title": "홈", "check": False, "depth": 0, "children": len(TREE)})
    render(TREE, home)
    # 전체 목차(사이트맵) 페이지
    def tree_html(nodes):
        out = "<ul>"
        for n in nodes:
            out += f'<li><a href="{n["link"] or n["path"]}">{esc(n["title"])}</a>' + (tree_html(n["children"]) if n["children"] else "") + "</li>"
        return out + "</ul>"
    write("/sitemap/", layout("전체 목차", home + [("/sitemap/", "전체 목차")], "<h1>전체 목차</h1>\n" + tree_html(TREE)))
    with open(os.path.join(OUT, "assets", "style.css"), "w") as f:
        f.write("/* 디자인 추후 적용 */\nbody{font-family:sans-serif;max-width:960px;margin:0 auto;padding:16px;line-height:1.6}\n.breadcrumb{font-size:14px;margin:8px 0}\n.note{color:#555}\n")
    with open(os.path.join(OUT, "CNAME"), "w") as f: f.write("wiki.primeasset.info\n")
    with open(os.path.join(OUT, ".nojekyll"), "w") as f: f.write("")
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(layout("페이지 없음", home, '<h1>페이지를 찾을 수 없습니다</h1><p><a href="/">홈으로</a></p>'))
    with open(os.path.join(os.path.dirname(__file__), "pages.json"), "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=1)
    print("pages:", len(pages), "check:", sum(p["check"] for p in pages))

if __name__ == "__main__":
    main()
