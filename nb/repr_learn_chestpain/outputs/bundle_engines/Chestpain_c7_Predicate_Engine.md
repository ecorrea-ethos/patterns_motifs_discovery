# Chest Pain Care Pattern c7: Acute respiratory infection

*Working Draft — October 2026*

---

## Overview

This document describes the predicates and composites for care pattern c7 of the chest pain predicate engine. The cohort has 139,416 chest pain patients. A data method groups these patients by the care they receive. The method found 8 care patterns. Care pattern c7 is **acute respiratory infection**. It has 11,154 patients (8.0%).

This care pattern is care of a cold, a sore throat, or a similar infection. Cough, infection diagnoses, and rapid tests dominate it. The ED work-up engine ([Chestpain_Workup_Predicate_Engine_v3.md](../Chestpain_Workup_Predicate_Engine_v3.md)) defines the rules. This document applies the same rules to the 5 most frequent entities and to the 3 most specific ordered patterns of care pattern c7. It contains no underwriting logic. It is a draft and has no validation yet.

The draft triage for this care pattern is **Routine**. It comes from the entities and the name of the care pattern. It does not come from the literature. An underwriter reviews it.

The first event of each of the 5 entities has a median between 18 d before and same day against the first chest pain. 1 of the 5 entities have a median more than 1 day from the first chest pain. The window of 1 day is short against these medians. The share of patients in the window is not measured. The window needs a calibration before any use.

---

## Predicates and Composites

Each predicate uses a list of codes. The code of each list is in the text. The member table `token_members_k8_chestpain_AHA.csv` shows every concept of a code group.

### Atomic Predicates

A predicate answers one question about the event history of an applicant. It returns true or false. The code and the date are attributes of one event.

**Chest pain present.** The applicant has at least one chest pain event. The list holds chest pain (77670), precordial pain (134159), chest pain on breathing (4168213), and pain of the space between the ribs (42539051).

`chest_pain_present = event IS chest pain diagnosis`

**First chest pain date.** This is the date of the first chest pain event. The engine measures the other dates from this date.

`first_chest_pain_date = MIN(event_date) over chest pain events`

**Cough present.** The applicant has at least one cough diagnosis. Cough is a diagnosis of a cough. Code: SNOMED 49727002 (concept_id 254761).

`cough_present = event IS cough diagnosis`

**Acute upper respiratory infection present.** The applicant has at least one acute upper respiratory infection diagnosis. Acute upper respiratory infection is a cold or a similar infection of the nose and throat. Code: SNOMED 54398005 (concept_id 257011).

`upper_respiratory_infection_present = event IS acute upper respiratory infection diagnosis`

**Acute pharyngitis present.** The applicant has at least one acute pharyngitis diagnosis. Acute pharyngitis is a sore throat from an infection. Code: SNOMED 363746003 (concept_id 25297).

`pharyngitis_present = event IS acute pharyngitis diagnosis`

**Rapid antigen test present.** The applicant has at least one rapid antigen test. A rapid antigen test finds an infection by a protein of the germ. The list holds 2 codes (87880 and 87804). The engine counts them as one service. Code: CPT4 87880 (concept_id 2213187) + CPT4 87804 (concept_id 2213181).

`rapid_antigen_test_present = event IS rapid antigen test (87880 OR 87804)`

**ECG present.** The applicant has at least one ECG. The ECG (electrocardiogram) is a heart tracing. The list holds 5 ECG codes, with or without the report. It is a step of a sequence, not one of the 4 entities. Code: group `ekg`, 5 concepts (see the member table).

`ecg_present = event IS ECG (any of 5 codes)`

**Entity in window.** An entity is in the window when its event is not more than 1 day before or after a chest pain event. The window is 1 day. It is the window of the ED work-up engine.

`workup_window_days = 1`

`<entity>_in_window = <entity>_present AND EXISTS chest pain event date d, entity event date e with |e - d| <= workup_window_days`

There is one predicate for each of the 4 entities: `cough_in_window`, `upper_respiratory_infection_in_window`, `pharyngitis_in_window`, `rapid_antigen_test_in_window`.

---

### Composites

A composite combines atomic predicates, or other composites, into a named clinical pattern. Composites are in three groups: entities, sequences, and the care pattern.

#### Entities

**Entity count.** This is the number of the 4 entities that are in the window for the applicant.

`resp_entity_count = cough_in_window + upper_respiratory_infection_in_window + pharyngitis_in_window + rapid_antigen_test_in_window`

**Entities.** The applicant has 3 or more of the 4 entities in the window. The value 3 is a draft. It has no calibration yet.

`composite_resp_entities = resp_entity_count >= 3`

#### Sequences

A sequence is a list of events in a fixed order. Other events between the steps do not break the sequence. Every sequence has one chest pain step. A step after the chest pain step is not more than 1 day after that chest pain event. A step before the chest pain step has no time limit. A step is true for any code of its list.

`sequence_window_days = 1`

The data method found these 3 sequences. They are the 3 patterns of care pattern c7 with the highest lift. Each sequence has 3 steps.

**Sequence A.** The applicant has an acute pharyngitis diagnosis, then a chest pain event, then an ECG.

`composite_seq_pharyngitis_cp_ecg = pharyngitis -> chest_pain -> ecg`

**Sequence B.** The applicant has a chest pain event, then an ECG, then an acute upper respiratory infection diagnosis.

`composite_seq_ecg_uri = chest_pain -> ecg -> upper_respiratory_infection`

**Sequence C.** The applicant has a cough diagnosis, then a chest pain event, then an ECG.

`composite_seq_cough_cp_ecg = cough -> chest_pain -> ecg`

**Sequence of care pattern c7.** The applicant has at least one of the sequences A, B, or C.

`composite_resp_sequence = composite_seq_pharyngitis_cp_ecg OR composite_seq_ecg_uri OR composite_seq_cough_cp_ecg`

#### Same-day order

Claims have a date and no time. The engine puts the events of one day in a fixed order: diagnosis, procedure, lab test, then drug. Inside one type, a lower code ID comes first. For a same-day pattern, the order of the steps is a rule. It is not the clock time.

#### Care pattern

**Care pattern c7.** The applicant has chest pain, 3 or more entities in the window, and at least one sequence. This pattern shows the type of care. It does not show a diagnosis. The predicates test that an event happened, not the result.

`composite_resp_pattern = chest_pain_present AND composite_resp_entities AND composite_resp_sequence`

---

## Population Coverage

Counts come from the chest pain cohort of 139,416 patients. The tables come from the k=8 run of the data method (`nmf_k8_chestpain_AHA`). The engine has no measured rate for any predicate or composite yet.

### Entity rates

The rates are for the 11,154 patients of care pattern c7. They count an entity at any time, not only in the window.

| Entity | Patients with the entity | Median day against first chest pain | Share that had it before first chest pain |
| :---- | ----: | :---- | ----: |
| Cough (SNOMED 49727002) | 66% | 18 d before | 53% |
| Acute upper respiratory infection (SNOMED 54398005) | 60% | same day | 48% |
| Acute pharyngitis (SNOMED 363746003) | 61% | same day | 49% |
| Rapid antigen test (CPT4 87880) | 55% | same day | 48% |
| Rapid antigen test (CPT4 87804) | 53% | same day | 48% |

### Sequence rates

The shares count the steps in this order at any time. They do not use the 1-day limit. The other care patterns are a random sample of 1,500 patients.

| Sequence | Patients of c7 | Patients of the other care patterns | Times as common | Held-out pass rate | Verdict |
| :---- | ----: | ----: | ----: | ----: | :---- |
| A. Acute pharyngitis diagnosis, chest pain, ECG | 30.6% | 10.6% | 2.7 | 100% | Solid |
| B. Chest pain, ECG, acute upper respiratory infection diagnosis | 30.1% | 13.1% | 2.2 | 100% | Solid |
| C. Cough diagnosis, chest pain, ECG | 32.5% | 15.5% | 2.0 | 100% | Solid |

The held-out check repeats the test on random halves of the patients, in 40 runs. All 3 sequences passed it.

---

## References

- Gulati M, et al. *2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain.* Circulation 2021;144:e368. doi:10.1161/CIR.0000000000001029.
- Schmutzler L et al. *From Streptococcal Pharyngitis/Tonsillitis to Myocarditis: A Systematic Review.* J Cardiovasc Dev Dis 2022. PMID 35735799.
- Jaiswal V et al. *COVID-19 Infection and Myocarditis: A State-of-the-Art Systematic Review.* J Prim Care Community Health 2021. PMID 34854348.

The papers above come from the literature check of the final table (rating: Partly). They cover the care type. They do not test the order of the steps.
