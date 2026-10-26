
/* ===== 7b. DECK BUILDERS [CONTENT] ===== */
/* Builders that only make sense for this deck's data. They use the engine helpers (ZONE, A, label, caps, pal, T, R, F, ...). */
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
  T(svg, ZONE.x0 + 30, 906, 'All three hold on held-out halves, but every step is same-day: the order is a tie-break, not clock time.', { size: S.body, fill: P.ink });
};

/* timeline: dot plot of median days against an anchor event, one row per group; zero is the anchor */
G.meta.timeline = { use: 'when events happen relative to an anchor, across groups', data: 'values.rows[{id, name, ents[{k, med}]}]', limits: '4 to 10 rows, 3 to 6 dots', notes: 'compressed (symlog) axis; o.highlight/o.also rows in accent' };
G.timeline = function (svg, ds, o) {
  svg.textContent = ''; const P = pal(svg), rows = ds.values.rows, x0 = 600, x1 = 1740, s0 = symlog(-250), s1 = symlog(190), X = d => lin(s0, s1, x0, x1)(symlog(d)), y0 = 384, pitch = 64, ticks = [-180, -90, -30, 0, 30, 90, 180];
  ticks.forEach(t => { Ln(svg, X(t), y0 - 10, X(t), y0 + rows.length * pitch - 8, { stroke: t ? P.line : P.ink2, sw: t ? 1.5 : 2, dash: t ? undefined : '2 8' }); T(svg, X(t), y0 + rows.length * pitch + 26, t ? F.delta(t) : '0', { size: S.axis, fill: P.ink3, a: 'middle' }); });
  T(svg, X(0), y0 - 20, 'first chest pain', { size: S.axis, w: W.strong, fill: P.ink2, a: 'middle' });
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
