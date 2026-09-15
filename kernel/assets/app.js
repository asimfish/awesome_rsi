(()=>{'use strict';
const LIVE='https://raw.githubusercontent.com/asimfish/awesome_rsi/server-data/research.json',SERVER='https://raw.githubusercontent.com/asimfish/awesome_rsi/server-data/servers.json';
const $=id=>document.getElementById(id),fmt=(n,d=2)=>Number.isFinite(n)?n.toFixed(d):'—',time=s=>new Date(s).toLocaleString('zh-CN',{hour12:false}),safe=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let data,op='softmax',shapeIndex=1,candidate='retest',codeKey='',generation=0;
for(let i=0;i<96;i++)document.querySelector('.matrix').append(document.createElement('i'));
try{document.body.classList.toggle('dark',localStorage.getItem('kernel-theme')==='dark')}catch{}
$('theme').onclick=()=>{document.body.classList.toggle('dark');try{localStorage.setItem('kernel-theme',document.body.classList.contains('dark')?'dark':'light')}catch{}};
async function fetchJSON(url){const r=await fetch(url,{cache:'no-store',signal:AbortSignal.timeout(12000)});if(!r.ok)throw Error('HTTP');return r.json()}
function statusText(s,workers){if(s.state==='running')return workers>0?'● 实验运行中':'◷ 记录标为运行中，暂未检测到工作进程';return s.state==='completed'?'✓ 本轮实验已完成':'! 本轮实验异常结束'}
function artifact(path){return typeof path==='string'&&/^evidence\/(relu|gelu|softmax)\/(naive|block256|block1024|warps8|warps16|retest)\/result\.json$/.test(path)?path:null}
function render(){
 if(!data)return;const s=data.projects.kernel,results=s.results.filter(r=>r.operator===op);if(!results.length)return;
 if(!results.some(r=>r.candidate===candidate))candidate=results.at(-1).candidate;
 const r=results.find(r=>r.candidate===candidate),m=r.measurements?.[shapeIndex];
 $('shape').innerHTML=(r.measurements||[]).map((m,i)=>`<option value="${i}" ${i===shapeIndex?'selected':''}>${m.shape.join(' × ')}</option>`).join('');
 $('selection').textContent=op.toUpperCase()+' / '+candidate+(candidate==='retest'?' ← '+s.selected?.[op]:'');
 if(!m){$('result-title').textContent='该候选没有有效计时';$('verdict').textContent=r.reason||'等待测量';$('bars').replaceChildren();return;}
 $('result-title').textContent=fmt(m.speedup_vs_compiled)+'× 相对编译后的 PyTorch';
 $('verdict').textContent=(m.speedup_vs_compiled>1?'当前形状测得更快。':'当前形状未超过编译基线。')+(m.stable?' 本组计时波动较小，仍需更多独立复测。':' 本组计时波动较大，暂不认定为稳定收益。');
 const max=Math.max(...['eager','compiled','candidate'].map(k=>m[k].max_us))*1.07;
 $('bars').innerHTML=[['eager','普通 PyTorch'],['compiled','torch.compile'],['candidate','我们的 Triton']].map(([key,label])=>{const v=m[key];return `<div class="bar-row"><div class="bar-label"><span>${label}</span><b>${fmt(v.median_us,3)} µs</b></div><div class="bar-track"><div class="bar-fill" style="width:${100*v.median_us/max}%"></div><i class="range" style="left:${100*v.min_us/max}%;width:${Math.max(.2,100*(v.max_us-v.min_us)/max)}%"></i></div></div>`}).join('');
 $('detail').innerHTML=[['正确性',r.correctness?.pass?'18 / 18 + 计时形状通过':'未通过'],['相对普通 PyTorch',fmt(m.speedup_vs_eager)+'×'],['候选计时范围',fmt(m.candidate.min_us,3)+'–'+fmt(m.candidate.max_us,3)+' µs'],['候选标准差',fmt(m.candidate.stdev_us,3)+' µs'],['成组重复','7 组 × 300 次'],['候选源码 SHA-256',(r.candidate_sha256||'').slice(0,14)+'…']].map(([k,v])=>`<div><dt>${safe(k)}</dt><dd>${safe(v)}</dd></div>`).join('');
 const path=artifact(r.artifact);$('links').innerHTML=path?`<a href="${path}">完整测量 JSON ↗</a><a href="${path.replace('result.json','candidate.py')}">候选源码 ↗</a>`:'';
 $('results').innerHTML=results.map(x=>{const t=x.measurements?.[shapeIndex];return `<tr class="${x.candidate===candidate?'chosen':''}"><td><button data-candidate="${safe(x.candidate)}">${safe(x.candidate)}${x.candidate==='retest'?' · 复测':''}</button></td><td>${x.correctness?.pass?'✓ 通过':'未通过'}</td><td>${fmt(t?.candidate.median_us,3)}</td><td>${fmt(t?.speedup_vs_eager)}×</td><td class="${t?.speedup_vs_compiled>1?'good':'warn'}">${fmt(t?.speedup_vs_compiled)}×</td><td class="${t?.stable?'good':'warn'}">${t?.stable?'较小':'较大 / 待复测'}</td></tr>`}).join('');
 if(path&&codeKey!==path){codeKey=path;$('code').textContent='读取源码…';fetch(path.replace('result.json','candidate.py')).then(r=>{if(!r.ok)throw Error();return r.text()}).then(t=>{if(codeKey===path)$('code').textContent=t}).catch(()=>{$('code').textContent='源码尚未同步，请稍后重试。'})}
}
async function refresh(){const turn=++generation;let d,fallback=false;try{d=await fetchJSON(LIVE+'?t='+Date.now())}catch{fallback=true;try{d=await fetchJSON('research.json')}catch{$('state').textContent='研究记录暂不可用';return}}
 if(turn!==generation)return;data=d;const s=d.projects.kernel,stale=Date.now()-Date.parse(d.published_at)>d.stale_after_s*1000;
 $('state').textContent=statusText(s,d.workers.kernel);$('freshness').textContent=(fallback?'本站发布快照 · ':stale?'同步已过期 · ':'数据同步 · ')+time(d.published_at);
 $('progress').textContent=s.completed+' / '+s.planned;$('run').textContent=s.run_id+' · '+(s.current||'进入结果审阅');
 $('correctness').textContent=s.results.filter(r=>r.correctness?.pass).length+' / '+s.completed;
 const headline=s.results.find(r=>r.operator==='softmax'&&r.candidate==='retest')?.measurements?.[1];$('headline-speed').textContent=headline?fmt(headline.speedup_vs_compiled)+'×':'—';$('headline-note').textContent=headline?'1024 × 4096 · '+(headline.stable?'复测波动较小':'复测波动较大'):'等待独立复测';
 $('workers').textContent=stale||fallback?'—':d.workers.kernel;$('worker-note').textContent=stale||fallback?'快照不作为当前进程数':d.workers.kernel?'检测到本项目工作进程':s.state==='running'?'暂未检测到工作进程':'当前无工作进程 · 本轮已停止';
 $('next').textContent=s.next;$('method').textContent=s.method;$('chip-state').textContent=d.projects.chip.run_id+' · '+statusText(d.projects.chip,d.workers.chip)+' · '+d.projects.chip.completed+'/'+d.projects.chip.planned;
 $('events').innerHTML=s.events.slice(-14).reverse().map(e=>`<li><time datetime="${safe(e.at)}">${safe(new Date(e.at).toLocaleTimeString('zh-CN',{hour12:false}))}</time><span>${safe(e.text)}</span></li>`).join('');render();
}
async function server(){try{const s=await fetchJSON(SERVER+'?t='+Date.now()),n=s.node,stale=Date.now()-Date.parse(s.updated_at)>s.stale_after_s*1000;const cards=[['CPU / '+n.cpu.logical_cpus+' 线程',n.cpu.util_pct,n.cpu.model],['内存',n.memory.used_pct,fmt(n.memory.used_bytes/2**30,1)+' / '+fmt(n.memory.total_bytes/2**30,1)+' GiB'],...n.gpus.cards.map(g=>['GPU '+g.index+' / '+g.model.replace('NVIDIA GeForce ',''),g.util_pct,fmt(g.memory_used_mib/1024,1)+' / '+fmt(g.memory_total_mib/1024,1)+' GiB · '+fmt(g.temperature_c,0)+'°C'])];$('server-cards').innerHTML=cards.map(([name,value,note])=>`<div class="server-card"><small>${safe(name)}</small><strong>${fmt(value,0)}<small style="display:inline"> %</small></strong><div class="meter"><i style="width:${Math.min(100,Math.max(0,value||0))}%"></i></div><p>${safe(note)}</p></div>`).join('');$('server-freshness').textContent=(stale?'采样已过期 · ':'最近采样 · ')+time(s.updated_at)}catch{$('server-freshness').textContent='服务器采样暂不可用，未推断当前负载。'}}
 $('ops').onclick=e=>{const b=e.target.closest('[data-op]');if(!b)return;op=b.dataset.op;candidate='retest';document.querySelectorAll('[data-op]').forEach(x=>x.classList.toggle('active',x===b));render()};$('shape').onchange=e=>{shapeIndex=Number(e.target.value);render()};$('results').onclick=e=>{const b=e.target.closest('[data-candidate]');if(b){candidate=b.dataset.candidate;render()}};$('refresh').onclick=()=>{refresh();server()};refresh();server();setInterval(refresh,30000);setInterval(server,60000);
})();
