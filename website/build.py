"""Export the English reading site while preserving unrelated destination files."""
from pathlib import Path
import argparse
import json
import runpy
import shutil

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT.is_relative_to(output):
        raise SystemExit("Choose a separate output directory.")
    runpy.run_path(str(ROOT / "scripts/build_site.py"), run_name="__main__")
    paths = ["index.html", "guide.html", "LICENSE", ".nojekyll", "assets/library.css",
             "assets/library.js", "assets/overview.svg", "assets/overview-mobile.svg",
             "assets/favicon.svg", "data/library.json"]
    for relative in paths:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    # Preserve the existing papers URL and its query parameters.
    shutil.copyfile(ROOT / "index.html", output / "papers.html")
    cfg = json.loads((ROOT / "data/site.json").read_text())
    papers = json.loads((ROOT / "data/library.json").read_text())
    (output / "build-info.json").write_text(json.dumps({
        "language": "en", "references": len(papers), "topics": len(cfg["categories"]),
        "snapshot": cfg["snapshot"], "generator": "scripts/build_site.py"
    }, indent=2) + "\n")
    print(f"Exported English reading pages to {output}")

if __name__ == "__main__":
    main()
