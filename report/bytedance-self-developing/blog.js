(() => {
  const button = document.querySelector('#theme');
  let dark = false;
  try { dark = localStorage.getItem('rsi-theme') === 'dark'; } catch (_) {}
  function applyTheme() {
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    button.textContent = dark ? '浅色阅读' : '深色阅读';
    button.setAttribute('aria-label', dark ? '切换浅色模式' : '切换深色模式');
  }
  applyTheme();
  button.addEventListener('click', () => {
    dark = !dark; applyTheme();
    try { localStorage.setItem('rsi-theme', dark ? 'dark' : 'light'); } catch (_) {}
  });
  const headings = [...document.querySelectorAll('.article-body h2[id]')];
  const links = [...document.querySelectorAll('aside nav a')];
  const progress = document.querySelector('.progress');
  function update() {
    const height = document.documentElement.scrollHeight - innerHeight;
    progress.style.width = `${height > 0 ? Math.min(100, scrollY / height * 100) : 100}%`;
    const current = headings.filter(h => h.getBoundingClientRect().top <= 150).pop();
    links.forEach(a => {
      const active = current && a.hash === '#' + current.id;
      a.classList.toggle('active', Boolean(active));
      if (active) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current');
    });
  }
  addEventListener('scroll', update, {passive:true});
  addEventListener('resize', update); update();
})();
