(() => {
  const buttons = [...document.querySelectorAll('[data-teaser]')];
  const image = document.getElementById('teaser-image');
  if (!image || !buttons.length) return;
  function select(button) {
    const id = button.dataset.teaser;
    if (!/^C0[1-4]$/.test(id)) return;
    const path = `assets/teaser/${id}.png`;
    const title = button.querySelector('span').textContent;
    image.src = path;
    image.alt = `${title}：研究者引导的 RTL 优化闭环与 C03 分层仲裁示意`;
    document.getElementById('teaser-original').href = path;
    const download = document.getElementById('teaser-download');
    download.href = path;
    download.download = `RSI-${id}.png`;
    document.getElementById('teaser-title').textContent = title;
    buttons.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
  }
  buttons.forEach(button => button.addEventListener('click', () => select(button)));
  const initial = new URLSearchParams(location.search).get('figure');
  const match = buttons.find(b => b.dataset.teaser === initial);
  if (match) select(match);
})();
