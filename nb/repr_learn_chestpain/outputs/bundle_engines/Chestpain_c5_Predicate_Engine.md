# Chest Pain Care Pattern c5: Muscle and bone care and physical therapy

*Working Draft — October 2026*

---

## Overview

This document describes the predicates and composites for care pattern c5 of the chest pain predicate engine. The cohort has 139,416 chest pain patients. A data method groups these patients by the care they receive. The method found 8 care patterns. Care pattern c5 is **muscle and bone care and physical therapy**. It has 19,127 patients (13.7%).

This care pattern is physical therapy for pain of muscle and bone. Therapy codes and back pain dominate it. The ED work-up engine ([Chestpain_Workup_Predicate_Engine_v3.md](../Chestpain_Workup_Predicate_Engine_v3.md)) defines the rules. This document applies the same rules to the 5 most frequent entities and to the 3 most specific ordered patterns of care pattern c5. It contains no underwriting logic. It is a draft and has no validation yet.

The draft triage for this care pattern is **Routine**. It comes from the entities and the name of the care pattern. It does not come from the literature. An underwriter reviews it.

The first event of each of the 5 entities has a median between 115 d before and 133 d after against the first chest pain. All 5 entities have a median more than 1 day from the first chest pain. The window of 1 day is short against these medians. The share of patients in the window is not measured. The window needs a calibration before any use.

---

## Predicates and Composites

Each predicate uses a list of codes. The code of each list is in the text. The member table `token_members_k8_chestpain_AHA.csv` shows every concept of a code group.

### Atomic Predicates

A predicate answers one question about the event history of an applicant. It returns true or false. The code and the date are attributes of one event.

**Chest pain present.** The applicant has at least one chest pain event. The list holds chest pain (77670), precordial pain (134159), chest pain on breathing (4168213), and pain of the space between the ribs (42539051).

`chest_pain_present = event IS chest pain diagnosis`

**First chest pain date.** This is the date of the first chest pain event. The engine measures the other dates from this date.

`first_chest_pain_date = MIN(event_date) over chest pain events`

**Therapeutic procedure present.** The applicant has at least one therapeutic procedure. A therapeutic procedure is physical therapy in units of 15 minutes. The list holds the exercise code (97110) and the movement training code (97112). The engine counts them as one service. Code: CPT4 97110 (concept_id 2314284) + CPT4 97112 (concept_id 2314285).

`therapeutic_procedure_present = event IS therapeutic procedure (97110 OR 97112)`

**Manual therapy present.** The applicant has at least one manual therapy session. Manual therapy is hands-on treatment by a therapist, for example joint movement. Code: CPT4 97140 (concept_id 2314290).

`manual_therapy_present = event IS manual therapy techniques`

**Therapeutic activities present.** The applicant has at least one therapeutic activities session. Therapeutic activities are one-on-one physical therapy with movements of daily life. Code: CPT4 97530 (concept_id 2314294).

`therapeutic_activities_present = event IS therapeutic activities`

**Low back pain present.** The applicant has at least one low back pain diagnosis. Low back pain is a diagnosis of pain in the lower back. Code: SNOMED 279039007 (concept_id 194133).

`low_back_pain_present = event IS low back pain diagnosis`

**Therapeutic exercise present.** The applicant has at least one therapeutic exercise session. Therapeutic exercise is physical therapy with exercises, in units of 15 minutes. It is one code of the therapeutic procedure list. It is a step of a sequence, not one of the 4 entities. Code: CPT4 97110 (concept_id 2314284).

`therapeutic_exercise_present = event IS therapeutic exercise (97110)`

**Entity in window.** An entity is in the window when its event is not more than 1 day before or after a chest pain event. The window is 1 day. It is the window of the ED work-up engine.

`workup_window_days = 1`

`<entity>_in_window = <entity>_present AND EXISTS chest pain event date d, entity event date e with |e - d| <= workup_window_days`

There is one predicate for each of the 4 entities: `therapeutic_procedure_in_window`, `manual_therapy_in_window`, `therapeutic_activities_in_window`, `low_back_pain_in_window`.

---

### Composites

A composite combines atomic predicates, or other composites, into a named clinical pattern. Composites are in three groups: entities, sequences, and the care pattern.

#### Entities

**Entity count.** This is the number of the 4 entities that are in the window for the applicant.

`msk_entity_count = therapeutic_procedure_in_window + manual_therapy_in_window + therapeutic_activities_in_window + low_back_pain_in_window`

**Entities.** The applicant has 3 or more of the 4 entities in the window. The value 3 is a draft. It has no calibration yet.

`composite_msk_entities = msk_entity_count >= 3`

#### Sequences

A sequence is a list of events in a fixed order. Other events between the steps do not break the sequence. Every sequence starts at a chest pain event. The last step is not more than 1 day after that chest pain event. A step is true for any code of its list.

`sequence_window_days = 1`

The data method found these 3 sequences. They are the 3 patterns of care pattern c5 with the highest lift. Each sequence has 3 steps.

**Sequence A.** The applicant has a chest pain event, then a manual therapy session, then a therapeutic exercise session.

`composite_seq_manual_ther97110 = chest_pain -> manual_therapy -> therapeutic_exercise`

**Sequence B.** The applicant has a chest pain event, then a manual therapy session, then a second manual therapy session.

`composite_seq_manual_x2 = chest_pain -> manual_therapy -> manual_therapy`

**Sequence C.** The applicant has a chest pain event, then a therapeutic exercise session, then a manual therapy session.

`composite_seq_ther97110_manual = chest_pain -> therapeutic_exercise -> manual_therapy`

**Sequence of care pattern c5.** The applicant has at least one of the sequences A, B, or C.

`composite_msk_sequence = composite_seq_manual_ther97110 OR composite_seq_manual_x2 OR composite_seq_ther97110_manual`

#### Same-day order

Claims have a date and no time. The engine puts the events of one day in a fixed order: diagnosis, procedure, lab test, then drug. Inside one type, a lower code ID comes first. For a same-day pattern, the order of the steps is a rule. It is not the clock time.

#### Care pattern

**Care pattern c5.** The applicant has chest pain, 3 or more entities in the window, and at least one sequence. This pattern shows the type of care. It does not show a diagnosis. The predicates test that an event happened, not the result.

`composite_msk_pattern = chest_pain_present AND composite_msk_entities AND composite_msk_sequence`

---

## Population Coverage

Counts come from the chest pain cohort of 139,416 patients. The tables come from the k=8 run of the data method (`nmf_k8_chestpain_AHA`). The engine has no measured rate for any predicate or composite yet.

### Entity rates

The rates are for the 19,127 patients of care pattern c5. They count an entity at any time, not only in the window.

| Entity | Patients with the entity | Median day against first chest pain | Share that had it before first chest pain |
| :---- | ----: | :---- | ----: |
| Therapeutic procedure (CPT4 97110) | 85% | 36 d before | 52% |
| Manual therapy (CPT4 97140) | 75% | 5 d before | 50% |
| Therapeutic activities (CPT4 97530) | 55% | 132 d after | 42% |
| Low back pain (SNOMED 279039007) | 65% | 115 d before | 56% |
| Therapeutic procedure (CPT4 97112) | 54% | 133 d after | 42% |

### Sequence rates

The shares count the steps in this order at any time. They do not use the 1-day limit. The other care patterns are a random sample of 1,500 patients.

| Sequence | Patients of c5 | Patients of the other care patterns | Times as common | Held-out pass rate | Verdict |
| :---- | ----: | ----: | ----: | ----: | :---- |
| A. Chest pain, manual therapy session, therapeutic exercise session | 45.6% | 6.4% | 6.3 | 100% | Solid |
| B. Chest pain, manual therapy session, second manual therapy session | 47.1% | 6.9% | 6.1 | 100% | Solid |
| C. Chest pain, therapeutic exercise session, manual therapy session | 48.7% | 7.5% | 5.9 | 100% | Solid |

The held-out check repeats the test on random halves of the patients, in 40 runs. All 3 sequences passed it.

---

## References

- Gulati M, et al. *2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain.* Circulation 2021;144:e368. doi:10.1161/CIR.0000000000001029.
- Ayloo A et al. *Evaluation and treatment of musculoskeletal chest pain.* Prim Care 2013. PMID 24209723.
- Burgstaller JM et al. *Treatment efficacy for non-cardiovascular chest pain: a systematic review and meta-analysis.* PLoS One 2014. PMID 25111147.
- Sturm C et al. *[Musculoskeletal-related chest pain].* Internist (Berl) 2017. PMID 27921113.
- Suryavanshi AR et al. *Effect of Diaphragmatic Breathing Exercise, Jacobson's Relaxation Technique and Dynamic Neuromuscular Stabilization on Gastrointestinal and Psychological Causes of Noncardiac Chest Pain: A Randomized Controlled Trial.* Pain Res Manag 2025. PMID 40860980.

The papers above come from the literature check of the final table (rating: Partly). They cover the care type. They do not test the order of the steps.
