(() => {
  const toggle = document.querySelector('#theme');
  const font = document.querySelector('#font-size');
  let dark = false, large = false;
  try {
    dark = localStorage.getItem('rsi-theme') === 'dark';
    large = localStorage.getItem('rsi-large') === 'true';
  } catch (_) {}
  function preferences() {
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    document.documentElement.dataset.large = String(large);
    toggle.textContent = dark ? '浅色' : '深色';
    toggle.setAttribute('aria-label', dark ? '切换浅色模式' : '切换深色模式');
    font.textContent = large ? 'A－' : 'A＋';
    font.setAttribute('aria-pressed', String(large));
    font.setAttribute('aria-label', large ? '恢复正文字号' : '放大正文字号');
    try { localStorage.setItem('rsi-theme', dark ? 'dark' : 'light'); localStorage.setItem('rsi-large', String(large)); } catch (_) {}
  }
  const mobile = matchMedia('(max-width:760px)');
  const panel = document.querySelector('.toc-panel');
  function layoutTOC() { if (panel) panel.open = !mobile.matches; }
  layoutTOC(); mobile.addEventListener('change', layoutTOC);
  preferences();
  toggle.addEventListener('click', () => { dark = !dark; preferences(); });
  font.addEventListener('click', () => { large = !large; preferences(); });
  const input = document.querySelector('#search');
  const category = document.querySelector('#category');
  const groups = [...document.querySelectorAll('.paper-group')];
  const items = [...document.querySelectorAll(groups.length ? '.paper-entry' : '.search-card')];
  const normalize = text => text.normalize('NFKC').toLocaleLowerCase();
  function filter() {
    const query = normalize((input?.value || '').trim());
    let count = 0;
    items.forEach(item => {
      const group = item.closest('.paper-group');
      const match = normalize(item.dataset.search || item.textContent).includes(query) &&
        (!category?.value || group?.dataset.category === category.value);
      item.hidden = !match;
      if (match) count++;
    });
    groups.forEach(group => { group.hidden = ![...group.querySelectorAll('.paper-entry')].some(item => !item.hidden); });
    const result = document.querySelector('#result-count');
    if (result) result.textContent = `显示 ${count} / ${items.length} ${groups.length ? '条文献与项目' : '篇解读'}`;
    const empty = document.querySelector('#empty');
    if (empty) empty.hidden = count !== 0;
  }
  input?.addEventListener('input', filter);
  category?.addEventListener('change', filter);
  filter();
  const toc = [...document.querySelectorAll('aside a[href^="#"]')];
  toc.forEach(link => link.addEventListener('click', () => {
    if (groups.length) {
      const id = decodeURIComponent(link.hash.slice(1));
      if (category && [...category.options].some(option => option.value === id)) {
        category.value = id; input.value = ''; filter();
      }
    }
    if (matchMedia('(max-width:760px)').matches) link.closest('details')?.removeAttribute('open');
  }));
  let scheduled = false;
  function progress() {
    scheduled = false;
    const height = document.documentElement.scrollHeight - innerHeight;
    document.querySelector('#progress').style.width = `${height > 0 ? Math.min(100, scrollY / height * 100) : 100}%`;
    const current = [...document.querySelectorAll('main h2[id],main h3[id]')].filter(h => h.getBoundingClientRect().top < 170).pop();
    toc.forEach(a => {
      const active = current && decodeURIComponent(a.hash.slice(1)) === current.id;
      a.classList.toggle('active', Boolean(active));
      if (active) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current');
    });
  }
  addEventListener('scroll', () => { if (!scheduled) { scheduled = true; requestAnimationFrame(progress); } }, { passive: true });
  addEventListener('resize', progress);
  progress();
})();
