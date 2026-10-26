# Chest Pain Care Pattern c6: Nutrition and hormone blood tests

*Working Draft — October 2026*

---

## Overview

This document describes the predicates and composites for care pattern c6 of the chest pain predicate engine. The cohort has 139,416 chest pain patients. A data method groups these patients by the care they receive. The method found 8 care patterns. Care pattern c6 is **nutrition and hormone blood tests**. It has 10,987 patients (7.9%).

This care pattern is blood testing for vitamins, iron, and hormones. Lipid and HbA1c tests follow chest pain in its sequences. The ED work-up engine ([Chestpain_Workup_Predicate_Engine_v3.md](../Chestpain_Workup_Predicate_Engine_v3.md)) defines the rules. This document applies the same rules to the 5 most frequent entities and to the 3 most specific ordered patterns of care pattern c6. It contains no underwriting logic. It is a draft and has no validation yet.

The draft triage for this care pattern is **Routine**. It comes from the entities and the name of the care pattern. It does not come from the literature. An underwriter reviews it.

The first event of each of the 5 entities has a median between 29 d before and 21 d after against the first chest pain. 4 of the 5 entities have a median more than 1 day from the first chest pain. The window of 1 day is short against these medians. The share of patients in the window is not measured. The window needs a calibration before any use.

---

## Predicates and Composites

Each predicate uses a list of codes. The code of each list is in the text. The member table `token_members_k8_chestpain_AHA.csv` shows every concept of a code group.

### Atomic Predicates

A predicate answers one question about the event history of an applicant. It returns true or false. The code and the date are attributes of one event.

**Chest pain present.** The applicant has at least one chest pain event. The list holds chest pain (77670), precordial pain (134159), chest pain on breathing (4168213), and pain of the space between the ribs (42539051).

`chest_pain_present = event IS chest pain diagnosis`

**First chest pain date.** This is the date of the first chest pain event. The engine measures the other dates from this date.

`first_chest_pain_date = MIN(event_date) over chest pain events`

**Vitamin B12 present.** The applicant has at least one vitamin B12 test. Vitamin B12 is a blood test for the level of this vitamin. Code: SNOMED 14598005 (concept_id 4032173).

`vitamin_b12_present = event IS vitamin B12 measurement`

**Vitamin D present.** The applicant has at least one vitamin D test. The vitamin D test measures 25-hydroxy vitamin D in the blood. Code: SNOMED 12199005 (concept_id 4007831).

`vitamin_d_present = event IS 25-hydroxy vitamin D measurement`

**Free T4 present.** The applicant has at least one free T4 test. Free T4 is a blood test for the level of the thyroid hormone. Code: SNOMED 5113004 (concept_id 4196969).

`free_t4_present = event IS free T4 measurement`

**Iron present.** The applicant has at least one iron test. The iron test measures the iron of the blood. Code: SNOMED 42950004 (concept_id 4178785).

`iron_present = event IS iron measurement`

**Ferritin present.** The applicant has at least one ferritin test. Ferritin is a blood test for the iron stores of the body. Code: SNOMED 489004 (concept_id 4176561).

`ferritin_present = event IS ferritin measurement`

**Lipid panel present.** The applicant has at least one lipid panel. A lipid panel is a blood test for cholesterol and other fats. Doctors order it at check-ups, so it alone does not show chest pain care. It is a step of a sequence, not one of the 5 entities. Code: CPT4 80061 (concept_id 2212095).

`lipid_panel_present = event IS lipid panel`

**HbA1c present.** The applicant has at least one HbA1c test. HbA1c is a blood test for the average blood sugar of the last 3 months. The list holds 1 code. It is a step of a sequence, not one of the 5 entities. Code: group `hba1c`, 1 concepts (see the member table).

`hba1c_present = event IS HbA1c test`

**ECG present.** The applicant has at least one ECG. The ECG (electrocardiogram) is a heart tracing. The list holds 5 ECG codes, with or without the report. It is a step of a sequence, not one of the 5 entities. Code: group `ekg`, 5 concepts (see the member table).

`ecg_present = event IS ECG (any of 5 codes)`

**Entity in window.** An entity is in the window when its event is not more than 1 day before or after a chest pain event. The window is 1 day. It is the window of the ED work-up engine.

`workup_window_days = 1`

`<entity>_in_window = <entity>_present AND EXISTS chest pain event date d, entity event date e with |e - d| <= workup_window_days`

There is one predicate for each of the 5 entities: `vitamin_b12_in_window`, `vitamin_d_in_window`, `free_t4_in_window`, `iron_in_window`, `ferritin_in_window`.

---

### Composites

A composite combines atomic predicates, or other composites, into a named clinical pattern. Composites are in three groups: entities, sequences, and the care pattern.

#### Entities

**Entity count.** This is the number of the 5 entities that are in the window for the applicant.

`labs_entity_count = vitamin_b12_in_window + vitamin_d_in_window + free_t4_in_window + iron_in_window + ferritin_in_window`

**Entities.** The applicant has 3 or more of the 5 entities in the window. The value 3 is a draft. It has no calibration yet.

`composite_labs_entities = labs_entity_count >= 3`

#### Sequences

A sequence is a list of events in a fixed order. Other events between the steps do not break the sequence. Every sequence starts at a chest pain event. The last step is not more than 1 day after that chest pain event. A step is true for any code of its list.

`sequence_window_days = 1`

The data method found these 3 sequences. They are the 3 patterns of care pattern c6 with the highest lift. Each sequence has 3 steps.

**Sequence A.** The applicant has a chest pain event, then a lipid panel, then a vitamin D test.

`composite_seq_lipid_vitd = chest_pain -> lipid_panel -> vitamin_d`

**Sequence B.** The applicant has a chest pain event, then a lipid panel, then an HbA1c test.

`composite_seq_lipid_hba1c = chest_pain -> lipid_panel -> hba1c`

**Sequence C.** The applicant has a chest pain event, then an ECG, then a lipid panel.

`composite_seq_ecg_lipid = chest_pain -> ecg -> lipid_panel`

**Sequence of care pattern c6.** The applicant has at least one of the sequences A, B, or C.

`composite_labs_sequence = composite_seq_lipid_vitd OR composite_seq_lipid_hba1c OR composite_seq_ecg_lipid`

#### Same-day order

Claims have a date and no time. The engine puts the events of one day in a fixed order: diagnosis, procedure, lab test, then drug. Inside one type, a lower code ID comes first. For a same-day pattern, the order of the steps is a rule. It is not the clock time.

#### Care pattern

**Care pattern c6.** The applicant has chest pain, 3 or more entities in the window, and at least one sequence. This pattern shows the type of care. It does not show a diagnosis. The predicates test that an event happened, not the result.

`composite_labs_pattern = chest_pain_present AND composite_labs_entities AND composite_labs_sequence`

---

## Population Coverage

Counts come from the chest pain cohort of 139,416 patients. The tables come from the k=8 run of the data method (`nmf_k8_chestpain_AHA`). The engine has no measured rate for any predicate or composite yet.

### Entity rates

The rates are for the 10,987 patients of care pattern c6. They count an entity at any time, not only in the window.

| Entity | Patients with the entity | Median day against first chest pain | Share that had it before first chest pain |
| :---- | ----: | :---- | ----: |
| Vitamin B12 (SNOMED 14598005) | 88% | same day | 48% |
| Vitamin D (SNOMED 12199005) | 90% | 29 d before | 53% |
| Free T4 (SNOMED 5113004) | 75% | 14 d before | 52% |
| Iron (SNOMED 42950004) | 71% | 19 d after | 44% |
| Ferritin (SNOMED 489004) | 71% | 21 d after | 44% |

### Sequence rates

The shares count the steps in this order at any time. They do not use the 1-day limit. The other care patterns are a random sample of 1,500 patients.

| Sequence | Patients of c6 | Patients of the other care patterns | Times as common | Held-out pass rate | Verdict |
| :---- | ----: | ----: | ----: | ----: | :---- |
| A. Chest pain, lipid panel, vitamin D test | 64.6% | 19.4% | 3.2 | 100% | Solid |
| B. Chest pain, lipid panel, HbA1c test | 68.8% | 36.3% | 1.9 | 100% | Solid |
| C. Chest pain, ECG, lipid panel | 65.0% | 41.2% | 1.6 | 100% | Solid |

The held-out check repeats the test on random halves of the patients, in 40 runs. All 3 sequences passed it.

---

## References

- Gulati M, et al. *2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain.* Circulation 2021;144:e368. doi:10.1161/CIR.0000000000001029.
- Alkhatatbeh MJ et al. *Association of 25-hydroxyvitamin D with HDL-cholesterol and other cardiovascular risk biomarkers in subjects with non-cardiac chest pain.* Lipids Health Dis 2019. PMID 30684966.
- Khater WA et al. *The Association Between Vitamin D Level and Chest Pain, Anxiety, and Fatigue in Patients With Coronary Artery Disease.* Clin Nurs Res 2023. PMID 36205377.
- Ewid M et al. *Glycated hemoglobin predicts coronary artery disease in non-diabetic adults.* BMC Cardiovasc Disord 2019. PMID 31864310.
- Chun AA et al. *Bedside diagnosis of coronary artery disease: a systematic review.* Am J Med 2004. PMID 15336583.

The papers above come from the literature check of the final table (rating: Partly). They cover the care type. They do not test the order of the steps.
