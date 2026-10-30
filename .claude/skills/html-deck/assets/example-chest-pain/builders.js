
/* ===== 7b. DECK BUILDERS [CONTENT] ===== */
/* Builders that only make sense for this deck's data. They use the engine helpers (ZONE, A, label, caps, pal, T, R, F, ...). */
/* ---- pipeline station pictures: G.art.name(g, x, y, w, h, P, svg), each drawn inside a 245 x 226 card ---- */
const person = (g, cx, cy, s, fill) => {
  Ci(g, cx, cy - s * .62, s * .36, { fill });
  Pa(g, 'M' + (cx - s * .6) + ' ' + (cy + s * .62) + 'V' + (cy + s * .25) + 'a' + (s * .6) + ' ' + (s * .6) + ' 0 0 1 ' + (s * 1.2) + ' 0V' + (cy + s * .62) + 'Z', { fill });
};
G.art.guideline = (g, x, y, w, h, P) => {
  const cx = x + w / 2, sx = cx - 52, sy = y + 40, sw = 112, sh = 164, hi = i => i === 2 || i === 3 || i === 5;
  R(g, sx - 14, sy - 14, sw, sh, { rx: 10, fill: P.surface, stroke: P.line, sw: 3 });
  Pa(g, 'M' + (sx + 10) + ' ' + sy + 'H' + (sx + sw - 30) + 'L' + (sx + sw) + ' ' + (sy + 30) + 'V' + (sy + sh - 10) + 'a10 10 0 0 1 -10 10H' + (sx + 10) + 'a10 10 0 0 1 -10 -10V' + (sy + 10) + 'a10 10 0 0 1 10 -10Z', { fill: P.surface, stroke: P.lineStrong, sw: 3 });
  Pa(g, 'M' + (sx + sw - 30) + ' ' + sy + 'V' + (sy + 30) + 'H' + (sx + sw) + 'Z', { fill: P.surface2, stroke: P.lineStrong, sw: 3 });
  R(g, sx + 16, sy + 24, 50, 12, { rx: 6, fill: P.accent });
  [86, 70, 86, 56, 86, 70, 46].forEach((lw, i) => R(g, sx + 16, sy + 56 + i * 15, lw, 7, { rx: 3.5, fill: hi(i) ? P.accent : P.line }));
  Ci(g, sx + sw - 6, sy + sh - 12, 24, { fill: P.accent, stroke: P.bgAlt, sw: 4 });
  icoC(g, 'check', sx + sw - 6, sy + sh - 12, 26, P.accentContrast);
};
G.art.cohort = (g, x, y, w, h, P) => {
  R(g, x + 16, y + 18, w - 32, h - 36, { rx: 22, stroke: P.accent, sw: 3, dash: '2 10' });
  for (let r = 0; r < 3; r++) for (let c = 0; c < 5; c++) person(g, x + w / 2 + (c - 2) * 38, y + 64 + r * 52, 24, P.accent);
};
G.art.bag = (g, x, y, w, h, P) => {
  const cx = x + w / 2, y0 = y + 82;
  [['heart', -62], ['flask', 0], ['box', 62]].forEach(([ic, dx], i) => {
    const cy = y + (i === 1 ? 32 : 44);
    Ln(g, cx + dx, cy + 22, cx + dx * .3, y0 - 4, { stroke: P.lineStrong, sw: 2, dash: '2 8' });
    Ci(g, cx + dx, cy, 22, { fill: P.surface, stroke: P.accent, sw: 4 }); icoC(g, ic, cx + dx, cy, 26, P.accent);
  });
  Pa(g, 'M' + (cx - 26) + ' ' + y0 + 'C' + (cx - 28) + ' ' + (y0 + 12) + ' ' + (cx - 96) + ' ' + (y0 + 14) + ' ' + (cx - 100) + ' ' + (y0 + 60) + 'C' + (cx - 104) + ' ' + (y0 + 98) + ' ' + (cx - 86) + ' ' + (y0 + 124) + ' ' + (cx - 60) + ' ' + (y0 + 130)
    + 'Q' + cx + ' ' + (y0 + 140) + ' ' + (cx + 60) + ' ' + (y0 + 130) + 'C' + (cx + 86) + ' ' + (y0 + 124) + ' ' + (cx + 104) + ' ' + (y0 + 98) + ' ' + (cx + 100) + ' ' + (y0 + 60) + 'C' + (cx + 96) + ' ' + (y0 + 14) + ' ' + (cx + 28) + ' ' + (y0 + 12) + ' ' + (cx + 26) + ' ' + y0 + 'Z', { fill: P.accentTint, stroke: P.accent, sw: 4 });
  R(g, cx - 34, y0 - 7, 68, 14, { rx: 7, fill: P.accent });
  [['Condition', 'Drug'], ['Procedure', 'Test']].forEach((row, r) => {
    const ws = row.map(t => measure(t, S.axis, W.strong) + 14); let px = cx - (ws[0] + ws[1] + 6) / 2;
    row.forEach((t, k) => { R(g, px, y0 + 44 + r * 40, ws[k], 32, { rx: 16, fill: P.surface, stroke: P.accent, sw: 2 }); T(g, px + ws[k] / 2, y0 + 67 + r * 40, t, { size: S.axis, w: W.strong, fill: P.ink, a: 'middle' }); px += ws[k] + 6; });
  });
};
G.art.clusters = (g, x, y, w, h, P) => {
  const rand = rng(11), cx = x + w / 2;
  [[cx - 50, y + 84, 44, P.accent, 9], [cx + 52, y + 64, 38, P.info, 7], [cx + 6, y + 164, 46, P.ink2, 10]].forEach(([mx, my, r, col, n]) => {
    Ci(g, mx, my, r, { fill: col, fo: .12, stroke: col, sw: 2, dash: '2 8' });
    for (let i = 0; i < n; i++) { const a = rand() * Math.PI * 2, d = Math.sqrt(rand()) * (r - 12); Ci(g, mx + Math.cos(a) * d, my + Math.sin(a) * d, 6.5, { fill: col }); }
  });
};
G.art.sequence = (g, x, y, w, h, P, svg) => {
  const mk = arrowMarker(svg, 'pipe-arrow', P.accent), pts = [[x + 40, y + 190], [x + 98, y + 138], [x + 156, y + 86], [x + 214, y + 34]], ics = ['heart', 'pulse', 'search', 'flask'];
  pts.slice(0, 3).forEach((p, i) => {
    const q = pts[i + 1], dx = q[0] - p[0], dy = q[1] - p[1], d = Math.hypot(dx, dy), a = 23 / d, b = (d - 23) / d;
    Ln(g, p[0] + dx * a, p[1] + dy * a, p[0] + dx * b, p[1] + dy * b, { stroke: P.accent, sw: 3 }).setAttribute('marker-end', mk);
  });
  pts.forEach((p, i) => { const last = i === 3; Ci(g, p[0], p[1], 18, { fill: last ? P.accent : P.surface, stroke: P.accent, sw: 4 }); icoC(g, ics[i], p[0], p[1], 20, last ? P.accentContrast : P.accent); });
};
G.art.pubmed = (g, x, y, w, h, P) => {
  const plate = lum(C.bg) > .5 ? C.surface : C.ink, lw = w - 56, lh = lw * 68.8 / 202.3;
  R(g, x + 14, y + 58, w - 28, 110, { rx: 14, fill: plate, stroke: P.line, sw: 2 });
  el('image', { href: PHOTO.pubmed, x: x + 28, y: y + 113 - lh / 2, width: lw, height: lh, preserveAspectRatio: 'xMidYMid meet' }, g);
};

/* seqStrip: ordered sequences as chains, with in-group vs rest bars and the ratio */
G.meta.seqStrip = { use: 'show ordered steps and how much more common they are inside a group than outside', data: 'values.rows[i].seqs[{steps[], inB, out, lift, verdict, order}]', limits: '3 sequences, 5 steps', notes: 'o.i = row index; dark-slide aware' };
G.seqStrip = function (svg, ds, o) {
  svg.textContent = ''; const P = pal(svg), b = ds.values.rows[o.i], mk = arrowMarker(svg, 'seqstrip-arrow', P.ink3), bx = ZONE.x0, bw = 760, sc = .72;
  b.seqs.forEach((s, r) => {
    const y = 336 + r * 178; let x = bx;
    s.steps.forEach((st, k) => {
      const w = measure(st, S.body, W.strong) + 40;
      R(svg, x, y, w, 62, { rx: 31, fill: k === 0 ? P.surface2 : 'none', stroke: k === 0 ? P.surface2 : P.accent, sw: 3 });
      T(svg, x + w / 2, y + 40, st, { size: S.body, w: W.strong, fill: P.ink, a: 'middle' });
      x += w; if (k < s.steps.length - 1) { Ln(svg, x + 4, y + 31, x + 34, y + 31, { stroke: P.ink3, sw: 3 }).setAttribute('marker-end', mk); x += 38; }
    });
    [['inB', P.accent, 'inside the pattern', 84], ['out', P.lineStrong, 'everyone else', 124]].forEach(([k, col, txt, dy]) => {
      A(R(svg, bx, y + dy - 6, s[k] / sc * bw, 26, { rx: 6, fill: col }), 'x');
      const vx = bx + s[k] / sc * bw + 16; T(svg, vx, y + dy + 16, F.pct0(s[k]), { size: S.body, w: W.strong, fill: P.ink });
      T(svg, vx + measure(F.pct0(s[k]), S.body, W.strong) + 12, y + dy + 16, txt, { size: S.label, fill: P.ink2 });
    });
    T(svg, 1560, y + 92, F.x1(s.lift), { size: S.stat, w: W.display, font: 'display', fill: P.accent });
    T(svg, 1560, y + 128, 'as common', { size: S.label, fill: P.ink2 });
    if (r < 2) Ln(svg, bx, y + 160, ZONE.x1, y + 160, { stroke: P.line, sw: 1.5 });
  });
  Ci(svg, ZONE.x0 + 8, 898, 7, { fill: P.caution });
  T(svg, ZONE.x0 + 30, 906, 'All three hold in validation, but every step is same-day: the order is a tie-break, not clock time.', { size: S.body, fill: P.ink });
};

/* timeline: dot plot of median days against an anchor event, one row per group; zero is the anchor */
G.meta.timeline = { use: 'when events happen relative to an anchor, across groups', data: 'values.rows[{id, name, ents[{k, med}]}]', limits: '4 to 10 rows, 3 to 6 dots', notes: 'compressed (symlog) axis; o.highlight/o.also rows in accent; o.pitch row spacing (default 64); o.window shades the draft window around day zero (width from DATA.rule.values.windowDays)' };
G.timeline = function (svg, ds, o) {
  svg.textContent = ''; const P = pal(svg), rows = ds.values.rows, x0 = 600, x1 = 1740, s0 = symlog(-250), s1 = symlog(190), X = d => lin(s0, s1, x0, x1)(symlog(d)), y0 = 384, pitch = o.pitch || 64, ticks = [-180, -90, -30, 0, 30, 90, 180], win = o.window ? DATA.rule.values.windowDays : 0;
  if (win) A(R(svg, X(-win), y0 - 10, X(win) - X(-win), rows.length * pitch + 2, { fill: P.accentTint, stroke: P.accent, sw: 2 }), 'fade');
  ticks.forEach(t => { Ln(svg, X(t), y0 - 10, X(t), y0 + rows.length * pitch - 8, { stroke: t ? P.line : P.ink2, sw: t ? 1.5 : 2, dash: t ? undefined : '2 8' }); T(svg, X(t), y0 + rows.length * pitch + 26, t ? F.delta(t) : '0', { size: S.axis, fill: P.ink3, a: 'middle' }); });
  T(svg, X(0), y0 - 20, win ? 'first chest pain · shaded: ' + F.word(win) + '-day window' : 'first chest pain', { size: S.axis, w: W.strong, fill: P.ink2, a: 'middle' });
  T(svg, ZONE.x0, y0 + rows.length * pitch + 26, 'Days (compressed scale)', { size: S.axis, fill: P.ink3 });
  rows.forEach((r, i) => {
    const cy = y0 + i * pitch + pitch / 2 - 10, hot = i === o.highlight || i === o.also, g = Gr(svg);
    const f = fit(r.id + '  ' + r.name, 420, { max: S.label, min: 20, lines: 2, w: hot ? W.strong : W.body }); TL(g, ZONE.x0, cy - 2 - (f.lines.length - 1) * 11, f.lines, { size: f.size, w: hot ? W.strong : W.body, fill: hot ? P.ink : P.ink2, lh: f.size * 1.18 });
    const seen = {}; r.ents.forEach(e => { const k = seen[e.med] = (seen[e.med] || 0) + 1, n = r.ents.filter(q => q.med === e.med).length;
      A(Ci(g, X(e.med), cy + (k - 1 - (n - 1) / 2) * 7, 9, { fill: hot ? P.accent : P.lineStrong, stroke: P.bg, sw: 2 }), 'fade'); });
    if (hot) { const m = r.ents.map(e => e.med).sort((a, b) => a - b)[2]; T(g, X(0) + 30, cy + 7, 'Middle event: ' + F.dur(m), { size: S.label, w: W.strong, fill: P.accentInk }); }
  });
};

/* verdictGrid: one cell per ordered sequence, colored by verdict, with the ratio inside */
G.meta.verdictGrid = { use: 'a status for every item of a small matrix, with a legend that carries the counts', data: 'values.rows[].seqs[{verdict, lift, order}]; counts from DATA.verdicts', limits: '8 rows x 3 columns', notes: 'verdict words sit inside the cell so color is never alone' };
G.verdictGrid = function (svg, ds) {
  svg.textContent = ''; const P = pal(svg), V = DATA.verdicts.values, rows = ds.values.rows, cx = 640, cw = 360, gap = 12, y0 = 446, pitch = 58;
  const role = { Solid: [P.positiveTint, P.positive, P.positiveInk], Suggestive: [P.infoTint, P.info, P.infoInk], Unstable: [P.negativeTint, P.negative, P.negativeInk] };
  [['Solid', V.solid, 'holds; order shows in dates'], ['Suggestive', V.suggestive, 'holds; steps are same-day'], ['Unstable', V.unstable, 'does not hold']].forEach(([k, n, d], i) => {
    const x = ZONE.x0 + i * 560; R(svg, x, 336, 28, 28, { rx: 6, fill: role[k][0], stroke: role[k][1], sw: 3 });
    T(svg, x + 44, 360, n + ' ' + k, { size: S.body, w: W.strong, fill: P.ink }); T(svg, x + 44 + measure(n + ' ' + k, S.body, W.strong) + 12, 360, d, { size: S.label, fill: P.ink2 });
  });
  ['Top by lift', 'Second', 'Third'].forEach((t, i) => caps(svg, cx + i * (cw + gap) + 18, y0 - 14, t, P.ink3));
  rows.forEach((r, i) => {
    const y = y0 + i * pitch, f = fit(r.id + '  ' + r.name, 480, { max: S.label, min: 20, lines: 2, w: W.body }); TL(svg, ZONE.x0, y + 28 - (f.lines.length - 1) * 11, f.lines, { size: f.size, fill: P.ink, lh: f.size * 1.18 });
    r.seqs.forEach((s, k) => {
      const x = cx + k * (cw + gap), c = role[s.verdict];
      A(R(svg, x, y, cw, pitch - 10, { rx: SH.radiusInner, fill: c[0], stroke: c[1], sw: 2 }), 'fade');
      T(svg, x + 18, y + 34, s.verdict, { size: S.label, w: W.strong, fill: c[2] }); T(svg, x + 170, y + 34, F.x1(s.lift), { size: S.label, w: W.strong, fill: P.ink });
      T(svg, x + cw - 18, y + 34, s.order === 'same-day' ? 'same day' : 'dated order', { size: S.axis, fill: P.ink2, a: 'end' });
    });
  });
};

/* bundleCard: one backup page for a group: identity, five main events with timing, three sequences with verdicts */
G.meta.bundleCard = { use: 'a backup page that shows one group in full', data: 'values.rows[i]: n, pct, ents[5], seqs[3]', limits: '5 events, 3 sequences', notes: 'o.i = row index' };
G.bundleCard = function (svg, ds, o) {
  svg.textContent = ''; const P = pal(svg), b = ds.values.rows[o.i], vc = { Solid: P.positive, Suggestive: P.info, Unstable: P.negative };
  R(svg, ZONE.x0, 330, 420, 610, { rx: SH.radiusCard, fill: P.accentTint });
  T(svg, ZONE.x0 + 32, 450, b.id, { size: S.big, w: W.display, font: 'display', fill: P.accent });
  const f = fit(b.name, 356, { max: S.card, min: 24, lines: 4, w: W.strong }); TL(svg, ZONE.x0 + 32, 508, f.lines, { size: f.size, w: W.strong, fill: P.accentInk, lh: f.size * 1.2 });
  T(svg, ZONE.x0 + 32, 760, F.int(b.n), { size: S.stat, w: W.display, font: 'display', fill: P.ink });
  T(svg, ZONE.x0 + 32, 800, 'applicants', { size: S.label, fill: P.ink2 }); T(svg, ZONE.x0 + 32, 870, F.pct1(b.pct), { size: S.card, w: W.strong, fill: P.accentInk }); T(svg, ZONE.x0 + 32, 906, 'of the cohort', { size: S.label, fill: P.ink2 });
  caps(svg, 600, 350, 'Five main events', P.ink3); caps(svg, 1210, 350, 'Three top sequences', P.ink3);
  b.ents.forEach((e, i) => {
    const y = 380 + i * 104; label(svg, 600, y + 26, e.k, 540, { lines: 1 });
    A(R(svg, 600, y + 40, e.share * 420, 18, { rx: 5, fill: P.accent }), 'x'); T(svg, 600 + e.share * 420 + 12, y + 56, F.pct0(e.share) + ' of the pattern', { size: S.label, fill: P.ink2 });
    T(svg, 600, y + 90, F.dur(e.med) + (e.med ? '' : ' as first chest pain'), { size: S.label, fill: P.ink3 });
  });
  b.seqs.forEach((s, i) => {
    const y = 380 + i * 182; Ln(svg, 1210, y - 14, ZONE.x1, y - 14, { stroke: P.line, sw: 1.5 });
    const f2 = fit(s.steps.join(' → '), 560, { max: S.body, min: 22, lines: 3, w: W.strong }); TL(svg, 1210, y + 24, f2.lines, { size: f2.size, w: W.strong, fill: P.ink, lh: f2.size * 1.22 });
    T(svg, 1210, y + 114, F.pct0(s.inB) + ' inside · ' + F.pct0(s.out) + ' elsewhere · ' + F.x1(s.lift) + ' as common', { size: S.label, fill: P.ink2 });
    const w = measure(s.verdict, S.axis, W.strong, 'body', .06) + 30; R(svg, 1210, y + 130, w, 32, { rx: 16, fill: vc[s.verdict] });
    T(svg, 1210 + w / 2, y + 153, s.verdict, { size: S.axis, w: W.strong, fill: P.bg, a: 'middle', ls: .06 });
    T(svg, 1210 + w + 14, y + 153, s.order === 'same-day' ? 'same-day steps' : 'order shows in dates', { size: S.axis, fill: P.ink3 });
  });
};

/* chipField: an inventory in labelled panels; a chip's weight shows how many groups use it */
G.meta.chipField = { use: 'a whole inventory on one page, grouped, with reuse visible', data: 'values.families[{id, name, n, items[{k, n}]}]; ids lab, proc left to right on top, dx, drug below', limits: 'about 40 chips in 4 panels, names up to 30 characters', notes: 'chips with n >= 2 carry a times-n tag and the accent tint; the most used is filled; ends above y 860' };
G.chipField = function (svg, ds) {
  svg.textContent = ''; const P = pal(svg), fam = ds.values.families, by = id => fam.find(f => f.id === id), top = Math.max(...fam.flatMap(f => f.items.map(i => i.n)));
  const PW = 805, GAP = 40, CH = 38, PITCH = 46, SZ = S.axis, X = [ZONE.x0, ZONE.x0 + PW + GAP];
  const flow = f => { let cx = 0, cy = 0; const out = f.items.map(it => { const txt = it.k + (it.n > 1 ? '  ×' + it.n : ''), w = Math.ceil(measure(txt, SZ, W.strong)) + 30;
      if (cx + w > PW) { cx = 0; cy += PITCH; } const r = { it, txt, w, x: cx, y: cy }; cx += w + 10; return r; }); return { out, h: cy + CH }; };
  const panel = (f, x, y) => { const L = flow(f); caps(svg, x, y, f.name + ' · ' + f.n, P.ink3); Ln(svg, x, y + 14, x + PW, y + 14, { stroke: P.line, sw: 2 });
    L.out.forEach(c => { const hot = c.it.n === top, mid = c.it.n > 1, cy = y + 34 + c.y;
      A(R(svg, x + c.x, cy, c.w, CH, { rx: CH / 2, fill: hot ? P.accent : mid ? P.accentTint : P.surface2, stroke: hot || mid ? P.accent : P.line, sw: 2 }), 'fade');
      T(svg, x + c.x + 15, cy + 26, c.txt, { size: SZ, w: W.strong, fill: hot ? P.accentContrast : mid ? P.accentInk : P.ink }); });
    return 34 + L.h; };
  const y1 = 346, h1 = Math.max(panel(by('lab'), X[0], y1), panel(by('proc'), X[1], y1)), y2 = y1 + h1 + 46;
  panel(by('dx'), X[0], y2); panel(by('drug'), X[1], y2);
};

/* gapTable: numbered findings with the evidence and the question for the room side by side */
G.meta.gapTable = { use: 'a numbered list of findings with the evidence and one open question each', data: 'values.cols[3], values.rows[{t, e, q}]', limits: '5 to 8 rows; evidence about 120 characters, question about 60', notes: 'each cell fits in two lines; the last column is tinted; optional rows[].g puts a small group label under a one-line title' };
G.gapTable = function (svg, ds) {
  svg.textContent = ''; const P = pal(svg), v = ds.values, rows = v.rows, gx = 35, cw = [372, 700, 508], xs = [ZONE.x0, ZONE.x0 + cw[0] + gx, ZONE.x0 + cw[0] + cw[1] + 2 * gx], pitch = Math.min(70, 540 / rows.length), y0 = 372;
  v.cols.forEach((c, i) => caps(svg, xs[i] + (i === 2 ? 20 : 0), 344, c, P.ink3)); Ln(svg, ZONE.x0, 358, ZONE.x1, 358, { stroke: P.lineStrong, sw: 2 });
  rows.forEach((r, i) => {
    const y = y0 + i * pitch, cy = y + pitch / 2, g = Gr(svg);
    if (i) Ln(g, ZONE.x0, y, ZONE.x1, y, { stroke: P.line, sw: 1.5 });
    R(g, xs[2], y + 5, cw[2], pitch - 10, { rx: SH.radiusInner, fill: P.accentTint });
    Ci(g, ZONE.x0 + 20, cy, 20, { fill: P.accent }); T(g, ZONE.x0 + 20, cy + 8, String(i + 1), { size: S.label, w: W.strong, fill: P.accentContrast, a: 'middle' });
    const cell = (x, w, text, max, wt, fill, dy = 0) => { const f = fit(resolve(text), w, { max, min: 20, lines: 2, w: wt }), lh = f.size * 1.2; TL(g, x, cy + dy + f.size * .32 - (f.lines.length - 1) * lh / 2, f.lines, { size: f.size, w: wt, fill, lh }); };
    if (r.g) caps(g, ZONE.x0 + 54, cy + 25, r.g, P.ink3);
    cell(ZONE.x0 + 54, cw[0] - 54, r.t, S.body, W.strong, P.ink, r.g ? -12 : 0);
    cell(xs[1], cw[1], r.e, S.label, W.body, P.ink);
    cell(xs[2] + 20, cw[2] - 40, r.q, S.label, W.strong, P.accentInk);
    A(g, 'fade');
  });
};

