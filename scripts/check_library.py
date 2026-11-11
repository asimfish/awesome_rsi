"""Validate generated English entry pages and their local resources."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ["README.md", "guide.md", "index.html", "guide.html", "data/library.json",
           "assets/overview.svg", "assets/overview-mobile.svg", "assets/favicon.svg"]
CJK = re.compile(r"[\u3400-\u9fff]")

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.refs = []
        self.images = []
        self.lang = None
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.refs.append(attrs[key])
        if "srcset" in attrs:
            self.refs.extend(item.strip().split()[0] for item in attrs["srcset"].split(","))
        if tag == "img":
            self.images.append(attrs)
        if tag == "a" and attrs.get("target") == "_blank":
            assert "noopener" in attrs.get("rel", ""), "External tab missing noopener"

def check_local(base, url):
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc:
        return
    if not parsed.path:
        return
    target = (base / unquote(parsed.path)).resolve()
    assert target.is_relative_to(ROOT), f"Link leaves the repository: {url}"
    assert target.exists(), f"Missing local reference: {url}"

def main():
    papers = json.loads((ROOT / "data/library.json").read_text(encoding="utf-8"))
    assert len(papers) == len({p["id"] for p in papers}), "Duplicate IDs"
    for name in PRIMARY:
        path = ROOT / name
        source = path.read_text(encoding="utf-8")
        assert not CJK.search(source), f"Non-English entry-page text: {name}"
        if path.suffix == ".html":
            page = Page()
            page.feed(source)
            assert page.lang == "en", f"Wrong document language: {name}"
            assert len(page.ids) == len(set(page.ids)), f"Duplicate HTML IDs: {name}"
            for url in page.refs:
                check_local(path.parent, url)
                if url.startswith("#"):
                    assert url[1:] in page.ids, f"Missing HTML anchor: {name} {url}"
            for img in page.images:
                assert img.get("alt"), f"Missing image description: {name}"
        elif path.suffix == ".md":
            for url in re.findall(r"\]\(([^)]+)\)", source):
                check_local(path.parent, url)
            anchors=set(re.findall(r'<a id="([^"]+)"',source))
            anchors.update(re.sub(r"[^\w\s-]","",line.lstrip("# ").lower()).replace(" ","-")
                           for line in source.splitlines() if line.startswith("#"))
            for fragment in re.findall(r"\]\(#([^)]*)\)",source):
                assert fragment in anchors, f"Missing Markdown anchor: {fragment}"
        elif path.suffix == ".svg":
            ET.fromstring(source)
    for path in (ROOT / "assets/figures/en").glob("*.svg"):
        source = path.read_text(encoding="utf-8")
        assert not CJK.search(source), f"Non-English figure: {path.name}"
        ET.fromstring(source)
    for p in papers:
        for link in p["links"]:
            check_local(ROOT, link["url"])
    print(f"PASS: {len(papers)} references; English text, IDs, local links, anchors, image descriptions, and SVG syntax.")

if __name__ == "__main__":
    main()
