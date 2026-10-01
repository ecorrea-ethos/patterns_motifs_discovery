# Event labels and the prevalence floor

## What this covers
How every event in the claims data gets a name (its column in the bag of codes), and how
rare codes are removed. Terms: see [glossary.md](glossary.md).

## The label
Events whose concept is in a hand-built codeset (`codesets.yaml`) are named after the
codeset (`chest_pain`, `troponin`, `ekg`, ...). Every other event gets a **fallback label**
built in `ethos_omop._fallback_label` (called from `tag_events`):

```
<name, first 20 characters>__<concept_class_id>__<concept_id>
e.g. cough__clinical_finding__254761
     complete_blood_count__cpt4__3012345
```

Steps (the same as the Snowflake `concept_name2..6` recipe the team uses):
1. Lower-case the name and fold accents (`é` to `e`) with a fixed 49-character table.
2. Remove every character that is not a-z, 0-9 or a space.
3. Replace spaces with `_`.
4. Cut the **name** to 20 characters.
5. Append `__` and the `concept_class_id`, cleaned by steps 1-3 but **never cut**.
6. Append `__` and the `concept_id`, **never cut**.

Details worth knowing:
- The 20-character cut is not re-stripped, so a name that ends on a word boundary gives three
  underscores (`electrocardiogramme___quant_branded_drug__2`). This matches the SQL literally.
  Do not split labels on `__` without handling that.
- `concept_class_id` is carried through `load_events` (it comes from `concept.csv`).
- Labels are built once per distinct untagged concept, not once per event.

## Why
The old label cut names at 22 characters and merged different concepts that shared a prefix.
On the chest pain `concept.csv`, 29,490 distinct names collapsed to 19,021 labels, and
14,330 names shared a label with another name (for example 184 different
"primary malignant neoplasm of ..." concepts became one column). Adding the `concept_id` makes
every concept its own column, so nothing is merged silently.

Cost: more, sparser columns (for example drug doses are no longer pooled). Every result
computed on the old labels (NMF k, stability, Table 1 labels, Day 2/3 results) had to be rerun.

## The prevalence floor
`bag_of_codes(min_count=...)` counts **events**, so one patient with 20 refills can keep a code.
What limits a model is how many **patients** carry a code, so the Day 1 notebook adds a cell,
"Choosing `min_count` from prevalence", that:
- counts patients per code and events per code,
- tabulates, for floors from 1 to 500 patients, the columns kept and the share of
  patient-code pairs kept,
- suggests a floor of `ceil(5 * cohort / training_split_size)` patients, so a code is
  expected to appear in at least 5 patients of a training split (35 patients for the 139,416
  patient chest pain cohort),
- lists any codeset tag that falls below the floor,
- defines `KEEP_TAGS`.

The matrix is then built from the kept codes only:

```python
X = eo.bag_of_codes(events[events.tag.isin(KEEP_TAGS)], min_count=1)
```

`min_count=1` is intentional: the patient floor is already applied, so an event floor would
remove nothing. In the chest pain run, the 35-patient floor made no visible difference to the
NMF stability numbers (k=10-13, seed 2: ARI 0.67/0.66/0.61/0.67 without it, 0.70/0.68/0.60/0.73
with it; other settings also differed between those runs, so treat this as a rough comparison).

## Not yet done
Days 2-5 still call `eo.bag_of_codes(events, min_count=20)` on their own, so they do not use the
patient floor. A `min_patients=` argument on `bag_of_codes()` would let every notebook share it.
