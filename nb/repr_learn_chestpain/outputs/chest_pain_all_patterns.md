# Chest Pain Predicates and Composites: All Care Patterns

*Working Draft — October 2026*

---

## Overview

This document defines the predicates and composites for chest pain applicants. It is one page for all care patterns. The cohort has 139,416 chest pain patients. A data method groups these patients by the care they receive. The method found 8 care patterns, c0 to c7. Each predicate has one definition, and all care patterns use it.

The same rules apply to every care pattern. An entity is one of the 5 most frequent entities of the care pattern. The entity is in the window when its event is not more than 1 day from a chest pain event. A care pattern needs 3 or more entities in the window and one of its 3 ordered sequences. The sequences are the 3 patterns with the highest lift.

The document contains no underwriting logic and no product decision. It is a clinical grouping of codes. It is a draft and has no validation yet.

| Care pattern | Name | Patients | % cohort |
| :---- | :---- | ----: | ----: |
| c0 | outpatient check-up and elective cardiac testing | 31,113 | 22.3% |
| c1 | prescriptions for acute and chronic illness | 24,606 | 17.6% |
| c2 | women's health and urinary tract | 16,770 | 12.0% |
| c3 | ED work-up | 17,250 | 12.4% |
| c4 | stomach and bowel work-up and cancer screening | 8,409 | 6.0% |
| c5 | muscle and bone care and physical therapy | 19,127 | 13.7% |
| c6 | nutrition and hormone blood tests | 10,987 | 7.9% |
| c7 | acute respiratory infection | 11,154 | 8.0% |

---

## Predicates and Composites

Each predicate uses a list of codes. The code is in the text. The member table `token_members_k8_chestpain_AHA.csv` shows every concept of a code group.

### Atomic Predicates

A predicate answers one question about the event history of an applicant. It returns true or false. The code and the date are attributes of one event.

**Chest pain present.** The applicant has at least one chest pain event. The list holds chest pain (77670), precordial pain (134159), chest pain on breathing (4168213), and pain of the space between the ribs (42539051). All care patterns use it.

`chest_pain_present = event IS chest pain diagnosis`

**First chest pain date.** This is the date of the first chest pain event. The engine measures the other dates from this date.

`first_chest_pain_date = MIN(event_date) over chest pain events`

#### Diagnoses

**Hyperlipidemia present.** The applicant has at least one hyperlipidemia diagnosis. Hyperlipidemia is a high level of fats in the blood. The list holds 6 diagnosis codes. Code: group `hyperlipidemia`, 6 concepts (see the member table); care patterns: c0 (step).

`hyperlipidemia_present = event IS hyperlipidemia diagnosis (any of 6 codes)`

**GERD present.** The applicant has at least one GERD diagnosis. GERD is acid reflux from the stomach into the food pipe. The list holds 4 diagnosis codes, and heartburn is one of them. Code: group `gerd`, 4 concepts (see the member table); care patterns: c4 (entity and step).

`gerd_present = event IS GERD diagnosis (any of 4 codes)`

**Low back pain present.** The applicant has at least one low back pain diagnosis. Low back pain is a diagnosis of pain in the lower back. Code: SNOMED 279039007 (concept_id 194133); care patterns: c5 (entity).

`low_back_pain_present = event IS low back pain diagnosis`

**Cough present.** The applicant has at least one cough diagnosis. Cough is a diagnosis of a cough. Code: SNOMED 49727002 (concept_id 254761); care patterns: c7 (entity and step).

`cough_present = event IS cough diagnosis`

**Acute upper respiratory infection present.** The applicant has at least one acute upper respiratory infection diagnosis. Acute upper respiratory infection is a cold or a similar infection of the nose and throat. Code: SNOMED 54398005 (concept_id 257011); care patterns: c7 (entity and step).

`upper_respiratory_infection_present = event IS acute upper respiratory infection diagnosis`

**Acute pharyngitis present.** The applicant has at least one acute pharyngitis diagnosis. Acute pharyngitis is a sore throat from an infection. Code: SNOMED 363746003 (concept_id 25297); care patterns: c7 (entity and step).

`pharyngitis_present = event IS acute pharyngitis diagnosis`

#### Lab tests

**Troponin present.** The applicant has at least one troponin test. Troponin is a blood test for injury to the heart muscle. The data does not show the type of test. A high-sensitivity test and a standard test look the same. Code: group `troponin`, 2 concepts (see the member table); care patterns: c3 (entity and step).

`troponin_present = event IS troponin test`

**Lipase present.** The applicant has at least one lipase test. Lipase is a blood test for the pancreas. Doctors also use it for abdominal pain. Code: SNOMED 104988000 (concept_id 4021288); care patterns: c3 (entity).

`lipase_present = event IS lipase test`

**Lipid panel present.** The applicant has at least one lipid panel. A lipid panel is a blood test for cholesterol and other fats. Doctors order it at check-ups, so it alone does not show chest pain care. Code: CPT4 80061 (concept_id 2212095); care patterns: c0 (entity and step), c6 (step).

`lipid_panel_present = event IS lipid panel`

**Venipuncture present.** The applicant has at least one venipuncture. Venipuncture is a blood draw from a vein. It does not show which test. Code: SNOMED 28520004 (concept_id 4102442); care patterns: c0 (entity), c2 (step).

`venipuncture_present = event IS venipuncture for a blood test`

**CMP present.** The applicant has at least one CMP test. The CMP (comprehensive metabolic panel) is a blood chemistry test. It measures kidney function, liver function, and blood salts. Code: SNOMED 371361000119107 (concept_id 3661905); care patterns: c0 (entity), c3 (step).

`cmp_present = event IS comprehensive metabolic panel`

**CBC present.** The applicant has at least one CBC test. The CBC is the complete blood count with a white cell count. It counts the cells of the blood. Code: SNOMED 9564003 (concept_id 4319466); care patterns: c2 (step), c3 (step).

`cbc_present = event IS complete blood count with white cell count`

**HbA1c present.** The applicant has at least one HbA1c test. HbA1c is a blood test for the average blood sugar of the last 3 months. The list holds 1 code. Code: group `hba1c`, 1 concepts (see the member table); care patterns: c6 (step).

`hba1c_present = event IS HbA1c test`

**Vitamin B12 present.** The applicant has at least one vitamin B12 test. Vitamin B12 is a blood test for the level of this vitamin. Code: SNOMED 14598005 (concept_id 4032173); care patterns: c6 (entity).

`vitamin_b12_present = event IS vitamin B12 measurement`

**Vitamin D present.** The applicant has at least one vitamin D test. The vitamin D test measures 25-hydroxy vitamin D in the blood. Code: SNOMED 12199005 (concept_id 4007831); care patterns: c6 (entity and step).

`vitamin_d_present = event IS 25-hydroxy vitamin D measurement`

**Free T4 present.** The applicant has at least one free T4 test. Free T4 is a blood test for the level of the thyroid hormone. Code: SNOMED 5113004 (concept_id 4196969); care patterns: c6 (entity).

`free_t4_present = event IS free T4 measurement`

**Iron present.** The applicant has at least one iron test. The iron test measures the iron of the blood. Code: SNOMED 42950004 (concept_id 4178785); care patterns: c6 (entity).

`iron_present = event IS iron measurement`

**Ferritin present.** The applicant has at least one ferritin test. Ferritin is a blood test for the iron stores of the body. Code: SNOMED 489004 (concept_id 4176561); care patterns: c6 (entity).

`ferritin_present = event IS ferritin measurement`

**Urine pregnancy test present.** The applicant has at least one urine pregnancy test. The urine pregnancy test is a quick test for a pregnancy. Code: SNOMED 104405006 (concept_id 4014769); care patterns: c2 (entity).

`urine_pregnancy_test_present = event IS urine pregnancy test`

**STI test present.** The applicant has at least one STI test. The STI test finds the DNA or RNA of an infection that passes by sex. The list holds the chlamydia code and the gonorrhea code. The engine counts them as one service. Code: CPT4 87491 (concept_id 2213115) + CPT4 87591 (concept_id 2213162); care patterns: c2 (entity).

`sti_nucleic_acid_test_present = event IS STI nucleic acid test (chlamydia OR gonorrhea)`

**Cervical cytology present.** The applicant has at least one cervical cytology test. Cervical cytology is a test of cells from the cervix or the vagina. It is also the Pap test. Code: CPT4 88175 (concept_id 2213244); care patterns: c2 (entity).

`cervical_cytology_present = event IS cervical or vaginal cytology`

**Rapid antigen test present.** The applicant has at least one rapid antigen test. A rapid antigen test finds an infection by a protein of the germ. The list holds 2 codes (87880 and 87804). The engine counts them as one service. Code: CPT4 87880 (concept_id 2213187) + CPT4 87804 (concept_id 2213181); care patterns: c7 (entity).

`rapid_antigen_test_present = event IS rapid antigen test (87880 OR 87804)`

**Surgical pathology present.** The applicant has at least one surgical pathology exam. Surgical pathology is the study of a tissue sample by eye and under a microscope. A biopsy gives such a sample. Code: CPT4 88305 (concept_id 2213283); care patterns: c4 (entity and step).

`surgical_pathology_present = event IS surgical pathology level IV`

#### Procedures, imaging, and visits

**ECG present.** The applicant has at least one ECG. The ECG (electrocardiogram) is a heart tracing. The list holds 5 ECG codes, with or without the report. Code: group `ekg`, 5 concepts (see the member table); care patterns: c0 (entity and step), c1 (step), c2 (step), c3 (step), c6 (step), c7 (step).

`ecg_present = event IS ECG (any of 5 codes)`

**Chest X-ray present.** The applicant has at least one chest X-ray. The list holds X-rays of 1, 2, 3, and 4 or more views. Code: group `chest_xray`, 4 concepts (see the member table); care patterns: c3 (entity and step).

`cxr_present = event IS chest X-ray`

**IV push present.** The applicant has at least one IV push. An IV push puts a drug into a vein with a syringe. The list holds the first drug and each additional drug. The engine counts them as one service. Code: CPT4 96374 (concept_id 2314215) + CPT4 96375 (concept_id 2314216); care patterns: c3 (entity).

`iv_push_present = event IS IV push (first drug OR each additional drug)`

**General examination present.** The applicant has at least one general examination. The general examination is the routine physical examination of a visit. Most patients at a check-up have it. Code: SNOMED 162673000 (concept_id 4036803); care patterns: c0 (entity and step).

`general_exam_present = event IS general examination of the patient`

**Gynecologic examination present.** The applicant has at least one gynecologic examination. The gynecologic examination is the pelvic examination of a woman. It is part of women's check-ups. Code: SNOMED 83607001 (concept_id 4306780); care patterns: c2 (entity).

`gyn_exam_present = event IS gynecologic examination`

**Periodic preventive visit present.** The applicant has at least one periodic preventive visit. The periodic preventive visit is the check-up of an adult of 40 to 64 years. Code: CPT4 99396 (concept_id 2514528); care patterns: c4 (entity).

`periodic_preventive_visit_present = event IS periodic comprehensive preventive visit (99396)`

**Colon cancer screening present.** The applicant has at least one colon cancer screening. Colon cancer screening is a test for colon cancer in a person with no symptoms. Code: SNOMED 275978004 (concept_id 4175226); care patterns: c4 (entity).

`colon_cancer_screening_present = event IS screening for malignant neoplasm of colon`

**Upper endoscopy with biopsy present.** The applicant has at least one upper endoscopy with biopsy. Upper endoscopy is a look into the food pipe and the stomach with a camera. The doctor also takes a tissue sample. Code: SNOMED 445982009 (concept_id 40485932); care patterns: c4 (entity and step).

`upper_endoscopy_biopsy_present = event IS endoscopy and biopsy of the upper gastrointestinal tract`

**Therapeutic procedure present.** The applicant has at least one therapeutic procedure. A therapeutic procedure is physical therapy in units of 15 minutes. The list holds the exercise code (97110) and the movement training code (97112). The engine counts them as one service. Code: CPT4 97110 (concept_id 2314284) + CPT4 97112 (concept_id 2314285); care patterns: c5 (entity).

`therapeutic_procedure_present = event IS therapeutic procedure (97110 OR 97112)`

**Therapeutic exercise present.** The applicant has at least one therapeutic exercise session. Therapeutic exercise is physical therapy with exercises, in units of 15 minutes. It is one code of the therapeutic procedure list. Code: CPT4 97110 (concept_id 2314284); care patterns: c5 (step).

`therapeutic_exercise_present = event IS therapeutic exercise (97110)`

**Manual therapy present.** The applicant has at least one manual therapy session. Manual therapy is hands-on treatment by a therapist, for example joint movement. Code: CPT4 97140 (concept_id 2314290); care patterns: c5 (entity and step).

`manual_therapy_present = event IS manual therapy techniques`

**Therapeutic activities present.** The applicant has at least one therapeutic activities session. Therapeutic activities are one-on-one physical therapy with movements of daily life. Code: CPT4 97530 (concept_id 2314294); care patterns: c5 (entity).

`therapeutic_activities_present = event IS therapeutic activities`

#### Drugs

**Methylprednisolone present.** The applicant has at least one methylprednisolone prescription. Methylprednisolone is a steroid drug. The code is the 21-tablet dose pack. Code: RxNorm 762675 (concept_id 19129398); care patterns: c1 (entity and step).

`methylprednisolone_present = event IS methylprednisolone 21-tablet pack`

**Amoxicillin with clavulanate present.** The applicant has at least one amoxicillin with clavulanate prescription. Amoxicillin with clavulanate is an antibiotic. The code is the tablet of 875 mg with 125 mg. Code: RxNorm 562508 (concept_id 19115197); care patterns: c1 (entity).

`amoxicillin_clavulanate_present = event IS amoxicillin 875 mg with clavulanate 125 mg tablet`

**Azithromycin present.** The applicant has at least one azithromycin prescription. Azithromycin is an antibiotic. The code is the pack of 6 tablets of 250 mg. Code: RxNorm 749783 (concept_id 19128020); care patterns: c1 (entity and step).

`azithromycin_present = event IS azithromycin 6-tablet pack`

**PPI or H2 blocker present.** The applicant has at least one PPI or H2 blocker prescription. A PPI or an H2 blocker is a drug that lowers stomach acid. The list holds 85 drug codes. Code: group `ppi_h2`, 85 concepts (see the member table); care patterns: c1 (entity).

`ppi_h2_present = event IS PPI or H2 blocker drug (any of 85 codes)`

**Prednisone present.** The applicant has at least one prednisone prescription. Prednisone is a steroid drug. The code is the tablet of 20 mg. Code: RxNorm 312615 (concept_id 1551170); care patterns: c1 (entity).

`prednisone_present = event IS prednisone 20 mg tablet`

#### Entity in window

An entity is in the window when its event is not more than 1 day before or after a chest pain event. The window is 1 day. Each of the 5 entities of a care pattern has one window predicate. The window is a draft and has no calibration yet.

`workup_window_days = 1`

`<entity>_in_window = <entity>_present AND EXISTS chest pain event date d, entity event date e with |e - d| <= workup_window_days`

---

### Composites

A composite combines atomic predicates, or other composites, into a named clinical pattern. Each care pattern has the same four composites: entity count, entities, sequence, and care pattern.

**Entities.** The applicant has 3 or more of the entities of the care pattern in the window. The value 3 is a draft. It has no calibration yet.

**Sequences.** A sequence is a list of events in a fixed order. Other events between the steps do not break the sequence. A step after the chest pain step is not more than 1 day after that chest pain event. A step before the chest pain step has no time limit. A step is true for any code of its list.

`sequence_window_days = 1`

**Same-day order.** Claims have a date and no time. The engine puts the events of one day in a fixed order: diagnosis, procedure, lab test, then drug. Inside one type, a lower code ID comes first. For a same-day pattern, the order of the steps is a rule. It is not the clock time.

**Care pattern.** The applicant has chest pain, 3 or more entities in the window, and at least one sequence. This pattern shows the type of care. It does not show a diagnosis. The predicates test that an event happened, not the result.

#### c0: Outpatient check-up and elective cardiac testing

`checkup_entity_count = lipid_panel_in_window + venipuncture_in_window + general_exam_in_window + ecg_in_window + cmp_in_window`

`composite_checkup_entities = checkup_entity_count >= 3`

**Sequence c0-A.** The applicant has a chest pain event, then an ECG, then a hyperlipidemia diagnosis.

`composite_seq_ecg_hld = chest_pain -> ecg -> hyperlipidemia`

**Sequence c0-B.** The applicant has a chest pain event, then a general examination, then a lipid panel.

`composite_seq_genexam_lipid = chest_pain -> general_exam -> lipid_panel`

**Sequence c0-C.** The applicant has a chest pain event, then an ECG, then a general examination.

`composite_seq_ecg_genexam = chest_pain -> ecg -> general_exam`

`composite_checkup_sequence = composite_seq_ecg_hld OR composite_seq_genexam_lipid OR composite_seq_ecg_genexam`

`composite_checkup_pattern = chest_pain_present AND composite_checkup_entities AND composite_checkup_sequence`

#### c1: Prescriptions for acute and chronic illness

`rx_entity_count = methylprednisolone_in_window + amoxicillin_clavulanate_in_window + azithromycin_in_window + ppi_h2_in_window + prednisone_in_window`

`composite_rx_entities = rx_entity_count >= 3`

**Sequence c1-A.** The applicant has a methylprednisolone prescription, then a chest pain event, then an ECG.

`composite_seq_methylpred_cp_ecg = methylprednisolone -> chest_pain -> ecg`

**Sequence c1-B.** The applicant has an azithromycin prescription, then a chest pain event, then an ECG.

`composite_seq_azithro_cp_ecg = azithromycin -> chest_pain -> ecg`

**Sequence c1-C.** The applicant has a chest pain event, then an ECG, then a methylprednisolone prescription.

`composite_seq_ecg_methylpred = chest_pain -> ecg -> methylprednisolone`

`composite_rx_sequence = composite_seq_methylpred_cp_ecg OR composite_seq_azithro_cp_ecg OR composite_seq_ecg_methylpred`

`composite_rx_pattern = chest_pain_present AND composite_rx_entities AND composite_rx_sequence`

#### c2: Women's health and urinary tract

`womens_entity_count = gyn_exam_in_window + sti_nucleic_acid_test_in_window + cervical_cytology_in_window + urine_pregnancy_test_in_window`

`composite_womens_entities = womens_entity_count >= 3`

**Sequence c2-A.** The applicant has a chest pain event, then a CBC test, then a venipuncture.

`composite_seq_cbc_venip = chest_pain -> cbc -> venipuncture`

**Sequence c2-B.** The applicant has a chest pain event, then a venipuncture, then a second venipuncture.

`composite_seq_venip_x2 = chest_pain -> venipuncture -> venipuncture`

**Sequence c2-C.** The applicant has a venipuncture, then a chest pain event, then an ECG.

`composite_seq_venip_cp_ecg = venipuncture -> chest_pain -> ecg`

`composite_womens_sequence = composite_seq_cbc_venip OR composite_seq_venip_x2 OR composite_seq_venip_cp_ecg`

`composite_womens_pattern = chest_pain_present AND composite_womens_entities AND composite_womens_sequence`

#### c3: ED work-up

`ed_workup_entity_count = troponin_in_window + iv_push_in_window + lipase_in_window + cxr_in_window`

`composite_ed_workup_entities = ed_workup_entity_count >= 3`

**Sequence c3-A.** The applicant has a chest pain event, then a chest X-ray, then a troponin test, then a CMP test.

`composite_seq_cxr_trop_cmp = chest_pain -> cxr -> troponin -> cmp`

**Sequence c3-B.** The applicant has a chest pain event, then an ECG, then a troponin test, then a CMP test.

`composite_seq_ecg_trop_cmp = chest_pain -> ecg -> troponin -> cmp`

**Sequence c3-C.** The applicant has a chest pain event, then a troponin test, then a CMP test, then a CBC test.

`composite_seq_trop_cmp_cbc = chest_pain -> troponin -> cmp -> cbc`

`composite_ed_workup_sequence = composite_seq_cxr_trop_cmp OR composite_seq_ecg_trop_cmp OR composite_seq_trop_cmp_cbc`

`composite_ed_workup_pattern = chest_pain_present AND composite_ed_workup_entities AND composite_ed_workup_sequence`

#### c4: Stomach and bowel work-up and cancer screening

`gi_entity_count = surgical_pathology_in_window + colon_cancer_screening_in_window + upper_endoscopy_biopsy_in_window + gerd_in_window + periodic_preventive_visit_in_window`

`composite_gi_entities = gi_entity_count >= 3`

**Sequence c4-A.** The applicant has a chest pain event, then a GERD diagnosis, then an upper endoscopy with biopsy.

`composite_seq_gerd_egd = chest_pain -> gerd -> upper_endoscopy_biopsy`

**Sequence c4-B.** The applicant has a chest pain event, then a surgical pathology exam, then an upper endoscopy with biopsy.

`composite_seq_path_egd = chest_pain -> surgical_pathology -> upper_endoscopy_biopsy`

**Sequence c4-C.** The applicant has a chest pain event, then a GERD diagnosis, then a surgical pathology exam.

`composite_seq_gerd_path = chest_pain -> gerd -> surgical_pathology`

`composite_gi_sequence = composite_seq_gerd_egd OR composite_seq_path_egd OR composite_seq_gerd_path`

`composite_gi_pattern = chest_pain_present AND composite_gi_entities AND composite_gi_sequence`

#### c5: Muscle and bone care and physical therapy

`msk_entity_count = therapeutic_procedure_in_window + manual_therapy_in_window + therapeutic_activities_in_window + low_back_pain_in_window`

`composite_msk_entities = msk_entity_count >= 3`

**Sequence c5-A.** The applicant has a chest pain event, then a manual therapy session, then a therapeutic exercise session.

`composite_seq_manual_ther97110 = chest_pain -> manual_therapy -> therapeutic_exercise`

**Sequence c5-B.** The applicant has a chest pain event, then a manual therapy session, then a second manual therapy session.

`composite_seq_manual_x2 = chest_pain -> manual_therapy -> manual_therapy`

**Sequence c5-C.** The applicant has a chest pain event, then a therapeutic exercise session, then a manual therapy session.

`composite_seq_ther97110_manual = chest_pain -> therapeutic_exercise -> manual_therapy`

`composite_msk_sequence = composite_seq_manual_ther97110 OR composite_seq_manual_x2 OR composite_seq_ther97110_manual`

`composite_msk_pattern = chest_pain_present AND composite_msk_entities AND composite_msk_sequence`

#### c6: Nutrition and hormone blood tests

`labs_entity_count = vitamin_b12_in_window + vitamin_d_in_window + free_t4_in_window + iron_in_window + ferritin_in_window`

`composite_labs_entities = labs_entity_count >= 3`

**Sequence c6-A.** The applicant has a chest pain event, then a lipid panel, then a vitamin D test.

`composite_seq_lipid_vitd = chest_pain -> lipid_panel -> vitamin_d`

**Sequence c6-B.** The applicant has a chest pain event, then a lipid panel, then an HbA1c test.

`composite_seq_lipid_hba1c = chest_pain -> lipid_panel -> hba1c`

**Sequence c6-C.** The applicant has a chest pain event, then an ECG, then a lipid panel.

`composite_seq_ecg_lipid = chest_pain -> ecg -> lipid_panel`

`composite_labs_sequence = composite_seq_lipid_vitd OR composite_seq_lipid_hba1c OR composite_seq_ecg_lipid`

`composite_labs_pattern = chest_pain_present AND composite_labs_entities AND composite_labs_sequence`

#### c7: Acute respiratory infection

`resp_entity_count = cough_in_window + upper_respiratory_infection_in_window + pharyngitis_in_window + rapid_antigen_test_in_window`

`composite_resp_entities = resp_entity_count >= 3`

**Sequence c7-A.** The applicant has an acute pharyngitis diagnosis, then a chest pain event, then an ECG.

`composite_seq_pharyngitis_cp_ecg = pharyngitis -> chest_pain -> ecg`

**Sequence c7-B.** The applicant has a chest pain event, then an ECG, then an acute upper respiratory infection diagnosis.

`composite_seq_ecg_uri = chest_pain -> ecg -> upper_respiratory_infection`

**Sequence c7-C.** The applicant has a cough diagnosis, then a chest pain event, then an ECG.

`composite_seq_cough_cp_ecg = cough -> chest_pain -> ecg`

`composite_resp_sequence = composite_seq_pharyngitis_cp_ecg OR composite_seq_ecg_uri OR composite_seq_cough_cp_ecg`

`composite_resp_pattern = chest_pain_present AND composite_resp_entities AND composite_resp_sequence`

---

## Population Coverage

Counts come from the chest pain cohort of 139,416 patients. The tables come from the k=8 run of the data method (`nmf_k8_chestpain_AHA`). The engine has no measured rate for any predicate or composite yet. Each patient is in the care pattern with the highest weight for that patient.

### Window fit

The window is 1 day. The table shows how far the 5 entities of each care pattern are from the first chest pain. The median is the median day of the first event of the entity.

| Care pattern | Earliest median | Latest median | Entities more than 1 day from the first chest pain |
| :---- | :---- | :---- | ----: |
| c0 | 104 d before | same day | 3 of 5 |
| c1 | 187 d before | 46 d before | 5 of 5 |
| c2 | 193 d before | 97 d before | 5 of 5 |
| c3 | same day | same day | 0 of 5 |
| c4 | 175 d before | 61 d after | 4 of 5 |
| c5 | 115 d before | 133 d after | 5 of 5 |
| c6 | 29 d before | 21 d after | 4 of 5 |
| c7 | 18 d before | same day | 1 of 5 |

### Entity rates

The rates count an entity at any time, not only in the window. The share is the share of the patients of the care pattern.

| Care pattern | Entity | Patients with the entity | Median day against first chest pain | Share that had it before first chest pain |
| :---- | :---- | ----: | :---- | ----: |
| c0 | Lipid panel (CPT4 80061) | 81% | 85 d before | 57% |
| c0 | Venipuncture (SNOMED 28520004) | 81% | 84 d before | 57% |
| c0 | General examination (SNOMED 162673000) | 76% | 104 d before | 57% |
| c0 | ECG (code group ekg) | 87% | same day | 27% |
| c0 | CMP (SNOMED 371361000119107) | 74% | same day | 49% |
| c1 | Methylprednisolone (RxNorm 762675) | 55% | 83 d before | 54% |
| c1 | Amoxicillin with clavulanate (RxNorm 562508) | 55% | 97 d before | 54% |
| c1 | Azithromycin (RxNorm 749783) | 54% | 187 d before | 59% |
| c1 | PPI or H2 blocker (code group ppi_h2) | 52% | 109 d before | 56% |
| c1 | Prednisone (RxNorm 312615) | 49% | 46 d before | 53% |
| c2 | Gynecologic examination (SNOMED 83607001) | 69% | 193 d before | 61% |
| c2 | STI test (CPT4 87491) | 65% | 124 d before | 57% |
| c2 | STI test (CPT4 87591) | 65% | 124 d before | 57% |
| c2 | Cervical cytology (CPT4 88175) | 63% | 97 d before | 55% |
| c2 | Urine pregnancy test (SNOMED 104405006) | 63% | 128 d before | 58% |
| c3 | Troponin (code group troponin) | 81% | same day | 21% |
| c3 | IV push (CPT4 96374) | 66% | same day | 33% |
| c3 | Lipase (SNOMED 104988000) | 59% | same day | 34% |
| c3 | Chest X-ray (code group chest_xray) | 86% | same day | 33% |
| c3 | IV push (CPT4 96375) | 55% | same day | 34% |
| c4 | Surgical pathology (CPT4 88305) | 83% | 8 d after | 48% |
| c4 | Colon cancer screening (SNOMED 275978004) | 68% | 55 d after | 42% |
| c4 | Upper endoscopy with biopsy (SNOMED 445982009) | 63% | 61 d after | 37% |
| c4 | GERD (code group gerd) | 70% | same day | 49% |
| c4 | Periodic preventive visit (CPT4 99396) | 61% | 175 d before | 59% |
| c5 | Therapeutic procedure (CPT4 97110) | 85% | 36 d before | 52% |
| c5 | Manual therapy (CPT4 97140) | 75% | 5 d before | 50% |
| c5 | Therapeutic activities (CPT4 97530) | 55% | 132 d after | 42% |
| c5 | Low back pain (SNOMED 279039007) | 65% | 115 d before | 56% |
| c5 | Therapeutic procedure (CPT4 97112) | 54% | 133 d after | 42% |
| c6 | Vitamin B12 (SNOMED 14598005) | 88% | same day | 48% |
| c6 | Vitamin D (SNOMED 12199005) | 90% | 29 d before | 53% |
| c6 | Free T4 (SNOMED 5113004) | 75% | 14 d before | 52% |
| c6 | Iron (SNOMED 42950004) | 71% | 19 d after | 44% |
| c6 | Ferritin (SNOMED 489004) | 71% | 21 d after | 44% |
| c7 | Cough (SNOMED 49727002) | 66% | 18 d before | 53% |
| c7 | Acute upper respiratory infection (SNOMED 54398005) | 60% | same day | 48% |
| c7 | Acute pharyngitis (SNOMED 363746003) | 61% | same day | 49% |
| c7 | Rapid antigen test (CPT4 87880) | 55% | same day | 48% |
| c7 | Rapid antigen test (CPT4 87804) | 53% | same day | 48% |

### Sequence rates

The shares count the steps in this order at any time. They do not use the 1-day limit. The other care patterns are a random sample of 1,500 patients. The held-out check repeats the test on random halves of the patients, in 40 runs.

| Sequence | Steps | Patients of the care pattern | Patients of the other care patterns | Times as common | Held-out pass rate | Verdict |
| :---- | :---- | ----: | ----: | ----: | ----: | :---- |
| c0-A | chest pain, ECG, hyperlipidemia diagnosis | 44.7% | 27.4% | 1.6 | 50% | Unstable |
| c0-B | chest pain, general examination, lipid panel | 44.6% | 28.3% | 1.6 | 18% | Unstable |
| c0-C | chest pain, ECG, general examination (same-day order) | 47.3% | 32.5% | 1.4 | 0% | Unstable |
| c1-A | methylprednisolone prescription, chest pain, ECG (same-day order) | 24.4% | 4.9% | 4.3 | 100% | Suggestive |
| c1-B | azithromycin prescription, chest pain, ECG (same-day order) | 26.3% | 7.1% | 3.4 | 100% | Suggestive |
| c1-C | chest pain, ECG, methylprednisolone prescription (same-day order) | 26.0% | 7.5% | 3.2 | 100% | Suggestive |
| c2-A | chest pain, CBC test, venipuncture | 46.7% | 34.9% | 1.3 | 0% | Unstable |
| c2-B | chest pain, venipuncture, second venipuncture | 52.9% | 40.4% | 1.3 | 0% | Unstable |
| c2-C | venipuncture, chest pain, ECG | 51.7% | 39.9% | 1.3 | 0% | Unstable |
| c3-A | chest pain, chest X-ray, troponin test, CMP test (same-day order) | 59.4% | 24.4% | 2.4 | 100% | Suggestive |
| c3-B | chest pain, ECG, troponin test, CMP test (same-day order) | 64.9% | 26.7% | 2.4 | 100% | Suggestive |
| c3-C | chest pain, troponin test, CMP test, CBC test (same-day order) | 62.8% | 25.5% | 2.4 | 100% | Suggestive |
| c4-A | chest pain, GERD diagnosis, upper endoscopy with biopsy | 37.7% | 6.0% | 5.5 | 100% | Solid |
| c4-B | chest pain, surgical pathology exam, upper endoscopy with biopsy (same-day order) | 39.1% | 6.4% | 5.4 | 100% | Suggestive |
| c4-C | chest pain, GERD diagnosis, surgical pathology exam | 41.1% | 8.6% | 4.4 | 100% | Solid |
| c5-A | chest pain, manual therapy session, therapeutic exercise session | 45.6% | 6.4% | 6.3 | 100% | Solid |
| c5-B | chest pain, manual therapy session, second manual therapy session | 47.1% | 6.9% | 6.1 | 100% | Solid |
| c5-C | chest pain, therapeutic exercise session, manual therapy session | 48.7% | 7.5% | 5.9 | 100% | Solid |
| c6-A | chest pain, lipid panel, vitamin D test | 64.6% | 19.4% | 3.2 | 100% | Solid |
| c6-B | chest pain, lipid panel, HbA1c test | 68.8% | 36.3% | 1.9 | 100% | Solid |
| c6-C | chest pain, ECG, lipid panel | 65.0% | 41.2% | 1.6 | 100% | Solid |
| c7-A | acute pharyngitis diagnosis, chest pain, ECG | 30.6% | 10.6% | 2.7 | 100% | Solid |
| c7-B | chest pain, ECG, acute upper respiratory infection diagnosis | 30.1% | 13.1% | 2.2 | 100% | Solid |
| c7-C | cough diagnosis, chest pain, ECG | 32.5% | 15.5% | 2.0 | 100% | Solid |

18 of the 24 sequences passed the held-out check. The other sequences did not pass it. Read them as a draft. The window and the rule of 3 entities narrow the match.

---

## References

- Gulati M, et al. *2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain.* Circulation 2021;144:e368. doi:10.1161/CIR.0000000000001029.
- McConaghy JR et al. *Acute Chest Pain in Adults: Outpatient Evaluation.* Am Fam Physician 2020. PMID 33320506.
- Chun AA et al. *Bedside diagnosis of coronary artery disease: a systematic review.* Am J Med 2004. PMID 15336583.
- McConaghy JR et al. *Outpatient diagnosis of acute chest pain in adults.* Am Fam Physician 2013. PMID 23418761.
- Hornick J et al. *The Electrocardiogram: Still a Useful Tool in the Primary Care Office.* Med Clin North Am 2019. PMID 31378324.
- Jaiswal V et al. *COVID-19 Infection and Myocarditis: A State-of-the-Art Systematic Review.* J Prim Care Community Health 2021. PMID 34854348.
- Cremer PC et al. *Diagnosis, Risk Stratification, and Treatment of Pericarditis: A Review.* JAMA 2024. PMID 39235771.
- Imazio M et al. *Evaluation and Treatment of Pericarditis: A Systematic Review.* JAMA 2015. PMID 26461998.
- Cemin R et al. *Blood cells characteristics as determinants of acute myocardial infarction.* Clin Chem Lab Med 2011. PMID 21534844.
- Stopyra JP et al. *EMS blood collection from patients with acute chest pain reduces emergency department length of stay.* Am J Emerg Med 2021. PMID 33964547.
- Martínez-Sellés M et al. *Chest pain in the emergency department: incidence, clinical characteristics and risk stratification.* Rev Esp Cardiol 2008. PMID 18775237.
- Reamy BV et al. *Pleuritic Chest Pain: Sorting Through the Differential Diagnosis.* Am Fam Physician 2017. PMID 28925655.
- Writing Committee et al. *2022 ACC Expert Consensus Decision Pathway on the Evaluation and Disposition of Acute Chest Pain in the Emergency Department: A Report of the American College of Cardiology Solution Set Oversight Committee.* J Am Coll Cardiol 2022. PMID 36241466.
- Möckel M et al. *[Acute chest pain].* Internist (Berl) 2017. PMID 28765984.
- Yadlapati R et al. *AGA Clinical Practice Update on the Personalized Approach to the Evaluation and Management of GERD: Expert Review.* Clin Gastroenterol Hepatol 2022. PMID 35123084.
- Cremonini F et al. *Diagnostic and therapeutic use of proton pump inhibitors in non-cardiac chest pain: a metaanalysis.* Am J Gastroenterol 2005. PMID 15929749.
- Attwood SE et al. *Overview of eosinophilic oesophagitis.* Br J Hosp Med (Lond) 2019. PMID 30860925.
- Ayloo A et al. *Evaluation and treatment of musculoskeletal chest pain.* Prim Care 2013. PMID 24209723.
- Burgstaller JM et al. *Treatment efficacy for non-cardiovascular chest pain: a systematic review and meta-analysis.* PLoS One 2014. PMID 25111147.
- Sturm C et al. *[Musculoskeletal-related chest pain].* Internist (Berl) 2017. PMID 27921113.
- Suryavanshi AR et al. *Effect of Diaphragmatic Breathing Exercise, Jacobson's Relaxation Technique and Dynamic Neuromuscular Stabilization on Gastrointestinal and Psychological Causes of Noncardiac Chest Pain: A Randomized Controlled Trial.* Pain Res Manag 2025. PMID 40860980.
- Alkhatatbeh MJ et al. *Association of 25-hydroxyvitamin D with HDL-cholesterol and other cardiovascular risk biomarkers in subjects with non-cardiac chest pain.* Lipids Health Dis 2019. PMID 30684966.
- Khater WA et al. *The Association Between Vitamin D Level and Chest Pain, Anxiety, and Fatigue in Patients With Coronary Artery Disease.* Clin Nurs Res 2023. PMID 36205377.
- Ewid M et al. *Glycated hemoglobin predicts coronary artery disease in non-diabetic adults.* BMC Cardiovasc Disord 2019. PMID 31864310.
- Schmutzler L et al. *From Streptococcal Pharyngitis/Tonsillitis to Myocarditis: A Systematic Review.* J Cardiovasc Dev Dis 2022. PMID 35735799.

The papers come from the literature check of the final table. They cover the care type of the pattern. They do not test the order of the steps.
