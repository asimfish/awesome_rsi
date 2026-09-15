'use strict';
const $ = s => document.querySelector(s);
const data = window.PAPER_DATA;
const root = document.documentElement;
try { const saved = localStorage.getItem('silicon-theme'); if (saved === 'light' || saved === 'dark') root.dataset.theme = saved; } catch {}
function themeLabel(){ $('#theme').setAttribute('aria-label',root.dataset.theme==='dark'?'切换浅色主题':'切换深色主题'); }
themeLabel();
$('#theme').addEventListener('click',()=>{ root.dataset.theme=root.dataset.theme==='dark'?'light':'dark'; try{ localStorage.setItem('silicon-theme',root.dataset.theme); }catch{} themeLabel(); });
const fmt=(n,d=2)=>Number(n).toLocaleString('en-US',{maximumFractionDigits:d});
const codeBase = `https://github.com/hkust-zhiyao/DR_RTL/blob/${data.commit}/`;
$('#commit-link').href = `https://github.com/hkust-zhiyao/DR_RTL/tree/${data.commit}`;
let selected = 'cpu_pipe';
function designList(){
 const q=$('#search').value.trim().toLowerCase(), order=$('#sort').value;
 const rows=data.rows.filter(r=>r.design.includes(q)).sort((a,b)=>order==='loc'?b.loc-a.loc:b.improvement[order]-a.improvement[order]);
 $('#count').textContent=rows.length;
 const container=$('#design-items');container.replaceChildren();
 if(!rows.length){const p=document.createElement('p');p.className='empty';p.textContent='未找到设计，试试 cpu 或 aes。';container.append(p);return;}
 rows.forEach(r=>{const button=document.createElement('button');button.className='design-item'+(r.design===selected?' active':'');button.setAttribute('aria-pressed',String(r.design===selected));
 const v=order==='loc'?fmt(r.loc,0):`${r.improvement[order]<0?'−':'+'}${Math.abs(r.improvement[order]).toFixed(1)}%`;
 button.innerHTML=`<span><strong>${r.design}</strong><small>${fmt(r.loc,0)} LOC · ${r.modules} MODULE${r.modules>1?'S':''}</small></span><span class="design-value ${order!=='loc'&&r.improvement[order]<0?'negative':''}">${v}</span>`;
 button.addEventListener('click',()=>{selected=r.design;designList();renderDesign();});container.append(button);});
}
function renderDesign(){
 const r=data.rows.find(r=>r.design===selected);$('#design-name').textContent=r.design;
 const badge=$('#design-badge');badge.className='badge'+(r.improvement.area<0?' warn':'');badge.textContent=r.improvement.area>0?'面积与时序同时改善':r.improvement.area<0?'时序改善 · 面积增加':'时序改善 · 面积持平';
 $('#design-meta').innerHTML=`<span>${fmt(r.loc,0)} 行 RTL</span><span>${r.modules} 个模块</span><span>商业综合 → Dr. RTL</span>`;
 $('#comparison').innerHTML=['wns','tns','area'].map(k=>{const vals=r[k],max=Math.max(...vals.map(Math.abs)),v=r.improvement[k],unit=k==='area'?'μm²':'ns';return `<div class="compare-row"><div class="compare-name">${k.toUpperCase()}<small>${k==='area'?'综合面积':'负裕量幅度'} · ${unit}</small></div><div class="bars">${vals.map((value,i)=>`<div class="bar-track"><div class="bar-fill ${i?'after':''}" style="width:${Math.max(18,Math.abs(value)/max*100)}%"><span class="bar-value">${fmt(value)}</span></div></div>`).join('')}</div><div class="change ${v<0?'negative':''}">${v<0?'−':'+'}${Math.abs(v).toFixed(1)}%<small>${v<0?'退步':'改善'}</small></div></div>`;}).join('');
 $('#sec-rate').textContent=r.sec+'%';$('#sec-bar').style.width=r.sec+'%';
 $('#design-note').textContent=r.improvement.area<0?`该设计的面积增加了 ${Math.abs(r.improvement.area).toFixed(1)}%。更好的时序不一定带来更小的面积；选择时需要明确权衡。`:`该设计的 WNS 从 ${r.wns[0]} ns 改善至 ${r.wns[1]} ns。负裕量仍未归零，不能解读为已完成时序收敛。`;
}
$('#search').addEventListener('input',designList);$('#sort').addEventListener('change',designList);designList();renderDesign();
const steps=[
 ['分析','ANALYZE','关键路径是诊断入口','分析器读取综合后的时序报告，选择 10–25 条关键路径，区分组合逻辑、扇出和控制依赖等瓶颈，形成有位置依据的改写建议。','.claude/agents/rtl-timing-analyzer.md','timing_word.json\n↓\ncritical_paths + diagnosis'],
 ['改写','REWRITE','从同一父版本探索不同实现','每个主版本生成 5 个不同策略的候选。它们从同一父版本独立出发，优化器参考技能库改写 RTL；同一设计的候选比较是技能提炼的依据。','.claude/agents/rtl-optimizer.md','v0\n├ v0.1 / v0.2 / v0.3\n└ v0.4 / v0.5'],
 ['验证','VERIFY','先验证功能，再比较收益','综合工具给出时序和面积。SEC 对照原始设计检查顺序行为；公开主入口对 LSTM 使用仿真分支。验证未通过的候选不能仅靠 PPA 得分晋升。','syn_flow_eda/run_design.py','reference RTL: v0\nSEC / simulation → gate\nPPA_report.json'],
 ['晋升','SELECT','保留通过验证的最佳候选','公开规则按归一化 WNS、TNS、面积与面积惩罚计算分数。候选须先通过验证，再按较低分数选择。预算最多 10 个主轮次；停止条件的文字仍需统一。','CLAUDE.md','0.50 × ΔWNS / WNS₀\n0.35 × ΔTNS / TNS₀\n0.15 × ΔArea / Area₀ + penalty'],
 ['学习','LEARN','把差异变成下一次可用的经验','比较成功与失败的修改，提炼“结构模式—改写策略”，同时保留避免策略。论文报告 47 条；这体现技能层面的自改进，不是模型权重训练。','.claude/agents/rtl-opt-skill-extractor.md','pattern → strategy\n12 high / 16 medium\n6 low / 13 avoid']
];
let currentStep=0,timer=null;
steps.forEach((s,i)=>{const b=document.createElement('button');b.className='step';b.innerHTML=`<b>0${i+1}</b><span>${s[0]}</span><small>${s[1]}</small>`;b.addEventListener('click',()=>{stopLoop();showStep(i);});$('#loop-steps').append(b);});
function showStep(i){currentStep=i;const s=steps[i];document.querySelectorAll('.step').forEach((b,j)=>{b.classList.toggle('active',i===j);b.setAttribute('aria-pressed',String(i===j));});$('#loop-index').textContent='0'+(i+1);$('#loop-title').textContent=s[2];$('#loop-description').textContent=s[3];$('#loop-source').href=codeBase+s[4];$('#loop-artifact').textContent=s[5];}
function stopLoop(){clearInterval(timer);timer=null;$('#play-loop').textContent='▶ 播放机制';$('#play-loop').setAttribute('aria-pressed','false');}
$('#play-loop').addEventListener('click',()=>{if(timer){stopLoop();return;}$('#play-loop').textContent='Ⅱ 暂停播放';$('#play-loop').setAttribute('aria-pressed','true');timer=setInterval(()=>showStep((currentStep+1)%steps.length),2400);});document.addEventListener('visibilitychange',()=>{if(document.hidden)stopLoop();});showStep(0);
let candidate='ripple';
function circuitValue(a,b,ci){
 if(candidate==='broken')ci=0;
 const p=Array.from({length:8},(_,i)=>((a>>i)&1)^((b>>i)&1));let g=Array.from({length:8},(_,i)=>((a>>i)&1)&((b>>i)&1)),out=0;
 if(candidate==='ripple'){let carry=ci;for(let i=0;i<8;i++){out|=(p[i]^carry)<<i;carry=g[i]|(p[i]&carry);}return out|(carry<<8);}
 let gp=p.slice();for(const d of [1,2,4]){const og=g.slice(),op=gp.slice();for(let i=d;i<8;i++){g[i]=og[i]|(op[i]&og[i-d]);gp[i]=op[i]&op[i-d];}}
 for(let i=0;i<8;i++){const carry=i===0?ci:g[i-1]|(gp[i-1]&ci);out|=(p[i]^carry)<<i;}return out|((g[7]|(gp[7]&ci))<<8);
}
function showSum(){let a=Number($('#input-a').value),b=Number($('#input-b').value);const valid=[a,b].every(n=>Number.isInteger(n)&&n>=0&&n<=255)&&$('#input-a').value!==''&&$('#input-b').value!=='';
 if(!valid){$('#expected').textContent='—';$('#actual').textContent='—';$('#input-status').textContent='请输入 0–255 整数';$('#input-status').className='negative';return;}
 const ci=Number($('#input-cin').value),expected=a+b+ci,actual=circuitValue(a,b,ci);$('#expected').textContent=expected;$('#actual').textContent=actual;$('#input-status').textContent=actual===expected?'一致 ✓':'不一致 ×';$('#input-status').className=actual===expected?'':'negative';}
function drawAdder(){const n=8,w=480,spacing=54,points=Array.from({length:n},(_,i)=>29+i*spacing);let paths='';if(candidate==='ripple'){for(let i=0;i<7;i++)paths+=`<path d="M${points[i]+15} 76 H${points[i+1]-15}"/>`;}else{for(let layer=0;layer<3;layer++){const distance=2**layer;for(let i=distance;i<8;i++)paths+=`<path d="M${points[i-distance]} ${33+layer*31} L${points[i]} ${64+layer*31}" opacity="${.7-layer*.15}"/>`;}}
 const nodes=points.map((x,i)=>`<text x="${x}" y="17" text-anchor="middle">b${i}</text><rect x="${x-15}" y="${candidate==='ripple'?60:113}" width="30" height="29" rx="4" fill="var(--accent-dim)" stroke="var(--accent)"/><text x="${x}" y="${candidate==='ripple'?79:132}" text-anchor="middle">${candidate==='ripple'?'FA':'P/G'}</text>`).join('');
 $('#adder-diagram').innerHTML=`<svg viewBox="0 0 ${w} 158" role="img" aria-label="${candidate==='ripple'?'串行进位链':'并行前缀网络'}"><g fill="none" stroke="${candidate==='broken'?'var(--red)':'var(--accent)'}" stroke-width="1.4">${paths}</g>${nodes}</svg>`;}
function showCandidate(){const r=window.LOCAL_DATA.results.find(x=>x.id===candidate);document.querySelectorAll('[data-candidate]').forEach(b=>{const on=b.dataset.candidate===candidate;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});$('#lab-status').textContent=r.status;$('#lab-status').className='badge '+(r.failed?'fail':'cyan');$('#verified-number').innerHTML=`${fmt(r.passed,0)}<small> / ${fmt(r.inputs,0)} 组输入通过</small>`;$('#gate-depth').textContent=r.depth;$('#gate-count').textContent=r.gates;
 $('#candidate-note').textContent=candidate==='ripple'?'基线：进位逐位传播。这个实现有 40 个布尔门，最长输出路径为 17 层，全部输入通过验证。':candidate==='prefix'?'并行前缀把逻辑深度从 17 层降至 8 层，但门数从 40 增至 91。正确性保持，结构成本增加。':'故意忽略 Cin 的缺陷候选有 65,536 个反例。首个反例：A=0、B=0、Cin=1，正确结果为 1，候选却输出 0。';drawAdder();showSum();}
for(const b of document.querySelectorAll('[data-candidate]'))b.addEventListener('click',()=>{candidate=b.dataset.candidate;showCandidate();});for(const id of ['#input-a','#input-b','#input-cin'])$(id).addEventListener('input',showSum);showCandidate();
