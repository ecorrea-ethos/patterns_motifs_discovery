# dx_9487 chest-pain triage — 5 days, on the real Ethos OMOP extract

One notebook per day. Every subtopic uses the single most common technique; alternatives are
named in a table so you know what you skipped. All five run end to end against the real
150,368-patient dx_9487 cohort already extracted into `../data_input/`.

**The problem.** `dx_9487` (Atypical Chest Pain) maps to five nonspecific ICD-10 codes
(R07.89, R07.9, R07.2, R07.8, R07.82) and currently routes every case to manual review at
RUW. The working hypothesis — to test, not assume — is that a meaningful share are
anxiety/panic presentations coded as chest pain. Five days: extract → cluster → sequence-mine
→ embed → rule + real outcome, aimed squarely at that question.

## Files

| File | What it is |
|---|---|
| `ethos_omop.py` | extract + load layer, plus `chest_pain_labels()` and `cardiac_workup_outcome()` for this problem specifically |
| `codesets.yaml` | the clinical code sets, as config -- edit this to change what a tag matches, no code changes needed |
| `make_demo_extract.py` | writes a synthetic `omop_extract/` with the same schema, for running without Snowflake |
| `Day1_Extract_and_Representation.ipynb` | the extract, its four preprocessing decisions, and why bag-of-codes fails on dx_9487 |
| `Day2_Clustering.ipynb` | k-means, HDBSCAN, and bootstrap stability |
| `Day3_Sequence_Mining.ipynb` | PrefixSpan → psych vs cardiac motif catalog (the hypothesis test) |
| `Day4_Representation_Learning.ipynb` | PPMI embeddings, and the precise case for CLMBR |
| `Day5_Rules_and_Outcomes.ipynb` | surrogate rules + does the rule predict a real downstream cardiac workup |

## Setup

```bash
pip install numpy pandas scikit-learn scipy matplotlib networkx jupyter pyyaml
# plus snowflake-connector-python if you are re-extracting
```

Then, from this directory (`repr_learn_chestpain/`) so relative paths line up, one of:

```python
import ethos_omop as eo
eo.extract_cohort("../sql/chest_pain_cohort.sql")     # -> ../data_input/
```

or, with no Snowflake access:

```bash
python make_demo_extract.py 2000
```

(the demo extract is unchanged from the generic version — it does not plant
panic_attack/benzodiazepine/gerd/costochondritis concepts, so `chest_pain_labels()` and
`cardiac_workup_outcome()` will find little on it; it's a fallback for the mechanics, not
for this cohort's specific question.)

`../data_input/` already has the real extract as of this writing — Day 1's extract cell
skips re-pulling if it's populated. `extract_cohort()` takes a cohort-defining query — raw
SQL or a path to a `.sql` file — that returns `person_id` (only the first column is used;
extra columns like counts are fine). A path-looking string that doesn't resolve raises
immediately instead of silently being sent to Snowflake as a query. The seed ids are then
used to dump the same shape `extract_omop()` does — `master_*` tables, `person`, `death`, a
slimmed `concept` — so `load_events()` and everything downstream needs no changes.

Nothing else is required. PrefixSpan, Kaplan-Meier, the log-rank test, and the PPMI
embeddings are all implemented in the notebooks — roughly 25 lines each. Implementing them
once is what lets you reason about their failure modes.

## What's specific to this cohort

**`CODESETS` additions** beyond the base set: `panic_attack`, `benzodiazepine`, `gerd`,
`costochondritis` — covering the stated hypothesis (anxiety/panic + SSRI/benzo) and the two
named alternative explanations, so the analysis can genuinely discriminate rather than only
confirm the anxiety story.

**`chest_pain_labels()`** replaces the generic `weak_labels()` pattern for this cohort: probe
labels from corroborating co-evidence only — `psych` (anxiety/panic/ssri/benzodiazepine) vs
`cardiac` (troponin/stress-test/coronary-angio/cad-dx). Ambiguous and no-evidence patients
are dropped, and the counts are printed. The time order between `chest_pain` and the
evidence is never used to build the label, because Days 3-4 test that order directly —
labelling on order and then testing order would be circular.

**`cardiac_workup_outcome()`** is the Day 5 primary outcome: did a real cardiac workup code
land within a window (default 180 days) after the patient's first `chest_pain` code. There is
no mortality endpoint for a triage question, so this replaces Kaplan-Meier-on-death as the
primary validation; a short KM-on-death cut stays as a secondary robustness check since the
real `death` table is available for this cohort.

**Codesets live in `codesets.yaml`, not in code.** Each tag is either
`{patterns: [...], vocabularies: [...]}` (name-matched via `resolve()`, portable across the
real extract and the demo extract alike) or `{concept_ids: [...]}` (a literal, verified id
set, for a tag that can't tolerate name-matching drift). `eo.build_codesets()` loads and
resolves the file; `eo.resolve()` shows you what a pattern matched — always look before
trusting it.

**`tag` collapses many concept_ids to one readable label.** Mining raw concept_ids produces
patterns nobody can read; this is the hand-rolled version of ontology rollup, and it is what
makes Day 3's output legible.

## The four preprocessing decisions, up front

1. **Standard concepts only** — `standard_concept == 'S'`, `concept_id != 0`. And the
   exclusion idiom is `IS DISTINCT FROM`, not `<>`, which silently drops NULLs.
2. **`concept_code` stays a string.** Never let pandas parse it as numeric.
3. **Claims carry a DATE, not a timestamp.** Same-day events have no true order.
   `DOMAIN_ORDER` breaks ties deterministically. It is arbitrary and it is written down.
4. **No `observation_period` in the extract.** `observation_window()` derives a proxy from
   first and last event, which understates the true window. "No prior diagnosis" may mean
   "not observed yet" — carry `lookback_days` and exclude short-lookback patients from
   anything that depends on absence of a code.

## The arc, in three findings

**Day 1** finds two dx_9487 patients with a near-identical bag of codes and opposite triage
answers — same `chest_pain` + `ekg`, but one's timeline shows anxiety/SSRI evidence, the
other's shows troponin/stress-test/angiography. **Day 2** shows that clustering that
representation produces clusters with a roughly flat psych:cardiac mix — utilisation and
comorbidity burden dominate, not the distinction that matters. **Day 3** mines psych vs
cardiac motifs directly with sequential pattern mining, and a signed gap
(`chest_pain -> troponin`) carries most of the workup-timing signal in a single integer.

That progression is the argument to make internally: the temporal representation is where
the value is, and the cheapest version of it may be enough.

**Day 4** is the counterweight. A static concept embedding puts `chest_pain` next to *both*
the cardiac-workup bundle and the psych bundle, because it has one vector per concept. That
is the precise case for a contextual model like CLMBR — a much better argument than
"foundation models are good." It also flags the two things to settle before that sprint: the
non-commercial licence, and the out-of-vocabulary rate on claims codes.

**Day 5** closes the loop: cluster → surrogate decision tree → rule → does it predict a real
downstream cardiac workup, plus the section on why that outcome itself is confounded with
past manual-review behaviour, and a secondary check against real mortality.

## If you only have one day

Day 3. It produces the actual deliverable — discrete, nameable, countable ordered patterns
that can be written as a triage rule — and it needs nothing but the extract and a laptop.

## Codeset v2 (2021 AHA/ACC chest pain guideline) and the AHA notebook

`codesets_v2.yaml` is a guideline rewrite of `codesets.yaml` (Gulati et al., *Circulation* 2021;144:e368,
doi:10.1161/CIR.0000000000001029). `codesets.yaml` is untouched, so the `k5_full` results stay reproducible.

| What | Where |
|---|---|
| New code sets: anchor equivalents, test ladder (ECG, cTn, CXR, TTE/TEE, stress ECG / echo / SPECT / PET, CMR, CCTA, CAC, FFR-CT, ICA, D-dimer, V/Q), cardiac causes, noncardiac causes (Table 9), CAD risk factors, therapy | `codesets_v2.yaml` (70 tags; every v4 tag name kept; `chest_pain` identical) |
| Check a codeset against the extract's `concept.csv` (matched names, empty tags, overlaps, diff vs v4) | `python check_codesets.py [codesets_v2.yaml] [--tags a,b] [--names N] [--details]` (conda env `ethos_llm`) |
| Notebook that runs on v2 (clone of `Chestpain_NMF_PrefixSpan_full`, outputs cleared) | `Chestpain_NMF_PrefixSpan_AHA.ipynb`, settings in cell 2 |
| Sankey of patients between the bundles of two runs (AHA k=8 vs full k=8, vs full k=5) | `python sankey_runs.py [LEFT RIGHT]` (conda env `ethos_llm`; run labels `AHA`, `full_k8`, `full`); writes `sankey_AHA_k8_vs_full_k8.png`, `sankey_AHA_k8_vs_full_k5.png` |
| Animated trajectory graph, one self-contained HTML (time cursor sweeps, ~60 dots per entity drawn from Normal(median, SD), jitter slider, hover numbers, **Export GIF** button: 12 s, 12 fps, up to 1000 px, about 3 MB on the synthetic test). After changing the template, rebuild without the notebook: `python trajectory_anim.py trajectory_k8_chestpain_AHA.json` | last two cells of the AHA notebook ("7 · Animation export", needs cells 58 and 60 in the same kernel) write `trajectory_k{K}_{TAG}.json` and `trajectory_k{K}_{TAG}_animation.html`; builder `trajectory_anim.py`, page `trajectory_anim_template.html`, d3 v7.9.0 in `vendor/d3.v7.min.js` (ISC license) |
| Member table: which concepts sit behind each token (needed to turn a group token into `concept_id IN (...)` for the predicate engine) | section "5 · Member table" of the AHA notebook (cells 62-63, just before the final table); writes `token_members_k{K}_{TAG}.csv` |
| Predicate engine on the AHA k=8 run (care pattern c3, ED work-up), plain English first; version 1 (k=5, c0) is kept with a banner pointing here | `Chestpain_Workup_Predicate_Engine_v2.md`; flow image `chestpain_c3_flag_flow.png` from `python make_c3_flag_flow.py` (conda env `omop_local`) |
| Triage / Supported literature / PMIDs of the AHA final table (PubMed, skill `pubmed-literature-check`; audit files `final_table_chestpain_k8_AHA_literature_*.csv`) | `literature_search/aha_k8/`: `search_entities_patterns_AHA.py`, `search_setting_AHA.py`, `fetch_abstracts.py`, then `python fill_literature_AHA.py` (conda env `ethos_llm`; the search and verify steps need the sandbox off; `--check` re-tests the decisions) |
| Short engine page for the UW team in ASD-STE100 style, shaped like `Diabetes_Rx_Predicate_Engine.md` (no code table, no flag rule, no evaluation text; ends in `composite_ed_workup_pattern`) | `Chestpain_Workup_Predicate_Engine_v3.md`; neutral flow image `chestpain_c3_pattern_flow.png` from `python make_c3_flag_flow.py --neutral` (conda env `omop_local`, embedded as base64 in the page). `_v2.md` stays as the long version with Annex A / B |
| Plain-English wording and the parallel table to OMOP (abbreviations, UW wording against data-team wording, one label per code list, every code with its OMOP ID), so the UW team and the data team use the same words | edit `chestpain_plain_labels.yaml`, then `python build_plain_english_annex.py` (conda env `ethos_llm`): writes `chestpain_plain_english_omop_map.csv` (878 rows) and refreshes the entity registry table and Annex A / B of the v2 md between its `REGISTRY` and `ANNEX` markers; it stops with an error when the labels and `codesets_v2.yaml` differ |

How to switch: cell 2 of the AHA notebook has `CODESETS_FILE` (`codesets_v2.yaml` or `codesets.yaml`) and `TOKEN_LEVEL`.

- `TOKEN_LEVEL='concept'` keeps one NMF token per concept, as `k5_full`. The NMF is then identical to `k5_full`; v2 only changes
  anchors, labels, the loadings check and coverage. Use it as the regression check (139,416 patients, same bundle sizes and top-5 tokens).
- `TOKEN_LEVEL='group'` makes each codeset tag the NMF token (38 ECG / monitor concepts become `ekg` and `ecg_ambulatory`, etc.). This is
  the real test of v2. YAML order is load-bearing: at group level a concept belongs to the FIRST tag that lists it, so the umbrella
  tags `stress_test` and `cad` are last.
- Files written by the AHA notebook carry the `AHA` label (`nmf_k5_chestpain_AHA.npz`, `..._components.json`,
  `nmf_components_chestpain_k5_AHA.xlsx`, `final_table_chestpain_k5_AHA.xlsx`). `DESCR` is empty: read the printed top tokens, paste the
  printed block, run the cell again.
- Member table (`token_members_k8_chestpain_AHA.csv` for the k=8 run): one row per OMOP concept, the token it carries, `groups` (every tag
  it belongs to; the token is the first one in YAML order), `n_events` / `n_patients` for the concept, `token_n_concepts` /
  `token_n_patients` for the token, `in_nmf`, `nmf_owner`, `owner_share`, `n_motifs`. It also lists codeset members never seen in the
  cohort (`in_cohort` False, `n_events` 0) so an entity defined on this cohort still covers them. Run it before the final-table cell
  (it reads `K`, `H`, `hyb` from Part B; the final table reads its result). Works at both token levels; at `'concept'` every token has
  one row. Freeze this file when a predicate engine is written on a group-level run: the yaml can change later, the table cannot.
- Final table (`final_table_chestpain_k{K}_{VARIANT}.xlsx`) has two extra columns at the end, Q and R: "Members of the group tokens in the
  entities" (bundle level, merged) and "... in the pattern" (per row). For each group token: concept count, how many occur in the cohort,
  and its 3 most frequent members with concept_id and patient count; the rest are in the csv. Columns A-P are unchanged, so the manual
  Triage / Literature / PMIDs columns (M, O, P) keep their letters. Rows grow when there is members text; at concept level the columns
  are empty.

Limits of this extract (claims-coded; LOINC has 51 unrelated concepts): hs-cTn cannot be told from conventional cTn, obstructive from
nonobstructive CAD cannot be told at all, and the guideline's advice to stop saying "atypical" chest pain is a naming point only.
