# Automated Pattern Discovery — 5 days, on the Ethos OMOP extract

One notebook per day. Every subtopic uses the single most common technique; alternatives are
named in a table so you know what you skipped. All five run end to end.

## Files

| File | What it is |
|---|---|
| `ethos_omop.py` | extract + load layer. Your Snowflake script, refactored, plus the feature helpers the notebooks use |
| `make_demo_extract.py` | writes a synthetic `omop_extract/` with the same schema, for running without Snowflake |
| `Day1_Extract_and_Representation.ipynb` | the extract, its four preprocessing decisions, and why bag-of-codes fails |
| `Day2_Clustering.ipynb` | k-means, HDBSCAN, and bootstrap stability |
| `Day3_Sequence_Mining.ipynb` | PrefixSpan → a named motif catalog |
| `Day4_Representation_Learning.ipynb` | PPMI embeddings, and the precise case for CLMBR |
| `Day5_Rules_and_Outcomes.ipynb` | surrogate rules + Kaplan-Meier on the real `death` table |

## Setup

```bash
pip install numpy pandas scikit-learn scipy matplotlib networkx jupyter
# plus snowflake-connector-python if you are extracting
```

Then, from this directory (`repr_learn/`) so relative paths line up, one of:

```python
import ethos_omop as eo
eo.extract_omop(n_patients=10_000)                    # random sample -> omop_extract/

eo.extract_cohort("../sql/chest_pain_cohort.sql")     # cohort seeds -> data_input/
```

or, with no Snowflake access:

```bash
python make_demo_extract.py 2000
```

`extract_cohort()` takes a cohort-defining query — raw SQL or a path to a `.sql`
file — that returns `person_id` (only the first column is used; extra columns like
counts are fine). A path-looking string that doesn't resolve raises immediately
instead of silently being sent to Snowflake as a query. Once you have the seed ids,
they're used to dump the exact same shape `extract_omop()` does — `master_*`
tables, `person`, `death`, a slimmed `concept` — so `load_events()` and everything
downstream needs no changes to read either output directory.

Nothing else is required. PrefixSpan, Kaplan-Meier, the log-rank test, and the PPMI
embeddings are all implemented in the notebooks — roughly 25 lines each. Implementing them
once is what lets you reason about their failure modes.

## What changed from the generic version

**`extract_omop()` keeps your structure** — `master_*` as the source of truth, `ethos_dip`
excluded on both `concept_id` and `source_concept_id` for every domain table,
standard-named symlinks so `meds_etl_omop` can find the files. Two additions:

* `concept.csv` is slimmed to the concept_ids the sample actually references, instead of the
  full multi-million-row table
* `concept_ancestor` is dumped for rows touching the sample — that is what ontology rollup
  needs, and rollup is directly relevant to the unspecified cardiac codes

**`extract_cohort()` swaps the random sample for a cohort query.** Instead of `SAMPLE (n)`,
the person_ids come from any SQL you supply — e.g. `sql/chest_pain_cohort.sql`, which expands
ICD10CM chest-pain codes through `concept_relationship` to standard concepts and matches on
concept_id, source_concept_id, or source_value. `extract_omop()` was refactored so both
functions share one `_dump_core()` (same dip exclusion, slimming, symlinks); only where the
person_id seed list comes from differs.

**Codesets resolve by name, not by hardcoded concept_id.** `CODESETS` maps a clinical label
to name patterns plus vocabularies, so the same notebook runs against real Athena concepts
and the demo extract alike. `eo.resolve()` shows you what matched — always look before
trusting it.

**`tag` collapses many concept_ids to one readable label.** Mining raw concept_ids produces
patterns nobody can read; this is the hand-rolled version of ontology rollup, and it is what
makes Day 3's output legible.

**There are no labels.** `weak_labels()` builds probe labels for the letrozole indication
from corroborating co-evidence only, and deliberately excludes the breast cancer diagnosis
itself — a fertility patient can develop cancer years later, so the diagnosis is confounded
with the thing you are disambiguating. The time delta is never used, because labelling on
"drug before diagnosis" and then testing whether the delta predicts the label is circular.
Validation therefore rests on **stability** (Day 2) and **outcome separation** (Day 5), not
on accuracy against a label.

**Day 5 uses the real `death` table** instead of a simulated outcome, and adds a
confounding check against enrolment year.

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

**Day 1** finds two patients with an identical bag of codes and opposite clinical meaning —
in the demo run, letrozole in 2020 then a cancer diagnosis in 2026, versus biopsy, cancer,
mastectomy, then letrozole. **Day 2** shows that clustering that representation cannot
separate stable from progressive diabetes at any k. **Day 3** separates the letrozole
indications at 60x+ lift with sequential pattern mining, and recovers
`infertility -> clomiphene -> letrozole` versus `mammogram -> breast_biopsy -> letrozole`
directly.

That progression is the argument to make internally: the temporal representation is where
the value is, and the cheapest version of it may be enough.

**Day 4** is the counterweight. A static concept embedding puts `letrozole` next to *both*
the fertility bundle and the oncology bundle, because it has one vector per concept. That is
the precise case for a contextual model like CLMBR — a much better argument than "foundation
models are good." It also flags the two things to settle before that sprint: the
non-commercial licence, and the out-of-vocabulary rate on claims codes.

**Day 5** closes the loop: cluster → surrogate decision tree → rule → survival separation,
plus the section on confounding by your own ordering rules.

## If you only have one day

Day 3. It produces the actual deliverable — discrete, nameable, countable ordered patterns
that can be written as rules — and it needs nothing but the extract and a laptop.
