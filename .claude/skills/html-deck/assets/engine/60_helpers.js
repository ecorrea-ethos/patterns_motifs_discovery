
/* ===== 6. HELPERS [ENGINE] ===== */
const NS = 'http://www.w3.org/2000/svg';
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const camel = s => s.replace(/-([a-z0-9])/g, (m, c) => c.toUpperCase());
const COLOR_TOKENS = ['bg', 'bg-alt', 'surface', 'surface-2', 'bg-dark', 'letterbox', 'ink', 'ink-2', 'ink-3', 'ink-on-dark', 'ink-2-on-dark', 'ink-3-on-dark', 'line', 'line-strong', 'line-on-dark', 'line-strong-on-dark', 'accent-contrast', 'motif-a', 'motif-b', 'photo-ring']
  .concat(['accent', 'positive', 'caution', 'negative', 'info'].flatMap(r => [r, r + '-tint', r + '-ink', r + '-on-dark']))
  .concat([1, 2, 3, 4, 5, 6, 7, 8].map(i => 's' + i), [1, 2, 3, 4, 5, 6].map(i => 'seq-' + i), [1, 2, 3, 4, 5, 6, 7].map(i => 'div-' + i));
const SIZE_TOKENS = ['hero', 'display', 'divider', 'title', 'lede', 'card', 'body', 'label', 'kicker', 'foot', 'big', 'stat', 'axis', 'eyebrow', 'name', 'statement', 'num', 'cap', 'title2'];
let C = {}, S = {}, FONT = {}, W = {}, SH = {};
const cs = () => getComputedStyle(document.documentElement);
/* readTokens(): resolve every color token to a plain rgb() string (color-mix included) via a hidden probe, so JS contrast math works */
function normColor(v) {
  let m = v.match(/^rgba?\(([^)]+)\)/);
  if (m) { const p = m[1].split(/[ ,\/]+/).map(Number); return 'rgb(' + p.slice(0, 3).map(Math.round).join(', ') + ')'; }
  m = v.match(/^color\(srgb ([^)]+)\)/);
  if (m) { const p = m[1].split(/[ \/]+/).map(Number); return 'rgb(' + p.slice(0, 3).map(x => Math.round(x * 255)).join(', ') + ')'; }
  return v;
}
function readTokens() {
  let pr = $('#probe'); if (!pr) { pr = document.createElement('span'); pr.id = 'probe'; pr.style.cssText = 'position:absolute;visibility:hidden;pointer-events:none'; document.body.append(pr); }
  const st = cs();
  C = {};
  COLOR_TOKENS.forEach(t => { pr.style.color = 'var(--' + t + ')'; C[camel(t)] = normColor(getComputedStyle(pr).color); });
  SIZE_TOKENS.forEach(t => { S[t] = parseFloat(st.getPropertyValue('--fs-' + t)); });
  ['display', 'body', 'mono'].forEach(k => { FONT[k] = st.getPropertyValue('--font-' + k).trim(); });
  ['display', 'body', 'strong'].forEach(k => { W[k] = st.getPropertyValue('--w-' + k).trim(); });
  ['radius-card', 'radius-inner', 'stroke', 'stroke-strong', 'icon-stroke'].forEach(k => { SH[camel(k)] = parseFloat(st.getPropertyValue('--' + k)); });
  return C;
}
/* dark-slide palette: the same names, read from the -on-dark tokens */
function pal(svg) {
  if (!svg.closest('.dark')) return { ...C, dark: false };
  return { ...C, dark: true, bg: C.bgDark, ink: C.inkOnDark, ink2: C.ink2OnDark, ink3: C.ink3OnDark, line: C.lineOnDark, lineStrong: C.lineStrongOnDark,
    accent: C.accentOnDark, positive: C.positiveOnDark, caution: C.cautionOnDark, negative: C.negativeOnDark, info: C.infoOnDark, surface: C.bgDark, surface2: C.lineOnDark,
    accentTint: C.lineOnDark, accentInk: C.accentOnDark };
}
/* colors and contrast */
const rgbOf = c => Array.isArray(c) ? c : (c.match(/[\d.]+/g) || [0, 0, 0]).slice(0, 3).map(Number);
const lum = c => { const [r, g, b] = rgbOf(c).map(v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }); return .2126 * r + .7152 * g + .0722 * b; };
const contrast = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
const mixc = (a, b, t) => { const p = rgbOf(a), q = rgbOf(b); return 'rgb(' + p.map((v, i) => Math.round(v + (q[i] - v) * t)).join(', ') + ')'; };
/* nearest passing value: move fg toward black or white until it reaches the ratio against bg */
function nearestPass(fg, bg, need) {
  const to = lum(bg) > .5 ? [0, 0, 0] : [255, 255, 255];
  for (let t = 0; t <= 1.001; t += .02) { const c = mixc(fg, to, t); if (contrast(c, bg) >= need) return c; }
  return to;
}
/* text measuring and wrapping (SVG text does not wrap) */
const _cv = document.createElement('canvas').getContext('2d'), _mc = {};
function measure(text, size, w = W.body, font = 'body', ls = 0) {
  const k = [text, size, w, font, ls, FONT[font]].join('|');
  if (_mc[k] === undefined) { _cv.font = w + ' ' + size + 'px ' + FONT[font]; _mc[k] = _cv.measureText(text).width + ls * size * text.length; }
  return _mc[k];
}
function wrap(text, maxW, o = {}) {
  const { size = S.body, w = W.body, font = 'body', ls = 0 } = o, out = []; let cur = '';
  String(text).split(/\s+/).forEach(word => {
    const t = cur ? cur + ' ' + word : word;
    if (cur && measure(t, size, w, font, ls) > maxW) { out.push(cur); cur = word; } else cur = t;
  });
  if (cur) out.push(cur);
  return out;
}
/* fit(): largest size at or above min whose wrapped text stays within maxLines */
function fit(text, maxW, o = {}) {
  const { max = S.card, min = 20, lines = 2 } = o;
  for (let s = max; s >= min; s -= 1) { const l = wrap(text, maxW, { ...o, size: s }); if (l.length <= lines) return { size: s, lines: l }; }
  return { size: min, lines: wrap(text, maxW, { ...o, size: min }) };
}
/* SVG primitives: parent first, every one returns the element */
const r2 = v => typeof v === 'number' ? Math.round(v * 100) / 100 : v;
function el(tag, at, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in at) if (at[k] !== undefined && at[k] !== null) e.setAttribute(k, r2(at[k]));
  if (parent) parent.append(e);
  return e;
}
const Gr = (p, at = {}) => el('g', at, p);
const R = (p, x, y, w, h, o = {}) => el('rect', { x, y, width: Math.max(w, 0), height: Math.max(h, 0), rx: o.rx, fill: o.fill || 'none', stroke: o.stroke, 'stroke-width': o.sw, 'stroke-dasharray': o.dash, 'fill-opacity': o.fo, opacity: o.op }, p);
const Ln = (p, x1, y1, x2, y2, o = {}) => el('line', { x1, y1, x2, y2, stroke: o.stroke || C.line, 'stroke-width': o.sw || 2, 'stroke-dasharray': o.dash, 'stroke-linecap': o.cap || 'round', opacity: o.op }, p);
const Ci = (p, cx, cy, r, o = {}) => el('circle', { cx, cy, r, fill: o.fill || 'none', stroke: o.stroke, 'stroke-width': o.sw, 'fill-opacity': o.fo, 'stroke-dasharray': o.dash, opacity: o.op }, p);
const Pa = (p, d, o = {}) => el('path', { d, fill: o.fill || 'none', stroke: o.stroke, 'stroke-width': o.sw, 'stroke-dasharray': o.dash, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'fill-opacity': o.fo, opacity: o.op, 'marker-end': o.marker }, p);
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
/* T: one line of text, y is the baseline. font is 'body' | 'display' | 'mono'; a is the anchor (start, middle, end) */
function T(p, x, y, text, o = {}) {
  const e = el('text', { x, y, 'font-size': o.size || S.body, 'font-weight': o.w || W.body, fill: o.fill || C.ink, 'text-anchor': o.a || 'start', 'letter-spacing': o.ls ? o.ls + 'em' : undefined, opacity: o.op,
    'font-family': FONT[o.font || 'body'], 'text-transform': o.caps ? 'uppercase' : undefined }, p);
  e.textContent = o.caps ? String(text).toUpperCase() : text;
  return e;
}
function TL(p, x, y, lines, o = {}) {
  const lh = o.lh || (o.size || S.body) * 1.28;
  return lines.map((l, i) => T(p, x, y + i * lh, l, o));
}
/* markers need unique ids per builder */
function arrowMarker(svg, id, color) {
  const d = svg.querySelector('defs') || el('defs', {}, svg);
  el('path', { d: 'M0 0L10 5L0 10z', fill: color }, el('marker', { id, viewBox: '0 0 10 10', refX: 8, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse' }, d));
  return 'url(#' + id + ')';
}
/* icons: ico(x, y, size) places the top-left, icoC centers. Icons are 24-unit line art in currentColor. */
function ico(p, name, x, y, size, color) {
  const g = Gr(p, { transform: 'translate(' + r2(x) + ' ' + r2(y) + ') scale(' + r2(size / 24) + ')', fill: 'none', stroke: color || C.ink, 'stroke-width': SH.iconStroke, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
  el('use', { href: '#i-' + name, width: 24, height: 24 }, g);
  return g;
}
const icoC = (p, name, cx, cy, size, color) => ico(p, name, cx - size / 2, cy - size / 2, size, color);
/* avatar: a real photo from PHOTO[key] (data URI or relative path), or initials on a tinted disc. The clip path id is unique per call: the cover and the closing slide both draw it, and a url(#id) must not point into a hidden slide. */
let AVN = 0;
function AV(p, key, name, cx, cy, r, ring) {
  const g = Gr(p);
  if (PHOTO[key]) {
    const id = 'av-' + key + '-' + (++AVN), cp = el('clipPath', { id }, g); Ci(cp, cx, cy, r);
    el('image', { href: PHOTO[key], x: cx - r, y: cy - r, width: 2 * r, height: 2 * r, 'clip-path': 'url(#' + id + ')', preserveAspectRatio: 'xMidYMid slice' }, g);
  } else {
    Ci(g, cx, cy, r, { fill: C.accentTint });
    T(g, cx, cy + r * .17, name.split(/\s+/).map(w => w[0]).join('').slice(0, 2), { size: r * .72, w: W.strong, fill: C.accentInk, a: 'middle' });
  }
  if (ring) Ci(g, cx, cy, r + 5, { stroke: C.photoRing, sw: 3 });
  return g;
}
/* scales and ticks */
const lin = (d0, d1, r0, r1) => v => r0 + (v - d0) / (d1 - d0) * (r1 - r0);
const symlog = v => Math.sign(v) * Math.log10(1 + Math.abs(v) / 10);
/* formatters: shares are fractions */
const MINUS = '−', WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve'];
const F = {
  int: v => Math.round(v).toLocaleString('en-US'),
  compact: v => v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : v >= 1e3 ? (v / 1e3).toFixed(1) + 'k' : String(Math.round(v)),
  pct0: v => Math.round(v * 100) + '%', pct1: v => (v * 100).toFixed(1) + '%',
  dec1: v => v.toFixed(1), dec2: v => v.toFixed(2), x1: v => v.toFixed(1) + '×',
  delta: v => (v < 0 ? MINUS : '+') + Math.abs(v), dur: v => v === 0 ? 'same day' : Math.abs(v) + ' days ' + (v < 0 ? 'before' : 'after'),
  absdays: v => Math.abs(v) + ' days', absmonths: v => Math.round(Math.abs(v) / 30.4) + ' months',
  approx: v => '≈' + Math.round(v), word: v => WORDS[v], Word: v => WORDS[v][0].toUpperCase() + WORDS[v].slice(1)
};
const dig = (o, path) => path.split('.').reduce((a, k) => (a == null ? a : a[k]), o);
/* {{dataset.path|fmt}}: the first segment is a DATA key, the rest is a path inside its values */
function resolve(str, issues) {
  return String(str).replace(/\{\{\s*([\w.]+)\s*(?:\|\s*(\w+))?\s*\}\}/g, (m, path, fmt) => {
    const [k, ...rest] = path.split('.'), v = DATA[k] && dig(DATA[k].values, rest.join('.'));
    if (v === undefined || v === null || (fmt && !F[fmt])) { if (issues) issues.push('unresolved ' + m); return m; }
    return fmt ? F[fmt](v) : String(v);
  });
}
/* deterministic random numbers for the motif */
const rng = seed => () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
/* generative motif: rings of small marks whose color shifts outward, with clear zones around text */
function drawMotif(svg, clear = []) {
  svg.textContent = '';
  const alpha = parseFloat(cs().getPropertyValue('--motif-alpha')), rand = rng(7), cx = 1500, cy = 560, g = Gr(svg, { 'data-breathe': 1, style: 'transform-origin:' + cx + 'px ' + cy + 'px' });
  for (let ring = 0; ring < 11; ring++) {
    const r = 150 + ring * 78, n = Math.round(r / 11), col = mixc(C.motifA, C.motifB, ring / 10);
    for (let i = 0; i < n; i++) {
      const a = i / n * Math.PI * 2 + ring * .21, x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r;
      if (x < 20 || x > 1900 || y < 20 || y > 1060 || clear.some(c => x > c.x0 && x < c.x1 && y > c.y0 && y < c.y1)) continue;
      const d = Ci(g, x, y, 3.4 + (10 - ring) * .42 + rand() * 1.2, { fill: col, fo: alpha });
      d.setAttribute('data-ring', ring);
    }
  }
}
function drawMarks(svg) {
  svg.textContent = ''; const rand = rng(3);
  for (let c = 0; c < 13; c++) for (let r = 0; r < 7; r++) Ci(svg, 10 + c * 41, 12 + r * 46, 5, { fill: 'currentColor', fo: .2 + rand() * .6 * (c / 12) });
}
/* footnote text generated from the dataset, never typed by hand */
function footParts(ds) {
  if (!ds || ds.kind === 'concept') return null;
  return { left: ds.formula || '', right: [ds.window && 'Window: ' + ds.window, ds.denominator && 'Denominator: ' + ds.denominator, ds.exclusions && 'Excluded: ' + ds.exclusions, ds.source && 'Source: ' + ds.source].filter(Boolean).join(' · ') };
}
const KIND = { counted: 'Counted', estimate: 'Estimate', illustrative: 'Illustrative', draft: 'Draft setting' };
