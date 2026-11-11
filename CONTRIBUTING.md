# Contributing

Contributions should help readers find, understand, and compare relevant research.

## Add or correct a reference

1. Edit [data/papers.json](data/papers.json); keep titles, authors, and source links accurate.
2. Select the closest existing topic. Use a short English summary that describes the method and its scope.
3. Include the original paper or project link. Add code and a local original-language PDF when available.
4. Preserve existing IDs. Distinguish publication years from first-preprint dates.
5. Support quantitative claims with the original source and its evaluation conditions.

Each JSON record has `id`, `title`, `authors`, `year`, `venue`, `category`, `tags`, `summary`, `kind`, `core`, and `links`. A link contains `label` and `url`. Use one primary category. Resource kinds distinguish Paper, Survey, Article, Book, Tool, and Benchmark.

## Keep the public entry pages in English

Use English for README text, reading guides, interface labels, catalog summaries, alt text, and new diagrams. Keep archival research materials separate from the entry pages. Do not link readers to a translated document under an English-resource label.

## Rebuild

```bash
python3 scripts/build_site.py
```

The build uses only the Python standard library. It validates IDs, categories, English catalog text, and local source links before producing the README and browser.

- Edit `data/site.json` for the introduction, topic descriptions, and reading guide.
- Edit `assets/library.css` and `assets/library.js` for the browser.
- Edit `scripts/build_site.py` for generated page markup and overview diagrams.

Do not hand-edit generated README, HTML, or `data/library.json` files.

## Review before submitting

- Rebuild twice and confirm that the second build produces no further changes.
- Open `index.html` directly and test search, topic/year filters, sorting, saving, and reset.
- Check both desktop and mobile widths and keyboard navigation.
- Test a query with no matches and unavailable browser storage.
- Confirm that local links resolve and diagrams have readable English labels.
- Use the original collection date unless a new literature search was actually performed.

The browser has no external scripts, fonts, or runtime dependencies. Saved readings stay in the current browser; they are not included in shared links.

## Automated checks

```bash
python3 scripts/check_library.py
node scripts/check_browser.cjs
```

The browser check requires Playwright and Chromium. Set `PLAYWRIGHT_MODULE` to an existing Playwright module and `CHROME_BIN` to an installed Chrome executable if needed. It checks desktop and mobile layouts, filters, persistence, keyboard focus, storage failures, and the no-JavaScript fallback. Screenshots and its report are written to a temporary directory.
