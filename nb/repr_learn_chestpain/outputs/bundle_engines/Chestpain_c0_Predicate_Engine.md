# Chest Pain Care Pattern c0: Outpatient check-up and elective cardiac testing

*Working Draft — October 2026*

---

## Overview

This document describes the predicates and composites for care pattern c0 of the chest pain predicate engine. The cohort has 139,416 chest pain patients. A data method groups these patients by the care they receive. The method found 8 care patterns. Care pattern c0 is **outpatient check-up and elective cardiac testing**. It has 31,113 patients (22.3%).

This care pattern is routine outpatient care. Lipid tests, ECG, and check-up visits dominate it. The ED work-up engine ([Chestpain_Workup_Predicate_Engine_v3.md](../Chestpain_Workup_Predicate_Engine_v3.md)) defines the rules. This document applies the same rules to the 5 most frequent entities and to the 3 most specific ordered patterns of care pattern c0. It contains no underwriting logic. It is a draft and has no validation yet.

The draft triage for this care pattern is **Unclear**. It comes from the entities and the name of the care pattern. It does not come from the literature. An underwriter reviews it.

The first event of each of the 5 entities has a median between 104 d before and same day against the first chest pain. 3 of the 5 entities have a median more than 1 day from the first chest pain. The window of 1 day is short against these medians. The share of patients in the window is not measured. The window needs a calibration before any use.

---

## Predicates and Composites

Each predicate uses a list of codes. The code of each list is in the text. The member table `token_members_k8_chestpain_AHA.csv` shows every concept of a code group.

### Atomic Predicates

A predicate answers one question about the event history of an applicant. It returns true or false. The code and the date are attributes of one event.

**Chest pain present.** The applicant has at least one chest pain event. The list holds chest pain (77670), precordial pain (134159), chest pain on breathing (4168213), and pain of the space between the ribs (42539051).

`chest_pain_present = event IS chest pain diagnosis`

**First chest pain date.** This is the date of the first chest pain event. The engine measures the other dates from this date.

`first_chest_pain_date = MIN(event_date) over chest pain events`

**Lipid panel present.** The applicant has at least one lipid panel. A lipid panel is a blood test for cholesterol and other fats. Doctors order it at check-ups, so it alone does not show chest pain care. Code: CPT4 80061 (concept_id 2212095).

`lipid_panel_present = event IS lipid panel`

**Venipuncture present.** The applicant has at least one venipuncture. Venipuncture is a blood draw from a vein. It does not show which test. Code: SNOMED 28520004 (concept_id 4102442).

`venipuncture_present = event IS venipuncture for a blood test`

**General examination present.** The applicant has at least one general examination. The general examination is the routine physical examination of a visit. Most patients at a check-up have it. Code: SNOMED 162673000 (concept_id 4036803).

`general_exam_present = event IS general examination of the patient`

**ECG present.** The applicant has at least one ECG. The ECG (electrocardiogram) is a heart tracing. The list holds 5 ECG codes, with or without the report. Code: group `ekg`, 5 concepts (see the member table).

`ecg_present = event IS ECG (any of 5 codes)`

**CMP present.** The applicant has at least one CMP test. The CMP (comprehensive metabolic panel) is a blood chemistry test. It measures kidney function, liver function, and blood salts. Code: SNOMED 371361000119107 (concept_id 3661905).

`cmp_present = event IS comprehensive metabolic panel`

**Hyperlipidemia present.** The applicant has at least one hyperlipidemia diagnosis. Hyperlipidemia is a high level of fats in the blood. The list holds 6 diagnosis codes. It is a step of a sequence, not one of the 5 entities. Code: group `hyperlipidemia`, 6 concepts (see the member table).

`hyperlipidemia_present = event IS hyperlipidemia diagnosis (any of 6 codes)`

**Entity in window.** An entity is in the window when its event is not more than 1 day before or after a chest pain event. The window is 1 day. It is the window of the ED work-up engine.

`workup_window_days = 1`

`<entity>_in_window = <entity>_present AND EXISTS chest pain event date d, entity event date e with |e - d| <= workup_window_days`

There is one predicate for each of the 5 entities: `lipid_panel_in_window`, `venipuncture_in_window`, `general_exam_in_window`, `ecg_in_window`, `cmp_in_window`.

---

### Composites

A composite combines atomic predicates, or other composites, into a named clinical pattern. Composites are in three groups: entities, sequences, and the care pattern.

#### Entities

**Entity count.** This is the number of the 5 entities that are in the window for the applicant.

`checkup_entity_count = lipid_panel_in_window + venipuncture_in_window + general_exam_in_window + ecg_in_window + cmp_in_window`

**Entities.** The applicant has 3 or more of the 5 entities in the window. The value 3 is a draft. It has no calibration yet.

`composite_checkup_entities = checkup_entity_count >= 3`

#### Sequences

A sequence is a list of events in a fixed order. Other events between the steps do not break the sequence. Every sequence starts at a chest pain event. The last step is not more than 1 day after that chest pain event. A step is true for any code of its list.

`sequence_window_days = 1`

The data method found these 3 sequences. They are the 3 patterns of care pattern c0 with the highest lift. Each sequence has 3 steps.

**Sequence A.** The applicant has a chest pain event, then an ECG, then a hyperlipidemia diagnosis.

`composite_seq_ecg_hld = chest_pain -> ecg -> hyperlipidemia`

**Sequence B.** The applicant has a chest pain event, then a general examination, then a lipid panel.

`composite_seq_genexam_lipid = chest_pain -> general_exam -> lipid_panel`

**Sequence C.** The applicant has a chest pain event, then an ECG, then a general examination.

`composite_seq_ecg_genexam = chest_pain -> ecg -> general_exam`

**Sequence of care pattern c0.** The applicant has at least one of the sequences A, B, or C.

`composite_checkup_sequence = composite_seq_ecg_hld OR composite_seq_genexam_lipid OR composite_seq_ecg_genexam`

#### Same-day order

Claims have a date and no time. The engine puts the events of one day in a fixed order: diagnosis, procedure, lab test, then drug. Inside one type, a lower code ID comes first. For a same-day pattern, the order of the steps is a rule. It is not the clock time.

#### Care pattern

**Care pattern c0.** The applicant has chest pain, 3 or more entities in the window, and at least one sequence. This pattern shows the type of care. It does not show a diagnosis. The predicates test that an event happened, not the result.

`composite_checkup_pattern = chest_pain_present AND composite_checkup_entities AND composite_checkup_sequence`

---

## Population Coverage

Counts come from the chest pain cohort of 139,416 patients. The tables come from the k=8 run of the data method (`nmf_k8_chestpain_AHA`). The engine has no measured rate for any predicate or composite yet.

### Entity rates

The rates are for the 31,113 patients of care pattern c0. They count an entity at any time, not only in the window.

| Entity | Patients with the entity | Median day against first chest pain | Share that had it before first chest pain |
| :---- | ----: | :---- | ----: |
| Lipid panel (CPT4 80061) | 81% | 85 d before | 57% |
| Venipuncture (SNOMED 28520004) | 81% | 84 d before | 57% |
| General examination (SNOMED 162673000) | 76% | 104 d before | 57% |
| ECG (code group ekg) | 87% | same day | 27% |
| CMP (SNOMED 371361000119107) | 74% | same day | 49% |

### Sequence rates

The shares count the steps in this order at any time. They do not use the 1-day limit. The other care patterns are a random sample of 1,500 patients.

| Sequence | Patients of c0 | Patients of the other care patterns | Times as common | Held-out pass rate | Verdict |
| :---- | ----: | ----: | ----: | ----: | :---- |
| A. Chest pain, ECG, hyperlipidemia diagnosis | 44.7% | 27.4% | 1.6 | 50% | Unstable |
| B. Chest pain, general examination, lipid panel | 44.6% | 28.3% | 1.6 | 18% | Unstable |
| C. Chest pain, ECG, general examination (same-day order) | 47.3% | 32.5% | 1.4 | 0% | Unstable |

The held-out check repeats the test on random halves of the patients, in 40 runs. No sequence of this care pattern passed it. Read the sequences as a draft.

---

## References

- Gulati M, et al. *2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain.* Circulation 2021;144:e368. doi:10.1161/CIR.0000000000001029.
- McConaghy JR et al. *Acute Chest Pain in Adults: Outpatient Evaluation.* Am Fam Physician 2020. PMID 33320506.
- Chun AA et al. *Bedside diagnosis of coronary artery disease: a systematic review.* Am J Med 2004. PMID 15336583.
- McConaghy JR et al. *Outpatient diagnosis of acute chest pain in adults.* Am Fam Physician 2013. PMID 23418761.
- Hornick J et al. *The Electrocardiogram: Still a Useful Tool in the Primary Care Office.* Med Clin North Am 2019. PMID 31378324.

The papers above come from the literature check of the final table (rating: Partly). They cover the care type. They do not test the order of the steps.
