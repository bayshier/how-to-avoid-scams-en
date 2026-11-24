#!/usr/bin/env python3
"""Render the Markdown sources into a static site under _site/ (run by GitHub Actions).

No Jekyll theme or plugin is involved: plain python-markdown plus one stylesheet,
so every page gets the same header, a "back" link and the emergency banner.
"""
import os
import re
import sys

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_site")

STYLE = """
:root{--ink:#1c1c1e;--dim:#5c5c63;--line:#e4e4e8;--bg:#fff;--soft:#f6f6f8;--red:#b42318;--red-bg:#fff1f0;--link:#0b57d0}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif}
main{max-width:760px;margin:0 auto;padding:28px 20px 80px}
header.top{border-bottom:1px solid var(--line);margin-bottom:26px;padding-bottom:14px;font-size:14px;color:var(--dim)}
header.top a{color:var(--dim);text-decoration:none;margin-right:14px}header.top a:hover{color:var(--link)}
.alert{background:var(--red-bg);border:1px solid #f4b7b2;border-radius:10px;padding:14px 16px;margin:0 0 26px;font-size:15px}
.alert b{color:var(--red)}
h1{font-size:1.9em;line-height:1.25;margin:.2em 0 .6em;letter-spacing:-.01em}h2{font-size:1.45em;margin:2em 0 .6em;padding-top:.4em;border-top:1px solid var(--line)}
h3{font-size:1.15em;margin:1.6em 0 .5em}p{margin:.8em 0}
a{color:var(--link)}img,video{max-width:100%;height:auto}
table{border-collapse:collapse;width:100%;font-size:15px;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:7px 10px;text-align:left}th{background:var(--soft)}
code{background:var(--soft);padding:.1em .35em;border-radius:4px;font-size:.9em}pre{background:var(--soft);padding:14px;border-radius:8px;overflow-x:auto}pre code{background:none;padding:0}
blockquote{margin:1em 0;padding:.2em 1em;border-left:4px solid var(--line);color:var(--dim)}
details{border:1px solid var(--line);border-radius:10px;padding:10px 16px;margin:1em 0}summary{cursor:pointer}
footer{margin-top:60px;padding-top:16px;border-top:1px solid var(--line);font-size:14px;color:var(--dim)}
sub{font-size:.75em}
"""

ALERT = (
    '<div class="alert"><b>Being pressured to transfer money, install an app, or share your screen right now?</b> '
    "Hang up first. Then call your bank and the police. "
    '(In China: <b>110</b>, or answer <b>96110</b>. Elsewhere: your local police, or '
    '<a href="https://www.ic3.gov">IC3.gov</a> (US) / Action Fraud (UK).)</div>'
)

md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"], output_format="html5")


def page(title, body_html, depth, path):
    prefix = "../" * depth
    nav = (
        f'<a href="{prefix}index.html">Home</a>'
        f'<a href="{prefix}docs-en/five-blades.html">The Five Blades</a>'
        f'<a href="{prefix}docs-en/glossary-of-scam-slang.html">Glossary</a>'
        f'<a href="https://github.com/bayshier/how-to-avoid-scams-en">GitHub</a>'
    )
    back = f'<p><a href="{prefix}index.html">← All volumes &amp; essays</a></p>' if depth else ""
    # 让 README 里指向 .md 的站内链接在站点上落到 .html
    body_html = re.sub(r'href="((?:\.\./|\./)?(?:book-en|docs-en)/[^"#]+?)\.md(#[^"]*)?"', r'href="\1.html\2"', body_html)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title if title != 'How to Avoid Scams' else title + ' — a field guide to how scams really work'}</title>
<meta name="description" content="Scams change costumes. The manipulation never does. A curated English edition of China's 405-story anti-scam handbook.">
<meta property="og:type" content="website"><meta property="og:title" content="How to Avoid Scams">
<meta property="og:description" content="Scams change costumes. The manipulation never does. Five moves sit behind every con — pig-butchering, money mules, fake police, AI deepfakes.">
<meta property="og:image" content="https://bayshier.github.io/how-to-avoid-scams-en/assets/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="How to Avoid Scams"><meta name="twitter:description" content="Scams change costumes. The manipulation never does."><meta name="twitter:image" content="https://bayshier.github.io/how-to-avoid-scams-en/assets/og.png">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%230f1115'/%3E%3Ctext x='50' y='72' font-size='62' text-anchor='middle' fill='%23ff5a4f' font-family='Arial' font-weight='800'%3E%3F%3C/text%3E%3C/svg%3E">
<style>{STYLE}</style></head><body><main>
<header class="top">{nav}</header>
{ALERT}{back}
{body_html}
<footer>A curated English edition of 《人间防骗指南》 by <a href="https://github.com/QERSSD/HowToAvoidScams">QERSSD</a> ·
translation by <a href="https://github.com/bayshier">bayshier</a> · CC BY-NC-SA 4.0 · Not legal advice.</footer>
</main></body></html>"""


def render(src, dst, depth):
    with open(os.path.join(ROOT, src), encoding="utf-8") as f:
        text = f.read()
    md.reset()
    body = md.convert(text)
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else "How to Avoid Scams"
    os.makedirs(os.path.dirname(os.path.join(OUT, dst)), exist_ok=True)
    with open(os.path.join(OUT, dst), "w", encoding="utf-8") as f:
        f.write(page(title, body, depth, dst))
    return title


titles = [("README.md", "index.html", 0)]
for d in ("book-en", "docs-en"):
    for name in sorted(os.listdir(os.path.join(ROOT, d))):
        if name.endswith(".md"):
            titles.append((f"{d}/{name}", f"{d}/{name[:-3]}.html", 1))

for src, dst, depth in titles:
    t = render(src, dst, depth)
    print(f"{dst:60s} {t[:60]}")
# 静态资源（社交预览图等）原样带入站点
assets = os.path.join(ROOT, "assets")
if os.path.isdir(assets):
    import shutil
    shutil.copytree(assets, os.path.join(OUT, "assets"), dirs_exist_ok=True)

print(f"\n{len(titles)} pages -> _site/ (+ assets/)")
