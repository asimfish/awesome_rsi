(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  if (!$('overview')) return;
  let experiment = null, telemetry = null, experimentSource = '', telemetrySource = '', experimentFailed = false, telemetryFailed = false;
  let experimentBusy = false, telemetryBusy = false;
  const stages = {baseline:'建立基线',generating:'模型生成候选',formal:'验证功能等价',synthesis:'综合标准单元',timing:'测量关键路径',selection:'选择或回退',learning:'记录优化经验',revalidation:'独立复跑'};
  const finite = n => typeof n === 'number' && Number.isFinite(n);
  const stamp = s => Number.isFinite(Date.parse(s));
  const put = (id, text) => { $(id).textContent = text; };
  const date = value => new Date(value).toLocaleString('zh-CN', {month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false});
  async function read(remote, local, validate) {
    for (const [url, source] of [[remote,'实时记录'],[local,'站点快照']]) {
      try {
        const r = await fetch(url + '?t=' + Date.now(), {cache:'no-store', signal:AbortSignal.timeout(12000)});
        if (!r.ok) throw Error('HTTP ' + r.status);
        const data = await r.json();
        if (!validate(data)) throw Error('Invalid data');
        return {data, source};
      } catch (error) { if (source === '站点快照') throw error; }
    }
  }
  function experimentValid(s) {
    return s?.schema === 1 && ['running','completed','failed'].includes(s.state) && stamp(s.updated_at) &&
      Number.isInteger(s.completed) && s.completed >= 0 && Number.isInteger(s.budget) && s.budget > 0 &&
      typeof s.run_id === 'string' && /^[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}$/.test(s.run_id) && Array.isArray(s.events);
  }
  function telemetryValid(s) {
    return s?.schema === 1 && stamp(s.updated_at) && s.stale_after_s === 900 &&
      Number.isInteger(s.project?.active_process_count) && s.project.active_process_count >= 0 && Array.isArray(s.project.runs);
  }
  function render() {
    if (experiment) {
      const s = experiment, age = (Date.now() - Date.parse(s.heartbeat_at || s.updated_at)) / 1000;
      const uncertain = experimentFailed || experimentSource === '站点快照' || (s.state === 'running' && (!finite(age) || age > 180));
      const state = uncertain ? 'uncertain' : s.state;
      $('overview-dot').dataset.state = state;
      put('overview-state', uncertain ? (experimentFailed ? '同步失败 · 显示最近记录' : experimentSource === '站点快照' ? '站点快照 · 当前状态待核实' : '心跳过期 · 当前状态待核实') : s.state === 'completed' ? '本轮已完成 · 等待下一轮实验' : s.state === 'failed' ? '实验已停止 · 需要处理错误' : '实验运行中 · ' + (stages[s.stage] || '处理中'));
      put('overview-run', s.run_id);
      put('overview-updated', '实验记录 ' + date(s.updated_at) + ' · 每 30 秒读取');
      put('overview-progress', s.completed + ' / ' + s.budget);
      const b = s.best, base = s.baseline;
      const measured = b?.formal === 'pass' && finite(b.adp) && finite(base?.adp) && base.adp > 0;
      put('overview-gain', measured ? (100 * (1 - b.adp / base.adp)).toFixed(2) + '%' : '待验证');
      put('overview-delay', measured && finite(b.delay_ns) ? (b.delay_ns * 1000).toFixed(1) + ' ps' : '—');
      put('overview-best', measured ? b.id + ' · ' + (s.revalidation?.pass ? '独立复跑通过' : '已通过 RTL 等价') : '仅展示通过验证的测量');
      const area = measured && finite(b.area_um2) && finite(base.area_um2) && base.area_um2 > 0 ? 100 * (b.area_um2 / base.area_um2 - 1) : null;
      put('overview-tradeoff', area === null ? '面积数据待验证' : '面积' + (area >= 0 ? '增加 ' : '减少 ') + Math.abs(area).toFixed(2) + '% · 布局布线前');
      const event = s.events.at(-1);
      put('overview-event', event && typeof event.text === 'string' ? (stamp(event.at) ? date(event.at) + ' · ' : '') + event.text : '暂无实验事件');
    } else if (experimentFailed) {
      put('overview-state', '暂时无法读取实验记录'); $('overview-dot').dataset.state = 'uncertain';
      put('overview-event','实验数据暂不可用，30 秒后自动重试。');
    }
    if (telemetry) {
      const s = telemetry, age = (Date.now() - Date.parse(s.updated_at)) / 1000;
      const uncertain = telemetryFailed || telemetrySource === '站点快照' || age > 900;
      put('overview-processes', uncertain ? '待核实' : String(s.project.active_process_count));
      put('overview-server', uncertain ? '采样 ' + date(s.updated_at) + ' · ' + (telemetryFailed ? '同步失败' : '快照或过期记录') : (s.project.active_process_count ? '检测到本项目进程' : '当前无本项目实验进程') + ' · ' + date(s.updated_at));
      const runs = s.project.runs.filter(r => /^[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}$/.test(r.run_id) && Number.isInteger(r.completed) && r.completed >= 0);
      put('overview-total', runs.length ? '记录累计 ' + runs.length + ' 轮 · ' + runs.reduce((n,r) => n+r.completed,0) + ' 个候选' : '暂无累计实验记录');
    } else if (telemetryFailed) {
      put('overview-processes', '待核实'); put('overview-server', '服务器采样读取失败'); put('overview-total', '累计记录暂不可用');
    }
  }
  async function refreshExperiment() {
    if (experimentBusy) return; experimentBusy = true;
    try {
      const r = await read('https://raw.githubusercontent.com/asimfish/awesome_rsi/gh-pages/live/status.json', 'live/status.json', experimentValid);
      if (experiment && Date.parse(r.data.updated_at) < Date.parse(experiment.updated_at)) throw Error('Older record');
      experiment = r.data; experimentSource = r.source; experimentFailed = false;
    } catch (_) { experimentFailed = true; }
    finally { experimentBusy = false; render(); }
  }
  async function refreshTelemetry() {
    if (telemetryBusy) return; telemetryBusy = true;
    try {
      const r = await read('https://raw.githubusercontent.com/asimfish/awesome_rsi/server-data/servers.json', 'live/server-snapshot.json', telemetryValid);
      if (telemetry && Date.parse(r.data.updated_at) < Date.parse(telemetry.updated_at)) throw Error('Older snapshot');
      telemetry = r.data; telemetrySource = r.source; telemetryFailed = false;
    } catch (_) { telemetryFailed = true; }
    finally { telemetryBusy = false; render(); }
  }
  refreshExperiment(); refreshTelemetry();
  setInterval(refreshExperiment, 30000); setInterval(refreshTelemetry, 60000); setInterval(render, 10000);
})();
