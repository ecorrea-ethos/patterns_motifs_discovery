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
| `make_demo_extract.py` | writes a synthetic `omop_extract/` with the same schema, for running without Snowflake |
| `Day1_Extract_and_Representation.ipynb` | the extract, its four preprocessing decisions, and why bag-of-codes fails on dx_9487 |
| `Day2_Clustering.ipynb` | k-means, HDBSCAN, and bootstrap stability |
| `Day3_Sequence_Mining.ipynb` | PrefixSpan → psych vs cardiac motif catalog (the hypothesis test) |
| `Day4_Representation_Learning.ipynb` | PPMI embeddings, and the precise case for CLMBR |
| `Day5_Rules_and_Outcomes.ipynb` | surrogate rules + does the rule predict a real downstream cardiac workup |

## Setup

```bash
pip install numpy pandas scikit-learn scipy matplotlib networkx jupyter
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

**Codesets resolve by name, not by hardcoded concept_id.** `CODESETS` maps a clinical label
to name patterns plus vocabularies, so the same notebook runs against real Snowflake
concepts and the demo extract alike. `eo.resolve()` shows you what matched — always look
before trusting it.

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
