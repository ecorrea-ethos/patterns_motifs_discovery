# Chest Pain Care Pattern c4: Stomach and bowel work-up and cancer screening

*Working Draft — October 2026*

---

## Overview

This document describes the predicates and composites for care pattern c4 of the chest pain predicate engine. The cohort has 139,416 chest pain patients. A data method groups these patients by the care they receive. The method found 8 care patterns. Care pattern c4 is **stomach and bowel work-up and cancer screening**. It has 8,409 patients (6.0%).

This care pattern is care of the stomach and the bowel. Biopsy, pathology, and screening dominate it. The ED work-up engine ([Chestpain_Workup_Predicate_Engine_v3.md](../Chestpain_Workup_Predicate_Engine_v3.md)) defines the rules. This document applies the same rules to the 5 most frequent entities and to the 3 most specific ordered patterns of care pattern c4. It contains no underwriting logic. It is a draft and has no validation yet.

The draft triage for this care pattern is **Routine**. It comes from the entities and the name of the care pattern. It does not come from the literature. An underwriter reviews it.

The first event of each of the 5 entities has a median between 175 d before and 61 d after against the first chest pain. 4 of the 5 entities have a median more than 1 day from the first chest pain. The window of 1 day is short against these medians. The share of patients in the window is not measured. The window needs a calibration before any use.

---

## Predicates and Composites

Each predicate uses a list of codes. The code of each list is in the text. The member table `token_members_k8_chestpain_AHA.csv` shows every concept of a code group.

### Atomic Predicates

A predicate answers one question about the event history of an applicant. It returns true or false. The code and the date are attributes of one event.

**Chest pain present.** The applicant has at least one chest pain event. The list holds chest pain (77670), precordial pain (134159), chest pain on breathing (4168213), and pain of the space between the ribs (42539051).

`chest_pain_present = event IS chest pain diagnosis`

**First chest pain date.** This is the date of the first chest pain event. The engine measures the other dates from this date.

`first_chest_pain_date = MIN(event_date) over chest pain events`

**Surgical pathology present.** The applicant has at least one surgical pathology exam. Surgical pathology is the study of a tissue sample by eye and under a microscope. A biopsy gives such a sample. Code: CPT4 88305 (concept_id 2213283).

`surgical_pathology_present = event IS surgical pathology level IV`

**Colon cancer screening present.** The applicant has at least one colon cancer screening. Colon cancer screening is a test for colon cancer in a person with no symptoms. Code: SNOMED 275978004 (concept_id 4175226).

`colon_cancer_screening_present = event IS screening for malignant neoplasm of colon`

**Upper endoscopy with biopsy present.** The applicant has at least one upper endoscopy with biopsy. Upper endoscopy is a look into the food pipe and the stomach with a camera. The doctor also takes a tissue sample. Code: SNOMED 445982009 (concept_id 40485932).

`upper_endoscopy_biopsy_present = event IS endoscopy and biopsy of the upper gastrointestinal tract`

**GERD present.** The applicant has at least one GERD diagnosis. GERD is acid reflux from the stomach into the food pipe. The list holds 4 diagnosis codes, and heartburn is one of them. Code: group `gerd`, 4 concepts (see the member table).

`gerd_present = event IS GERD diagnosis (any of 4 codes)`

**Periodic preventive visit present.** The applicant has at least one periodic preventive visit. The periodic preventive visit is the check-up of an adult of 40 to 64 years. Code: CPT4 99396 (concept_id 2514528).

`periodic_preventive_visit_present = event IS periodic comprehensive preventive visit (99396)`

**Entity in window.** An entity is in the window when its event is not more than 1 day before or after a chest pain event. The window is 1 day. It is the window of the ED work-up engine.

`workup_window_days = 1`

`<entity>_in_window = <entity>_present AND EXISTS chest pain event date d, entity event date e with |e - d| <= workup_window_days`

There is one predicate for each of the 5 entities: `surgical_pathology_in_window`, `colon_cancer_screening_in_window`, `upper_endoscopy_biopsy_in_window`, `gerd_in_window`, `periodic_preventive_visit_in_window`.

---

### Composites

A composite combines atomic predicates, or other composites, into a named clinical pattern. Composites are in three groups: entities, sequences, and the care pattern.

#### Entities

**Entity count.** This is the number of the 5 entities that are in the window for the applicant.

`gi_entity_count = surgical_pathology_in_window + colon_cancer_screening_in_window + upper_endoscopy_biopsy_in_window + gerd_in_window + periodic_preventive_visit_in_window`

**Entities.** The applicant has 3 or more of the 5 entities in the window. The value 3 is a draft. It has no calibration yet.

`composite_gi_entities = gi_entity_count >= 3`

#### Sequences

A sequence is a list of events in a fixed order. Other events between the steps do not break the sequence. Every sequence starts at a chest pain event. The last step is not more than 1 day after that chest pain event. A step is true for any code of its list.

`sequence_window_days = 1`

The data method found these 3 sequences. They are the 3 patterns of care pattern c4 with the highest lift. Each sequence has 3 steps.

**Sequence A.** The applicant has a chest pain event, then a GERD diagnosis, then an upper endoscopy with biopsy.

`composite_seq_gerd_egd = chest_pain -> gerd -> upper_endoscopy_biopsy`

**Sequence B.** The applicant has a chest pain event, then a surgical pathology exam, then an upper endoscopy with biopsy.

`composite_seq_path_egd = chest_pain -> surgical_pathology -> upper_endoscopy_biopsy`

**Sequence C.** The applicant has a chest pain event, then a GERD diagnosis, then a surgical pathology exam.

`composite_seq_gerd_path = chest_pain -> gerd -> surgical_pathology`

**Sequence of care pattern c4.** The applicant has at least one of the sequences A, B, or C.

`composite_gi_sequence = composite_seq_gerd_egd OR composite_seq_path_egd OR composite_seq_gerd_path`

#### Same-day order

Claims have a date and no time. The engine puts the events of one day in a fixed order: diagnosis, procedure, lab test, then drug. Inside one type, a lower code ID comes first. For a same-day pattern, the order of the steps is a rule. It is not the clock time.

#### Care pattern

**Care pattern c4.** The applicant has chest pain, 3 or more entities in the window, and at least one sequence. This pattern shows the type of care. It does not show a diagnosis. The predicates test that an event happened, not the result.

`composite_gi_pattern = chest_pain_present AND composite_gi_entities AND composite_gi_sequence`

---

## Population Coverage

Counts come from the chest pain cohort of 139,416 patients. The tables come from the k=8 run of the data method (`nmf_k8_chestpain_AHA`). The engine has no measured rate for any predicate or composite yet.

### Entity rates

The rates are for the 8,409 patients of care pattern c4. They count an entity at any time, not only in the window.

| Entity | Patients with the entity | Median day against first chest pain | Share that had it before first chest pain |
| :---- | ----: | :---- | ----: |
| Surgical pathology (CPT4 88305) | 83% | 8 d after | 48% |
| Colon cancer screening (SNOMED 275978004) | 68% | 55 d after | 42% |
| Upper endoscopy with biopsy (SNOMED 445982009) | 63% | 61 d after | 37% |
| GERD (code group gerd) | 70% | same day | 49% |
| Periodic preventive visit (CPT4 99396) | 61% | 175 d before | 59% |

### Sequence rates

The shares count the steps in this order at any time. They do not use the 1-day limit. The other care patterns are a random sample of 1,500 patients.

| Sequence | Patients of c4 | Patients of the other care patterns | Times as common | Held-out pass rate | Verdict |
| :---- | ----: | ----: | ----: | ----: | :---- |
| A. Chest pain, GERD diagnosis, upper endoscopy with biopsy | 37.7% | 6.0% | 5.5 | 100% | Solid |
| B. Chest pain, surgical pathology exam, upper endoscopy with biopsy (same-day order) | 39.1% | 6.4% | 5.4 | 100% | Suggestive |
| C. Chest pain, GERD diagnosis, surgical pathology exam | 41.1% | 8.6% | 4.4 | 100% | Solid |

The held-out check repeats the test on random halves of the patients, in 40 runs. All 3 sequences passed it.

---

## References

- Gulati M, et al. *2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain.* Circulation 2021;144:e368. doi:10.1161/CIR.0000000000001029.
- Yadlapati R et al. *AGA Clinical Practice Update on the Personalized Approach to the Evaluation and Management of GERD: Expert Review.* Clin Gastroenterol Hepatol 2022. PMID 35123084.
- Cremonini F et al. *Diagnostic and therapeutic use of proton pump inhibitors in non-cardiac chest pain: a metaanalysis.* Am J Gastroenterol 2005. PMID 15929749.
- Attwood SE et al. *Overview of eosinophilic oesophagitis.* Br J Hosp Med (Lond) 2019. PMID 30860925.

The papers above come from the literature check of the final table (rating: Partly). They cover the care type. They do not test the order of the steps.
