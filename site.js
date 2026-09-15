(() => {
 const oldAnchors=document.body.dataset.legacyChipAnchors;
 if(oldAnchors&&location.hash){try{if(JSON.parse(oldAnchors).includes(decodeURIComponent(location.hash.slice(1)))){location.replace('chip/'+location.hash);return}}catch(_){}}

 const toggle=document.querySelector('#theme');
 let dark=false;try{dark=localStorage.getItem('rsi-theme')==='dark'}catch(_){}
 function theme(){document.documentElement.dataset.theme=dark?'dark':'light';toggle.textContent=dark?'浅色阅读':'深色阅读';toggle.setAttribute('aria-label',dark?'切换浅色模式':'切换深色模式')}
 theme();toggle.addEventListener('click',()=>{dark=!dark;theme();try{localStorage.setItem('rsi-theme',dark?'dark':'light')}catch(_){}});
 const input=document.querySelector('#search'),category=document.querySelector('#category');
 const groups=[...document.querySelectorAll('.paper-group')];
 const items=groups.length?groups:[...document.querySelectorAll('.search-card')];
 function filter(){const q=(input?.value||'').trim().toLocaleLowerCase();let n=0;items.forEach(item=>{const match=(item.dataset.search||item.textContent).toLocaleLowerCase().includes(q)&&(!category?.value||item.dataset.category===category.value);item.hidden=!match;if(match)n++});const count=document.querySelector('#result-count');if(count)count.textContent=`显示 ${n} / ${items.length} ${groups.length?'个研究分类':'篇解读'}`;const empty=document.querySelector('#empty');if(empty)empty.hidden=n!==0}
 input?.addEventListener('input',filter);category?.addEventListener('change',filter);filter();
 const toc=[...document.querySelectorAll('aside a[href^="#"]')];
 function progress(){const height=document.documentElement.scrollHeight-innerHeight;document.querySelector('#progress').style.width=(height>0?Math.min(100,scrollY/height*100):100)+'%';const current=[...document.querySelectorAll('main h2[id],main h3[id]')].filter(h=>h.getBoundingClientRect().top<160).pop();toc.forEach(a=>{const active=current&&decodeURIComponent(a.hash.slice(1))===current.id;a.classList.toggle('active',Boolean(active));if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current')})}
 addEventListener('scroll',progress,{passive:true});addEventListener('resize',progress);progress();
})();
