"""Build the English README, reading guide, and offline paper browser.

Uses the Python standard library. Edit data/site.json and the paper catalog,
then run this script; generated files remain identical on repeated builds.
"""
from pathlib import Path
from collections import Counter
import csv
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
LOOP_MAP = {
    "Foundations & Precursors": "Foundations & theory",
    "Theory: Expressivity, ICL & Length Generalization": "Foundations & theory",
    "Scaled Pretraining": "Architectures & pretraining",
    "Tiny Recursive Reasoners": "Architectures & pretraining",
    "Stability & Training Theory": "Training & adaptation",
    "Retrofitting & Training-Free": "Training & adaptation",
    "Post-Training & RL for Looped Models": "Training & adaptation",
    "Efficiency: Latency, KV Cache & Quantization": "Inference & efficiency",
    "Adaptive Computation & Halting": "Inference & efficiency",
    "Interpretability & Latent Dynamics": "Analysis & applications",
    "Applications & Cross-Modal": "Analysis & applications",
    "Surveys": "Surveys & related reasoning",
    "Related: Latent Reasoning Beyond Looping": "Surveys & related reasoning",
}
CORE_NOTES = {
    "1807.03819": ("01_universal_transformers", "A shared transformer block with optional adaptive computation time."),
    "2502.05171": ("02_recurrent_depth_huginn", "Recurrent-depth pretraining with a variable amount of latent computation at inference."),
    "2605.23872": ("03_training_free_looped", "A training-free route to repeated computation in a pretrained transformer."),
    "2606.18023": ("04_loopcoder_v2", "Parallel looping for coding models, with explicit compute and latency trade-offs."),
    "2607.16051": ("05_loop_the_loopies", "Studies loop granularity and mixture-of-experts models under matched training budgets."),
}

def esc(value):
    return html.escape(str(value), quote=True)

def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def load_papers():
    if CONFIG["repo"] == "awesome_rsi":
        papers = json.loads((ROOT / "data/papers.json").read_text(encoding="utf-8"))
        for p in papers:
            p["categories"] = [p["category"]]
        return papers
    with (ROOT / "data/papers.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    papers = []
    for r in rows:
        tags = [c.strip() for c in r["category"].split(";") if c.strip() != "Core Papers"]
        categories = list(dict.fromkeys(LOOP_MAP[c] for c in tags))
        links = [{"label": "Paper", "url": r["link"]}]
        if r.get("code"):
            links.append({"label": "Model" if "huggingface.co/" in r["code"] else "Code", "url": r["code"]})
        summary = r.get("note", "") if r.get("note") != "core" else ""
        if r["arxiv"] in CORE_NOTES:
            note, summary = CORE_NOTES[r["arxiv"]]
            links.extend([
                {"label": "Notes", "url": "reports/en/" + note + ".md"},
                {"label": "PDF", "url": "papers/original/" + r["arxiv"] + ".pdf"},
            ])
        papers.append({
            "id": "loop-" + r["arxiv"], "title": r["title"].rstrip("."),
            "year": int(r["year"]), "venue": r["publisher"],
            "authors": r["authors"], "links": links, "core": r.get("note") == "core",
            "category": categories[0], "categories": categories, "tags": tags,
            "summary": summary, "kind": "Survey" if "Surveys" in tags else "Paper",
        })
    return papers

def validate(papers):
    if len({p["id"] for p in papers}) != len(papers):
        raise ValueError("Duplicate paper IDs")
    known = {name for name, _ in CONFIG["categories"]}
    for p in papers:
        if not p["categories"] or not set(p["categories"]) <= known:
            raise ValueError("Unknown or missing category: " + p["title"])
        if re.search(r"[\u3400-\u9fff]", json.dumps(p, ensure_ascii=False)):
            raise ValueError("Non-English catalog text: " + p["title"])
        if not p["links"]:
            raise ValueError("Missing source: " + p["title"])
        for link in p["links"]:
            url = link["url"]
            if re.match(r"https?://", url):
                continue
            if url.startswith(("/", "\\")) or ".." in Path(url).parts:
                raise ValueError("Unsafe local link: " + url)
            if not (ROOT / url).exists():
                raise ValueError("Missing local file: " + url)

def site_url(url):
    if not url.startswith(("https://", "http://")) and url.endswith(".md"):
        return "https://github.com/asimfish/" + CONFIG["repo"] + "/blob/main/" + url
    if CONFIG["repo"] == "awesome_rsi" and url.endswith(".pdf") and not url.startswith(("https://", "http://")):
        return "https://raw.githubusercontent.com/asimfish/awesome_rsi/main/" + url
    return url

def html_links(links):
    return "".join('<a href="' + esc(site_url(l["url"])) + '">' + esc(l["label"]) + '<span aria-hidden="true"> ↗</span></a>' for l in links)

def md_links(links):
    return " · ".join("[" + l["label"] + "](" + l["url"] + ")" for l in links)

def article(p):
    return f'''<article class="paper" id="{esc(p["id"])}" data-id="{esc(p["id"])}">
  <div class="paper-top"><span class="paper-meta">{esc(p["year"])} / {esc(p["venue"])} / {esc(p["kind"])}</span>
  {"<span class='core-label'>Core reading</span>" if p["core"] else ""}</div>
  <h3><a href="{esc(site_url(p["links"][0]["url"]))}">{esc(p["title"])}</a></h3>
  <p class="authors">{esc(p["authors"])}</p>
  {"<p class='summary'>" + esc(p["summary"]) + "</p>" if p["summary"] else ""}
  <div class="paper-bottom"><div class="paper-links">{html_links(p["links"])}</div>
  <button class="save js-only" type="button" data-save="{esc(p["id"])}" aria-pressed="false" aria-label="Save: {esc(p["title"])}">Save</button></div>
  <p class="tags">{esc(" · ".join(p["tags"]))}</p>
</article>'''

def document(title, body, scripts=""):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{esc(CONFIG["short"])}">
<meta name="color-scheme" content="light">
<title>{esc(title)}</title>
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/library.css">
</head>
<body style="--accent: {CONFIG["accent"]}">
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="header-inner">
<a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">↻</span>{esc(CONFIG["brand"])}</a>
<nav aria-label="Main navigation"><a href="index.html#library">Library</a><a href="guide.html">Reading guide</a><a href="https://github.com/asimfish/{CONFIG["repo"]}">GitHub <span aria-hidden="true">↗</span></a></nav>
</div></header>
{body}
<footer class="site-footer"><span>{esc(CONFIG["title"])}<br><small>Collection snapshot: {esc(CONFIG["snapshot"])} · <a href="LICENSE">CC BY 4.0</a></small></span><a href="#main">Back to top ↑</a></footer>
{scripts}
</body>
</html>
'''

def overview():
    is_loop = CONFIG["repo"] == "awesome_loop_transformer"
    labels = ["Input", "Shared block", "Output"] if is_loop else ["Propose", "Evaluate", "Retain"]
    subtitles = ["Embed tokens", "Update the hidden state", "Read out a prediction"] if is_loop else ["Change an artifact", "Check the candidate", "Keep a useful revision"]
    top = "RECURRENT DEPTH" if is_loop else "THE IMPROVEMENT CYCLE"
    feedback = "Repeat with the same parameters" if is_loop else "Use feedback to propose the next revision"
    bottom = "Loop count controls computation; shared weights control parameter reuse." if is_loop else "Compare the change target, feedback source, and acceptance rule."
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="300" viewBox="0 0 1100 300" role="img" aria-labelledby="title desc">
<title id="title">{esc(top)}</title><desc id="desc">{esc(feedback + ". " + bottom)}</desc>
<rect width="1100" height="300" rx="16" fill="#132d35"/>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#91c9c0"/></marker></defs>
<g font-family="Verdana, sans-serif"><text x="38" y="38" fill="#9bb8bf" font-size="12" letter-spacing="3">{esc(top)}</text>''']
    for i, (label, subtitle) in enumerate(zip(labels, subtitles)):
        x = 80 + i * 340
        parts.append(f'<rect x="{x}" y="92" width="260" height="104" rx="8" fill="{"#28544f" if i == 1 else "#1e3b44"}" stroke="{"#91c9c0" if i == 1 else "#47646b"}"/>')
        parts.append(f'<text x="{x+22}" y="128" fill="#f6f5ed" font-size="24">{esc(label)}</text><text x="{x+22}" y="159" fill="#c7d8da" font-size="14">{esc(subtitle)}</text>')
        if i < 2:
            parts.append(f'<path d="M{x+268} 144H{x+327}" stroke="#91c9c0" stroke-width="2" marker-end="url(#arrow)"/>')
    if is_loop:
        parts.append('<path d="M650 92V65H450V86" fill="none" stroke="#91c9c0" stroke-width="2" marker-end="url(#arrow)"/>')
        parts.append(f'<text x="550" y="52" text-anchor="middle" fill="#c7d8da" font-size="13">{esc(feedback)}</text>')
    else:
        parts.append('<path d="M890 201V230H210V203" fill="none" stroke="#91c9c0" stroke-width="2" marker-end="url(#arrow)"/>')
        parts.append(f'<rect x="354" y="217" width="392" height="26" fill="#132d35"/><text x="550" y="235" text-anchor="middle" fill="#c7d8da" font-size="13">{esc(feedback)}</text>')
    parts.append(f'<text x="550" y="276" text-anchor="middle" fill="#9bb8bf" font-size="14">{esc(bottom)}</text></g></svg>\n')
    return "".join(parts)


def mobile_overview():
    is_loop = CONFIG["repo"] == "awesome_loop_transformer"
    labels = ["Input", "Shared block", "Output"] if is_loop else ["Propose", "Evaluate", "Retain"]
    subs = ["Embed tokens", "Update the hidden state", "Read out a prediction"] if is_loop else ["Change an artifact", "Check the candidate", "Keep a useful revision"]
    heading = "RECURRENT DEPTH" if is_loop else "THE IMPROVEMENT CYCLE"
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="430" viewBox="0 0 480 430" role="img" aria-labelledby="t"><title id="t">{heading}</title><rect width="480" height="430" rx="12" fill="#132d35"/><defs><marker id="a" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0L7 3.5L0 7Z" fill="#91c9c0"/></marker></defs><g font-family="Verdana,sans-serif"><text x="32" y="34" fill="#9bb8bf" font-size="13" letter-spacing="2">{heading}</text>']
    for i,(label,sub) in enumerate(zip(labels,subs)):
        y=59+i*112
        out.append(f'<rect x="40" y="{y}" width="350" height="84" rx="7" fill="{"#28544f" if i==1 else "#1e3b44"}" stroke="#5d8588"/><text x="62" y="{y+33}" fill="#f6f5ed" font-size="24">{label}</text><text x="62" y="{y+59}" fill="#c7d8da" font-size="15">{sub}</text>')
        if i<2:
            out.append(f'<path d="M215 {y+90}V{y+105}" fill="none" stroke="#91c9c0" stroke-width="2" marker-end="url(#a)"/>')
    if is_loop:
        out.append('<path d="M395 238H430V182H397" stroke="#91c9c0" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    else:
        out.append('<path d="M395 325H435V100H397" stroke="#91c9c0" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    caption = "Repeat with the same parameters." if is_loop else "Use feedback for the next revision."
    out.append(f'<text x="40" y="400" font-size="15" fill="#c7d8da">{caption}</text></g></svg>\n')
    return "".join(out)

def build_readme(papers):
    c = CONFIG
    counts = Counter(cat for p in papers for cat in p["categories"])
    core = [p for p in papers if p["core"]]
    chunks = [f'''# {c["title"]}

{c["short"]}

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re) [![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-596d75)](LICENSE) ![Entries](https://img.shields.io/badge/entries-{len(papers)}-17675d)

[Browse online](https://asimfish.github.io/{c["repo"]}/) · [Start reading](#start-reading) · [Browse by topic](#topics) · [Core readings](#core-readings) · [Contribute](CONTRIBUTING.md)

![{"A shared transformer block repeatedly updates a hidden state." if c["repo"] == "awesome_loop_transformer" else "A self-improvement cycle: propose a change, evaluate it, and retain a useful revision."}](assets/overview.svg)

## Start reading

{c["description"]}

| Your goal | Start here |
| --- | --- |
| Understand the field | [English reading guide](guide.md) |
| Follow a short route | [Core readings](#core-readings) |
| Find a specific method | [Topic index](#topics) or the searchable [paper browser](https://asimfish.github.io/{c["repo"]}/#library) |
| Reuse the collection | [Machine-readable catalog]({"data/papers.csv" if c["repo"] == "awesome_loop_transformer" else "data/papers.json"}) |

Open <code>index.html</code> in a browser for search, topic and year filters, sorting, saved readings, and links to papers and code. It works offline; external resources still need a connection. Filter links can be shared when the page is served over HTTP.

## Topics

Choose a subject first; use the core reading route for an introduction.

| Topic | Entries | Scope |
| --- | ---: | --- |
''']
    for name, desc in c["categories"]:
        chunks.append(f"| [{name}](#{slug(name)}) | {counts[name]} | {desc} |\n")
    if c["repo"] == "awesome_loop_transformer":
        chunks.append("\nPapers may appear in more than one topic; the catalog contains **" + str(len(papers)) + " unique entries**. Original fine-grained categories remain searchable in the browser.\n")
    else:
        chunks.append("\nEach reference has one primary topic. Resource labels distinguish papers, surveys, articles, books, and tools.\n")
    chunks.append("\n## Core readings\n\n")
    for i,p in enumerate(core,1):
        chunks.append(f'{i}. **{p["title"]}.** {md_links(p["links"])}\n\n   {p["summary"]}\n\n')
    chunks.append("## Catalog\n\nExpand a topic to see its references. Listed years follow the source catalog and may reflect a publication venue rather than the first preprint date.\n\n")
    for name,desc in c["categories"]:
        chunks.append(f'<a id="{slug(name)}"></a>\n\n### {name}\n\n{desc}\n\n<details>\n<summary>View {counts[name]} entries</summary>\n\n')
        group=sorted((p for p in papers if name in p["categories"]), key=lambda p:(-p["year"],p["title"].lower()))
        for p in group:
            chunks.append(f'- **{p["title"]}.** {p["venue"]}, {p["year"]}. {md_links(p["links"])}\n')
            if p["summary"]:
                chunks.append(f'\n  {p["summary"]}\n')
            chunks.append("\n")
        chunks.append("</details>\n\n[Back to topics](#topics)\n\n")
    chunks.append(f'''## Maintain the collection

Collection snapshot: **{c["snapshot"]}**. This presentation update does not claim a new literature search.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the catalog fields and validation steps.

~~~bash
python3 {"src/generator.py" if c["repo"] == "awesome_loop_transformer" else "scripts/build_site.py"}
~~~

This rebuilds the README, reading guide, diagrams, and offline browser from the catalog. It requires only the Python standard library.

## Citation

~~~bibtex
@misc{{{c["repo"]}_2026,
  title = {{{c["title"]}}},
  author = {{{{Repository contributors}}}},
  year = {{2026}},
  url = {{https://github.com/asimfish/{c["repo"]}}}
}}
~~~

## License

Repository text is available under [CC BY 4.0](LICENSE). Original papers and third-party software retain their respective licenses.
''')
    return "".join(chunks)

def build_guide():
    c=CONFIG
    md=[f'# Reading guide: {c["brand"]}\n\n[Back to the collection](README.md)\n\n']
    body=['<main id="main" class="guide"><p class="eyebrow">A practical reading route</p><h1>Start with the questions.</h1><p class="lead">'+esc(c["short"])+'</p><ol class="guide-sections">']
    for item in c["guide"]:
        links=[{"label":label,"url":url} for label,url in item["links"]]
        md.append(f'## {item["title"]}\n\n{item["text"]}\n\n{md_links(links)}\n\n')
        body.append(f'<li id="{slug(item["title"])}"><h2>{esc(item["title"])}</h2><p>{esc(item["text"])}</p><div class="paper-links">{html_links(links)}</div></li>')
    body.append('</ol><a class="primary-link" href="index.html#library">Explore the collection →</a></main>')
    return "".join(md),document("Reading guide · "+c["brand"],"".join(body))

def main():
    papers=load_papers()
    validate(papers)
    c=CONFIG
    categories=c["categories"]
    counts=Counter(cat for p in papers for cat in p["categories"])
    count=len(papers)
    core_count=sum(p["core"] for p in papers)
    years=sorted({p["year"] for p in papers},reverse=True)
    kinds=sorted({p["kind"] for p in papers})
    sidebar='<button type="button" class="category active" data-category="" aria-pressed="true"><span>All topics</span><span>'+str(count)+'</span></button>'
    sidebar+="".join(f'<button type="button" class="category" data-category="{esc(name)}" aria-pressed="false"><span>{esc(name)}</span><span>{counts[name]}</span></button>' for name,_ in categories)
    body=f'''<main id="main">
<section class="hero" aria-labelledby="hero-title">
  <div class="hero-copy"><p class="eyebrow">{esc(c["eyebrow"])}</p><h1 id="hero-title">{esc(c["headline"]).replace(chr(10), "<br>")}</h1><p class="lead">{esc(c["description"])}</p><div class="hero-actions"><a class="primary-link" href="#library">Explore the library ↓</a><a href="guide.html">Follow the reading guide →</a></div></div>
  <div class="collection-stats" aria-label="Collection overview"><div><strong>{count}</strong><span>curated references</span></div><div><strong>{len(categories):02d}</strong><span>research areas</span></div><p>Collection snapshot<br><time datetime="{esc(c["snapshot"])}">{esc(c["snapshot"])}</time></p></div>
</section>
<figure class="overview"><picture><source media="(max-width: 540px)" srcset="assets/overview-mobile.svg"><img src="assets/overview.svg" width="1100" height="300" alt="{"Input tokens pass through a shared block that repeatedly updates the hidden state, then produce an output." if c["repo"]=="awesome_loop_transformer" else "Propose a change, evaluate the candidate, retain a useful revision, and use feedback for the next cycle."}"></picture></figure>
<section class="library" id="library" aria-labelledby="library-title">
<aside class="topic-panel js-only"><p class="eyebrow">Browse by topic</p><div class="categories" role="group" aria-label="Research topics">{sidebar}</div><p class="sidebar-note">One collection, several ways in.<br><a href="guide.html">Find your reading route →</a></p></aside>
<div class="library-main">
<div class="section-heading"><div><p class="eyebrow">The collection</p><h2 id="library-title">Research library</h2></div><button id="share" class="text-button js-only" type="button">Copy filter link ↗</button></div>
<div class="controls js-only">
<label class="search-label" for="search">Search the collection</label><div class="search-wrap"><span aria-hidden="true">⌕</span><input id="search" type="search" placeholder="Search titles, authors, topics…" autocomplete="off" aria-keyshortcuts="/"><kbd aria-hidden="true">/</kbd></div>
<div class="filter-row"><label>Year<select id="year"><option value="">All years</option>{"".join(f'<option>{y}</option>' for y in years)}</select></label><label>Resource<select id="kind"><option value="">All resources</option>{"".join(f'<option>{esc(k)}</option>' for k in kinds)}</select></label><label>Sort<select id="sort"><option value="recommended">Reading order</option><option value="newest">Newest first</option><option value="oldest">Oldest first</option><option value="title">Title A–Z</option></select></label></div>
<div class="toggle-row"><label><input type="checkbox" id="core"> Core readings <span>{core_count}</span></label><label><input type="checkbox" id="code"> With code</label><label><input type="checkbox" id="saved"> Saved <span id="saved-count">0</span></label><button id="reset" type="button" class="text-button">Reset filters</button></div>
</div>
<div class="results-bar"><p id="result-count" role="status" aria-live="polite">{count} references</p><p id="active-topic">All topics</p></div>
<noscript><p>All references are listed below. Enable JavaScript for search, filters, and saved readings.</p></noscript>
<div id="papers">{"".join(article(p) for p in papers)}</div>
<div id="empty" class="empty" hidden><h3>No matching references</h3><p>Try a broader search or clear the filters. Save a reference to add it to your reading list.</p><button type="button" id="empty-reset" class="primary-link">Clear all filters</button></div>
<button type="button" id="more" class="load-more js-only" hidden>Show more references</button>
<p class="catalog-note">Listed years follow the source catalog; publication and first-preprint dates may differ.</p>
</div>
</section>
</main>
<div id="notice" class="notice" role="status" aria-live="polite" hidden></div>
<dialog id="share-dialog"><form method="dialog"><h2>Share this view</h2><p>Copy this link to keep your search and filters.</p><label for="share-url">Filter link</label><input id="share-url" readonly><button type="submit" class="primary-link">Done</button></form></dialog>'''
    payload=json.dumps({"repo":c["repo"],"papers":papers},ensure_ascii=False).replace("<","\\u003c")
    scripts='<script type="application/json" id="catalog">'+payload+'</script><script src="assets/library.js" defer></script>'
    guide_md,guide_html=build_guide()
    outputs={
        "README.md":build_readme(papers), "index.html":document(c["title"],body,scripts),
        "guide.md":guide_md, "guide.html":guide_html, "assets/overview.svg":overview(),
        "assets/overview-mobile.svg":mobile_overview(),
        "assets/favicon.svg":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect width="40" height="40" rx="9" fill="'+c["accent"]+'"/><path d="M29 15A11 11 0 1 0 30 24M29 7V16H20" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round"/></svg>\n',
        "data/library.json":json.dumps(papers,ensure_ascii=False,indent=2)+"\n",
        ".nojekyll":"",
    }
    for path,content in outputs.items():
        content = ("\n".join(line.rstrip() for line in content.splitlines()).rstrip() + "\n") if content else ""
        if re.search(r"[\u3400-\u9fff]",content):
            raise ValueError("Non-English output: "+path)
        dest=ROOT/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(content,encoding="utf-8")
    print(f"Built {c['repo']}: {count} references, {len(categories)} topics, English README and browser.")

if __name__ == "__main__":
    main()
