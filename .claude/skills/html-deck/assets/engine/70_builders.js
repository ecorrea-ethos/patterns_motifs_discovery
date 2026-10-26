
/* ===== 7. BUILDERS [ENGINE] ===== */
/* G.<name>(svg, dataset, options) draws one composition. Pure and idempotent: same inputs, same SVG. Colors come from C / pal() only.
   Library: rankedBars, lanes, pipeline, cards, treemap, layers, quadrant, askList. Deck-specific builders go in the deck's builders.js (section 7b). */
const G = { meta: {} };
const ZONE = { x0: 135, x1: 1785, y0: 316, y1: 946 };
const A = (e, k) => { e.setAttribute('data-anim', k); return e; };
const label = (g, x, y, text, w, o = {}) => { const f = fit(text, w, { max: o.max || S.body, min: 20, lines: o.lines || 2, w: o.w || W.strong }); TL(g, x, y, f.lines, { size: f.size, w: o.w || W.strong, fill: o.fill || C.ink, a: o.a, lh: f.size * 1.2 }); return f; };
const caps = (g, x, y, text, fill, a) => T(g, x, y, text, { size: S.axis, w: W.strong, fill, ls: .12, caps: true, a });

/* rankedBars: horizontal bars sorted by value, the first `top` highlighted, optional reference line and a callout card */
G.meta.rankedBars = { use: 'compare a few categories on one measure; the claim is that one or two lead', data: 'values.rows[{k, l?, v, hi?}], optional values.bar', limits: '2 to 8 rows', notes: 'o: head, note[], top (rows in accent, default 1, 0 for none; r.hi still marks single rows), together (word before the summed share), scale, ref, refLabel, fmt, pitch (row spacing in px, default min(104, 520 / rows); 60 keeps 7 rows above y 860 for a room band)' };
G.rankedBars = function (svg, ds, o) {
  svg.textContent = ''; const P = pal(svg), rows = ds.values.rows, fm = F[o.fmt || 'pct1'], top = o.top === undefined ? 1 : o.top;
  const bx = 600, bw = 520, y0 = 410, pitch = o.pitch || Math.min(104, 520 / rows.length), sc = o.scale || Math.max(...rows.map(r => r.v)) * 1.06, X = v => bx + v / sc * bw;
  if (o.head) caps(svg, ZONE.x0, 366, o.head, P.ink3);
  Ln(svg, bx, y0 - 14, bx, y0 + rows.length * pitch - 10, { stroke: P.lineStrong, sw: 2 });
  rows.forEach((r, i) => {
    const y = y0 + i * pitch, hi = i < top || r.hi, bh = 52, cy = y + bh / 2;
    T(svg, ZONE.x0, cy - (r.l ? 2 : -8), r.k, { size: S.body, w: W.strong, fill: P.ink });
    if (r.l) T(svg, ZONE.x0, cy + 26, r.l, { size: S.label, fill: P.ink2 });
    A(R(svg, bx, y, X(r.v) - bx, bh, { rx: 10, fill: hi ? P.accent : P.lineStrong }), 'x');
    T(svg, X(r.v) + 16, cy + 8, fm(r.v), { size: S.body, w: W.strong, fill: hi ? P.accentInk : P.ink2 });
  });
  if (o.ref !== undefined) {
    Ln(svg, X(o.ref), y0 - 30, X(o.ref), y0 + rows.length * pitch - 6, { stroke: P.ink2, sw: 2, dash: '2 8' });
    T(svg, X(o.ref), y0 - 40, o.refLabel || '', { size: S.axis, w: W.strong, fill: P.ink2, a: 'middle' });
  }
  if (o.note) {
    const nx = 1330, ny = y0 - 10, nh = Math.max(top * pitch + 30, 190), sum = rows.slice(0, top).reduce((a, r) => a + r.v, 0);
    if (top > 1) { const x = nx - 52, ya = y0 + 4, yb = y0 + (top - 1) * pitch + 48; Pa(svg, 'M' + (x - 14) + ' ' + ya + 'H' + x + 'V' + yb + 'H' + (x - 14), { stroke: P.lineStrong, sw: 2 }); Ln(svg, x, (ya + yb) / 2, nx, (ya + yb) / 2, { stroke: P.lineStrong, sw: 2 }); Ci(svg, nx, (ya + yb) / 2, 5, { fill: P.lineStrong }); }
    R(svg, nx, ny, ZONE.x1 - nx, nh, { rx: SH.radiusCard, fill: P.accentTint });
    let y = ny + 54;
    if (top > 1) { T(svg, nx + 28, y, (o.together || 'Together') + ' ' + fm(sum), { size: S.card, w: W.strong, fill: P.accentInk }); y += 44; }
    TL(svg, nx + 28, y, o.note, { size: S.body, fill: P.ink, lh: 32 });
  }
};

/* lanes: two swimlanes with the same stations; one station differs */
G.meta.lanes = { use: 'show that two cases share a start and diverge; the difference is the claim', data: 'values{lanes[{who,end,icon}], steps[2], stepIcons[2], same, later, bag}', limits: '2 lanes, 2 shared steps', notes: 'schematic, not a rate' };
G.lanes = function (svg, ds) {
  svg.textContent = ''; const P = pal(svg), v = ds.values, xs = [640, 1070, 1500], ys = [470, 745];
  R(svg, 520, 336, 650, 560, { rx: SH.radiusCard, stroke: P.lineStrong, sw: 2, dash: '2 10' });
  v.lanes.forEach((l, i) => {
    const cy = ys[i];
    R(svg, ZONE.x0, cy - 105, ZONE.x1 - ZONE.x0, 210, { rx: SH.radiusCard, fill: P.bgAlt });
    T(svg, ZONE.x0 + 30, cy + 10, l.who, { size: S.card, w: W.strong, fill: P.ink });
    Ln(svg, xs[0], cy, xs[1], cy, { stroke: P.accent, sw: 10 });
    Ln(svg, xs[1], cy, xs[2], cy, { stroke: P.accent, sw: 10, dash: '1 22' });
    T(svg, (xs[1] + xs[2]) / 2, cy - 22, v.later, { size: S.label, fill: P.ink2, a: 'middle' });
    [0, 1, 2].forEach(k => {
      const last = k === 2, ic = last ? l.icon : (v.stepIcons || [])[k] || 'spark', nm = last ? l.end : v.steps[k];
      Ci(svg, xs[k], cy, 48, { fill: last ? P.accent : P.surface, stroke: P.accent, sw: 6 });
      icoC(svg, ic, xs[k], cy, 48, last ? P.accentContrast : P.accent);
      T(svg, xs[k], cy + 96, nm, { size: S.body, w: W.strong, fill: P.ink, a: 'middle' });
    });
  });
  const my = (ys[0] + ys[1]) / 2 + 4, pw = measure(v.same, S.label, W.strong) + 44;
  R(svg, 845 - pw / 2, my - 24, pw, 48, { rx: 24, fill: P.surface, stroke: P.lineStrong, sw: 2 });
  T(svg, 845, my + 8, v.same, { size: S.label, w: W.strong, fill: P.ink, a: 'middle' });
  T(svg, 960, 930, v.bag, { size: S.body, fill: P.ink2, a: 'middle' });
};

/* pipeline: stations on one track under phase tabs. Under them, either a band of data rules tied to stations (values.band) or a picture card per station (stations[].art, a key of G.art) */
G.art = {};   /* G.art.name(g, x, y, w, h, P, svg) draws a small illustration inside a station card; write them in the deck's builders.js */
G.meta.pipeline = { use: 'a method as a short ordered chain, with rules that shape it or a picture per step', data: 'values{phases[{t,a,b,hot?}], stations[{t,d,i,hot?,art?}], band?[{at,t}], bandTitle?}', limits: '4 to 6 stations, 3 rules; titles about 15 characters, descriptions about 80', notes: 'stations spread evenly over the width: 330 px apart at 5, 275 px at 6; picture cards are 245 x 226 at 6 stations and use G.art; rules sit under their station, so rules on neighbouring stations must be short' };
G.pipeline = function (svg, ds) {
  svg.textContent = ''; const P = pal(svg), v = ds.values, n = v.stations.length, pitch = (ZONE.x1 - ZONE.x0) / n, cx = i => ZONE.x0 + pitch / 2 + i * pitch, ty = v.stations.some(s => s.art) ? 500 : 520;
  v.phases.forEach((p, i) => {
    const x = cx(p.a) - (pitch - 50) / 2, w = cx(p.b) - cx(p.a) + pitch - 50, hot = !!p.hot;
    R(svg, x, 368, w, 44, { rx: 22, fill: hot ? P.accent : P.accentTint });
    T(svg, x + w / 2, 398, p.t, { size: S.label, w: W.strong, fill: hot ? P.accentContrast : P.accentInk, a: 'middle', ls: .12, caps: true });
  });
  Ln(svg, cx(0), ty, cx(n - 1), ty, { stroke: P.line, sw: 12 });
  v.stations.forEach((s, i) => {
    const hot = !!s.hot;
    Ci(svg, cx(i), ty, 48, { fill: hot ? P.accent : P.surface, stroke: P.accent, sw: 6 });
    icoC(svg, s.i, cx(i), ty, 46, hot ? P.accentContrast : P.accent);
    const ft = fit(s.t, pitch - 20, { max: S.card, min: 24, lines: 1, w: W.strong });
    T(svg, cx(i), ty + 98, ft.lines.join(' '), { size: ft.size, w: W.strong, fill: P.ink, a: 'middle' });
    TL(svg, cx(i), ty + 134, wrap(resolve(s.d), pitch - 40, { size: S.label }), { size: S.label, fill: P.ink2, a: 'middle', lh: 28 });
  });
  v.stations.forEach((s, i) => {
    if (!s.art) return;
    const w = pitch - 30, x = cx(i) - w / 2, g = Gr(svg);
    R(g, x, 756, w, 226, { rx: SH.radiusCard, fill: P.bgAlt });
    G.art[s.art](g, x, 756, w, 226, P, svg);
  });
  if (!v.band) return;
  R(svg, ZONE.x0, 772, ZONE.x1 - ZONE.x0, 168, { rx: SH.radiusCard, fill: P.bgAlt });
  caps(svg, ZONE.x0 + 28, 806, v.bandTitle || 'Rules', P.ink3);
  v.band.forEach(b => {
    const bw = pitch - 30, x = cx(b.at) - bw / 2;
    Ln(svg, cx(b.at), ty + 214, cx(b.at), 828, { stroke: P.lineStrong, sw: 2, dash: '2 8' });
    R(svg, x, 828, bw, 100, { rx: SH.radiusInner, fill: P.surface, stroke: P.line, sw: 2 });
    TL(svg, x + 18, 862, wrap(b.t, bw - 34, { size: S.label }), { size: S.label, fill: P.ink, lh: 28 });
  });
};

/* cards: 3 to 4 parallel cards (icon zone, title, body, takeaway) */
G.meta.cards = { use: 'three or four parallel ideas of equal weight, such as definitions or limits', data: 'values.cards[{t, pos?, d, k, i}]', limits: '4 cards 390 x 620; body 6 lines or fewer', notes: 'keep all cards the same shape' };
G.cards = function (svg, ds) {
  svg.textContent = ''; const P = pal(svg), cards = ds.values.cards, cw = 390, gap = 30, y0 = 324, ch = 620, defs = el('defs', {}, svg);
  cards.forEach((c, i) => {
    const x = ZONE.x0 + i * (cw + gap), id = 'cards-clip-' + i, g = Gr(svg);
    R(el('clipPath', { id }, defs), x, y0, cw, ch, { rx: SH.radiusCard });
    R(g, x, y0, cw, ch, { rx: SH.radiusCard, fill: P.surface, stroke: P.line, sw: 2 });
    const z = Gr(g, { 'clip-path': 'url(#' + id + ')' }); R(z, x, y0, cw, 150, { fill: P.accentTint });
    Ci(g, x + cw / 2, y0 + 75, 52, { fill: P.accent }); icoC(g, c.i, x + cw / 2, y0 + 75, 52, P.accentContrast);
    const tf = fit(c.t, cw - 56, { max: S.card, min: 24, lines: 2, w: W.strong });
    TL(g, x + 28, y0 + 208, tf.lines, { size: tf.size, w: W.strong, fill: P.ink, lh: tf.size * 1.2 });
    let y = y0 + 208 + (tf.lines.length - 1) * tf.size * 1.2 + 34;
    if (c.pos) { T(g, x + 28, y, c.pos, { size: S.label, fill: P.ink3 }); y += 14; }
    TL(g, x + 28, y + 26, wrap(resolve(c.d), cw - 56, { size: S.body + 2 }), { size: S.body + 2, fill: P.ink2, lh: 34 });
    Ln(g, x + 28, y0 + ch - 128, x + cw - 28, y0 + ch - 128, { stroke: P.line, sw: 2 });
    TL(g, x + 28, y0 + ch - 88, wrap(c.k, cw - 56, { size: S.body + 2, w: W.strong }), { size: S.body + 2, w: W.strong, fill: P.accentInk, lh: 33 });
  });
};

/* treemap: area is the quantity; one tile highlighted */
G.meta.treemap = { use: 'parts of a whole when the claim is how big each part is and which one matters', data: 'values.rows[{id, name, n, pct}]', limits: '4 to 10 tiles', notes: 'squarified; o.highlight = row index' };
function squarify(items, x, y, w, h) {
  const out = [], sc = w * h / items.reduce((a, i) => a + i.v, 0); let rest = items.slice();
  const worst = (row, s, a) => { const ar = row.map(i => i.v * sc); return Math.max(s * s * Math.max(...ar) / (a * a), a * a / (s * s * Math.min(...ar))); };
  while (rest.length) {
    const s = Math.min(w, h); let row = [rest[0]], a = rest[0].v * sc, i = 1;
    while (i < rest.length) { const nr = row.concat(rest[i]), na = a + rest[i].v * sc; if (worst(nr, s, na) <= worst(row, s, a)) { row = nr; a = na; i++; } else break; }
    if (w >= h) { const cw = a / h; let cy = y; row.forEach(it => { const chh = it.v * sc / cw; out.push({ it, x, y: cy, w: cw, h: chh }); cy += chh; }); x += cw; w -= cw; }
    else { const rh = a / w; let cx = x; row.forEach(it => { const cw = it.v * sc / rh; out.push({ it, x: cx, y, w: cw, h: rh }); cx += cw; }); y += rh; h -= rh; }
    rest = rest.slice(row.length);
  }
  return out;
}
G.treemap = function (svg, ds, o) {
  svg.textContent = ''; const P = pal(svg), rows = ds.values.rows.map((r, i) => ({ ...r, i, v: r.n })).sort((a, b) => b.v - a.v);
  squarify(rows, ZONE.x0, 330, ZONE.x1 - ZONE.x0, 596).forEach(t => {
    const r = t.it, hot = r.i === o.highlight, x = t.x + 4, y = t.y + 4, w = t.w - 8, h = t.h - 8, g = Gr(svg);
    A(R(g, x, y, w, h, { rx: SH.radiusInner, fill: hot ? P.accent : P.surface2 }), 'fade');
    const ink = hot ? P.accentContrast : P.ink, f = fit(r.name, w - 40, { max: S.card, min: 22, lines: 4, w: W.strong });
    T(g, x + 20, y + 40, r.id, { size: S.label, w: W.strong, fill: hot ? P.accentContrast : P.ink2, ls: .12, caps: true });
    TL(g, x + 20, y + 80, f.lines, { size: f.size, w: W.strong, fill: ink, lh: f.size * 1.2 });
    T(g, x + w - 20, y + 40, F.int(r.n) + ' · ' + F.pct1(r.pct), { size: S.label, fill: ink, a: 'end' });
  });
};

/* layers: a composite rule over its parts and the atomic yes-or-no questions beneath */
G.meta.layers = { use: 'how a composite is built from parts and atomic predicates', data: 'values{top, join?, legend?, parts[{t, d, chips[]}]}', limits: '3 parts, up to 4 chips each', notes: 'AND pills between parts' };
G.layers = function (svg, ds) {
  svg.textContent = ''; const P = pal(svg), v = ds.values, parts = ds.values.parts, pw = 520, gap = 45, px = i => ZONE.x0 + i * (pw + gap);
  R(svg, 405, 332, 1110, 82, { rx: 41, fill: P.accent }); T(svg, 960, 384, ds.values.top, { size: S.card, w: W.strong, fill: P.accentContrast, a: 'middle' });
  parts.forEach((p, i) => {
    const x = px(i), cxm = x + pw / 2; Ln(svg, cxm, 414, cxm, 470, { stroke: P.accent, sw: 4 });
    R(svg, x, 470, pw, 170, { rx: SH.radiusCard, fill: P.accentTint });
    Ci(svg, x + 52, 524, 26, { fill: P.accent }); T(svg, x + 52, 534, String(i + 1), { size: S.card, w: W.strong, fill: P.accentContrast, a: 'middle' });
    T(svg, x + 96, 534, p.t, { size: S.card, w: W.strong, fill: P.accentInk });
    TL(svg, x + 28, 586, wrap(resolve(p.d), pw - 56, { size: S.body }), { size: S.body, fill: P.ink, lh: 30 });
    if (i < 2) { const ax = x + pw + gap / 2; R(svg, ax - 32, 540, 64, 38, { rx: 19, fill: P.surface, stroke: P.lineStrong, sw: 2 }); T(svg, ax, 566, v.join || 'AND', { size: S.axis, w: W.strong, fill: P.ink2, a: 'middle' }); }
    Ln(svg, cxm, 640, cxm, 690, { stroke: P.lineStrong, sw: 2, dash: '2 8' });
    const two = p.chips.length > 1 && p.chips.length <= 4 && p.chips.every(c => measure(c, S.label, W.strong) < 200);
    p.chips.forEach((c, k) => {
      const w = two ? (pw - 14) / 2 : pw, cx0 = x + (two ? (k % 2) * (w + 14) : 0), f = wrap(c, w - 28, { size: S.label, w: W.strong }), h = 26 * f.length + 30;
      const cy = two ? 696 + Math.floor(k / 2) * 80 : 696 + k * 92;
      R(svg, cx0, cy, w, h, { rx: SH.radiusInner, fill: P.surface, stroke: P.accent, sw: 2 });
      TL(svg, cx0 + 14, cy + 34, f, { size: S.label, w: W.strong, fill: P.ink, lh: 26 });
    });
  });
  if (v.legend) { R(svg, 160, 926, 20, 20, { rx: 5, fill: P.surface, stroke: P.accent, sw: 2 }); T(svg, 192, 944, v.legend, { size: S.label, fill: P.ink2 }); }
};

/* quadrant: an empty 2 x 2 with items waiting to be placed */
G.meta.quadrant = { use: 'a judgment grid the audience fills in', data: 'values{x[2], y[2], cells[4], hint, good?}; o.chips = key of a dataset whose values.rows[] have {id, name}', limits: '4 cells, up to 8 chips', notes: 'cells are TL, TR, BL, BR; good = index of the highlighted cell, default 1' };
G.quadrant = function (svg, ds, o) {
  svg.textContent = ''; const P = pal(svg), v = ds.values, gx = 640, gy = 340, gw = 1145, gh = 540, mk = arrowMarker(svg, 'quad-arrow', P.ink3);
  caps(svg, ZONE.x0, 350, v.hint, P.ink3);
  ((o.chips && DATA[o.chips].values.rows) || []).forEach((r, i) => {
    const y = 372 + i * 68, f = fit(r.id + '  ' + r.name, 350, { max: S.label, min: 20, lines: 2, w: W.strong });
    R(svg, ZONE.x0, y, 410, 58, { rx: 29, fill: P.surface, stroke: P.lineStrong, sw: 2 }); TL(svg, ZONE.x0 + 22, y + 35 - (f.lines.length - 1) * 11, f.lines, { size: f.size, w: W.strong, fill: P.ink, lh: f.size * 1.14 });
  });
  const cw = (gw - 12) / 2, ch = (gh - 12) / 2;
  v.cells.forEach((c, i) => {
    const x = gx + (i % 2) * (cw + 12), y = gy + Math.floor(i / 2) * (ch + 12), good = i === (v.good === undefined ? 1 : v.good);
    R(svg, x, y, cw, ch, { rx: SH.radiusCard, fill: good ? P.accentTint : P.bgAlt, stroke: good ? P.accent : P.line, sw: 2 });
    T(svg, x + 28, y + 52, c, { size: S.card, w: W.strong, fill: good ? P.accentInk : P.ink });
  });
  T(svg, gx, gy + gh + 44, v.x[0], { size: S.body, w: W.strong, fill: P.ink2 }); T(svg, gx + gw, gy + gh + 44, v.x[1], { size: S.body, w: W.strong, fill: P.ink2, a: 'end' });
  Ln(svg, gx + 360, gy + gh + 34, gx + gw - 280, gy + gh + 34, { stroke: P.ink3, sw: 3 }).setAttribute('marker-end', mk);
  const yy = (t, x, y) => { const e = T(svg, 0, 0, t, { size: S.label, w: W.strong, fill: P.ink2, a: 'middle' }); e.setAttribute('transform', 'translate(' + x + ' ' + y + ') rotate(-90)'); };
  yy(v.y[1], gx - 20, gy + ch / 2); yy(v.y[0], gx - 20, gy + ch + 12 + ch / 2);
};

/* askList: numbered questions with a one-word tag */
G.meta.askList = { use: 'the closing ask: a short numbered list of questions', data: 'values.rows[{q, t}]', limits: '3 to 6 rows', notes: 'question text uses the caption size' };
G.askList = function (svg, ds) {
  svg.textContent = ''; const P = pal(svg), rows = ds.values.rows, pitch = 118;
  rows.forEach((r, i) => {
    const y = 336 + i * pitch; Ln(svg, ZONE.x0, y, ZONE.x1, y, { stroke: P.line, sw: 2 });
    T(svg, ZONE.x0, y + 82, String(i + 1), { size: S.stat * .75, w: W.display, font: 'display', fill: P.accent });
    TL(svg, ZONE.x0 + 120, y + 52, wrap(r.q, 1180, { size: S.cap * .88 }), { size: S.cap * .88, fill: P.ink, lh: 42 });
    const w = measure(r.t, S.label, W.strong, 'body', .12) + 44; R(svg, ZONE.x1 - w, y + 36, w, 46, { rx: 23, fill: P.accentTint }); T(svg, ZONE.x1 - w / 2, y + 67, r.t, { size: S.label, w: W.strong, fill: P.accentInk, a: 'middle', ls: .12, caps: true });
  });
  Ln(svg, ZONE.x0, 336 + rows.length * pitch, ZONE.x1, 336 + rows.length * pitch, { stroke: P.line, sw: 2 });
};

