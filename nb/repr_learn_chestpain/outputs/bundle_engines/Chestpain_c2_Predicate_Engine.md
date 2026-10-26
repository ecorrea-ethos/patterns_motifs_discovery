# Chest Pain Care Pattern c2: Women's health and urinary tract

*Working Draft — October 2026*

---

## Overview

This document describes the predicates and composites for care pattern c2 of the chest pain predicate engine. The cohort has 139,416 chest pain patients. A data method groups these patients by the care they receive. The method found 8 care patterns. Care pattern c2 is **women's health and urinary tract**. It has 16,770 patients (12.0%).

This care pattern is women's health care and urinary care. Pelvic examination and infection tests dominate it. The ED work-up engine ([Chestpain_Workup_Predicate_Engine_v3.md](../Chestpain_Workup_Predicate_Engine_v3.md)) defines the rules. This document applies the same rules to the 5 most frequent entities and to the 3 most specific ordered patterns of care pattern c2. It contains no underwriting logic. It is a draft and has no validation yet.

The draft triage for this care pattern is **Routine**. It comes from the entities and the name of the care pattern. It does not come from the literature. An underwriter reviews it.

The first event of each of the 5 entities has a median between 193 d before and 97 d before against the first chest pain. All 5 entities have a median more than 1 day from the first chest pain. The window of 1 day is short against these medians. The share of patients in the window is not measured. The window needs a calibration before any use.

The steps of the 3 sequences are not among the 5 entities. They are general steps of care.

---

## Predicates and Composites

Each predicate uses a list of codes. The code of each list is in the text. The member table `token_members_k8_chestpain_AHA.csv` shows every concept of a code group.

### Atomic Predicates

A predicate answers one question about the event history of an applicant. It returns true or false. The code and the date are attributes of one event.

**Chest pain present.** The applicant has at least one chest pain event. The list holds chest pain (77670), precordial pain (134159), chest pain on breathing (4168213), and pain of the space between the ribs (42539051).

`chest_pain_present = event IS chest pain diagnosis`

**First chest pain date.** This is the date of the first chest pain event. The engine measures the other dates from this date.

`first_chest_pain_date = MIN(event_date) over chest pain events`

**Gynecologic examination present.** The applicant has at least one gynecologic examination. The gynecologic examination is the pelvic examination of a woman. It is part of women's check-ups. Code: SNOMED 83607001 (concept_id 4306780).

`gyn_exam_present = event IS gynecologic examination`

**STI test present.** The applicant has at least one STI test. The STI test finds the DNA or RNA of an infection that passes by sex. The list holds the chlamydia code and the gonorrhea code. The engine counts them as one service. Code: CPT4 87491 (concept_id 2213115) + CPT4 87591 (concept_id 2213162).

`sti_nucleic_acid_test_present = event IS STI nucleic acid test (chlamydia OR gonorrhea)`

**Cervical cytology present.** The applicant has at least one cervical cytology test. Cervical cytology is a test of cells from the cervix or the vagina. It is also the Pap test. Code: CPT4 88175 (concept_id 2213244).

`cervical_cytology_present = event IS cervical or vaginal cytology`

**Urine pregnancy test present.** The applicant has at least one urine pregnancy test. The urine pregnancy test is a quick test for a pregnancy. Code: SNOMED 104405006 (concept_id 4014769).

`urine_pregnancy_test_present = event IS urine pregnancy test`

**CBC present.** The applicant has at least one CBC test. The CBC is the complete blood count with a white cell count. It counts the cells of the blood. It is a step of a sequence, not one of the 4 entities. Code: SNOMED 9564003 (concept_id 4319466).

`cbc_present = event IS complete blood count with white cell count`

**Venipuncture present.** The applicant has at least one venipuncture. Venipuncture is a blood draw from a vein. It does not show which test. It is a step of a sequence, not one of the 4 entities. Code: SNOMED 28520004 (concept_id 4102442).

`venipuncture_present = event IS venipuncture for a blood test`

**ECG present.** The applicant has at least one ECG. The ECG (electrocardiogram) is a heart tracing. The list holds 5 ECG codes, with or without the report. It is a step of a sequence, not one of the 4 entities. Code: group `ekg`, 5 concepts (see the member table).

`ecg_present = event IS ECG (any of 5 codes)`

**Entity in window.** An entity is in the window when its event is not more than 1 day before or after a chest pain event. The window is 1 day. It is the window of the ED work-up engine.

`workup_window_days = 1`

`<entity>_in_window = <entity>_present AND EXISTS chest pain event date d, entity event date e with |e - d| <= workup_window_days`

There is one predicate for each of the 4 entities: `gyn_exam_in_window`, `sti_nucleic_acid_test_in_window`, `cervical_cytology_in_window`, `urine_pregnancy_test_in_window`.

---

### Composites

A composite combines atomic predicates, or other composites, into a named clinical pattern. Composites are in three groups: entities, sequences, and the care pattern.

#### Entities

**Entity count.** This is the number of the 4 entities that are in the window for the applicant.

`womens_entity_count = gyn_exam_in_window + sti_nucleic_acid_test_in_window + cervical_cytology_in_window + urine_pregnancy_test_in_window`

**Entities.** The applicant has 3 or more of the 4 entities in the window. The value 3 is a draft. It has no calibration yet.

`composite_womens_entities = womens_entity_count >= 3`

#### Sequences

A sequence is a list of events in a fixed order. Other events between the steps do not break the sequence. Every sequence has one chest pain step. A step after the chest pain step is not more than 1 day after that chest pain event. A step before the chest pain step has no time limit. A step is true for any code of its list.

`sequence_window_days = 1`

The data method found these 3 sequences. They are the 3 patterns of care pattern c2 with the highest lift. Each sequence has 3 steps.

**Sequence A.** The applicant has a chest pain event, then a CBC test, then a venipuncture.

`composite_seq_cbc_venip = chest_pain -> cbc -> venipuncture`

**Sequence B.** The applicant has a chest pain event, then a venipuncture, then a second venipuncture.

`composite_seq_venip_x2 = chest_pain -> venipuncture -> venipuncture`

**Sequence C.** The applicant has a venipuncture, then a chest pain event, then an ECG.

`composite_seq_venip_cp_ecg = venipuncture -> chest_pain -> ecg`

**Sequence of care pattern c2.** The applicant has at least one of the sequences A, B, or C.

`composite_womens_sequence = composite_seq_cbc_venip OR composite_seq_venip_x2 OR composite_seq_venip_cp_ecg`

#### Same-day order

Claims have a date and no time. The engine puts the events of one day in a fixed order: diagnosis, procedure, lab test, then drug. Inside one type, a lower code ID comes first. For a same-day pattern, the order of the steps is a rule. It is not the clock time.

#### Care pattern

**Care pattern c2.** The applicant has chest pain, 3 or more entities in the window, and at least one sequence. This pattern shows the type of care. It does not show a diagnosis. The predicates test that an event happened, not the result.

`composite_womens_pattern = chest_pain_present AND composite_womens_entities AND composite_womens_sequence`

---

## Population Coverage

Counts come from the chest pain cohort of 139,416 patients. The tables come from the k=8 run of the data method (`nmf_k8_chestpain_AHA`). The engine has no measured rate for any predicate or composite yet.

### Entity rates

The rates are for the 16,770 patients of care pattern c2. They count an entity at any time, not only in the window.

| Entity | Patients with the entity | Median day against first chest pain | Share that had it before first chest pain |
| :---- | ----: | :---- | ----: |
| Gynecologic examination (SNOMED 83607001) | 69% | 193 d before | 61% |
| STI test (CPT4 87491) | 65% | 124 d before | 57% |
| STI test (CPT4 87591) | 65% | 124 d before | 57% |
| Cervical cytology (CPT4 88175) | 63% | 97 d before | 55% |
| Urine pregnancy test (SNOMED 104405006) | 63% | 128 d before | 58% |

### Sequence rates

The shares count the steps in this order at any time. They do not use the 1-day limit. The other care patterns are a random sample of 1,500 patients.

| Sequence | Patients of c2 | Patients of the other care patterns | Times as common | Held-out pass rate | Verdict |
| :---- | ----: | ----: | ----: | ----: | :---- |
| A. Chest pain, CBC test, venipuncture | 46.7% | 34.9% | 1.3 | 0% | Unstable |
| B. Chest pain, venipuncture, second venipuncture | 52.9% | 40.4% | 1.3 | 0% | Unstable |
| C. Venipuncture, chest pain, ECG | 51.7% | 39.9% | 1.3 | 0% | Unstable |

The held-out check repeats the test on random halves of the patients, in 40 runs. No sequence of this care pattern passed it. Read the sequences as a draft.

---

## References

- Gulati M, et al. *2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain.* Circulation 2021;144:e368. doi:10.1161/CIR.0000000000001029.
- Cemin R et al. *Blood cells characteristics as determinants of acute myocardial infarction.* Clin Chem Lab Med 2011. PMID 21534844.
- Stopyra JP et al. *EMS blood collection from patients with acute chest pain reduces emergency department length of stay.* Am J Emerg Med 2021. PMID 33964547.

The papers above come from the literature check of the final table (rating: Partly). They cover the care type. They do not test the order of the steps.
