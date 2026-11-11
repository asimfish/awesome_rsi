/* Offline catalog controls. No network calls or third-party dependencies. */
(() => {
  "use strict";
  const data = JSON.parse(document.getElementById("catalog").textContent);
  const papers = data.papers;
  const byId = new Map(papers.map(p => [p.id, p]));
  const nodes = new Map([...document.querySelectorAll(".paper")].map(n => [n.dataset.id, n]));
  const $ = id => document.getElementById(id);
  const fields = ["search", "year", "kind", "sort", "core", "code", "saved"];
  const storageKey = data.repo + ":saved:v1";
  let saved = new Set();
  let storageOK = true;
  try {
    const value = JSON.parse(localStorage.getItem(storageKey) || "[]");
    if (Array.isArray(value)) saved = new Set(value.filter(id => byId.has(id)));
  } catch { storageOK = false; }
  let category = "";
  let limit = 20;
  let current = [];
  let noticeTimer;
  let searchTimer;
  const searchable = new Map(papers.map(p => [p.id, normalize([p.title, p.authors, p.summary, p.venue, p.year, p.kind, p.id, ...p.tags, ...p.categories].join(" "))]));
  function normalize(value) {
    return String(value).normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  }
  function notify(message) {
    $("notice").textContent = message;
    $("notice").hidden = false;
    clearTimeout(noticeTimer);
    noticeTimer = setTimeout(() => { $("notice").hidden = true; }, 4500);
  }
  function restore() {
    const params = new URLSearchParams(location.search);
    $("search").value = params.get("q") || "";
    $("year").value = params.get("year") || "";
    $("kind").value = params.get("kind") || "";
    $("sort").value = params.get("sort") || "recommended";
    if (!$("sort").value) $("sort").value = "recommended";
    for (const name of ["core", "code", "saved"]) $(name).checked = params.get(name) === "1";
    const candidate = params.get("category") || "";
    category = [...document.querySelectorAll("[data-category]")].some(n => n.dataset.category === candidate) ? candidate : "";
    limit = 20;
    apply(false);
  }
  function syncURL() {
    const params = new URLSearchParams();
    if ($("search").value.trim()) params.set("q", $("search").value.trim());
    if (category) params.set("category", category);
    if ($("year").value) params.set("year", $("year").value);
    if ($("kind").value) params.set("kind", $("kind").value);
    if ($("sort").value !== "recommended") params.set("sort", $("sort").value);
    for (const name of ["core", "code", "saved"]) if ($(name).checked) params.set(name, "1");
    const next = new URL(location.href);
    next.search = params.toString();
    try { history.replaceState(null, "", next); } catch { /* File previews may restrict history. */ }
  }
  function apply(updateURL = true) {
    clearTimeout(searchTimer);
    const terms = normalize($("search").value.trim()).split(/\s+/).filter(Boolean);
    current = papers.filter(p =>
      (!category || p.categories.includes(category)) &&
      (!$("year").value || p.year === Number($("year").value)) &&
      (!$("kind").value || p.kind === $("kind").value) &&
      (!$("core").checked || p.core) &&
      (!$("code").checked || p.links.some(l => l.label === "Code")) &&
      (!$("saved").checked || saved.has(p.id)) &&
      terms.every(term => searchable.get(p.id).includes(term))
    );
    const mode = $("sort").value;
    if (mode === "title") current.sort((a, b) => a.title.localeCompare(b.title, "en"));
    else if (mode === "oldest") current.sort((a, b) => a.year - b.year || a.title.localeCompare(b.title, "en"));
    else if (mode === "newest") current.sort((a, b) => b.year - a.year || a.title.localeCompare(b.title, "en"));
    else current.sort((a, b) => Number(b.core) - Number(a.core) || (a.core && b.core ? papers.indexOf(a) - papers.indexOf(b) : b.year - a.year || a.title.localeCompare(b.title, "en")));
    render();
    if (updateURL) syncURL();
  }
  function render() {
    nodes.forEach(n => { n.hidden = true; });
    const visible = current.slice(0, limit);
    for (const p of visible) {
      const node = nodes.get(p.id);
      node.hidden = false;
      $("papers").appendChild(node);
    }
    $("result-count").textContent = current.length ? "Showing " + visible.length + " of " + current.length + " reference" + (current.length === 1 ? "" : "s") : "0 references";
    $("active-topic").textContent = category || "All topics";
    $("empty").hidden = current.length > 0;
    $("more").hidden = current.length <= limit;
    $("more").textContent = "Show " + Math.min(20, current.length - limit) + " more references";
    for (const button of document.querySelectorAll("[data-category]")) {
      const active = button.dataset.category === category;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    }
    $("saved-count").textContent = saved.size;
    for (const button of document.querySelectorAll("[data-save]")) {
      const active = saved.has(button.dataset.save);
      button.textContent = active ? "Saved" : "Save";
      button.setAttribute("aria-pressed", String(active));
      button.setAttribute("aria-label", (active ? "Unsave: " : "Save: ") + byId.get(button.dataset.save).title);
    }
  }
  function reset() {
    category = "";
    $("search").value = "";
    $("year").value = "";
    $("kind").value = "";
    $("sort").value = "recommended";
    for (const name of ["core", "code", "saved"]) $(name).checked = false;
    limit = 20;
    apply();
  }
  document.querySelectorAll("[data-category]").forEach(button => {
    button.addEventListener("click", () => {
      category = button.dataset.category;
      limit = 20;
      apply();
    });
  });
  for (const field of fields) {
    $(field).addEventListener(field === "search" ? "input" : "change", () => {
      limit = 20;
      clearTimeout(searchTimer);
      if (field === "search") searchTimer = setTimeout(apply, 120);
      else apply();
    });
  }
  $("reset").addEventListener("click", reset);
  $("empty-reset").addEventListener("click", () => { reset(); $("search").focus(); });
  $("more").addEventListener("click", () => {
    const firstNew = current[limit];
    limit += 20;
    render();
    if (firstNew) nodes.get(firstNew.id).querySelector("h3 a").focus({ preventScroll: true });
  });
  $("papers").addEventListener("click", event => {
    const button = event.target.closest("[data-save]");
    if (!button) return;
    const id = button.dataset.save;
    const wasSaved = saved.has(id);
    if (wasSaved) saved.delete(id); else saved.add(id);
    try { localStorage.setItem(storageKey, JSON.stringify([...saved])); storageOK = true; }
    catch { storageOK = false; }
    apply();
    if ($("saved").checked && wasSaved) {
      const next = $("papers").querySelector(".paper:not([hidden]) [data-save]");
      (next || $("saved")).focus({ preventScroll: true });
    } else {
      nodes.get(id).querySelector("[data-save]").focus({ preventScroll: true });
    }
    notify(storageOK ? (wasSaved ? "Removed from your reading list." : "Saved to this browser.") : (wasSaved ? "Removed for this session." : "Saved for this session.") + " Browser storage is unavailable.");
  });
  $("share").addEventListener("click", async () => {
    apply();
    if (location.protocol === "file:") {
      notify("To share filters with someone else, serve this folder over HTTP or GitHub Pages.");
      return;
    }
    const url = new URL(location.href);
    url.hash = "library";
    if ($("saved").checked) {
      url.searchParams.delete("saved");
      notify("Saved readings stay in your browser. The shared link includes the other filters.");
    }
    try {
      await navigator.clipboard.writeText(url.href);
      if (!$("saved").checked) notify("Filter link copied.");
    } catch {
      $("share-url").value = url.href;
      $("share-dialog").showModal();
      $("share-url").select();
    }
  });
  document.addEventListener("keydown", event => {
    const target = event.target;
    const editing = target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName);
    if (event.key === "/" && !editing && !event.ctrlKey && !event.metaKey && !event.altKey && !$("share-dialog").open) {
      event.preventDefault();
      $("search").focus();
      $("search").scrollIntoView({ block: "center" });
    }
    if (event.key === "Escape" && target === $("search")) {
      $("search").value = "";
      limit = 20;
      apply();
    }
  });
  window.addEventListener("popstate", restore);
  window.addEventListener("storage", event => {
    if (event.key !== storageKey) return;
    try {
      const value = JSON.parse(event.newValue || "[]");
      saved = new Set(Array.isArray(value) ? value.filter(id => byId.has(id)) : []);
      apply(false);
    } catch { /* Ignore malformed changes from another tab. */ }
  });
  document.body.classList.add("enhanced");
  restore();
})();
