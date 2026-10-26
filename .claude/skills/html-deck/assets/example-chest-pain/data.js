/* ===== 5. DATA [CONTENT] ===== */
/* The ONLY place numbers live. Text, notes and aria-labels cite them as {{dataset.path|fmt}}. Shares are fractions (0 to 1). */
const DECK = { name: 'Chest pain as care patterns', people: [{ key: 'ec', name: 'Esteban Correa', role: 'Bioinformatic Scientist MRN' }, { key: 'zm', name: 'Zack Moore', role: 'Product Performance Actuary Lead' }] };
const PHOTO = /*INJECT:photo*/{};   // key -> photo as a data URI (scripts/photo_to_datauri.py) or a relative path; a missing key means an initials avatar
const SRC = 'Guideline-list run, final_table_chestpain_k8_AHA.xlsx';
const DATA = {
  cohort: { id: 'cohort', title: 'Chest pain cohort', unit: 'applicants', kind: 'counted', window: 'full history of each applicant',
    denominator: '139,416 applicants with a chest pain code', exclusions: 'none beyond the cohort rule',
    source: SRC, formula: '', values: { n: 139416, patterns: 8, codes: 5, sequences: 24, perPattern: 3, heldRuns: 40 } },
  icd: { id: 'icd', title: 'Chest pain codes', unit: 'share of applicants', kind: 'counted', window: 'earlier extract, full history',
    denominator: '150,368 applicants with chest pain reported', exclusions: 'none stated', source: 'Atypical Chest Pain - Insights report',
    formula: 'applicants with the code ÷ applicants with chest pain reported',
    values: { n: 150368, top2: 0.906, rows: [
      { k: 'R07.89', l: 'Other chest pain', v: 0.481 }, { k: 'R07.9', l: 'Chest pain, unspecified', v: 0.425 }, { k: 'R07.2', l: 'Precordial pain', v: 0.065 },
      { k: 'R07.8', l: 'Other chest pain', v: 0.018 }, { k: 'R07.82', l: 'Intercostal pain', v: 0.011 }] } },
  pair: { id: 'pair', title: 'Two applicants with the same codes', unit: '', kind: 'illustrative', window: '', denominator: 'two applicants, no rate', exclusions: '', source: 'Atypical Chest Pain - Insights report', formula: '',
    values: { same: 'Same codes so far', stepIcons: ['heart', 'pulse'], lanes: [{ who: 'Applicant A', end: 'Anxiety diagnosis', icon: 'message' }, { who: 'Applicant B', end: 'Troponin test', icon: 'flask' }], steps: ['Chest pain', 'Electrocardiogram'], later: 'Later', bag: 'In a bag of codes the two records are identical.' } },
  method: { id: 'method', title: 'Method', unit: '', kind: 'concept', values: {
    phases: [{ t: 'Prepare', a: 0, b: 2 }, { t: 'Find', a: 3, b: 4, hot: true }, { t: 'Check', a: 5, b: 5 }],
    stations: [
      { t: 'Guideline', d: 'A language model reads the guideline and writes the code lists', i: 'file', art: 'guideline' },
      { t: 'Applicants', d: '{{cohort.n|int}} applicants with a chest pain code, and all their records', i: 'users', art: 'cohort' },
      { t: 'Bag of codes', d: 'Each applicant becomes one list of coded events', i: 'box', art: 'bag' },
      { t: 'Care patterns', d: '{{cohort.patterns}} groups of frequent codes that travel together, kept if stable', i: 'layers', hot: true, art: 'clusters' },
      { t: 'Sequences', d: 'Ordered steps around chest pain, top {{cohort.perPattern}} per pattern, validated on unseen halves', i: 'branch', hot: true, art: 'sequence' },
      { t: 'Literature', d: 'A language model searches PubMed for published support', i: 'search', art: 'pubmed' }] } },
  terms: { id: 'terms', title: 'Terms', unit: '', kind: 'concept', values: { cards: [
    { t: 'Care pattern', pos: 'noun', d: 'A group of codes that tend to appear together in the same applicants\' records.', k: 'Describes care delivered, not diagnosis.', i: 'layers' },
    { t: 'Sequence', pos: 'noun', d: 'Codes in the order they appear around chest pain. We keep the top {{cohort.perPattern}} per pattern.', k: 'Same-day steps have no true order.', i: 'branch' },
    { t: 'Times as common', pos: 'noun phrase', d: 'Share of the pattern\'s applicants with a sequence, divided by the share among everyone else.', k: 'Specific to a pattern, not necessarily important.', i: 'chart-bar' },
    { t: 'Validation', pos: 'noun', d: 'We re-test each sequence on a random half the pattern was not built from, {{cohort.heldRuns}} times.', k: 'Repeatable is not the same as clinically true.', i: 'refresh' }] } },
  patterns: { id: 'patterns', title: 'Care patterns, entities and top sequences', unit: 'applicants', kind: 'counted', window: 'full history of each applicant',
    denominator: '139,416 applicants, each in their dominant pattern', exclusions: 'visits removed, refills collapsed',
    source: SRC, formula: 'times as common = (share inside + 0.01) ÷ (share outside + 0.01)',
    values: { total: 139416, rows: /*INJECT:rows*/[] } },
  timing: { id: 'timing', title: 'Timing against first chest pain', unit: 'days', kind: 'counted', window: 'first occurrence of each event',
    denominator: 'pattern applicants with both chest pain and the event', exclusions: 'repeats read at first occurrence, so a test can look early',
    source: SRC, formula: 'median days from first chest pain to first occurrence of the event', values: { rows: null } },
  stability: { id: 'stability', title: 'Re-run stability', unit: 'agreement, 0 to 1', kind: 'counted', window: '{{stability.resamples}} resamples of the same applicants',
    denominator: 'same 139,416 applicants in all three runs', exclusions: 'none', source: 'sanity_check_AHA.md',
    formula: 'adjusted Rand index between each resample and the base fit, averaged',
    values: { bar: 0.75, resamples: 10, rows: [{ k: 'Guideline lists, 8 patterns', v: 0.88, hi: true }, { k: 'Own lists, 5 patterns', v: 0.77 }, { k: 'Own lists, 8 patterns', v: 0.71 }] } },
  psych: { id: 'psych', title: 'Psychiatric evidence before troponin', unit: 'share of applicants', kind: 'counted', window: 'first occurrence of each, full history',
    denominator: '27,042 applicants with both a psychiatric code and a troponin test', exclusions: 'antidepressants and sedatives not counted as psychiatric evidence',
    source: 'Guideline-list run, timing cell, all patterns pooled', formula: 'first psychiatric code earlier than first troponin ÷ applicants with both',
    values: { n: 27042, first: 0.572, same: 0.074, tropFirst: 0.354, medianDays: 108 } },
  verdicts: { id: 'verdicts', title: 'Validation verdicts of the 24 sequences', unit: 'sequences', kind: 'counted', window: '{{cohort.heldRuns}} runs per pattern: random half splits',
    denominator: '24 sequences, top 3 per pattern with chest pain', exclusions: 'sequences without chest pain',
    source: SRC, formula: 'pass = support ≥ 10% on the unseen half and lower 95% bound of the odds ratio ≥ 2',
    values: { total: 24, solid: 11, suggestive: 7, unstable: 6, hold: 18, bar: 0.7 } },
  limits: { id: 'limits', title: 'Limits of a code', unit: '', kind: 'concept', values: { sameDay: 8, total: 24, cards: [
    { t: 'A code shows a test, not its result', d: 'Troponin is present or absent. Its level and the electrocardiogram reading are not in the data.', k: 'We cannot tell normal from abnormal.', i: 'eye' },
    { t: 'Many codes are generic', d: 'A blood draw, a general examination and a lipid panel appear at most check-ups. Troponin type is not shown.', k: 'Some events say little alone.', i: 'layers' },
    { t: 'Same-day order is a rule', d: 'Claims carry dates, not times. {{limits.sameDay}} of {{limits.total}} sequences happen mostly on one day.', k: 'Read them as sets, not steps.', i: 'clock' },
    { t: 'Patterns are care, not diagnosis', d: 'We hold no confirmed cardiac outcome to test against. A missing code is not proof of absence.', k: 'Nothing here is validated against outcomes.', i: 'target' }] } },
  rule: { id: 'rule', title: 'From pattern to rule', unit: '', kind: 'draft', window: '', denominator: '', exclusions: '', source: 'Atypical Chest Pain - Insights report', formula: 'pattern rule = chest pain AND entities rule AND sequence rule',
    values: { legend: "Each box at the bottom is one yes-or-no question about an applicant's records.", windowDays: 1, minEntities: 3, entityCount: 4, sequences: 3, top: 'Emergency work-up rule: true when all three parts are true', parts: [
      { t: 'Chest pain present', d: 'At least one chest pain event', chips: ['Chest pain diagnosis'] },
      { t: 'Entities in the window', d: '{{rule.minEntities}} or more of {{rule.entityCount}} events within {{rule.windowDays}} day of chest pain', chips: ['Troponin test', 'Intravenous push', 'Lipase test', 'Chest X-ray'] },
      { t: 'An ordered sequence', d: 'Any one of {{rule.sequences}} sequences, steps in order', chips: ['Chest pain → chest X-ray → troponin → metabolic panel', 'Chest pain → electrocardiogram → troponin → metabolic panel', 'Chest pain → troponin → metabolic panel → blood count'] }] } },
  quad: { id: 'quad', title: 'Validation grid', unit: '', kind: 'concept', values: { x: ['Database correlation', 'Clinically real'], y: ['No change to review', 'Changes the review'],
    cells: ['Looks useful, may only correlate', 'Real and useful for underwriting', 'Correlation only', 'Real, not for underwriting'], hint: 'Patterns to place' } },
  asks: { id: 'asks', title: 'Questions', unit: '', kind: 'concept', values: { rows: [
    { q: 'Which patterns describe a real cardiac work-up, and which are routine care that only sits next to chest pain?', t: 'Patterns' },
    { q: 'Does the order of steps matter clinically, or is it a same-day artifact?', t: 'Sequences' },
    { q: 'Which single events carry clinical weight alone, and which are generic?', t: 'Events' },
    { q: 'What is missing from a code that you would need: a result, a test type, a severity?', t: 'Gaps' },
    { q: 'Are the draft settings sensible: a one-day window and three or more events?', t: 'Settings' }] } }
};
DATA.timing.values.rows = DATA.patterns.values.rows;

/* data checks run by ?check: each returns '' when fine or one issue sentence */
DECK.checks = [
  () => { const V = DATA.verdicts.values, all = DATA.patterns.values.rows.flatMap(r => r.seqs), tally = k => all.filter(s => s.verdict === k).length;
    return tally('Solid') !== V.solid || tally('Suggestive') !== V.suggestive || tally('Unstable') !== V.unstable || all.length !== V.total || V.solid + V.suggestive !== V.hold ? 'data: verdict tallies do not match the 24 sequences' : ''; },
  () => DATA.patterns.values.rows.flatMap(r => r.seqs).filter(s => s.order === 'same-day').length !== DATA.limits.values.sameDay ? 'data: same-day count does not match' : '',
  () => DATA.patterns.values.rows.reduce((a, r) => a + r.n, 0) !== DATA.cohort.values.n ? 'data: pattern sizes do not add up to the cohort' : ''
];
