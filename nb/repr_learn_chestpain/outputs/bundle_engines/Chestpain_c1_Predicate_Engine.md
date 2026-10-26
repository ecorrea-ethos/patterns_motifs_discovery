# Chest Pain Care Pattern c1: Prescriptions for acute and chronic illness

*Working Draft — October 2026*

---

## Overview

This document describes the predicates and composites for care pattern c1 of the chest pain predicate engine. The cohort has 139,416 chest pain patients. A data method groups these patients by the care they receive. The method found 8 care patterns. Care pattern c1 is **prescriptions for acute and chronic illness**. It has 24,606 patients (17.6%).

This care pattern is drug care for short illness and long illness. Steroids, antibiotics, and acid drugs dominate it. The ED work-up engine ([Chestpain_Workup_Predicate_Engine_v3.md](../Chestpain_Workup_Predicate_Engine_v3.md)) defines the rules. This document applies the same rules to the 5 most frequent entities and to the 3 most specific ordered patterns of care pattern c1. It contains no underwriting logic. It is a draft and has no validation yet.

The draft triage for this care pattern is **Unclear**. It comes from the entities and the name of the care pattern. It does not come from the literature. An underwriter reviews it.

The first event of each of the 5 entities has a median between 187 d before and 46 d before against the first chest pain. All 5 entities have a median more than 1 day from the first chest pain. The window of 1 day is short against these medians. The share of patients in the window is not measured. The window needs a calibration before any use.

---

## Predicates and Composites

Each predicate uses a list of codes. The code of each list is in the text. The member table `token_members_k8_chestpain_AHA.csv` shows every concept of a code group.

### Atomic Predicates

A predicate answers one question about the event history of an applicant. It returns true or false. The code and the date are attributes of one event.

**Chest pain present.** The applicant has at least one chest pain event. The list holds chest pain (77670), precordial pain (134159), chest pain on breathing (4168213), and pain of the space between the ribs (42539051).

`chest_pain_present = event IS chest pain diagnosis`

**First chest pain date.** This is the date of the first chest pain event. The engine measures the other dates from this date.

`first_chest_pain_date = MIN(event_date) over chest pain events`

**Methylprednisolone present.** The applicant has at least one methylprednisolone prescription. Methylprednisolone is a steroid drug. The code is the 21-tablet dose pack. Code: RxNorm 762675 (concept_id 19129398).

`methylprednisolone_present = event IS methylprednisolone 21-tablet pack`

**Amoxicillin with clavulanate present.** The applicant has at least one amoxicillin with clavulanate prescription. Amoxicillin with clavulanate is an antibiotic. The code is the tablet of 875 mg with 125 mg. Code: RxNorm 562508 (concept_id 19115197).

`amoxicillin_clavulanate_present = event IS amoxicillin 875 mg with clavulanate 125 mg tablet`

**Azithromycin present.** The applicant has at least one azithromycin prescription. Azithromycin is an antibiotic. The code is the pack of 6 tablets of 250 mg. Code: RxNorm 749783 (concept_id 19128020).

`azithromycin_present = event IS azithromycin 6-tablet pack`

**PPI or H2 blocker present.** The applicant has at least one PPI or H2 blocker prescription. A PPI or an H2 blocker is a drug that lowers stomach acid. The list holds 85 drug codes. Code: group `ppi_h2`, 85 concepts (see the member table).

`ppi_h2_present = event IS PPI or H2 blocker drug (any of 85 codes)`

**Prednisone present.** The applicant has at least one prednisone prescription. Prednisone is a steroid drug. The code is the tablet of 20 mg. Code: RxNorm 312615 (concept_id 1551170).

`prednisone_present = event IS prednisone 20 mg tablet`

**ECG present.** The applicant has at least one ECG. The ECG (electrocardiogram) is a heart tracing. The list holds 5 ECG codes, with or without the report. It is a step of a sequence, not one of the 5 entities. Code: group `ekg`, 5 concepts (see the member table).

`ecg_present = event IS ECG (any of 5 codes)`

**Entity in window.** An entity is in the window when its event is not more than 1 day before or after a chest pain event. The window is 1 day. It is the window of the ED work-up engine.

`workup_window_days = 1`

`<entity>_in_window = <entity>_present AND EXISTS chest pain event date d, entity event date e with |e - d| <= workup_window_days`

There is one predicate for each of the 5 entities: `methylprednisolone_in_window`, `amoxicillin_clavulanate_in_window`, `azithromycin_in_window`, `ppi_h2_in_window`, `prednisone_in_window`.

---

### Composites

A composite combines atomic predicates, or other composites, into a named clinical pattern. Composites are in three groups: entities, sequences, and the care pattern.

#### Entities

**Entity count.** This is the number of the 5 entities that are in the window for the applicant.

`rx_entity_count = methylprednisolone_in_window + amoxicillin_clavulanate_in_window + azithromycin_in_window + ppi_h2_in_window + prednisone_in_window`

**Entities.** The applicant has 3 or more of the 5 entities in the window. The value 3 is a draft. It has no calibration yet.

`composite_rx_entities = rx_entity_count >= 3`

#### Sequences

A sequence is a list of events in a fixed order. Other events between the steps do not break the sequence. Every sequence has one chest pain step. A step after the chest pain step is not more than 1 day after that chest pain event. A step before the chest pain step has no time limit. A step is true for any code of its list.

`sequence_window_days = 1`

The data method found these 3 sequences. They are the 3 patterns of care pattern c1 with the highest lift. Each sequence has 3 steps.

**Sequence A.** The applicant has a methylprednisolone prescription, then a chest pain event, then an ECG.

`composite_seq_methylpred_cp_ecg = methylprednisolone -> chest_pain -> ecg`

**Sequence B.** The applicant has an azithromycin prescription, then a chest pain event, then an ECG.

`composite_seq_azithro_cp_ecg = azithromycin -> chest_pain -> ecg`

**Sequence C.** The applicant has a chest pain event, then an ECG, then a methylprednisolone prescription.

`composite_seq_ecg_methylpred = chest_pain -> ecg -> methylprednisolone`

**Sequence of care pattern c1.** The applicant has at least one of the sequences A, B, or C.

`composite_rx_sequence = composite_seq_methylpred_cp_ecg OR composite_seq_azithro_cp_ecg OR composite_seq_ecg_methylpred`

#### Same-day order

Claims have a date and no time. The engine puts the events of one day in a fixed order: diagnosis, procedure, lab test, then drug. Inside one type, a lower code ID comes first. For a same-day pattern, the order of the steps is a rule. It is not the clock time.

#### Care pattern

**Care pattern c1.** The applicant has chest pain, 3 or more entities in the window, and at least one sequence. This pattern shows the type of care. It does not show a diagnosis. The predicates test that an event happened, not the result.

`composite_rx_pattern = chest_pain_present AND composite_rx_entities AND composite_rx_sequence`

---

## Population Coverage

Counts come from the chest pain cohort of 139,416 patients. The tables come from the k=8 run of the data method (`nmf_k8_chestpain_AHA`). The engine has no measured rate for any predicate or composite yet.

### Entity rates

The rates are for the 24,606 patients of care pattern c1. They count an entity at any time, not only in the window.

| Entity | Patients with the entity | Median day against first chest pain | Share that had it before first chest pain |
| :---- | ----: | :---- | ----: |
| Methylprednisolone (RxNorm 762675) | 55% | 83 d before | 54% |
| Amoxicillin with clavulanate (RxNorm 562508) | 55% | 97 d before | 54% |
| Azithromycin (RxNorm 749783) | 54% | 187 d before | 59% |
| PPI or H2 blocker (code group ppi_h2) | 52% | 109 d before | 56% |
| Prednisone (RxNorm 312615) | 49% | 46 d before | 53% |

### Sequence rates

The shares count the steps in this order at any time. They do not use the 1-day limit. The other care patterns are a random sample of 1,500 patients.

| Sequence | Patients of c1 | Patients of the other care patterns | Times as common | Held-out pass rate | Verdict |
| :---- | ----: | ----: | ----: | ----: | :---- |
| A. Methylprednisolone prescription, chest pain, ECG (same-day order) | 24.4% | 4.9% | 4.3 | 100% | Suggestive |
| B. Azithromycin prescription, chest pain, ECG (same-day order) | 26.3% | 7.1% | 3.4 | 100% | Suggestive |
| C. Chest pain, ECG, methylprednisolone prescription (same-day order) | 26.0% | 7.5% | 3.2 | 100% | Suggestive |

The held-out check repeats the test on random halves of the patients, in 40 runs. All 3 sequences passed it.

---

## References

- Gulati M, et al. *2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain.* Circulation 2021;144:e368. doi:10.1161/CIR.0000000000001029.
- Jaiswal V et al. *COVID-19 Infection and Myocarditis: A State-of-the-Art Systematic Review.* J Prim Care Community Health 2021. PMID 34854348.
- Cremer PC et al. *Diagnosis, Risk Stratification, and Treatment of Pericarditis: A Review.* JAMA 2024. PMID 39235771.
- Imazio M et al. *Evaluation and Treatment of Pericarditis: A Systematic Review.* JAMA 2015. PMID 26461998.

The papers above come from the literature check of the final table (rating: Partly). They cover the care type. They do not test the order of the steps.
