
/* ===== 8. BOOT [ENGINE] ===== */
const ERRORS = [];
window.addEventListener('error', e => ERRORS.push('script error: ' + e.message + ' (' + (e.filename || '').split('/').pop() + ':' + e.lineno + ')'));
const Q = new URLSearchParams(location.search), FLAGS = { check: Q.has('check'), static: Q.has('static'), notes: Q.has('notes') };
const ROOT = document.documentElement, THEMES = ROOT.dataset.theme === 'brand' ? ['brand', 'light', 'dark', 'paper'] : ['light', 'dark', 'paper'];
const MOTION = !(matchMedia('(prefers-reduced-motion: reduce)').matches || FLAGS.static || FLAGS.check);
let slides = [], cur = 0, scale = 1;
const BIND_ISSUES = [];
/* static attributes are captured before any builder runs, for the brand-leak scan */
const STATIC_ATTRS = [];
function captureStatic() { $$('[style],[fill],[stroke]').forEach(e => ['style', 'fill', 'stroke'].forEach(a => { const v = e.getAttribute(a); if (v) STATIC_ATTRS.push(e.nodeName.toLowerCase() + ' ' + a + '="' + v + '"'); })); }
function resolveData(o) {
  for (const k in o) { if (typeof o[k] === 'string' && o[k].includes('{{')) o[k] = resolve(o[k], BIND_ISSUES); else if (o[k] && typeof o[k] === 'object') resolveData(o[k]); }
}
function bindText() {
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT), nodes = [];
  while (w.nextNode()) nodes.push(w.currentNode);
  nodes.forEach(n => { if (n.nodeValue.includes('{{') && !/^(SCRIPT|STYLE)$/.test(n.parentNode.nodeName)) n.nodeValue = resolve(n.nodeValue, BIND_ISSUES); });
  $$('[aria-label]').forEach(e => { const v = e.getAttribute('aria-label'); if (v.includes('{{')) e.setAttribute('aria-label', resolve(v, BIND_ISSUES)); });
}
/* chrome added by script: kind chip, footnote from the dataset, footer */
function decorate() {
  slides.forEach((s, i) => {
    const key = s.dataset.d || (s.querySelector('svg[data-d]') || {}).dataset?.d, ds = DATA[key], kind = ds && ds.kind;
    if (kind && kind !== 'concept' && s.dataset.chip !== 'none') { const c = document.createElement('div'); c.className = 'chip ' + kind; c.textContent = KIND[kind]; s.append(c); }
    const bare = s.dataset.foot === 'none', fp = ds && !bare && s.dataset.chip !== 'none' && footParts(ds);
    if (fp && (fp.left || fp.right)) { const f = document.createElement('div'); f.className = 'fn'; ['left', 'right'].forEach(k => { const sp = document.createElement('span'); sp.textContent = fp[k]; f.append(sp); }); s.append(f); }
    if (!bare && !/\b(hero|divider)\b/.test(s.className)) { const f = document.createElement('div'); f.className = 'foot'; f.innerHTML = '<span></span><span></span>'; f.firstChild.textContent = DECK.name + ' | ' + s.dataset.sec; f.lastChild.textContent = i + 1; s.append(f); }
  });
}
function renderAll() {
  readTokens();
  $$('svg[data-g]').forEach(svg => {
    try { G[svg.dataset.g](svg, DATA[svg.dataset.d], JSON.parse(svg.dataset.o || '{}')); } catch (e) { ERRORS.push('builder ' + svg.dataset.g + ' (' + svg.dataset.d + '): ' + e.message); }
  });
  $$('[data-people]').forEach(box => {
    box.textContent = '';
    DECK.people.forEach(p => {
      const sv = el('svg', { width: 100, height: 100, viewBox: '0 0 100 100', 'aria-hidden': 'true' }); AV(sv, p.key, p.name, 50, 50, 42, true); box.append(sv);
      const t = document.createElement('div'); t.innerHTML = '<div class="nm"></div><div class="rl"></div>'; t.firstChild.textContent = p.name; if (p.role) t.lastChild.textContent = p.role; else t.lastChild.remove(); box.append(t);
    });
  });
  $$('svg[data-motif]').forEach(svg => {
    const sr = $('#stage').getBoundingClientRect(), box = svg.parentNode, clear = $$('.eyebrow,.title,.team,.people,.logo,.rule', box).map(e => { const r = e.getBoundingClientRect(); return { x0: (r.left - sr.left) / scale - 50, x1: (r.right - sr.left) / scale + 50, y0: (r.top - sr.top) / scale - 40, y1: (r.bottom - sr.top) / scale + 40 }; });
    drawMotif(svg, clear);
  });
  $$('svg[data-marks]').forEach(drawMarks);
}
/* stage scaling, letterboxed */
function layout() {
  const nh = document.body.classList.contains('notes') ? $('#notes').offsetHeight : 0, w = innerWidth, h = innerHeight - nh;
  scale = Math.min(w / 1920, h / 1080); const st = $('#stage');
  st.style.transform = 'translate(' + (w - 1920 * scale) / 2 + 'px,' + (h - 1080 * scale) / 2 + 'px) scale(' + scale + ')';
}
/* navigation */
function go(i, noHash) {
  cur = Math.max(0, Math.min(slides.length - 1, i));
  slides.forEach((s, k) => s.classList.toggle('active', k === cur));
  $('#notes').textContent = ($('.notes', slides[cur]) || {}).textContent || '';
  if (!noHash) history.replaceState(null, '', '#' + (cur + 1));
  $$('#overview .th').forEach((t, k) => t.classList.toggle('cur', k === cur));
  layout(); playMotion(slides[cur]);
}
const toggle = (cls, on) => { document.body.classList.toggle(cls, on); layout(); };
function setTheme(name) { ROOT.dataset.theme = name; renderAll(); if (document.body.classList.contains('ov')) buildOverview(); }
function buildOverview() {
  const ov = $('#overview'); ov.textContent = '';
  slides.forEach((s, i) => { const th = document.createElement('div'), inn = document.createElement('div'); th.className = 'th' + (i === cur ? ' cur' : ''); inn.className = 'in'; inn.append(s.cloneNode(true));
    th.append(inn); th.addEventListener('click', () => { toggle('ov', false); go(i); }); ov.append(th); const k = th.clientWidth / 1920; inn.style.transform = 'scale(' + k + ')'; });
}
/* motion: chart marks only; DOM always holds the final state */
function playMotion(s) {
  if (!MOTION) return; const dur = parseFloat(cs().getPropertyValue('--dur')), ease = cs().getPropertyValue('--ease').trim();
  $$('[data-anim]', s).forEach((e, i) => {
    const x = e.dataset.anim === 'x'; if (x) e.style.cssText += ';transform-box:fill-box;transform-origin:left center';
    e.animate(x ? [{ transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }] : [{ opacity: 0 }, { opacity: 1 }], { duration: dur, delay: Math.min(i * 30, 420), easing: ease, fill: 'backwards' });
  });
  $$('.statement .num', s).forEach(n => { const m = n.textContent.match(/^(\d+)%$/); if (!m) return; const v = +m[1], t0 = performance.now(); (function tick(t) { const p = Math.min(1, (t - t0) / dur); n.textContent = Math.round(v * (1 - Math.pow(1 - p, 3))) + '%'; if (p < 1) requestAnimationFrame(tick); })(t0); });
  const g = $('[data-breathe]', s); if (g) {
    $$('[data-ring]', g).forEach(c => c.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 1400, delay: c.dataset.ring * 150, easing: ease, fill: 'backwards' }));
    g.animate([{ transform: 'scale(1)' }, { transform: 'scale(1.02)' }], { duration: 9000, delay: 2200, direction: 'alternate', iterations: Infinity, easing: 'ease-in-out' });
  }
}
/* self-check: window.__deckCheck = { issues, notes } and the panel pre#deck-check */
const LEAK = { hex: new RegExp('#' + '[0-9a-fA-F]{3,8}\\b'), fn: new RegExp('rgb' + 'a?\\(\\s*\\d|hsl' + 'a?\\(\\s*\\d'), ff: new RegExp('font-family' + '\\s*:\\s*(?!var\\()[^;}]*[A-Za-z]') };
function leakScan() {
  const out = [], scan = (txt, where) => txt.split('\n').forEach((ln, i) => { for (const k in LEAK) { const m = ln.match(LEAK[k]); if (m) out.push('BRAND LEAK ' + where + ' line ' + (i + 1) + ': ' + m[0]); } });
  const st = $('style').textContent; scan(st.slice(st.indexOf('2. BASE')), 'style');
  $$('script').forEach(s => scan(s.textContent, 'script'));
  STATIC_ATTRS.forEach(a => scan(a, 'markup'));
  return out;
}
const PAIRS = [['ink', 'bg'], ['ink2', 'bg'], ['ink3', 'bg'], ['accent', 'bg'], ['accentContrast', 'accent'], ['inkOnDark', 'bgDark'], ['ink2OnDark', 'bgDark'], ['ink3OnDark', 'bgDark'], ['accentOnDark', 'bgDark'],
  ['positiveOnDark', 'bgDark'], ['cautionOnDark', 'bgDark'], ['negativeOnDark', 'bgDark'], ['infoOnDark', 'bgDark'], ['positiveInk', 'positiveTint'], ['cautionInk', 'cautionTint'], ['negativeInk', 'negativeTint'], ['infoInk', 'infoTint'], ['accentInk', 'accentTint'], ['ink3', 'surface2'], ['lineStrong', 'bg', 3]];
function contrastTable() {
  const keep = ROOT.dataset.theme, lines = [], bad = [];
  THEMES.forEach(t => {
    ROOT.dataset.theme = t; readTokens(); const row = [];
    PAIRS.forEach(([a, b, need = 4.5]) => { const r = contrast(C[a], C[b]); row.push(a + '/' + b + ' ' + r.toFixed(1)); if (r < need) bad.push('contrast ' + t + ': ' + a + ' on ' + b + ' is ' + r.toFixed(2) + ', needs ' + need + '; nearest passing ' + nearestPass(C[a], C[b], need)); });
    lines.push(t.padEnd(6) + ' ' + row.join('  '));
  });
  ROOT.dataset.theme = keep; readTokens(); return { lines, bad };
}
function textBoxes(slide) {
  const sr = $('#stage').getBoundingClientRect(), k = scale, out = [];
  const add = (e, rect, size, isSvg) => { if (!rect.width || !rect.height) return; const trim = isSvg ? .2 * size : .12 * size, rot = isSvg && /rotate/.test(e.getAttribute('transform') || '');
    out.push({ e, size, x0: (rect.left - sr.left) / k, x1: (rect.right - sr.left) / k, y0: (rect.top - sr.top) / k + (rot ? 0 : (isSvg ? .08 * size : trim)), y1: (rect.bottom - sr.top) / k - (rot ? 0 : trim), svg: isSvg, txt: e.textContent.trim().slice(0, 40) }); };
  $$('text', slide).forEach(e => { if (e.closest('symbol')) return; add(e, e.getBoundingClientRect(), parseFloat(e.getAttribute('font-size')), true); });
  const walker = document.createTreeWalker(slide, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) { const n = walker.currentNode, p = n.parentElement; if (!n.nodeValue.trim() || p.closest('svg') || p.closest('[aria-hidden="true"]') || p.closest('.notes') || /^(SCRIPT|STYLE)$/.test(p.nodeName)) continue;
    const rg = document.createRange(); rg.selectNodeContents(n); [...rg.getClientRects()].forEach(r => add(p, r, parseFloat(getComputedStyle(p).fontSize), false)); }
  return out;
}
async function runCheck() {
  await document.fonts.ready; const issues = [], notes = [], keep = cur;
  BIND_ISSUES.forEach(m => issues.push(m)); ERRORS.forEach(m => issues.push(m)); leakScan().forEach(m => issues.push(m));
  slides.forEach((s, i) => {
    slides.forEach((o, k) => o.classList.toggle('active', k === i)); const at = 'slide ' + (i + 1), boxes = textBoxes(s), hero = /\b(hero|divider)\b/.test(s.className);
    boxes.forEach(b => {
      if (b.x0 < -1 || b.x1 > 1921 || b.y0 < -1 || b.y1 > 1081) issues.push(at + ': text off the stage "' + b.txt + '"');
      if (!hero && !b.e.closest('.foot,.chip,.fn') && (b.x0 < 134 || b.x1 > 1786) && !b.e.closest('.statement,.divider')) notes.push('NOTE ' + at + ': text outside the side margins "' + b.txt + '"');
      if (b.svg && b.size < 19.9 && !b.e.closest('.foot,.chip')) issues.push(at + ': text smaller than 20 px "' + b.txt + '" (' + b.size + ')');
    });
    for (let a = 0; a < boxes.length; a++) for (let b = a + 1; b < boxes.length; b++) {
      const p = boxes[a], q = boxes[b]; if (p.e === q.e && !p.svg) continue; if (!p.svg && !q.svg && (p.e.contains(q.e) || q.e.contains(p.e))) continue;
      if (Math.min(p.x1, q.x1) - Math.max(p.x0, q.x0) > 3 && Math.min(p.y1, q.y1) - Math.max(p.y0, q.y0) > 3) issues.push(at + ': text overlaps "' + p.txt + '" and "' + q.txt + '"');
    }
    const ld = $('.lede', s); if (ld && ld.getBoundingClientRect().height / scale > parseFloat(getComputedStyle(ld).fontSize) * 1.6) notes.push('NOTE ' + at + ': lede wraps to two lines');
    if (!$('.notes', s) || !$('.notes', s).textContent.trim()) issues.push(at + ': no notes');
    if (!hero && !s.classList.contains('statement') && !s.querySelector('svg.full')) issues.push(at + ': content slide without a graphic');
    if (!/\b(hero|divider)\b/.test(s.className) && $$('h1', s).length !== 1 && !s.classList.contains('statement')) issues.push(at + ': needs exactly one h1');
  });
  (DECK.checks || []).forEach(f => { const m = f(); if (m) issues.push(m); });
  const ct = contrastTable(); ct.bad.forEach(m => issues.push(m));
  slides.forEach((o, k) => o.classList.toggle('active', k === keep));
  window.__deckCheck = { issues, notes };
  let pre = $('#deck-check'); if (!pre) { pre = document.createElement('pre'); pre.id = 'deck-check'; document.body.append(pre); }
  pre.className = issues.length ? 'bad' : '';
  pre.textContent = 'CHECK summary: ' + issues.length + ' issue(s) on ' + slides.length + ' slides\ntheme: ' + ROOT.dataset.theme + '\n' + issues.join('\n') + (issues.length ? '\n' : '') + notes.join('\n') + '\n\ncontrast (ratio, need 4.5; line-strong 3):\n' + ct.lines.join('\n');
  return window.__deckCheck;
}
window.runDeckCheck = runCheck;
/* input */
addEventListener('keydown', e => {
  if (e.ctrlKey || e.metaKey || e.altKey) return; const k = e.key;
  if (['ArrowRight', 'ArrowDown', 'PageDown', ' '].includes(k)) { e.preventDefault(); go(cur + 1); }
  else if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(k)) { e.preventDefault(); go(cur - 1); }
  else if (k === 'Home') go(0); else if (k === 'End') go(slides.length - 1);
  else if (k === 's' || k === 'S') toggle('notes'); else if (k === 'f' || k === 'F') { document.fullscreenElement ? document.exitFullscreen() : ROOT.requestFullscreen && ROOT.requestFullscreen(); }
  else if (k === 'o' || k === 'O') { toggle('ov'); if (document.body.classList.contains('ov')) buildOverview(); }
  else if (k === 't' || k === 'T') setTheme(THEMES[(THEMES.indexOf(ROOT.dataset.theme) + 1) % THEMES.length]);
  else if (k === '?') toggle('hp'); else if (k === 'Escape') { toggle('ov', false); toggle('hp', false); }
});
$('#viewport').addEventListener('click', e => { if (document.body.classList.contains('ov') || document.body.classList.contains('hp')) return; const f = e.clientX / innerWidth; if (f > .8) go(cur + 1); else if (f < .2) go(cur - 1); });
let tx = null; addEventListener('touchstart', e => { tx = e.touches[0].clientX; }, { passive: true });
addEventListener('touchend', e => { if (tx === null) return; const d = e.changedTouches[0].clientX - tx; if (Math.abs(d) > 50) go(cur + (d < 0 ? 1 : -1)); tx = null; });
addEventListener('resize', layout); addEventListener('fullscreenchange', layout); addEventListener('hashchange', () => go((parseInt(location.hash.slice(1)) || 1) - 1, true));
addEventListener('beforeprint', () => { document.getAnimations().forEach(a => a.cancel()); renderAll(); });
/* boot */
captureStatic();
resolveData(DATA);
slides = $$('.slide'); bindText(); decorate();
if (Q.get('theme') && THEMES.includes(Q.get('theme'))) ROOT.dataset.theme = Q.get('theme');
if (FLAGS.notes) document.body.classList.add('notes');
layout(); renderAll(); go((parseInt(location.hash.slice(1)) || 1) - 1, true);
document.fonts.ready.then(() => { renderAll(); layout(); if (FLAGS.check) runCheck(); });
</script>
</body>
</html>
