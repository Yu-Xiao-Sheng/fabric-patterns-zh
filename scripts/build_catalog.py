#!/usr/bin/env python3
"""Render catalog.md and docs/index.html from data/patterns.json.

Usage: python3 scripts/build_catalog.py
Single source of truth is data/patterns.json; both outputs are generated,
never edit them by hand.
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GROUP_ORDER = [
    "安全攻防", "开发与代码", "可视化生成", "摘要总结", "信息提取",
    "AI 与提示词工程", "商业与产品", "学习与研究", "个人成长与身心",
    "写作与文本加工", "分析与批判性思维", "格式转换与其他",
]
GROUP_DESC = {
    "安全攻防": "作者是安全研究者出身，这是全库最硬核的一组：威胁建模、恶意代码与日志分析、Sigma/Semgrep 规则生成等。",
    "开发与代码": "写代码、审代码、解释代码、生成提交信息与设计文档，日常开发最常用的一组。",
    "可视化生成": "把文本和数据变成 Mermaid 图、概念图、GraphViz 等可视化产物。",
    "摘要总结": "各种粒度的总结：全文、微摘要、五句摘要、辩论、播客、Git 变更、YouTube 等。",
    "信息提取": "从长内容里结构化淘金：观点、智慧、金句、洞见、书单、预测、要点等。extract_wisdom 是全库招牌。",
    "AI 与提示词工程": "提示词的创建与改进、AI 概念问答等元工具类 Pattern。",
    "商业与产品": "PRD、用户故事、协议审查、销售通话与产品反馈分析等。",
    "学习与研究": "论文分析、学术写作、测验与教案生成、概念讲解等。",
    "个人成长与身心": "自我提升、阅读计划、心理疗愈与健康类，个人色彩浓，不少偏小众。",
    "写作与文本加工": "写作改进、润色清理、文风转换、内容创作等。",
    "分析与批判性思维": "对观点、辩论、主张、文风、局势做结构化分析，查逻辑谬误与可证伪性。",
    "格式转换与其他": "转 Markdown/CSV、字幕处理等格式工具与杂项。",
}


def esc(s):
    return html.escape(s or "")


def load():
    with open(os.path.join(ROOT, "data", "patterns.json"), encoding="utf-8") as f:
        return json.load(f)


def group_items(data):
    groups = {g: [] for g in GROUP_ORDER}
    for p in data["patterns"]:
        groups.setdefault(p.get("group") or "格式转换与其他", []).append(p)
    for g in groups:
        groups[g].sort(key=lambda x: x["name"])
    return {g: v for g, v in groups.items() if v}


def render_md(data):
    groups = group_items(data)
    lines = [
        "# Fabric 全部提示词中文目录",
        "",
        f"上游：[{data['upstream_repo']}](https://github.com/{data['upstream_repo']})"
        f" · 同步于 {data['synced_at']} · 上游 commit `{data['upstream_commit'][:7]}`"
        f" · 共 {data['count']} 条",
        "",
        "每条的英文名即直达链接，指向源仓库中该 Pattern 的 `system.md` 原文。",
        "",
    ]
    for g, items in groups.items():
        lines += [f"## {g}（{len(items)} 个）", "", GROUP_DESC.get(g, ""), ""]
        lines.append("| Pattern | 中文名 | 简介 | 使用场景 | 标签 | 状态 |")
        lines.append("|---|---|---|---|---|---|")
        for m in items:
            d = (m["zh_desc"] or m.get("desc_en", "")).replace("|", "/")
            s = (m["scenario"] or "").replace("|", "/")
            st = "" if m.get("status") == "translated" else m.get("status", "")
            lines.append(
                f"| [{m['name']}]({m['source_url']}) | {m['zh_title']} | {d} | {s} "
                f"| {'/'.join(m['tags'])} | {st} |"
            )
        lines.append("")
    return "\n".join(lines)


def render_html(data):
    groups = group_items(data)
    nav, sections = [], []
    for g, items in groups.items():
        nav.append(f'<a href="#{esc(g)}">{esc(g)} <span>{len(items)}</span></a>')
        rows = []
        for m in items:
            tags = " · ".join(m["tags"])
            badge = "" if m.get("status") == "translated" else f'<span class="badge">{esc(m.get("status",""))}</span>'
            rows.append(
                f'<div class="row" data-search="{esc((m["name"] + " " + m["zh_title"] + " " + m["zh_desc"] + " " + m["scenario"] + " " + tags).lower())}">'
                f'<div class="rname"><a href="{esc(m["source_url"])}" target="_blank">{esc(m["name"])}</a>'
                f'<div class="rtitle">{esc(m["zh_title"])}{badge}</div></div>'
                f'<div class="rdesc">{esc(m["zh_desc"] or m.get("desc_en",""))}</div>'
                f'<div class="rscene">{esc(m["scenario"])}</div>'
                f'<div class="rtags">{esc(tags)} · <a href="{esc(m["source_url"])}" target="_blank">源仓库原文 ↗</a></div></div>'
            )
        sections.append(
            f'<section id="{esc(g)}"><h2>{esc(g)} <span class="cnt">{len(items)} 个</span></h2>'
            f'<p class="gdesc">{esc(GROUP_DESC.get(g, ""))}</p>{"".join(rows)}</section>'
        )
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fabric 全部提示词中文目录</title>
<style>
:root{{--bg:#0d0d10;--panel:#15151a;--line:#26262e;--txt:#e8e6e1;--dim:#9b978c;--acc:#d8a24a;--acc2:#7aa2f7}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--txt);font-family:"Noto Serif SC",Georgia,serif;line-height:1.65}}
.wrap{{max-width:1080px;margin:0 auto;padding:48px 22px 90px}}
.kicker{{color:var(--acc);letter-spacing:.35em;font-size:12px;font-family:ui-monospace,monospace}}
h1{{font-size:40px;line-height:1.25;margin:14px 0 10px}}
.sub{{color:var(--dim);font-size:16px;max-width:760px}}
.stats{{display:flex;gap:14px;flex-wrap:wrap;margin:28px 0}}
.stat{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 20px;min-width:150px}}
.stat b{{font-size:26px;display:block;color:#fff}}.stat span{{color:var(--dim);font-size:13px}}
nav{{display:flex;gap:8px;flex-wrap:wrap;margin:22px 0}}
nav a{{color:var(--txt);text-decoration:none;border:1px solid var(--line);padding:5px 13px;border-radius:99px;font-size:13.5px;background:var(--panel)}}
nav a span{{color:var(--acc)}}
.search{{position:sticky;top:0;background:var(--bg);padding:14px 0;z-index:5}}
.search input{{width:100%;padding:13px 16px;border-radius:10px;border:1px solid var(--line);background:var(--panel);color:var(--txt);font-size:16px;outline:none}}
h2{{font-size:25px;margin:52px 0 4px}}h2 .cnt{{color:var(--acc);font-size:16px}}
.gdesc{{color:var(--dim);margin:0 0 14px;font-size:14.5px}}
.row{{display:grid;grid-template-columns:210px 1fr 170px;gap:6px 18px;padding:13px 16px;border:1px solid var(--line);border-radius:10px;margin-bottom:8px;background:var(--panel)}}
.rname a{{color:var(--acc2);text-decoration:none;font-family:ui-monospace,Menlo,monospace;font-size:13.5px;word-break:break-all}}
.rtitle{{font-size:15px;color:#fff;margin-top:2px}}
.rdesc{{font-size:14.5px}}.rscene{{font-size:13.5px;color:var(--acc)}}
.rtags{{grid-column:1/-1;color:var(--dim);font-size:11.5px;font-family:ui-monospace,monospace}}
.rtags a{{color:var(--dim)}}
.badge{{background:var(--acc);color:#111;font-size:11px;border-radius:6px;padding:1px 7px;margin-left:8px;font-family:ui-monospace,monospace}}
.hide{{display:none}}footer{{color:var(--dim);font-size:13px;margin-top:60px;border-top:1px solid var(--line);padding-top:18px}}
@media(max-width:760px){{.row{{grid-template-columns:1fr}}h1{{font-size:30px}}}}
</style></head><body><div class="wrap">
<div class="kicker">Fabric Patterns · Chinese Catalog</div>
<h1>Fabric 全部提示词中文目录</h1>
<p class="sub">源仓库 danielmiessler/Fabric 全部 Pattern 的中文索引：逐个依据其 system.md 原文撰写中文简介与使用场景，每条附源仓库原文直达链接。本页每日自动与上游同步。</p>
<div class="stats">
<div class="stat"><b>{data['count']}</b><span>条目总数</span></div>
<div class="stat"><b>{data['synced_at']}</b><span>最近同步日期</span></div>
<div class="stat"><b>{esc(data['upstream_commit'][:7])}</b><span>上游 commit</span></div>
</div>
<div class="search"><input id="q" type="text" placeholder="搜索：英文名、中文名或关键词，如 review、审查、视频、威胁建模…"></div>
<nav>{''.join(nav)}</nav>
{''.join(sections)}
<footer>数据来源：github.com/danielmiessler/Fabric（MIT）。中文简介为依据原文的概括，非逐字翻译；使用前建议点开原文核对输出格式。本目录由脚本从 data/patterns.json 生成。</footer>
</div>
<script>
const q=document.getElementById('q');
q.addEventListener('input',()=>{{const v=q.value.trim().toLowerCase();document.querySelectorAll('.row').forEach(r=>{{r.classList.toggle('hide',v&&!r.dataset.search.includes(v))}});document.querySelectorAll('section').forEach(s=>{{const vis=[...s.querySelectorAll('.row')].some(r=>!r.classList.contains('hide'));s.classList.toggle('hide',!!v&&!vis)}})}});
</script></body></html>"""


def main():
    data = load()
    with open(os.path.join(ROOT, "catalog.md"), "w", encoding="utf-8") as f:
        f.write(render_md(data))
    with open(os.path.join(ROOT, "docs", "index.html"), "w", encoding="utf-8") as f:
        f.write(render_html(data))
    print(f"built catalog.md + docs/index.html from {data['count']} patterns")


if __name__ == "__main__":
    main()
