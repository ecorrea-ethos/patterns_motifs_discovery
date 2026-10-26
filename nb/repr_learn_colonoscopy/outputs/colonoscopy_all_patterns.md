# Colonoscopy Predicates and Composites: All Care Patterns

*Working Draft — October 2026*

---

## Overview

This document defines the predicates and composites for colonoscopy applicants. It is one page for all care patterns. The cohort has 211,291 colonoscopy patients. A data method groups these patients by the care they receive. The method found 7 care patterns, c0 to c6. Each predicate has one definition, and all care patterns use it.

The same rules apply to every care pattern. An entity is one of the 5 most frequent entities of the care pattern. The entity is in the window when its event is not more than 1 day from a colonoscopy event. A care pattern needs 3 or more entities in the window and one of its 3 ordered sequences. The sequences are the 3 patterns with the highest lift.

The document contains no underwriting logic and no product decision. It is a clinical grouping of codes. It is a draft and has no validation yet.

The page uses these abbreviations. Each line gives the full term, then the abbreviation.

- Current Procedural Terminology, fourth edition (CPT4)
- Systematized Nomenclature of Medicine (SNOMED)
- electrocardiogram (ECG)
- complete blood count (CBC)
- prostate specific antigen (PSA)
- proton pump inhibitor (PPI)
- histamine-2 (H2)
- human papillomavirus (HPV)
- hemoglobin A1c (HbA1c)
- thyroxine (T4)

RxNorm is the drug code system of the National Library of Medicine.

The cohort has patients of both sexes with at least one colonoscopy procedure. The data method does not use a colorectal cancer diagnosis to group the patients.

In care pattern c5, colonoscopy with polyp removal is itself a colonoscopy event, so it is always in the window. The other 4 entities of c5 have a median of 0 days against the first colonoscopy.

| Care pattern | Name | Patients | % cohort |
| :---- | :---- | ----: | ----: |
| c0 | acute care work-up, bowel complications, and colorectal cancer treatment | 21,216 | 10.0% |
| c1 | preventive check-up and screening labs | 59,585 | 28.2% |
| c2 | prescriptions for acute illness and bowel preparation | 31,949 | 15.1% |
| c3 | women's preventive care | 32,048 | 15.2% |
| c4 | physical therapy and muscle and bone pain | 22,560 | 10.7% |
| c5 | colonoscopy procedure episode | 30,080 | 14.2% |
| c6 | endocrine, nutrient, and iron blood tests | 13,853 | 6.6% |

---

## Predicates and Composites

Each predicate uses a list of codes. The code is in the text. The member table `token_members_k7_colonoscopy_v1.csv` shows every concept of a code group.

### Atomic Predicates

A predicate answers one question about the event history of an applicant. It returns true or false. The code and the date are attributes of one event.

**Colonoscopy present.** The applicant has at least one colonoscopy event. The list holds every colonoscopy procedure code. The main codes are diagnostic colonoscopy (CPT4 45378), colonoscopy with biopsy (CPT4 45380), and colonoscopy with polyp removal (CPT4 45385). All care patterns use it.

`colonoscopy_present = event IS colonoscopy procedure`

**First colonoscopy date.** This is the date of the first colonoscopy event. The engine measures the other dates from this date.

`first_colonoscopy_date = MIN(event_date) over colonoscopy events`

#### Diagnoses

**Abdominal pain present.** The applicant has at least one abdominal pain diagnosis. Abdominal pain is a diagnosis of pain in the belly. The list holds 6 codes, for example epigastric pain, lower abdominal pain, and swelling of the belly from gas. Code: group `abdominal_pain`, 6 concepts (see the member table); care patterns: c0 (entity).

`abdominal_pain_present = event IS abdominal pain diagnosis (any of 6 codes)`

**Colorectal polyp present.** The applicant has at least one colorectal polyp diagnosis. A colorectal polyp is a growth on the wall of the colon or the rectum. The list holds 2 diagnosis codes, one for the colon and one for the rectum. Code: group `colorectal_polyp`, 2 concepts (see the member table); care patterns: c5 (entity and step).

`colorectal_polyp_present = event IS colorectal polyp diagnosis (colon OR rectum)`

**Benign colorectal neoplasm present.** The applicant has at least one benign colorectal neoplasm diagnosis. A benign colorectal neoplasm is a growth of the colon or the rectum that is not cancer. The list holds 11 diagnosis codes for the colon, the rectum, the appendix, and the anus. Code: group `benign_colorectal_neoplasm`, 11 concepts (see the member table); care patterns: c5 (entity).

`benign_colorectal_neoplasm_present = event IS benign colorectal neoplasm diagnosis (any of 11 codes)`

**Diverticular disease present.** The applicant has at least one diverticular disease diagnosis. Diverticular disease is a condition with small pouches in the wall of a hollow organ. The list holds 24 diagnosis codes, with and without inflammation of the pouches. Most are for the large intestine. Code: group `diverticular_disease`, 24 concepts (see the member table); care patterns: c5 (step).

`diverticular_disease_present = event IS diverticular disease diagnosis (any of 24 codes)`

#### Lab tests

**Lipid panel present.** The applicant has at least one lipid panel. A lipid panel is a blood test for cholesterol and other fats. Doctors order it at check-ups, so it alone does not show the type of care. Code: CPT4 80061 (concept_id 2212095); care patterns: c1 (entity and step), c6 (step).

`lipid_panel_present = event IS lipid panel`

**Venipuncture present.** The applicant has at least one venipuncture. Venipuncture is a blood draw from a vein. It does not show which test. Code: SNOMED 28520004 (concept_id 4102442); care patterns: c0 (step), c1 (entity and step).

`venipuncture_present = event IS venipuncture for a blood test`

**Troponin present.** The applicant has at least one troponin test. Troponin is a blood test for injury to the heart muscle. The list holds the quantitative test. Code: CPT4 84484 (concept_id 2212605); care patterns: c0 (entity).

`troponin_quantitative_present = event IS quantitative troponin test`

**Chemistry panel present.** The applicant has at least one chemistry panel. A chemistry panel is a blood test of kidney function, blood sugar, and blood salts. The list holds the comprehensive panel and 2 basic panels. Code: group `chemistry_panel`, 3 concepts (see the member table); care patterns: c0 (step).

`chemistry_panel_present = event IS chemistry panel (any of 3 codes)`

**CBC present.** The applicant has at least one CBC test. The complete blood count (CBC) counts the cells of the blood. The list holds 5 codes of blood cell counts. Code: group `cbc`, 5 concepts (see the member table); care patterns: c0 (step).

`complete_blood_count_present = event IS complete blood count (any of 5 codes)`

**PSA present.** The applicant has at least one PSA test. The prostate specific antigen (PSA) test is a blood test for a protein of the prostate. Doctors use it to screen for prostate problems. Code: SNOMED 377981000000102 (concept_id 44793131); care patterns: c1 (step).

`prostate_specific_antigen_present = event IS total prostate specific antigen level`

**Vitamin B12 present.** The applicant has at least one vitamin B12 test. Vitamin B12 is a blood test for the level of this vitamin. Code: SNOMED 14598005 (concept_id 4032173); care patterns: c6 (entity and step).

`vitamin_b12_present = event IS vitamin B12 measurement`

**Vitamin D present.** The applicant has at least one vitamin D test. The vitamin D test measures 25-hydroxy vitamin D in the blood. Code: SNOMED 12199005 (concept_id 4007831); care patterns: c6 (entity and step).

`vitamin_d_present = event IS 25-hydroxy vitamin D measurement`

**Free T4 present.** The applicant has at least one free T4 test. Free thyroxine (T4) is a blood test for the level of the thyroid hormone. Code: SNOMED 5113004 (concept_id 4196969); care patterns: c6 (entity and step).

`free_t4_present = event IS free T4 measurement`

**Iron studies present.** The applicant has at least one iron study. Iron studies are blood tests for the iron of the body. The list holds 3 codes, for ferritin, iron, and total iron binding capacity. Code: group `iron_studies`, 3 concepts (see the member table); care patterns: c6 (entity).

`iron_studies_present = event IS iron studies (any of 3 codes)`

**Testosterone present.** The applicant has at least one testosterone test. Testosterone is a blood test for a sex hormone. The code is the total testosterone. Code: SNOMED 85470006 (concept_id 4309944); care patterns: c6 (entity).

`testosterone_present = event IS total testosterone measurement`

**HbA1c present.** The applicant has at least one HbA1c test. Hemoglobin A1c (HbA1c) is a blood test for the average blood sugar of the last 3 months. Code: SNOMED 43396009 (concept_id 4184637); care patterns: c6 (step).

`hba1c_present = event IS HbA1c test`

**Cervical screening present.** The applicant has at least one cervical screening test. Cervical screening is a group of tests of the cervix for cancer or for the human papillomavirus (HPV). The list holds 39 codes, for example cervical cytology (the Pap test) and the HPV test. Code: group `cervical_screening`, 39 concepts (see the member table); care patterns: c3 (entity and step).

`cervical_screening_present = event IS cervical screening test (any of 39 codes)`

**Surgical pathology present.** The applicant has at least one surgical pathology exam. Surgical pathology is the study of a tissue sample by eye and under a microscope. A biopsy gives such a sample. The list holds 3 codes, for the levels 3, 4, and 5 of the exam. Code: group `surgical_pathology`, 3 concepts (see the member table); care patterns: c5 (entity).

`surgical_pathology_present = event IS surgical pathology (levels 3, 4, and 5)`

#### Procedures, imaging, and visits

**General examination present.** The applicant has at least one general examination. The general examination is the routine physical examination of a visit. Most patients at a check-up have it. Code: SNOMED 162673000 (concept_id 4036803); care patterns: c1 (entity and step).

`general_exam_present = event IS general examination of the patient`

**Periodic preventive visit present.** The applicant has at least one periodic preventive visit. The periodic preventive visit is the check-up of an adult of 40 to 64 years. Code: CPT4 99396 (concept_id 2514528); care patterns: c1 (entity), c3 (entity and step).

`periodic_preventive_visit_present = event IS periodic comprehensive preventive visit (99396)`

**Gynecologic examination present.** The applicant has at least one gynecologic examination. The gynecologic examination is the pelvic examination of a woman. It is part of women's check-ups. Code: SNOMED 83607001 (concept_id 4306780); care patterns: c3 (entity and step).

`gyn_exam_present = event IS gynecologic examination`

**Immunization present.** The applicant has at least one immunization. An immunization is a vaccine or an antibody given to protect against a disease. It is a routine part of check-ups. Code: SNOMED 127785005 (concept_id 4132855); care patterns: c1 (entity).

`immunization_present = event IS active or passive immunization`

**ECG report or tracing present.** The applicant has at least one ECG. The electrocardiogram (ECG) is a heart tracing. The list holds the report code (93010) and the tracing code (93005). The engine counts them as one service. Code: CPT4 93010 (concept_id 2313816) + CPT4 93005 (concept_id 2313815); care patterns: c0 (entity).

`ecg_report_or_tracing_present = event IS ECG (report 93010 OR tracing 93005)`

**ECG tracing present.** The applicant has at least one ECG tracing. The ECG tracing is the record of the signal of the heart. It is one code of the ECG list. Code: CPT4 93005 (concept_id 2313815); care patterns: c0 (step).

`ecg_tracing_present = event IS ECG tracing (93005)`

**Colorectal screening visit present.** The applicant has at least one colorectal screening visit. The colorectal screening visit is a screening for cancer of the colon or the rectum in a person with no symptoms. The list holds 2 codes, one for the colon and one for the rectum. Code: group `colorectal_screening_visit`, 2 concepts (see the member table); care patterns: c1 (step), c5 (entity and step).

`colorectal_screening_visit_present = event IS screening for malignant neoplasm of colon OR rectum`

**Breast cancer screening tests present.** The applicant has at least one breast cancer screening test. Breast cancer screening tests are X-rays of the breasts of a woman with no symptoms. The list holds 6 codes, for screening mammography and breast tomosynthesis. Code: group `breast_cancer_screening`, 6 concepts (see the member table); care patterns: c3 (entity and step).

`breast_cancer_screening_test_present = event IS breast cancer screening test (any of 6 codes)`

**Breast cancer screening visit present.** The applicant has at least one breast cancer screening visit. The breast cancer screening visit is a screening for breast cancer in a person with no symptoms. Code: SNOMED 268547008 (concept_id 4147961); care patterns: c3 (entity).

`breast_cancer_screening_visit_present = event IS screening for malignant neoplasm of breast`

**Colonoscopy with polyp removal present.** The applicant has at least one colonoscopy with polyp removal. A colonoscopy with polyp removal is a colonoscopy in which the doctor removes polyps or other lesions. The list holds 7 codes. The main code is 45385. Code: group `colonoscopy_polypectomy`, 7 concepts (see the member table); care patterns: c5 (entity and step).

`colonoscopy_polypectomy_present = event IS colonoscopy with polyp removal (any of 7 codes)`

**Colonoscopy with biopsy present.** The applicant has at least one colonoscopy with biopsy. A colonoscopy with biopsy is a colonoscopy in which the doctor takes a tissue sample. The list holds 2 codes. The main code is 45380. Code: group `colonoscopy_biopsy`, 2 concepts (see the member table); care patterns: c5 (step).

`colonoscopy_biopsy_present = event IS colonoscopy with biopsy (any of 2 codes)`

**Therapeutic procedure present.** The applicant has at least one therapeutic procedure. A therapeutic procedure is physical therapy in units of 15 minutes. The list holds the exercise code (97110) and the movement training code (97112). The engine counts them as one service. Code: CPT4 97110 (concept_id 2314284) + CPT4 97112 (concept_id 2314285); care patterns: c4 (entity).

`therapeutic_procedure_present = event IS therapeutic procedure (97110 OR 97112)`

**Therapeutic exercise present.** The applicant has at least one therapeutic exercise session. Therapeutic exercise is physical therapy with exercises, in units of 15 minutes. It is one code of the therapeutic procedure list. Code: CPT4 97110 (concept_id 2314284); care patterns: c4 (step).

`therapeutic_exercise_present = event IS therapeutic exercise (97110)`

**Manual therapy present.** The applicant has at least one manual therapy session. Manual therapy is hands-on treatment by a therapist, for example joint movement. Code: CPT4 97140 (concept_id 2314290); care patterns: c4 (entity and step).

`manual_therapy_present = event IS manual therapy techniques`

**Therapeutic activities present.** The applicant has at least one therapeutic activities session. Therapeutic activities are one-on-one physical therapy with movements of daily life. Code: CPT4 97530 (concept_id 2314294); care patterns: c4 (entity and step).

`therapeutic_activities_present = event IS therapeutic activities`

**Physical therapy evaluation present.** The applicant has at least one physical therapy evaluation. The physical therapy evaluation is the first assessment by a therapist. The list holds the low complexity code. Code: CPT4 97161 (concept_id 42627952); care patterns: c4 (entity).

`physical_therapy_evaluation_present = event IS physical therapy evaluation (low complexity)`

#### Drugs

**Methylprednisolone present.** The applicant has at least one methylprednisolone prescription. Methylprednisolone is a steroid drug. The code is the 21-tablet dose pack. Code: RxNorm 762675 (concept_id 19129398); care patterns: c2 (entity).

`methylprednisolone_present = event IS methylprednisolone 21-tablet pack`

**Amoxicillin with clavulanate present.** The applicant has at least one amoxicillin with clavulanate prescription. Amoxicillin with clavulanate is an antibiotic. The code is the tablet of 875 mg with 125 mg. Code: RxNorm 562508 (concept_id 19115197); care patterns: c2 (entity and step).

`amoxicillin_clavulanate_present = event IS amoxicillin 875 mg with clavulanate 125 mg tablet`

**Azithromycin present.** The applicant has at least one azithromycin prescription. Azithromycin is an antibiotic. The code is the pack of 6 tablets of 250 mg. Code: RxNorm 749783 (concept_id 19128020); care patterns: c2 (entity and step).

`azithromycin_present = event IS azithromycin 6-tablet pack`

**Prednisone present.** The applicant has at least one prednisone prescription. Prednisone is a steroid drug. The code is the tablet of 20 mg. Code: RxNorm 312615 (concept_id 1551170); care patterns: c2 (entity).

`prednisone_present = event IS prednisone 20 mg tablet`

**PPI or H2 blocker present.** The applicant has at least one PPI or H2 blocker prescription. A proton pump inhibitor (PPI) or a histamine-2 (H2) blocker is a drug that lowers stomach acid. The list holds 80 drug codes. Code: group `ppi_h2`, 80 concepts (see the member table); care patterns: c2 (entity and step).

`ppi_h2_present = event IS PPI or H2 blocker drug (any of 80 codes)`

**Ondansetron present.** The applicant has at least one ondansetron injection. Ondansetron is a drug against nausea and vomiting. The code is the injection. Code: RxNorm 1740463 (concept_id 35605480); care patterns: c0 (entity).

`ondansetron_injection_present = event IS ondansetron injection`

#### Entity in window

An entity is in the window when its event is not more than 1 day before or after a colonoscopy event. The window is 1 day. Each of the 5 entities of a care pattern has one window predicate. The window is a draft and has no calibration yet.

`workup_window_days = 1`

`<entity>_in_window = <entity>_present AND EXISTS colonoscopy event date d, entity event date e with |e - d| <= workup_window_days`

---

### Composites

A composite combines atomic predicates, or other composites, into a named clinical pattern. Each care pattern has the same four composites: entity count, entities, sequence, and care pattern.

**Entities.** The applicant has 3 or more of the entities of the care pattern in the window. The value 3 is a draft. It has no calibration yet.

**Sequences.** A sequence is a list of events in a fixed order. Other events between the steps do not break the sequence. A sequence has no time limit between its steps. The data method found the sequences in the full history of the patient, with or without a colonoscopy step. A step is true for any code of its list.

**Same-day order.** Claims have a date and no time. The engine puts the events of one day in a fixed order: diagnosis, procedure, lab test, then drug. Inside one type, a lower concept identifier comes first. For a same-day pattern, the order of the steps is a rule. It is not the clock time.

**Care pattern.** The applicant has a colonoscopy event, 3 or more entities in the window, and at least one sequence. This pattern shows the type of care. It does not show a diagnosis. The predicates test that an event happened, not the result.

#### c0: Acute care work-up, bowel complications, and colorectal cancer treatment

`acute_entity_count = ecg_report_or_tracing_in_window + abdominal_pain_in_window + troponin_quantitative_in_window + ondansetron_injection_in_window`

`composite_acute_entities = acute_entity_count >= 3`

**Sequence c0-A.** The applicant has an ECG tracing, then a chemistry panel, then a second chemistry panel.

`composite_seq_ecg93005_chem_x2 = ecg_tracing -> chemistry_panel -> chemistry_panel`

**Sequence c0-B.** The applicant has an ECG tracing, then a chemistry panel, then a CBC test.

`composite_seq_ecg93005_chem_cbc = ecg_tracing -> chemistry_panel -> complete_blood_count`

**Sequence c0-C.** The applicant has an ECG tracing, then a venipuncture, then a chemistry panel.

`composite_seq_ecg93005_venip_chem = ecg_tracing -> venipuncture -> chemistry_panel`

`composite_acute_sequence = composite_seq_ecg93005_chem_x2 OR composite_seq_ecg93005_chem_cbc OR composite_seq_ecg93005_venip_chem`

`composite_acute_pattern = colonoscopy_present AND composite_acute_entities AND composite_acute_sequence`

#### c1: Preventive check-up and screening labs

`checkup_entity_count = general_exam_in_window + lipid_panel_in_window + periodic_preventive_visit_in_window + venipuncture_in_window + immunization_in_window`

`composite_checkup_entities = checkup_entity_count >= 3`

**Sequence c1-A.** The applicant has a general examination, then a lipid panel, then a PSA test.

`composite_seq_genexam_lipid_psa = general_exam -> lipid_panel -> prostate_specific_antigen`

**Sequence c1-B.** The applicant has a venipuncture, then a lipid panel, then a PSA test.

`composite_seq_venip_lipid_psa = venipuncture -> lipid_panel -> prostate_specific_antigen`

**Sequence c1-C.** The applicant has a general examination, then a lipid panel, then a colorectal screening visit.

`composite_seq_genexam_lipid_crcvisit = general_exam -> lipid_panel -> colorectal_screening_visit`

`composite_checkup_sequence = composite_seq_genexam_lipid_psa OR composite_seq_venip_lipid_psa OR composite_seq_genexam_lipid_crcvisit`

`composite_checkup_pattern = colonoscopy_present AND composite_checkup_entities AND composite_checkup_sequence`

#### c2: Prescriptions for acute illness and bowel preparation

`rx_entity_count = methylprednisolone_in_window + amoxicillin_clavulanate_in_window + azithromycin_in_window + ppi_h2_in_window + prednisone_in_window`

`composite_rx_entities = rx_entity_count >= 3`

**Sequence c2-A.** The applicant has a PPI or H2 blocker prescription, then a second PPI or H2 blocker prescription, then an azithromycin prescription.

`composite_seq_ppi_x2_azithro = ppi_h2 -> ppi_h2 -> azithromycin`

**Sequence c2-B.** The applicant has an amoxicillin with clavulanate prescription, then a PPI or H2 blocker prescription, then a second PPI or H2 blocker prescription.

`composite_seq_amoxclav_ppi_x2 = amoxicillin_clavulanate -> ppi_h2 -> ppi_h2`

**Sequence c2-C.** The applicant has a PPI or H2 blocker prescription, then a second PPI or H2 blocker prescription, then an amoxicillin with clavulanate prescription.

`composite_seq_ppi_x2_amoxclav = ppi_h2 -> ppi_h2 -> amoxicillin_clavulanate`

`composite_rx_sequence = composite_seq_ppi_x2_azithro OR composite_seq_amoxclav_ppi_x2 OR composite_seq_ppi_x2_amoxclav`

`composite_rx_pattern = colonoscopy_present AND composite_rx_entities AND composite_rx_sequence`

#### c3: Women's preventive care

`womens_entity_count = breast_cancer_screening_test_in_window + gyn_exam_in_window + cervical_screening_in_window + periodic_preventive_visit_in_window + breast_cancer_screening_visit_in_window`

`composite_womens_entities = womens_entity_count >= 3`

**Sequence c3-A.** The applicant has a cervical screening test, then a periodic preventive visit, then a breast cancer screening test.

`composite_seq_cervical_periodic_bcscreen = cervical_screening -> periodic_preventive_visit -> breast_cancer_screening_test`

**Sequence c3-B.** The applicant has a breast cancer screening test, then a periodic preventive visit, then a gynecologic examination.

`composite_seq_bcscreen_periodic_gyn = breast_cancer_screening_test -> periodic_preventive_visit -> gyn_exam`

**Sequence c3-C.** The applicant has a periodic preventive visit, then a second periodic preventive visit, then a gynecologic examination.

`composite_seq_periodic_x2_gyn = periodic_preventive_visit -> periodic_preventive_visit -> gyn_exam`

`composite_womens_sequence = composite_seq_cervical_periodic_bcscreen OR composite_seq_bcscreen_periodic_gyn OR composite_seq_periodic_x2_gyn`

`composite_womens_pattern = colonoscopy_present AND composite_womens_entities AND composite_womens_sequence`

#### c4: Physical therapy and muscle and bone pain

`pt_entity_count = therapeutic_procedure_in_window + manual_therapy_in_window + therapeutic_activities_in_window + physical_therapy_evaluation_in_window`

`composite_pt_entities = pt_entity_count >= 3`

**Sequence c4-A.** The applicant has a manual therapy session, then a therapeutic exercise session, then a second therapeutic exercise session, then a therapeutic activities session.

`composite_seq_manual_ther97110_x2_theract = manual_therapy -> therapeutic_exercise -> therapeutic_exercise -> therapeutic_activities`

**Sequence c4-B.** The applicant has a manual therapy session, then a therapeutic exercise session, then a therapeutic activities session.

`composite_seq_manual_ther97110_theract = manual_therapy -> therapeutic_exercise -> therapeutic_activities`

**Sequence c4-C.** The applicant has a therapeutic exercise session, then a manual therapy session, then a second manual therapy session, then a therapeutic activities session.

`composite_seq_ther97110_manual_x2_theract = therapeutic_exercise -> manual_therapy -> manual_therapy -> therapeutic_activities`

`composite_pt_sequence = composite_seq_manual_ther97110_x2_theract OR composite_seq_manual_ther97110_theract OR composite_seq_ther97110_manual_x2_theract`

`composite_pt_pattern = colonoscopy_present AND composite_pt_entities AND composite_pt_sequence`

#### c5: Colonoscopy procedure episode

`procedure_entity_count = colonoscopy_polypectomy_in_window + colorectal_polyp_in_window + surgical_pathology_in_window + benign_colorectal_neoplasm_in_window + colorectal_screening_visit_in_window`

`composite_procedure_entities = procedure_entity_count >= 3`

**Sequence c5-A.** The applicant has a diverticular disease diagnosis, then a colorectal polyp diagnosis, then a colonoscopy with polyp removal.

`composite_seq_diverticular_polyp_polypectomy = diverticular_disease -> colorectal_polyp -> colonoscopy_polypectomy`

**Sequence c5-B.** The applicant has a colorectal polyp diagnosis, then a colonoscopy with biopsy, then a colonoscopy with polyp removal.

`composite_seq_polyp_biopsy_polypectomy = colorectal_polyp -> colonoscopy_biopsy -> colonoscopy_polypectomy`

**Sequence c5-C.** The applicant has a diverticular disease diagnosis, then a colorectal polyp diagnosis, then a colonoscopy with polyp removal, then a colorectal screening visit.

`composite_seq_diverticular_polyp_polypectomy_crcvisit = diverticular_disease -> colorectal_polyp -> colonoscopy_polypectomy -> colorectal_screening_visit`

`composite_procedure_sequence = composite_seq_diverticular_polyp_polypectomy OR composite_seq_polyp_biopsy_polypectomy OR composite_seq_diverticular_polyp_polypectomy_crcvisit`

`composite_procedure_pattern = colonoscopy_present AND composite_procedure_entities AND composite_procedure_sequence`

#### c6: Endocrine, nutrient, and iron blood tests

`labs_entity_count = vitamin_d_in_window + vitamin_b12_in_window + free_t4_in_window + iron_studies_in_window + testosterone_in_window`

`composite_labs_entities = labs_entity_count >= 3`

**Sequence c6-A.** The applicant has a lipid panel, then a vitamin D test, then a free T4 test.

`composite_seq_lipid_vitd_t4 = lipid_panel -> vitamin_d -> free_t4`

**Sequence c6-B.** The applicant has a vitamin D test, then an HbA1c test, then a free T4 test.

`composite_seq_vitd_hba1c_t4 = vitamin_d -> hba1c -> free_t4`

**Sequence c6-C.** The applicant has a lipid panel, then a vitamin D test, then a vitamin B12 test, then an HbA1c test.

`composite_seq_lipid_vitd_b12_hba1c = lipid_panel -> vitamin_d -> vitamin_b12 -> hba1c`

`composite_labs_sequence = composite_seq_lipid_vitd_t4 OR composite_seq_vitd_hba1c_t4 OR composite_seq_lipid_vitd_b12_hba1c`

`composite_labs_pattern = colonoscopy_present AND composite_labs_entities AND composite_labs_sequence`

---

## Population Coverage

Counts come from the colonoscopy cohort of 211,291 patients. The tables come from the k=7 run of the data method (`nmf_k7_colonoscopy_v1`). The engine has no measured rate for any predicate or composite yet. Each patient is in the care pattern with the highest weight for that patient.

### Window fit

The window is 1 day. The table shows how far the 5 entities of each care pattern are from the first colonoscopy. The median is the median day of the first event of the entity.

| Care pattern | Earliest median | Latest median | Entities more than 1 day from the first colonoscopy |
| :---- | :---- | :---- | ----: |
| c0 | 119 days before | 17 days before | 5 of 5 |
| c1 | 438 days before | 286 days before | 5 of 5 |
| c2 | 416 days before | 287 days before | 5 of 5 |
| c3 | 529 days before | 303 days before | 5 of 5 |
| c4 | 249 days before | 31 days before | 5 of 5 |
| c5 | same day | same day | 0 of 5 |
| c6 | 213 days before | 78 days before | 5 of 5 |

### Entity rates

The rates count an entity at any time, not only in the window. The share is the share of the patients of the care pattern.

| Care pattern | Entity | Patients with the entity | Median day against first colonoscopy | Share that had it before first colonoscopy |
| :---- | :---- | ----: | :---- | ----: |
| c0 | ECG report or tracing (CPT4 93005) | 67% | 66 days before | 56% |
| c0 | ECG report or tracing (CPT4 93010) | 68% | 119 days before | 60% |
| c0 | Abdominal pain (code group abdominal_pain) | 69% | 69 days before | 69% |
| c0 | Troponin (CPT4 84484) | 59% | 65 days before | 56% |
| c0 | Ondansetron (RxNorm 1740463) | 54% | 17 days before | 52% |
| c1 | General examination (SNOMED 162673000) | 89% | 387 days before | 78% |
| c1 | Lipid panel (CPT4 80061) | 89% | 416 days before | 78% |
| c1 | Periodic preventive visit (CPT4 99396) | 80% | 286 days before | 72% |
| c1 | Venipuncture (SNOMED 28520004) | 86% | 438 days before | 78% |
| c1 | Immunization (SNOMED 127785005) | 64% | 379 days before | 73% |
| c2 | Methylprednisolone (RxNorm 762675) | 58% | 355 days before | 63% |
| c2 | Amoxicillin with clavulanate (RxNorm 562508) | 55% | 328 days before | 64% |
| c2 | Azithromycin (RxNorm 749783) | 54% | 416 days before | 66% |
| c2 | PPI or H2 blocker (code group ppi_h2) | 51% | 349 days before | 70% |
| c2 | Prednisone (RxNorm 312615) | 47% | 287 days before | 61% |
| c3 | Breast cancer screening tests (code group breast_cancer_screening) | 84% | 496 days before | 78% |
| c3 | Gynecologic examination (SNOMED 83607001) | 80% | 508 days before | 76% |
| c3 | Cervical screening (code group cervical_screening) | 77% | 442 days before | 74% |
| c3 | Periodic preventive visit (CPT4 99396) | 82% | 529 days before | 78% |
| c3 | Breast cancer screening visit (SNOMED 268547008) | 59% | 303 days before | 70% |
| c4 | Therapeutic procedure (CPT4 97110) | 91% | 249 days before | 62% |
| c4 | Manual therapy (CPT4 97140) | 83% | 225 days before | 60% |
| c4 | Therapeutic activities (CPT4 97530) | 64% | 38 days before | 52% |
| c4 | Therapeutic procedure (CPT4 97112) | 63% | 31 days before | 52% |
| c4 | Physical therapy evaluation (CPT4 97161) | 59% | 60 days before | 53% |
| c5 | Colonoscopy with polyp removal (code group colonoscopy_polypectomy) | 71% | same day | 0% |
| c5 | Colorectal polyp (code group colorectal_polyp) | 64% | same day | 1% |
| c5 | Surgical pathology (code group surgical_pathology) | 68% | same day | 13% |
| c5 | Benign colorectal neoplasm (code group benign_colorectal_neoplasm) | 55% | same day | 1% |
| c5 | Colorectal screening visit (code group colorectal_screening_visit) | 80% | same day | 31% |
| c6 | Vitamin D (SNOMED 12199005) | 89% | 213 days before | 65% |
| c6 | Vitamin B12 (SNOMED 14598005) | 84% | 129 days before | 62% |
| c6 | Free T4 (SNOMED 5113004) | 75% | 202 days before | 64% |
| c6 | Iron studies (code group iron_studies) | 67% | 78 days before | 60% |
| c6 | Testosterone (SNOMED 85470006) | 66% | 164 days before | 61% |

### Sequence rates

The shares count the steps in this order at any time. They have no time limit between the steps. The other care patterns are a random sample of 1,500 patients. The re-test splits the patients of a care pattern into 2 random halves, 5 times. It finds the sequence on one half and checks it on the other half. The column shows in how many of the 5 re-tests the sequence held.

| Sequence | Steps | Patients of the care pattern | Patients of the other care patterns | Times as common | Re-tests found (of 5) | Verdict |
| :---- | :---- | ----: | ----: | ----: | ----: | :---- |
| c0-A | ECG tracing, chemistry panel, second chemistry panel | 54.2% | 8.9% | 5.6 | 0 of 5 | Unstable |
| c0-B | ECG tracing, chemistry panel, CBC test | 62.3% | 10.7% | 5.4 | 5 of 5 | Solid |
| c0-C | ECG tracing, venipuncture, chemistry panel | 54.8% | 9.9% | 5.1 | 2 of 5 | Unstable |
| c1-A | general examination, lipid panel, PSA test | 50.9% | 9.5% | 5.0 | 3 of 5 | Suggestive |
| c1-B | venipuncture, lipid panel, PSA test | 52.4% | 11.5% | 4.3 | 5 of 5 | Solid |
| c1-C | general examination, lipid panel, colorectal screening visit | 52.2% | 20.6% | 2.5 | 5 of 5 | Solid |
| c2-A | PPI or H2 blocker prescription, second PPI or H2 blocker prescription, azithromycin prescription | 16.2% | 2.3% | 5.2 | 5 of 5 | Solid |
| c2-B | amoxicillin with clavulanate prescription, PPI or H2 blocker prescription, second PPI or H2 blocker prescription | 18.2% | 2.7% | 5.1 | 5 of 5 | Solid |
| c2-C | PPI or H2 blocker prescription, second PPI or H2 blocker prescription, amoxicillin with clavulanate prescription | 17.2% | 2.6% | 5.1 | 5 of 5 | Solid |
| c3-A | cervical screening test, periodic preventive visit, breast cancer screening test | 49.8% | 2.4% | 15.0 | 4 of 5 | Solid |
| c3-B | breast cancer screening test, periodic preventive visit, gynecologic examination | 50.2% | 2.7% | 14.0 | 5 of 5 | Solid |
| c3-C | periodic preventive visit, second periodic preventive visit, gynecologic examination | 50.8% | 2.9% | 13.4 | 5 of 5 | Solid |
| c4-A | manual therapy session, therapeutic exercise session, second therapeutic exercise session, therapeutic activities session | 46.1% | 6.3% | 6.4 | 0 of 5 | Unstable |
| c4-B | manual therapy session, therapeutic exercise session, therapeutic activities session | 49.3% | 6.9% | 6.3 | 5 of 5 | Solid |
| c4-C | therapeutic exercise session, manual therapy session, second manual therapy session, therapeutic activities session | 46.4% | 6.7% | 6.2 | 5 of 5 | Solid |
| c5-A | diverticular disease diagnosis, colorectal polyp diagnosis, colonoscopy with polyp removal (same-day order) | 20.4% | 8.1% | 2.4 | 5 of 5 | Solid |
| c5-B | colorectal polyp diagnosis, colonoscopy with biopsy, colonoscopy with polyp removal (same-day order) | 20.9% | 8.6% | 2.3 | 5 of 5 | Solid |
| c5-C | diverticular disease diagnosis, colorectal polyp diagnosis, colonoscopy with polyp removal, colorectal screening visit (same-day order) | 16.5% | 6.5% | 2.3 | 5 of 5 | Solid |
| c6-A | lipid panel, vitamin D test, free T4 test | 59.5% | 8.8% | 6.2 | 5 of 5 | Solid |
| c6-B | vitamin D test, HbA1c test, free T4 test | 54.2% | 7.9% | 6.2 | 4 of 5 | Solid |
| c6-C | lipid panel, vitamin D test, vitamin B12 test, HbA1c test (same-day order) | 59.8% | 9.7% | 5.7 | 5 of 5 | Solid |

17 of the 21 sequences passed the re-test. The other sequences did not pass it. Read them as a draft. The window and the rule of 3 entities narrow the match.

---

## References

- US Preventive Services Task Force. *Screening for Colorectal Cancer, Recommendation Statement.* JAMA 2021;325(19):1965-1977. doi:10.1001/jama.2021.6238.
- Gupta S, et al. *Recommendations for Follow-Up After Colonoscopy and Polypectomy, A Consensus Update by the US Multi-Society Task Force on Colorectal Cancer.* Gastroenterology 2020;158:1131-1153. doi:10.1053/j.gastro.2019.10.026.
