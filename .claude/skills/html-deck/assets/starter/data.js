/* ===== 5. DATA [CONTENT] ===== */
/* The ONLY place numbers live. Text, notes and aria-labels cite them as {{dataset.path|fmt}}. Shares are fractions (0 to 1). */
const DECK = { name: 'Review time case', people: [{ key: 'ab', name: 'Alex Brown', role: 'Product lead' }] };
const PHOTO = {};   // key -> photo as a data URI (made by scripts/photo_to_datauri.py, see engine.md) or a relative path; a missing key means an initials avatar
const DATA = {
  kpi: { id: 'kpi', title: 'Median review time', unit: 'hours', kind: 'illustrative', window: 'fictional quarter', denominator: 'fictional requests, no real count', exclusions: '', source: 'Invented for the starter deck', formula: 'cut = (before − after) ÷ before',
    values: { before: 20, after: 10, cut: 0.5 } },
  delay: { id: 'delay', title: 'Where review time went', unit: 'share of review time', kind: 'illustrative', window: 'fictional quarter before the change', denominator: 'all review time in the quarter', exclusions: 'drafts', source: 'Invented for the starter deck', formula: 'time in stage ÷ total review time',
    values: { rows: [{ k: 'Waiting for a reviewer', v: 0.46 }, { k: 'Rework after comments', v: 0.27 }, { k: 'Reading and commenting', v: 0.19 }, { k: 'Merging', v: 0.08 }] } },
  habits: { id: 'habits', title: 'Four habits', unit: '', kind: 'concept', values: { cards: [
    { t: 'Small requests', pos: 'habit', d: 'Keep a change small enough to review in one sitting.', k: 'Small first, then more.', i: 'box' },
    { t: 'Named reviewers', pos: 'habit', d: 'Every request names one reviewer, so nobody wonders whose turn it is.', k: 'One name, no queue.', i: 'user' },
    { t: 'Same-day first look', pos: 'habit', d: 'The reviewer gives a first answer the same day, even if it is only a question.', k: 'Answer, even partly.', i: 'clock' },
    { t: 'Comment templates', pos: 'habit', d: 'A short template tells the author what a good request contains.', k: 'Say it once, early.', i: 'file' }] } }
};

/* data checks run by ?check: each returns '' when fine or one issue sentence */
DECK.checks = [
  () => Math.abs(DATA.delay.values.rows.reduce((a, r) => a + r.v, 0) - 1) > 1e-9 ? 'data: stage shares do not add up to 100%' : '',
  () => Math.abs((DATA.kpi.values.before - DATA.kpi.values.after) / DATA.kpi.values.before - DATA.kpi.values.cut) > 1e-9 ? 'data: cut does not match before and after' : ''
];
