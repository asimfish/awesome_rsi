# Reading site

The English library and reading guide are generated from `data/papers.json` and `data/site.json`. The catalog includes 105 references from the November 6 collection and two introductory articles.

```bash
python3 scripts/build_site.py
python3 scripts/check_library.py
python3 website/build.py /path/to/pages-worktree
```

The exporter updates the homepage, guide, paper browser, styles, scripts, diagrams, and catalog. Existing topic routes and archival reading materials in the destination are preserved. Local PDF links use the original files on the repository main branch so the Pages branch does not need duplicate copies.

`papers.html` remains an alias for the searchable library. Publish the exported files to `gh-pages` with an ordinary fast-forward commit. Check both desktop and mobile layouts before publication.

The older `overview.md`, `site.css`, and `site.js` files are retained as archival sources; the current entry pages use `assets/library.css` and `assets/library.js`.
