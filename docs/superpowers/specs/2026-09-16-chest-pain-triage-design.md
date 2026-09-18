# Chest pain triage (dx_9487) — adapting the 5-day repr_learn arc

## Context

IRIX Dx code `dx_9487` (Atypical Chest Pain) currently routes every case to manual
review at RUW. It maps to five nonspecific ICD-10 chest-pain codes (R07.89, R07.9,
R07.2, R07.8, R07.82), each of which can reflect a real cardiac issue or a benign
non-cardiac cause (musculoskeletal, GI, anxiety/panic). Manual review on all of them
is costly and slow. The goal is to determine whether the surrounding clinical
picture — other Dx/Rx codes in the applicant's history — can triage `dx_9487` cases
into "likely benign" vs "needs manual cardiac workup," automating or partially
automating the review decision.

The working hypothesis (to test, not assume) is that a meaningful share of `dx_9487`
cases are miscoded anxiety/panic presentations, evidenced by comorbid anxiety/panic
Dx and SSRI/benzodiazepine Rx codes. The analysis must be built to let the data show
a different answer (GERD, costochondritis, genuine cardiac workup) if that's what's
there.

The existing `repr_learn_letrozole/` 5-day course (extract → cluster → sequence-mine
→ embed → rule+outcome) already has the right *mechanics* for exactly this kind of
problem — it was built around a fertility-vs-oncology disambiguation as the teaching
example, and Day 3 already independently converged on a chest-pain trajectory graph
as its "actual deliverable" example. This spec adapts the same 5 mechanics to make
dx_9487 the primary, real-data worked example throughout, using the cohort already
extracted in `sql/chest_pain_cohort.sql`.

## Data

`data_input/` at the repo root already contains a real extract for this exact
cohort: 150,368 patients pulled via `eo.extract_cohort("../sql/chest_pain_cohort.sql")`
(all patients carrying one of the five R07.x codes). No re-extraction is needed —
Day 1 of the new notebooks points at this directory directly.

## New folder

`repr_learn_chestpain/` — a copy of `repr_learn_letrozole/`'s five files
(`ethos_omop.py`, `make_demo_extract.py`, `README_repr_learn.md`, `Day1..5*.ipynb`),
edited independently. `repr_learn_letrozole/` is left untouched (it already ran
successfully against its own extract).

## `ethos_omop.py` changes (in the new copy only)

- **`CODESETS` additions**: `benzodiazepine`, `panic_attack`, `gerd`,
  `costochondritis`. Existing `anxiety`, `ssri`, `ekg`, `troponin`, `stress_test`,
  `coronary_angio`, `cad`, `beta_blocker`, `statin`, `chest_pain` are reused as-is.
- **`chest_pain_labels(events)`** — new function, same honesty contract as
  `weak_labels()`: builds co-evidence-only groups (never time-order, to avoid
  circularity with the temporal analyses in Days 3-4). `psych` = anxiety OR
  panic_attack OR ssri OR benzodiazepine; `cardiac` = troponin OR stress_test OR
  coronary_angio OR cad. Ambiguous (both) and no-evidence patients are dropped, and
  counts are printed, exactly like `weak_labels()`.
- **`cardiac_workup_outcome(events, window_days=180)`** — new function, the Day 5
  proxy outcome. For each patient: `index_date` = first `chest_pain` event;
  `workup` = whether a troponin/stress_test/coronary_angio/cad-dx event occurs
  within `window_days` after `index_date`. Returns `person_id, index_date, workup,
  days_to_workup`. This is the closest available proxy for "was this case actually
  triaged as cardiac downstream" — there is no mortality endpoint for a triage
  question, so this replaces Kaplan-Meier-on-death as the primary Day 5 validation.
  A short KM-on-death cut stays as a secondary robustness check since the real
  `death` table is available.
- `extract_cohort()`'s default `out_dir` and the notebooks' `OUT_DIR`/`COHORT_SQL`
  constants follow the same `../data_input` / `../sql/...` convention already fixed
  in `repr_learn_letrozole/` (cwd = the notebook's own directory).

## Per-notebook changes

Mechanics (SVD clustering, PrefixSpan, PPMI embeddings, surrogate decision trees)
are unchanged. What changes is which codesets/labels drive the narrative:

- **Day 1**: markdown reframed around the RUW cost problem and the five R07.x
  codes (with the prevalence percentages given). "Two patients, identical bag of
  codes, opposite meaning" is rebuilt from two real cohort patients found via
  `chest_pain_labels()` (one lands in `cardiac`, one in `psych`) instead of the
  letrozole/breast_cancer pair.
- **Day 2**: cluster profiling reads out psych-vs-cardiac tag prevalence/lift
  instead of the diabetes-archetype example. Confounding checks (utilisation,
  enrolment-year drift) are generic and unchanged.
- **Day 3**: already chest-pain-native (trajectory graph, `FOCUS` set). Expand
  `FOCUS` with `panic_attack`, `benzodiazepine`, `gerd`, `costochondritis`. Swap
  `weak_labels()` calls for `chest_pain_labels()`. Promote the discriminative
  sequence-mining section (psych vs cardiac motifs) from a secondary "same thing
  against weak labels" add-on to the primary analysis.
- **Day 4**: PPMI neighbour lookups center on `chest_pain`/`anxiety`/`troponin`
  instead of `letrozole`. Point-in-time truncation anchors on
  `index_dates(events, 'chest_pain')` instead of first letrozole exposure. t-SNE is
  colored by `chest_pain_labels()` groups.
- **Day 5**: surrogate-tree extraction from Day 2 clusters is unchanged. Outcome
  validation swaps to `cardiac_workup_outcome()` — does cluster membership / the
  surrogate rule predict who actually got a downstream cardiac workup (report as
  lift/precision, not survival curves). KM-on-death kept as a short secondary cut.
  Reporting template field names reworded to RUW/underwriting language
  (`dx_9487`, manual-review cost, etc.), and the confounding section is rewritten
  around the circularity risk specific to this problem: what triggers a workup
  code is itself a manual-review decision, so a rule "predicting" workup can be
  partly predicting the reviewer's own past behavior rather than true cardiac risk
  — name this explicitly as a limitation.

## Verification

- `python -m py_compile` on the new `ethos_omop.py`.
- Small offline fixture tests (no Snowflake) for `chest_pain_labels()` and
  `cardiac_workup_outcome()` — synthetic events frame, assert grouping/window logic.
- Because `data_input/` already has the real 150k-patient extract on disk, actually
  execute Day 1 through Day 5 top-to-bottom against it (not just fixtures) to
  confirm the narrative holds with real numbers — e.g., that `chest_pain_labels()`
  produces non-trivial group sizes, that clusters/motifs are non-degenerate, that
  `cardiac_workup_outcome()` has enough positive cases to be informative.
