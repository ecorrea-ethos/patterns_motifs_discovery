# Chest Pain Work-up Predicate Engine, version 2

*Working Draft — October 2026*

Version 2 replaces `Chestpain_Workup_Predicate_Engine.md` (NMF k=5 run, care pattern c0), which stays in the folder for comparison. The words used in this document are fixed in Annex A (UW wording against data-team wording). Every code behind every list of codes is in Annex B, with its OMOP ID.

---

## Overview

This document describes the design of the chest pain predicate engine for life underwriting. The engine separates chest pain that sits in an emergency department (ED) work-up (care pattern c3 of the chest pain NMF run, k=8) from chest pain that other care explains (the seven other care patterns c0, c1, c2, c4, c5, c6 and c7). The comparison is one against all: c3 against the other seven. Today every `dx_9487` (atypical chest pain) case routes to manual review at RUW; this rule is a candidate for narrowing that routing, and it is not yet validated for it.

The predicates are built on OMOP codes. Each code is identified by its OMOP concept (verbatim name, vocabulary, code, `concept_id`). The entity registry below is the single place that fixes the names. The first sections contain no underwriting logic. They are intended for clinical and medical review to validate that the definitions agree with the care that the care pattern describes. The flag rule has its own section.

Source of the codes and sequences:

* **Cohort.** 139,416 chest pain patients (`sql/chest_pain_cohort.sql`, any of the five R07.x codes).
* **Lists of codes.** 70 lists built from the 2021 AHA/ACC chest pain guideline (`codesets_v2.yaml`). The checker `check_codesets.py` reports 70 lists and 869 distinct codes; the `chest_pain` list is identical to the first version of the codesets; 39 codes sit in two lists and all 39 are in the two umbrella lists (`stress_test`, `cad`), so there are 0 unexpected overlaps.
* **Care patterns.** NMF k=8 on tokens made of these lists (`nmf_k8_chestpain_AHA`), PrefixSpan patterns per care pattern, and the final table `final_table_chestpain_k8_AHA.xlsx`.

### What changed from version 1

| Item | Version 1 (k=5, care pattern c0) | Version 2 (k=8, care pattern c3) |
| :---- | :---- | :---- |
| Code lists | `codesets.yaml`, 20 lists | `codesets_v2.yaml`, 70 lists, 869 codes, from the 2021 AHA/ACC guideline |
| Care pattern flagged | c0, acute / ED cardiac work-up, 25,953 patients (18.6%) | c3, acute / ED work-up, 17,250 patients (12.4%) |
| Compared against | 4 other care patterns | 7 other care patterns |
| Services counted (3 of 4) | ECG, troponin, chest X-ray, IV push | troponin, chest X-ray, lipase, IV push |
| ECG | counted as a service | not counted; used only in sequence B |
| Troponin | one code, CPT4 84484 | list of codes: CPT4 84484 and 84512 |
| Chest X-ray | one code, CPT4 71045 (single view) | list of codes: CPT4 71045, 71046, 71047, 71048 (1 to 4 or more views) |
| IV push | CPT4 96374 | CPT4 96374 (first drug) or 96375 (each additional drug) |
| Sequences | 3 steps, start at chest pain, end at troponin | 4 steps, start at chest pain, end at CMP (A, B) or CBC (C) |
| Same-day order | date, then domain, then code ID | the same rule; it decides more of the order here (see Same-day order) |
| Literature check | done, three sequences rated *Partly* | repeated for the k=8 table (PubMed, titles and abstracts): the three c3 sequences are *Partly*; the version 1 ratings were not carried over |

---

## Entity registry

An entity is a code, not an ingredient. A predicate is true only for the codes listed. Concept names are verbatim from the OMOP `concept` table of the extract. A list of codes (chest pain, troponin, chest X-ray, ECG) counts as one entity: any one of its codes makes the entity present. *Patients* is the number of the 139,416 chest pain patients with the code, at any time.

<!-- REGISTRY:BEGIN -->

| Predicate key | Plain label | Verbatim OMOP concept name | Code | `concept_id` | Patients |
| :---- | :---- | :---- | :---- | ----: | ----: |
| `chest_pain` | Chest pain diagnosis, chest pain | Chest pain | SNOMED 29857009 | 77670 | 133,792 |
| `chest_pain` | Chest pain diagnosis, precordial pain (pain over the heart) | Precordial pain | SNOMED 71884009 | 134159 | 13,768 |
| `chest_pain` | Chest pain diagnosis, chest pain on breathing | Chest pain on breathing | SNOMED 274664007 | 4168213 | 2,084 |
| `chest_pain` | Chest pain diagnosis, pain of the intercostal space (between the ribs) | Pain of intercostal space | SNOMED 735940001 | 42539051 | 2,039 |
| `troponin` | Troponin blood test, quantitative (measures the level) | Troponin, quantitative | CPT4 84484 | 2212605 | 56,341 |
| `troponin` | Troponin blood test, qualitative (positive or negative) | Troponin, qualitative | CPT4 84512 | 2212610 | 88 |
| `cxr` | Chest X-ray, 2 views | Radiologic examination, chest; 2 views | CPT4 71046 | 725069 | 57,811 |
| `cxr` | Chest X-ray, 1 view | Radiologic examination, chest; single view | CPT4 71045 | 725068 | 47,797 |
| `cxr` | Chest X-ray, 3 views | Radiologic examination, chest; 3 views | CPT4 71047 | 724942 | 132 |
| `cxr` | Chest X-ray, 4 or more views | Radiologic examination, chest; 4 or more views | CPT4 71048 | 724943 | 99 |
| `lipase` | Lipase blood test (pancreas marker) | Triacylglycerol lipase measurement | SNOMED 104988000 | 4021288 | 34,420 |
| `iv_push` | IV push, first drug | Therapeutic, prophylactic, or diagnostic injection (specify substance or drug); intravenous push, single or initial substance/drug | CPT4 96374 | 2314215 | 33,199 |
| `iv_push` | IV push, each additional drug | Therapeutic, prophylactic, or diagnostic injection (specify substance or drug); each additional sequential intravenous push of a new substance/drug (List separately in addition to code for primary procedure) | CPT4 96375 | 2314216 | 23,192 |
| `ecg` | ECG (resting 12-lead), interpretation only | Electrocardiogram, routine ECG with at least 12 leads; interpretation and report only | CPT4 93010 | 2313816 | 69,292 |
| `ecg` | ECG (resting 12-lead), tracing and interpretation together | Electrocardiogram, routine ECG with at least 12 leads; with interpretation and report | CPT4 93000 | 2313814 | 66,307 |
| `ecg` | ECG (resting 12-lead), tracing only | Electrocardiogram, routine ECG with at least 12 leads; tracing only, without interpretation and report | CPT4 93005 | 2313815 | 60,313 |
| `ecg` | ECG (resting 12-lead), screening ECG with interpretation (preventive visit) | Electrocardiogram, routine ecg with 12 leads; performed as a screening for the initial preventive physical examination with interpretation and report | HCPCS G0403 | 2617470 | 83 |
| `ecg` | ECG (resting 12-lead), screening ECG, tracing only (preventive visit) | Electrocardiogram, routine ecg with 12 leads; tracing only, without interpretation and report, performed as a screening for the initial preventive physical examination | HCPCS G0404 | 2617471 | 14 |
| `cmp` | Comprehensive metabolic panel (CMP) | Comprehensive metabolic panel | SNOMED 371361000119107 | 3661905 | 95,388 |
| `cbc` | Complete blood count (CBC) | Complete blood count with white cell differential, automated | SNOMED 9564003 | 4319466 | 94,699 |

<!-- REGISTRY:END -->

Five precision points:

* **The chest pain predicate is wider than one code.** The anchor `first_chest_pain_date` is the earliest event of any code in the list `chest_pain` (four codes). The sequences in the final table name the list, not one code.
* **A list is one token in the NMF.** The shares and loadings quoted for troponin and chest X-ray in this document are for the whole list. The members of each list are in Annex B and in `token_members_k8_chestpain_AHA.csv`.
* **ECG is one entity, five codes.** The tracing (CPT4 93005), the interpretation (CPT4 93010) and both together (CPT4 93000) are billing lines of one test. Any of them is an ECG for sequence B. ECG is not one of the four services that are counted (see the limits).
* **IV push is two codes.** CPT4 96375 is an add-on that is billed together with a first push (96374). Either code makes the IV push service present.
* **Lipase, IV push, CMP and CBC are not specific to chest pain.** They mark emergency or hospital care for any complaint. They are in the rule because they are among the strongest codes of the ED care pattern, and the limits section says what that costs.

---

## Predicates and Composites

### Atomic Predicates

A predicate answers one question about the event history of an applicant. It returns true or false. Atomic predicates check directly against raw event attributes: the OMOP code and the event date.

**Chest pain present.** The applicant has at least one chest pain event. The predicate defines the scope of the engine and the anchor date. Chest pain is nonspecific, so presence alone does not identify the care pathway.

`chest_pain_present = concept IS IN codeset(chest_pain)`

`first_chest_pain_date = MIN(event_date) over chest pain events`

**Work-up service present.** Four services are among the five highest-loading codes of care pattern c3 (ED work-up). Each one answers: has the applicant ever had this service?

`troponin_present = concept IS IN codeset(troponin)`

`cxr_present = concept IS IN codeset(chest_xray)`

`lipase_present = concept IS Triacylglycerol lipase measurement [SNOMED 104988000]`

`iv_push_present = concept IS Therapeutic, prophylactic, or diagnostic injection ... intravenous push, single or initial substance/drug [CPT4 96374] OR concept IS ... each additional sequential intravenous push of a new substance/drug [CPT4 96375]`

**Work-up service in window.** The applicant has an event of the service within 1 day, before or after, of a chest pain event. The window is `workup_window_days = 1`.

`<service>_in_window = <service>_present AND EXISTS chest pain event date d, service event date e with |e - d| <= workup_window_days`

The window replaces the letrozole rule "first seen 74 or more days after the anchor". The reason is that c3 is a same-day care pattern. For all five top codes of c3 the median first occurrence is the same day as the first chest pain, and 21% (troponin), 33% (chest X-ray), 34% (lipase), 33% (IV push, first drug) and 34% (IV push, each additional drug) of the patients who have the code had it before the first chest pain. A one-sided "late" threshold would remove the care the pattern describes. The window is symmetric because an ED test can be dated the day before the claim that carries the chest pain code. The rule uses any occurrence in the window, not the first occurrence ever. A window of 1 day is a draft value, it is not calibrated (see the evaluation protocol).

---

### Composites

A composite combines atomic predicates, or other composites, into a named clinical pattern.

#### Work-up service bundle

**Work-up service count.** The number of the four services that the applicant had within the window of a chest pain event.

`workup_entity_count = troponin_in_window + cxr_in_window + lipase_in_window + iv_push_in_window`

**Work-up bundle.** Three or more of the four services, each in the window. The value 3 is a draft: it lets the rule hold when one service is missing from the claims. It is not calibrated.

`composite_workup_bundle = workup_entity_count >= 3`

#### Work-up sequences

An ordered sequence is a subsequence of the applicant's event list: the steps appear in this order and need not be adjacent. Every sequence starts at a chest pain event, and its last step falls no later than `workup_window_days` after that chest pain event. A step is met by any code of its list. The three sequences are the three highest-lift patterns of c3 that contain chest pain, as mined (4 steps each).

**A. Chest pain, chest X-ray, troponin, CMP.**

`composite_seq_cxr_trop_cmp = chest_pain -> cxr -> troponin -> cmp`

**B. Chest pain, ECG, troponin, CMP.**

`composite_seq_ecg_trop_cmp = chest_pain -> ecg -> troponin -> cmp`

**C. Chest pain, troponin, CMP, CBC.**

`composite_seq_trop_cmp_cbc = chest_pain -> troponin -> cmp -> cbc`

**Work-up sequence.** At least one of the three sequences.

`composite_workup_sequence = composite_seq_cxr_trop_cmp OR composite_seq_ecg_trop_cmp OR composite_seq_trop_cmp_cbc`

Here `cmp` is Comprehensive metabolic panel [SNOMED 371361000119107] and `cbc` is Complete blood count with white cell differential, automated [SNOMED 9564003]; the other steps are the lists in the registry.

#### Same-day order

Claims carry a date, not a time. The order of events is: event date; then, on the same day, the domain (visit, condition, procedure, measurement, drug, observation: `DOMAIN_ORDER`); then the OMOP ID, smallest first. The three sequences were mined with this rule (`tie_ordered`). For these sequences it gives the following same-day order:

1. chest pain (condition);
2. chest X-ray or ECG (procedure);
3. the blood tests (measurement), by OMOP ID: troponin (2212605, 2212610), then CMP (3661905), then CBC (4319466).

This matters more here than for letrozole. c3 is a same-day care pattern (final verdict *Suggestive*, not *Solid*): with every step required on a strictly later day, the support of the patterns falls below half of its table value. For c3 the order inside the sequences is mostly the tie-break, not an order shown by dates. In particular "troponin, then CMP, then CBC" on one day is the order of their OMOP IDs. Read each sequence as "chest pain, an X-ray or ECG, a troponin and a basic blood panel in one episode". The evaluation reports the strict-date match next to the `tie_ordered` match, so the share of applicants whose "order" is only a tie-break is visible.

#### Ablation composites

These two composites are not part of the flag. They show what each half of the rule contributes.

`composite_workup_bundle_only = chest_pain_present AND composite_workup_bundle`

`composite_workup_sequence_only = chest_pain_present AND composite_workup_sequence`

---

## Flag rule (draft, underwriting logic)

An applicant with chest pain is flagged **Manual RUW (c3 pattern)** when all three conditions are true. The flag marks an applicant whose chest pain sits in an emergency-type work-up. It does not diagnose heart disease, and a normal troponin and ECG also meet it, because the predicates test that the tests were done, not their results.

`composite_c3_manual_ruw = chest_pain_present AND composite_workup_bundle AND composite_workup_sequence`

In words: the applicant has at least three of the four work-up services (troponin, chest X-ray, lipase, IV push), each within 1 day of a chest pain event, and the applicant has at least one of the three sequences A, B or C completed within 1 day of the chest pain event.

### How the flag is decided

For the underwriting review: three questions, top to bottom. The first "No" ends the check and the applicant is routine for this rule.

1. Does the applicant have a chest pain event? If no, the rule does not apply.
2. Did the applicant have at least 3 of the 4 work-up services within 1 day of a chest pain event? If no, routine for this rule.
3. Did the applicant have sequence A, B or C within 1 day of the chest pain event? If no, routine for this rule.

All three "Yes" gives **Manual RUW (c3 pattern)**. The checks run in this order; the first check that fails sends the applicant to *not flagged*.

![Decision flow of the chest pain c3 flag, underwriter version](chestpain_c3_flag_flow.png)

### Underwriter checklist

Tick every line that applies. The flag is **Manual RUW (c3 pattern)** only when sections 1, 2 and 3 are all met. Dates are counted from a chest pain event. Codes in brackets are billing or medical codes; the full lists are in Annex B.

**1. Chest pain**

| ☐ | Check |
| :---: | :---- |
| ☐ | The applicant has at least one chest pain diagnosis (chest pain [SNOMED 29857009], precordial pain, chest pain on breathing, or pain of the intercostal space) |

**2. At least 3 of the 4 services, each within 1 day of a chest pain event**

| ☐ | Service | Codes | Seen within 1 day of chest pain? |
| :---: | :---- | :---- | :---: |
| ☐ | Troponin blood test (quantitative or qualitative) | CPT4 84484, 84512 | ☐ |
| ☐ | Chest X-ray (1, 2, 3 or 4 or more views) | CPT4 71045, 71046, 71047, 71048 | ☐ |
| ☐ | Lipase blood test (pancreas marker) | SNOMED 104988000 | ☐ |
| ☐ | IV push injection (first drug or each additional drug) | CPT4 96374, 96375 | ☐ |

Section 2 is met when 3 or more of the last-column boxes are ticked. A service seen more than 1 day from every chest pain event does not count. An ECG does not count here.

**3. At least 1 sequence after a chest pain event** (in this order; other events may sit in between; last step within 1 day of the chest pain event)

| ☐ | Sequence |
| :---: | :---- |
| ☐ | A: chest pain → chest X-ray → troponin blood test → comprehensive metabolic panel (CMP) [SNOMED 371361000119107] |
| ☐ | B: chest pain → ECG (CPT4 93000, 93005, 93010, or HCPCS G0403, G0404) → troponin blood test → CMP |
| ☐ | C: chest pain → troponin blood test → CMP → complete blood count (CBC) [SNOMED 9564003] |

**Result:** sections 1, 2 and 3 all met → **Manual RUW (c3 pattern)**. Anything else → routine for this rule. The flag marks a care pattern, not a diagnosis.

### What the flag is compared against

One against all. The flag targets c3. Every other care pattern is a comparison group, grouped as the notebook groups them. Sizes are those of the k=8 run (`nmf_k8_chestpain_AHA_components.json`); patients are counted in the care pattern of their dominant NMF component.

| Group | Care pattern | Name | Patients | % of cohort | Draft triage |
| :---- | :---- | :---- | ----: | ----: | :---- |
| **Target** | c3 | acute / ED work-up (troponin, chest X-ray, IV injections, ondansetron, ketorolac, BMP, CBC, lipase) | 17,250 | 12.4% | manual UW review (troponin result, ECG, imaging, outcome of the work-up) |
| Cardiac work-up (comparison) | c0 | outpatient cardiometabolic check-up and elective cardiac testing (lipid panel, ECG, HbA1c, hyperlipidemia, hypertension, stress test, CCTA) | 31,113 | 22.3% | unclear (elective cardiac testing; may need its own rule) |
| Non-cardiac explanation | c4 | GI work-up and cancer screening (surgical pathology, endoscopy and biopsy, colonoscopy, mammography, GERD, peptic ulcer) | 8,409 | 6.0% | routine (non-cardiac explanation) |
| Non-cardiac explanation | c7 | acute respiratory infection (cough, upper respiratory infection, pharyngitis, COVID-19, antigen tests, sinusitis) | 11,154 | 8.0% | routine (non-cardiac explanation) |
| Non-cardiac explanation | | *subtotal* | 19,563 | 14.0% | |
| Background | c2 | women's health and genitourinary (gyn exam, infectious-agent tests, cytology, pregnancy test, urine culture, transvaginal echo) | 16,770 | 12.0% | routine (care unrelated to the chest pain) |
| Background | c5 | musculoskeletal and physical therapy (physical therapy, manual therapy, chiropractic; low back, neck, shoulder pain) | 19,127 | 13.7% | routine (non-cardiac explanation) |
| Background | c6 | nutrition and endocrine labs (vitamin B12 and D, iron, ferritin, folate, free T4, HbA1c, testosterone) | 10,987 | 7.9% | routine (care unrelated to the chest pain) |
| Background | | *subtotal* | 46,884 | 33.6% | |
| Drug domain | c1 | acute-illness and chronic prescriptions (steroids, antibiotics, NSAIDs, PPI and H2 blockers, SSRI, benzodiazepine) | 24,606 | 17.6% | unclear (the care pattern does not show the clinical context; use other evidence) |

The triage text is a draft inference and needs review by an underwriter. The triage column of `final_table_chestpain_k8_AHA.xlsx` holds the same draft by care pattern (c3 Manual RUW; c0 and c1 Unclear; the others Routine). The c0 care pattern is the closest competitor: it also holds ECGs and elective cardiac tests, so an applicant with a check-up and a scheduled stress test is the case the window and the 3-of-4 services are meant to separate.

---

## Evaluation protocol

*Defined here, not run. No coverage number below is measured.*

The flag is scored one against all against the c3 label (`labels` and `pids` of `nmf_k8_chestpain_AHA.npz`):

* the confusion table, precision, recall, specificity and lift over the 12.4% base rate;
* the same table for each other care pattern separately (c0, c1, c2, c4, c5, c6, c7), then pooled by group (cardiac work-up, non-cardiac explanation, background, drug domain);
* the distribution of `workup_entity_count` (0 to 4) in c3 and outside it, to check the value 3;
* the two ablation composites, and the `tie_ordered` against strict-date match of the sequences, each with and without the 1-day span;
* the calibration of the window: for the patients of c3, the share with each service within 0, 1, 3 and 7 days of a chest pain event. `workup_window_days = 1` stays a draft value until this table is read.

Limits to read the result with:

* **The comparison is circular by construction.** c3 is the NMF assignment, and the four services are top loadings of c3. High recall measures how well the rule restates the care pattern. It does not validate the rule clinically.
* **External check without the NMF.** The forward outcome `cardiac_workup_outcome()` (stress test, coronary angiography or coronary artery disease diagnosis after the chest pain index date) is independent of the care pattern. Report the flag against it with troponin removed from the outcome, because troponin is part of the rule. That outcome partly measures reviewer and clinician behaviour, not true cardiac risk.
* **The rule tests that care happened, not what it found.** Nothing in the predicates reads a troponin value or an ECG result. A normal work-up and an abnormal one both meet the flag. Results are the natural next layer for clinical review.
* **ECG is not counted.** ECG is not among the five top codes of c3, and it is one of the five top codes of the outpatient check-up care pattern (c0). Counting it would blur the two. It enters only through sequence B.
* **IV push, lipase, CMP and CBC are not specific to chest pain.** They mark emergency or hospital care for any complaint (abdominal pain, nausea, infection). The visit records that would show an ED visit are removed before the analysis (the list `ed_visit` has no patients), so the rule infers "ED-type care" from the services. An ED visit for another complaint with a chest pain code on the same claim can meet the flag.
* **The sequences are not very specific.** About a quarter of the patients outside c3 have each sequence (any time order, no 1-day span), against 59% to 65% inside c3. The window and the bundle are what narrow the rule.
* **Four steps against a three-step core.** The last step (CMP or CBC) is a routine blood panel that is also a top code of the check-up care pattern c0 (CMP is in its top five, CBC in its top ten), so it adds little to separate emergency care from check-ups. The version 1 shape was chest pain, a test, troponin. Whether to use the three-step core is a question for clinical review; its support in c3 is not measured here.
* **Troponin cannot be split by type.** The troponin codes in the extract (CPT4 84484 and 84512) do not tell high-sensitivity troponin from the standard test, so the rule cannot separate them.
* **Same-day order is a tie-break.** See the section Same-day order.
* **Care pattern statistics are not applicant statistics.** The window comes from care pattern medians (same day). The rule applies it to each applicant's own dates.
* **Literature support is partial.** The PubMed check of the k=8 final table (16 October 2026; titles and abstracts read, not full texts) rates all three c3 sequences *Partly*: papers on the emergency evaluation of chest pain with ECG, troponin and chest X-ray (PMIDs 18775237, 28925655, 28765984) and, kept on their titles, the 2021 AHA/ACC chest pain guideline (34709879) and the 2022 ACC emergency department consensus pathway (36241466). No abstract names a CMP step, only one names a CBC with troponin (21534844), and no paper tests the order of the steps. A clinician should confirm each *Partly*. Version 1 ratings were not carried over.

---

## Population Coverage

Not measured yet. The tables list what is known at the care pattern level, from the k=8 run and its final table.

| Quantity | Value |
| :---- | :---- |
| Cohort | 139,416 patients (any of the five R07.x chest pain codes) |
| Care pattern c3 | 17,250 patients, 12.4% |
| Troponin (list) in c3 | 81% of c3, median same day as first chest pain, 21% before |
| Chest X-ray (list) in c3 | 86% of c3, median same day, 33% before |
| Lipase (SNOMED 104988000) in c3 | 59% of c3, median same day, 34% before |
| IV push, first drug (CPT4 96374) in c3 | 66% of c3, median same day, 33% before |
| IV push, each additional drug (CPT4 96375) in c3 | 55% of c3, median same day, 34% before |

| Pattern of c3 | Share of c3 | Share of the other care patterns | Times as common | Held-out check (40 splits) |
| :---- | ----: | ----: | ----: | :---- |
| A. Chest pain → chest X-ray → troponin → CMP | 59.4% | 24.4% | 2.4 | passed |
| B. Chest pain → ECG → troponin → CMP | 64.9% | 26.7% | 2.4 | passed |
| C. Chest pain → troponin → CMP → CBC | 62.8% | 25.5% | 2.4 | passed |

Shares are those of the final table (any time order, no 1-day span; the other care patterns are a random sample of 1,500 patients). All three patterns passed the held-out check on every one of the 40 splits. The verdict is *Suggestive*, not *Solid*, because c3 is a same-day care pattern. Literature rating of the three patterns: *Partly* (see the limits).

| Predicate or composite | Policies | % cohort |
| :---- | ----: | ----: |
| `chest_pain_present` | not measured | |
| `composite_workup_bundle` (`workup_entity_count >= 3`) | not measured | |
| `composite_workup_sequence` | not measured | |
| `composite_c3_manual_ruw` | not measured | |

---

## References

* Final table of the chest pain k=8 run on the AHA/ACC lists: `nb/repr_learn_chestpain/outputs/final_table_chestpain_k8_AHA.xlsx` (notebook `Chestpain_NMF_PrefixSpan_AHA.ipynb`, section 6).
* Lists of codes: `nb/repr_learn_chestpain/codesets_v2.yaml`, checked with `check_codesets.py`; the 2021 AHA/ACC chest pain guideline is the source of the lists.
* Care patterns and top codes: `nmf_k8_chestpain_AHA_components.json`; the members of each list: `token_members_k8_chestpain_AHA.csv` (notebook section 5).
* Literature check of the k=8 table: `final_table_chestpain_k8_AHA_literature_evidence.csv` (steps found per paper), `..._literature_verified.csv`, `..._literature_search_log.csv`; scripts in `literature_search/aha_k8/`.
* Plain-English wording and the parallel mapping to OMOP: `chestpain_plain_labels.yaml`, `chestpain_plain_english_omop_map.csv`, built by `build_plain_english_annex.py` (Annex A and B below).
* Flow image: `chestpain_c3_flag_flow.png`, built by `make_c3_flag_flow.py`.
* Matching semantics (`tie_ordered`, `strict_date`, `windowed`): `nb/repr_learn_letrozole/motif_robustness/seqindex.py`.
* Forward outcome: `cardiac_workup_outcome()` in `nb/repr_learn_chestpain/ethos_omop.py`.
* Version 1 of this document (k=5, c0): `Chestpain_Workup_Predicate_Engine.md`.
* Format and voice: `Letrozole_Rx_Predicate_Engine.md`.

---

<!-- ANNEX:BEGIN -->

## Annex A. Plain-English guide

This annex is for the UW team. It fixes the words used in this document so that the UW team and the data team mean the same thing. The wording lives in `chestpain_plain_labels.yaml` and the tables are generated by `build_plain_english_annex.py`; edit the file and re-run the script, not the tables.

### A1. Abbreviations

| Abbreviation | Meaning |
| :---- | :---- |
| ACC | American College of Cardiology |
| ACS | acute coronary syndrome (heart attack or unstable angina) |
| AF | atrial fibrillation (irregular heart rhythm) |
| AHA | American Heart Association; AHA/ACC is the 2021 chest pain guideline the lists of codes follow |
| BMP | basic metabolic panel (blood chemistry: electrolytes, kidney function, glucose) |
| BNP | B-type natriuretic peptide (blood marker of heart strain) |
| CABG | coronary artery bypass graft (heart bypass surgery) |
| CAC | coronary artery calcium (score from a CT scan) |
| CAD | coronary artery disease (narrowed heart arteries) |
| CBC | complete blood count |
| CCTA | coronary CT angiogram (CT scan of the heart arteries) |
| CK-MB | creatine kinase MB (older blood marker of heart injury) |
| CKD | chronic kidney disease |
| CMP | comprehensive metabolic panel (BMP plus liver tests and protein) |
| CMR | cardiac magnetic resonance (heart MRI) |
| CPT4 | Current Procedural Terminology, the billing code system for procedures and tests |
| CXR | chest X-ray |
| ECG | electrocardiogram (heart tracing; also written EKG) |
| ED | emergency department |
| FFR-CT | fractional flow reserve from CT (estimate of how much an artery narrowing limits blood flow) |
| GERD | gastroesophageal reflux disease (acid reflux) |
| GI | gastrointestinal (stomach and bowel) |
| H2 | H2 blocker (acid-reducing medicine such as famotidine) |
| HbA1c | hemoglobin A1c (blood test of average blood sugar) |
| HCPCS | Healthcare Common Procedure Coding System, a billing code system (here for screening ECGs) |
| HTN | hypertension (high blood pressure) |
| ICA | invasive coronary angiogram (cardiac catheterisation) |
| INOCA | ischemia with no obstructive coronary arteries |
| IV | intravenous (into a vein) |
| MI | myocardial infarction (heart attack) |
| NMF | non-negative matrix factorization, the method that finds the care patterns |
| OMOP | the standard data model the codes are stored in; each code has an OMOP ID |
| PCI | percutaneous coronary intervention (stent or balloon) |
| PE | pulmonary embolism (blood clot in the lung) |
| PET | positron emission tomography (nuclear scan) |
| PMID | PubMed number of a published paper |
| PPI | proton pump inhibitor (acid-reducing medicine such as omeprazole) |
| PT | prothrombin time (clotting test) |
| RUW | the underwriting review step; Manual RUW is the route to manual review |
| SNOMED | SNOMED CT, a medical terminology used for diagnoses, tests and procedures |
| SPECT | single-photon emission CT (nuclear heart scan) |
| SSRI | selective serotonin reuptake inhibitor (a class of antidepressant) |
| T2DM | type 2 diabetes mellitus |
| T4 | thyroxine (thyroid hormone; free T4 is a thyroid blood test) |
| TEE | transesophageal echocardiogram (heart ultrasound through the food pipe) |
| TTE | transthoracic echocardiogram (heart ultrasound through the chest wall) |
| UW | underwriting / underwriter |
| V/Q | ventilation-perfusion (lung scan for clots) |

### A2. UW wording and data-team wording

| UW wording (used in this document) | Data-team wording | What it means |
| :---- | :---- | :---- |
| care pattern | bundle, NMF component, c0 to c7 | a group of services that tend to appear together in the same patients; the data method finds them, nobody chose them |
| service | entity, token | one test, procedure or medicine that the rule looks for |
| diagnosis | entity, condition concept | a diagnosis code on a claim |
| list of codes | codeset, tag, code group, [code group] | a hand-built list of billing and medical codes that mean the same thing for this purpose (for example every troponin code) |
| code | OMOP concept, concept_id | one billing or medical code as stored in the data, with an OMOP ID that only the data team needs |
| billing or medical code | vocabulary code (CPT4 84484, SNOMED 29857009) | the code a provider or system used on the claim |
| yes/no check | predicate, `*_present`, `*_in_window` | a single question about one applicant's history that has a yes or no answer |
| combined check | composite | several yes/no checks put together |
| chest pain date | anchor, `first_chest_pain_date`, index date | the date of a chest pain diagnosis; everything else is measured from it |
| within 1 day | `workup_window_days = 1` | the service is dated no more than one day before or after a chest pain date |
| same-day order rule | tie-break, `tie_ordered`, DOMAIN_ORDER | claims have a date but no time; steps on the same day are put in a fixed order (diagnosis, procedure, lab test), then by code ID |
| this care pattern compared with all the others | one versus all | how the rule is scored: the ED care pattern against the seven other care patterns |
| times as common | lift | how many times more common the pattern is inside the care pattern than outside it |
| re-test on half the patients | held-out check | the pattern is looked for again on a random half of the patients that was not used to find it |
| Manual RUW trigger | flag, `composite_c3_manual_ruw` | the rule result that sends the applicant to manual review |

### A3. Plain label of every list of codes

70 lists of codes (`codesets_v2.yaml`, validated with `check_codesets.py`). *Patients* is the number of the 139,416 chest pain patients with at least one code of the list; *Codes* is the number of codes in the list (codes that no patient in this extract has are counted but listed with 0 patients in Annex B).

**Chest pain and look-alike symptoms**

| Plain label | Abbr. | Data-team name | What it is | Used in the engine as | Codes | Patients |
| :---- | :---- | :---- | :---- | :---- | ----: | ----: |
| Chest pain diagnosis | — | `chest_pain` | Any diagnosis of chest pain, precordial pain, pain of the intercostal space or chest pain on breathing. Defines who is in the cohort and the chest pain date. | anchor: the chest pain date | 4 | 139,416 |
| Pain on breathing (pleuritic) diagnosis | — | `pleuritic_pain` | Sharp pain that changes with breathing or position; makes a heart cause less likely. | — | 1 | 5,721 |
| Shortness of breath diagnosis | — | `dyspnea` | Breathlessness, which the guideline treats as a possible equivalent of chest pain. | — | 1 | 44,119 |
| Palpitations diagnosis | — | `palpitations` | Awareness of the heartbeat (racing, pounding or skipping). | — | 1 | 28,381 |
| Fainting diagnosis | — | `syncope` | Passing out; can accompany a heart cause. | — | 2 | 10,343 |

**Tests used in the chest pain work-up**

| Plain label | Abbr. | Data-team name | What it is | Used in the engine as | Codes | Patients |
| :---- | :---- | :---- | :---- | :---- | ----: | ----: |
| ECG (resting 12-lead) | ECG | `ekg` | The standard heart tracing, billed as tracing only, interpretation only, or both together. Not the long-term monitors. | sequence B (not counted as a service) | 5 | 114,443 |
| Long-term heart rhythm monitor (Holter or event recorder) | — | `ecg_ambulatory` | Heart rhythm recorded for days or weeks, or by an implanted recorder. Not an emergency chest pain test. | — | 24 | 16,256 |
| Troponin blood test | — | `troponin` | The blood test for heart muscle injury, quantitative or qualitative. The data cannot tell high-sensitivity troponin from the standard test. | service 1 and every sequence | 2 | 56,384 |
| CK-MB or myoglobin blood test | CK-MB | `ck_mb_myoglobin` | Older heart-injury markers; the guideline sees no benefit once troponin is available. | — | 3 | 5,094 |
| BNP blood test | BNP | `bnp` | Blood marker of heart strain, used mainly for heart failure. | — | 1 | 20,375 |
| Chest X-ray | CXR | `chest_xray` | Chest X-ray of 1, 2, 3 or 4 or more views, in the hospital or clinic. | service 2 and sequence A | 4 | 84,611 |
| Heart ultrasound through the chest wall | TTE | `echo_tte` | Standard echocardiogram; first test for non-ischemic heart causes. Stress and congenital echocardiograms are listed separately. | — | 6 | 38,830 |
| Heart ultrasound through the food pipe | TEE | `echo_tee` | Echocardiogram with the probe in the esophagus; used for aortic and valve questions. | — | 4 | 815 |
| Exercise stress test with ECG (treadmill) | — | `stress_ecg` | Heart tracing while the patient exercises. | — | 4 | 28,641 |
| Stress echocardiogram | — | `stress_echo` | Heart ultrasound at rest and under stress. | — | 6 | 7,463 |
| Nuclear stress scan (SPECT) | SPECT | `stress_spect` | Heart blood-flow images with a radioactive tracer at rest and under stress. | — | 4 | 13,650 |
| PET heart scan | PET | `stress_pet` | Nuclear heart scan that measures blood flow. | — | 8 | 910 |
| Heart MRI | CMR | `cmr` | Magnetic resonance imaging of the heart. | — | 2 | 698 |
| Coronary CT angiogram | CCTA | `ccta` | CT scan with contrast that shows the heart arteries. | — | 1 | 5,054 |
| Coronary calcium score | CAC | `cac_score` | CT scan that counts calcium in the heart arteries. | — | 1 | 1,790 |
| CT-based flow estimate for artery narrowing | FFR-CT | `ffr_ct` | Computer estimate from a CT scan of how much a narrowing limits blood flow. | — | 5 | 311 |
| Invasive coronary angiogram (catheterisation) | ICA | `coronary_angio` | X-ray of the heart arteries through a catheter. Anesthesia and clot-dissolving codes are not included. | — | 18 | 4,656 |
| D-dimer blood test | — | `d_dimer` | Blood marker of clotting, used when a lung clot is possible. | — | 3 | 26,653 |
| Lung ventilation-perfusion scan | V/Q | `vq_scan` | Nuclear lung scan to look for blood clots. | — | 3 | 408 |

**Heart and blood-vessel diagnoses**

| Plain label | Abbr. | Data-team name | What it is | Used in the engine as | Codes | Patients |
| :---- | :---- | :---- | :---- | :---- | ----: | ----: |
| Heart attack or unstable angina diagnosis | ACS | `acs_mi` | Acute heart attack (MI), unstable angina or acute coronary syndrome. Complications of a heart attack are not included. | — | 16 | 3,419 |
| Old heart attack diagnosis | MI | `old_mi` | History of a past heart attack. | — | 1 | 1,823 |
| Angina diagnosis (stable or other) | — | `angina_stable` | Chest pain from the heart that comes with effort; unstable angina is under heart attack or unstable angina. | — | 4 | 5,432 |
| Coronary artery disease diagnosis (chronic) | CAD | `cad_chronic` | Narrowed heart arteries or chronic ischemic heart disease. The data cannot say how severe the narrowing is. | — | 4 | 10,053 |
| Angina with open arteries (small-vessel disease or spasm) | INOCA | `inoca_cmd` | Microvascular dysfunction, vasospastic or variant angina, coronary spasm. | — | 2 | 280 |
| Aortic dissection or aortic aneurysm diagnosis | — | `aortic_syndrome` | Tear or bulge of the main artery from the heart; a life-threatening cause of chest pain. | — | 3 | 748 |
| Blood clot in the lung diagnosis | PE | `pe` | Pulmonary embolism. | — | 3 | 1,773 |
| Inflammation of the heart sac or heart muscle diagnosis | — | `pericarditis_myocarditis` | Pericarditis, myocarditis, fluid around the heart, tamponade. | — | 16 | 1,114 |
| Heart valve disease diagnosis | — | `valvular_hd` | Narrowed or leaking aortic or mitral valve, mitral prolapse. Congenital valve disease is not included. | — | 9 | 1,541 |
| Heart muscle disease diagnosis | — | `cardiomyopathy` | Cardiomyopathy of any type. | — | 12 | 1,756 |
| Heart failure diagnosis | — | `heart_failure` | The heart does not pump well enough. | — | 15 | 5,833 |
| Abnormal heart rhythm diagnosis | AF | `arrhythmia` | Atrial fibrillation or flutter, supraventricular tachycardia, ventricular tachycardia or fibrillation. | — | 12 | 6,652 |

**Other diagnoses that can explain chest pain**

| Plain label | Abbr. | Data-team name | What it is | Used in the engine as | Codes | Patients |
| :---- | :---- | :---- | :---- | :---- | ----: | ----: |
| Pneumonia or fluid around the lung diagnosis | — | `pneumonia_pleural` | Pneumonia, pleural effusion, pleurisy, empyema. | — | 34 | 11,837 |
| Collapsed lung or blood in the chest cavity diagnosis | — | `pneumothorax` | Pneumothorax or hemothorax. | — | 10 | 494 |
| Acid reflux or heartburn diagnosis | GERD | `gerd` | Diagnosis codes only; a reflux test is not included. | — | 4 | 46,827 |
| Stomach or food-pipe irritation, ulcer or hernia diagnosis | — | `peptic_ulcer_gastritis` | Ulcer, gastritis, esophagitis, esophageal spasm, indigestion, hiatal hernia. | — | 38 | 20,062 |
| Gallbladder or pancreas diagnosis | — | `biliary_pancreatic` | Gallstones, gallbladder inflammation, biliary colic, pancreatitis. | — | 30 | 6,967 |
| Rib-cartilage inflammation diagnosis (costochondritis) | — | `costochondritis` | Chest wall pain from inflamed rib cartilage. | — | 1 | 4,506 |
| Chest wall injury or strain diagnosis | — | `chest_wall` | Rib or breastbone fracture, flail chest, bruised chest wall, thoracic outlet syndrome, chest wall strain. | — | 8 | 1,042 |
| Shingles diagnosis | — | `herpes_zoster` | Herpes zoster; the pain can come before the rash. | — | 2 | 3,258 |
| Anxiety diagnosis | — | `anxiety` | Any anxiety diagnosis. | — | 12 | 51,301 |
| Panic disorder diagnosis | — | `panic_attack` | Panic disorder; agoraphobia alone is not included. | — | 1 | 6,473 |
| Depression or somatic-symptom disorder diagnosis | — | `depression_somatic` | Major or recurrent depression, somatization, hypochondriasis. | — | 25 | 29,432 |
| Hyperventilation diagnosis | — | `hyperventilation` | Overbreathing, often with anxiety. | — | 1 | 267 |
| Sickle cell disease diagnosis | — | `sickle_cell` | Sickle cell disease (not the trait); can cause chest pain crises. | — | 8 | 76 |
| Cocaine or methamphetamine use diagnosis | — | `cocaine_meth` | Use or dependence diagnoses; a recognised cause of chest pain. | — | 11 | 710 |

**Risk factors and history**

| Plain label | Abbr. | Data-team name | What it is | Used in the engine as | Codes | Patients |
| :---- | :---- | :---- | :---- | :---- | ----: | ----: |
| High blood pressure diagnosis | HTN | `htn` | Essential or hypertensive heart disease; pregnancy-related and lung-artery types are not included. | — | 3 | 59,384 |
| High cholesterol or blood fat diagnosis | — | `hyperlipidemia` | Hyperlipidemia, hypercholesterolemia, hypertriglyceridemia, dyslipidemia. | — | 6 | 64,052 |
| Tobacco or nicotine use diagnosis | — | `tobacco` | Smoker, tobacco use, nicotine dependence. | — | 4 | 28,720 |
| Type 2 diabetes diagnosis | T2DM | `t2dm` | Type 2 diabetes in any form. | — | 6 | 18,966 |
| HbA1c blood test | HbA1c | `hba1c` | Blood test of average blood sugar. | — | 1 | 72,635 |
| Chronic kidney disease or dialysis | CKD | `ckd_dialysis` | Chronic or end-stage kidney disease and dialysis care. | — | 19 | 5,109 |
| Prior heart bypass or stent procedure | CABG / PCI | `prior_revasc` | Bypass surgery, balloon angioplasty, stent, atherectomy. | — | 33 | 1,012 |
| Nerve damage (neuropathy) diagnosis | — | `neuropathy` | Kept from the first code list version as a diabetes marker. | — | 32 | 7,615 |

**Medicines and visits**

| Plain label | Abbr. | Data-team name | What it is | Used in the engine as | Codes | Patients |
| :---- | :---- | :---- | :---- | :---- | ----: | ----: |
| Angina medicines (nitrates, ranolazine) | — | `nitrate_antianginal` | Nitroglycerin, isosorbide, ranolazine; rectal and ointment forms are not included. | — | 24 | 1,548 |
| Antiplatelet medicines | — | `antiplatelet` | Clopidogrel, prasugrel, ticagrelor and low-dose aspirin (81 mg). | — | 17 | 3,702 |
| Beta-blocker medicines | — | `beta_blocker` | Metoprolol, atenolol, carvedilol, bisoprolol, propranolol. | — | 65 | 12,316 |
| Statin medicines | — | `statin` | Atorvastatin, simvastatin, rosuvastatin, pravastatin. | — | 43 | 18,151 |
| Acid-reducing medicines (PPI or H2 blocker) | PPI / H2 | `ppi_h2` | Omeprazole, esomeprazole, pantoprazole, lansoprazole, rabeprazole, famotidine, ranitidine, cimetidine. | — | 85 | 32,244 |
| SSRI antidepressant medicines | SSRI | `ssri` | Sertraline, fluoxetine, escitalopram, citalopram, paroxetine. | — | 56 | 20,114 |
| Benzodiazepine (sedative) medicines | — | `benzodiazepine` | Alprazolam, lorazepam, diazepam, clonazepam, temazepam. | — | 63 | 20,204 |
| Psychiatric evaluation or psychotherapy visit | — | `psych_eval_therapy` | Shows psychiatric care took place, not that anxiety was the reason. | — | 15 | 25,458 |
| Brief mental-health screening | — | `psych_screen` | Shows a screening took place, not that anyone has anxiety. Kept apart from psychotherapy visits. | — | 1 | 19,572 |
| Emergency department visit | ED | `ed_visit` | A visit record for an emergency room or emergency department. Visit records are removed before the analysis, so the patient count is 0 here. | — | 1 | 0 |

**Combined lists (umbrellas)**

| Plain label | Abbr. | Data-team name | What it is | Used in the engine as | Codes | Patients |
| :---- | :---- | :---- | :---- | :---- | ----: | ----: |
| Any heart stress test (combined list) | — | `stress_test` | Everything in the exercise ECG, stress echo, nuclear (SPECT) and PET lists. Its codes are shown under those lists. | — | 19 | — |
| Any coronary artery disease or heart attack diagnosis (combined list) | CAD | `cad` | Everything in the chronic CAD and heart attack lists. Its codes are shown under those lists. | — | 20 | — |

## Annex B. Parallel mapping to OMOP codes

For each plain label, the OMOP concepts behind it, with the verbatim OMOP concept name, the billing or medical code and the OMOP ID (`concept_id`). The same rows are in `chestpain_plain_english_omop_map.csv` for the data team, with the extra columns *domain*, *in cohort* and *also in lists*. A code that belongs to two lists is shown under the first list in the order of `codesets_v2.yaml`, with the other list noted. *Patients* is the number of chest pain patients with that code.

### B0. Other codes used by the engine

Single codes that are not in a list of codes. Lipase, IV push, CMP and CBC are part of the rule; the other four are among the ten strongest codes of the ED care pattern and are not used.

| Plain label | Used as | Verbatim OMOP concept name | Code | OMOP ID | Patients |
| :---- | :---- | :---- | :---- | ----: | ----: |
| Lipase blood test (pancreas marker) | rule service | Triacylglycerol lipase measurement | SNOMED 104988000 | 4021288 | 34,420 |
| IV push, first drug | rule service (IV push) | Therapeutic, prophylactic, or diagnostic injection (specify substance or drug); intravenous push, single or initial substance/drug | CPT4 96374 | 2314215 | 33,199 |
| IV push, each additional drug | rule service (IV push) | Therapeutic, prophylactic, or diagnostic injection (specify substance or drug); each additional sequential intravenous push of a new substance/drug (List separately in addition to code for primary procedure) | CPT4 96375 | 2314216 | 23,192 |
| Comprehensive metabolic panel (CMP) | sequence step | Comprehensive metabolic panel | SNOMED 371361000119107 | 3661905 | 95,388 |
| Complete blood count (CBC) | sequence step | Complete blood count with white cell differential, automated | SNOMED 9564003 | 4319466 | 94,699 |
| Basic metabolic panel (BMP) | other top code of the ED care pattern, not in the rule | Basic metabolic panel (Calcium, total) This panel must include the following: Calcium, total (82310) Carbon dioxide (bicarbonate) (82374) Chloride (82435) Creatinine (82565) Glucose (82947) Potassium (84132) Sodium (84295) Urea nitrogen (BUN) (84520) | CPT4 80048 | 2212090 | 47,761 |
| Ondansetron injection (anti-nausea) | other top code of the ED care pattern, not in the rule | ondansetron Injection | RxNorm 1740463 | 35605480 | 28,500 |
| Ketorolac injection (pain medicine, Toradol) | other top code of the ED care pattern, not in the rule | ketorolac Injectable Solution [Toradol] | RxNorm 363077 | 40048832 | 35,794 |
| Prothrombin time (clotting test) | other top code of the ED care pattern, not in the rule | Prothrombin time | SNOMED 396451008 | 4245261 | 28,910 |

### B. Chest pain and look-alike symptoms

#### Chest pain diagnosis · `chest_pain`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| chest pain | Chest pain | SNOMED 29857009 | 77670 | 133,792 | — |
| precordial pain (pain over the heart) | Precordial pain | SNOMED 71884009 | 134159 | 13,768 | — |
| chest pain on breathing | Chest pain on breathing | SNOMED 274664007 | 4168213 | 2,084 | — |
| pain of the intercostal space (between the ribs) | Pain of intercostal space | SNOMED 735940001 | 42539051 | 2,039 | — |

#### Pain on breathing (pleuritic) diagnosis · `pleuritic_pain`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Pleuritic pain | SNOMED 2237002 | 4330445 | 5,721 | — |

#### Shortness of breath diagnosis · `dyspnea`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Dyspnea | SNOMED 267036007 | 312437 | 44,119 | — |

#### Palpitations diagnosis · `palpitations`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Palpitations | SNOMED 80313002 | 315078 | 28,381 | — |

#### Fainting diagnosis · `syncope`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Syncope and collapse | SNOMED 309585006 | 4206148 | 10,308 | — |
| — | Carotid sinus syncope | SNOMED 51723007 | 436392 | 44 | — |

### B. Tests used in the chest pain work-up

#### ECG (resting 12-lead) · `ekg`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| interpretation only | Electrocardiogram, routine ECG with at least 12 leads; interpretation and report only | CPT4 93010 | 2313816 | 69,292 | — |
| tracing and interpretation together | Electrocardiogram, routine ECG with at least 12 leads; with interpretation and report | CPT4 93000 | 2313814 | 66,307 | — |
| tracing only | Electrocardiogram, routine ECG with at least 12 leads; tracing only, without interpretation and report | CPT4 93005 | 2313815 | 60,313 | — |
| screening ECG with interpretation (preventive visit) | Electrocardiogram, routine ecg with 12 leads; performed as a screening for the initial preventive physical examination with interpretation and report | HCPCS G0403 | 2617470 | 83 | — |
| screening ECG, tracing only (preventive visit) | Electrocardiogram, routine ecg with 12 leads; tracing only, without interpretation and report, performed as a screening for the initial preventive physical examination | HCPCS G0404 | 2617471 | 14 | — |

#### Long-term heart rhythm monitor (Holter or event recorder) · `ecg_ambulatory`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | External electrocardiographic recording for more than 7 days up to 15 days by continuous rhythm recording and storage; review and interpretation | CPT4 93248 | 759712 | 2,746 | — |
| — | External electrocardiographic recording up to 48 hours by continuous rhythm recording and storage; includes recording, scanning analysis with report, review and interpretation by a physician or other qualified health care professional | CPT4 93224 | 2313828 | 2,661 | — |
| — | External electrocardiographic recording for more than 48 hours up to 7 days by continuous rhythm recording and storage; review and interpretation | CPT4 93244 | 759708 | 2,584 | — |
| — | External electrocardiographic recording up to 48 hours by continuous rhythm recording and storage; review and interpretation by a physician or other qualified health care professional | CPT4 93227 | 2313831 | 2,523 | — |
| — | External electrocardiographic recording for more than 7 days up to 15 days by continuous rhythm recording and storage; recording (includes connection and initial recording) | CPT4 93246 | 759710 | 2,388 | — |
| — | External electrocardiographic recording up to 48 hours by continuous rhythm recording and storage; recording (includes connection, recording, and disconnection) | CPT4 93225 | 2313829 | 2,244 | — |
| — | External electrocardiographic recording for more than 7 days up to 15 days by continuous rhythm recording and storage; scanning analysis with report | CPT4 93247 | 759711 | 2,233 | — |
| — | External electrocardiographic recording for more than 48 hours up to 7 days by continuous rhythm recording and storage; recording (includes connection and initial recording) | CPT4 93242 | 759706 | 2,173 | — |
| — | External patient and, when performed, auto activated electrocardiographic rhythm derived event recording with symptom-related memory loop with remote download capability up to 30 days, 24-hour attended monitoring; review and interpretation by a physici... | CPT4 93272 | 2313844 | 2,166 | — |
| — | External electrocardiographic recording up to 48 hours by continuous rhythm recording and storage; scanning analysis with report | CPT4 93226 | 2313830 | 2,068 | — |
| — | External electrocardiographic recording for more than 48 hours up to 7 days by continuous rhythm recording and storage; scanning analysis with report | CPT4 93243 | 759707 | 1,990 | — |
| — | External patient and, when performed, auto activated electrocardiographic rhythm derived event recording with symptom-related memory loop with remote download capability up to 30 days, 24-hour attended monitoring; transmission and analysis | CPT4 93271 | 2313843 | 1,966 | — |
| — | External mobile cardiovascular telemetry with electrocardiographic recording, concurrent computerized real time data analysis and greater than 24 hours of accessible ECG data storage (retrievable with query) with ECG triggered and patient selected even... | CPT4 93229 | 2313833 | 1,826 | — |
| — | External patient and, when performed, auto activated electrocardiographic rhythm derived event recording with symptom-related memory loop with remote download capability up to 30 days, 24-hour attended monitoring; recording (includes connection, record... | CPT4 93270 | 2313842 | 1,826 | — |
| — | External patient and, when performed, auto activated electrocardiographic rhythm derived event recording with symptom-related memory loop with remote download capability up to 30 days, 24-hour attended monitoring; includes transmission, review and inte... | CPT4 93268 | 2313841 | 757 | — |
| — | External electrocardiographic recording for more than 48 hours up to 7 days by continuous rhythm recording and storage; includes recording, scanning analysis with report, review and interpretation | CPT4 93241 | 759705 | 612 | — |
| — | External electrocardiographic recording for more than 48 hours up to 21 days by continuous rhythm recording and storage; review and interpretation (Deprecated) | CPT4 0298T | 43527887 | 327 | — |
| — | External electrocardiographic recording for more than 48 hours up to 21 days by continuous rhythm recording and storage; scanning analysis with report (Deprecated) | CPT4 0297T | 43527886 | 282 | — |
| — | External electrocardiographic recording for more than 48 hours up to 21 days by continuous rhythm recording and storage; recording (includes connection and initial recording) (Deprecated) | CPT4 0296T | 43527885 | 274 | — |
| — | External electrocardiographic recording for more than 7 days up to 15 days by continuous rhythm recording and storage; includes recording, scanning analysis with report, review and interpretation | CPT4 93245 | 759709 | 135 | — |
| — | External electrocardiographic recording for more than 48 hours up to 21 days by continuous rhythm recording and storage; includes recording, scanning analysis with report, review and interpretation (Deprecated) | CPT4 0295T | 43527884 | 39 | — |
| — | Signal-averaged electrocardiography | SNOMED 33442008 | 4140676 | 4 | — |
| — | External mobile cardiovascular telemetry with electrocardiographic recording, concurrent computerized real time data analysis and greater than 24 hours of accessible ECG data storage (retrievable with query) with ECG triggered and patient selected even... | CPT4 93228 | 2313832 | 0 | — |
| — | Interrogation device evaluation(s), (remote) up to 30 days; implantable cardiovascular physiologic monitor system, implantable loop recorder system, or subcutaneous cardiac rhythm monitor system, remote data acquisition(s), receipt of tran... (Deprecated) | HCPCS G2066 | 40217340 | 0 | — |

#### Troponin blood test · `troponin`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| quantitative (measures the level) | Troponin, quantitative | CPT4 84484 | 2212605 | 56,341 | — |
| qualitative (positive or negative) | Troponin, qualitative | CPT4 84512 | 2212610 | 88 | — |

#### CK-MB or myoglobin blood test · `ck_mb_myoglobin`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Creatine kinase MB measurement | SNOMED 104613001 | 4017058 | 4,586 | — |
| — | Myoglobin measurement | SNOMED 33606006 | 4143902 | 1,491 | — |
| — | Creatine kinase isoenzymes measurement | SNOMED 16614002 | 4042917 | 277 | — |

#### BNP blood test · `bnp`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Brain natriuretic peptide measurement | SNOMED 390917008 | 4307029 | 20,375 | — |

#### Chest X-ray (CXR) · `chest_xray`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| 2 views | Radiologic examination, chest; 2 views | CPT4 71046 | 725069 | 57,811 | — |
| 1 view | Radiologic examination, chest; single view | CPT4 71045 | 725068 | 47,797 | — |
| 3 views | Radiologic examination, chest; 3 views | CPT4 71047 | 724942 | 132 | — |
| 4 or more views | Radiologic examination, chest; 4 or more views | CPT4 71048 | 724943 | 99 | — |

#### Heart ultrasound through the chest wall (TTE) · `echo_tte`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Echocardiography, transthoracic, real-time with image documentation (2D), includes M-mode recording, when performed, complete, with spectral Doppler echocardiography, and with color flow Doppler echocardiography | CPT4 93306 | 2313869 | 38,155 | — |
| — | Echocardiography, transthoracic, real-time with image documentation (2D), includes M-mode recording, when performed, follow-up or limited study | CPT4 93308 | 2313871 | 1,414 | — |
| — | Transthoracic echocardiography with contrast, or without contrast followed by with contrast, real-time with image documentation (2d), includes m-mode recording, when performed, complete, with spectral doppler echocardiography, and with color flow doppl... | HCPCS C8929 | 2616271 | 869 | — |
| — | Echocardiography, transthoracic, real-time with image documentation (2D), includes M-mode recording, when performed, complete, without spectral or color Doppler echocardiography | CPT4 93307 | 2313870 | 148 | — |
| — | Transthoracic echocardiography with contrast, or without contrast followed by with contrast, real-time with image documentation (2d), includes m-mode recording, when performed, follow-up or limited study | HCPCS C8924 | 2616266 | 35 | — |
| — | Transthoracic echocardiography with contrast, or without contrast followed by with contrast, real-time with image documentation (2d), includes m-mode recording, when performed, complete, without spectral or color doppler echocardiography | HCPCS C8923 | 2616265 | 19 | — |

#### Heart ultrasound through the food pipe (TEE) · `echo_tee`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Echocardiography, transesophageal, real-time with image documentation (2D) (with or without M-mode recording); including probe placement, image acquisition, interpretation and report | CPT4 93312 | 2313872 | 768 | — |
| — | Echocardiography, transesophageal, real-time with image documentation (2D) (with or without M-mode recording); placement of transesophageal probe only | CPT4 93313 | 2313873 | 45 | — |
| — | Echocardiography, transesophageal, real-time with image documentation (2D) (with or without M-mode recording); image acquisition, interpretation and report only | CPT4 93314 | 2313874 | 39 | — |
| — | Transesophageal echocardiography (tee) with contrast, or without contrast followed by with contrast, real time with image documentation (2d) (with or without m-mode recording); including probe placement, image acquisition, interpretation and report | HCPCS C8925 | 2616267 | 15 | — |

#### Exercise stress test with ECG (treadmill) · `stress_ecg`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Cardiovascular stress test using maximal or submaximal treadmill or bicycle exercise, continuous electrocardiographic monitoring, and/or pharmacological stress; with supervision, interpretation and report | CPT4 93015 | 2313819 | 14,107 | stress_test |
| — | Cardiovascular stress test using maximal or submaximal treadmill or bicycle exercise, continuous electrocardiographic monitoring, and/or pharmacological stress; interpretation and report only | CPT4 93018 | 2313822 | 13,432 | stress_test |
| — | Cardiovascular stress test using maximal or submaximal treadmill or bicycle exercise, continuous electrocardiographic monitoring, and/or pharmacological stress; tracing only, without interpretation and report | CPT4 93017 | 2313821 | 11,720 | stress_test |
| — | Cardiovascular stress test using maximal or submaximal treadmill or bicycle exercise, continuous electrocardiographic monitoring, and/or pharmacological stress; supervision only, without interpretation and report | CPT4 93016 | 2313820 | 11,359 | stress_test |

#### Stress echocardiogram · `stress_echo`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Echocardiography, transthoracic, real-time with image documentation (2D), includes M-mode recording, when performed, during rest and cardiovascular stress test using treadmill, bicycle exercise and/or pharmacologically induced stress, with interpretati... | CPT4 93351 | 2313883 | 5,731 | stress_test |
| — | Echocardiography, transthoracic, real-time with image documentation (2D), includes M-mode recording, when performed, during rest and cardiovascular stress test using treadmill, bicycle exercise and/or pharmacologically induced stress, with interpretati... | CPT4 93350 | 2313882 | 2,218 | stress_test |
| — | Use of echocardiographic contrast agent during stress echocardiography (List separately in addition to code for primary procedure) | CPT4 93352 | 2313884 | 651 | — |
| — | Transthoracic echocardiography, with contrast, or without contrast followed by with contrast, real-time with image documentation (2d), includes m-mode recording, when performed, during rest and cardiovascular stress test using treadmill, bicycle exerci... | HCPCS C8930 | 2616272 | 302 | stress_test |
| — | Transthoracic echocardiography with contrast, or without contrast followed by with contrast, real-time with image documentation (2d), includes m-mode recording, when performed, during rest and cardiovascular stress test using treadmill, bicycle exercis... | HCPCS C8928 | 2616270 | 210 | stress_test |
| — | Myocardial contrast perfusion echocardiography, at rest or with stress, for assessment of myocardial ischemia or viability (List separately in addition to code for primary procedure) | CPT4 0439T | 42628042 | 3 | — |

#### Nuclear stress scan (SPECT) · `stress_spect`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Myocardial perfusion imaging, tomographic (SPECT) (including attenuation correction, qualitative or quantitative wall motion, ejection fraction by first pass or gated technique, additional quantification, when performed); multiple studies, at rest and/... | CPT4 78452 | 40756833 | 13,361 | stress_test |
| — | Myocardial perfusion imaging, tomographic (SPECT) (including attenuation correction, qualitative or quantitative wall motion, ejection fraction by first pass or gated technique, additional quantification, when performed); single study, at rest or stres... | CPT4 78451 | 40756922 | 340 | stress_test |
| — | Myocardial perfusion imaging, planar (including qualitative or quantitative wall motion, ejection fraction by first pass or gated technique, additional quantification, when performed); multiple studies, at rest and/or stress (exercise or pharmacologic)... | CPT4 78454 | 40757098 | 58 | stress_test |
| — | Myocardial perfusion imaging, planar (including qualitative or quantitative wall motion, ejection fraction by first pass or gated technique, additional quantification, when performed); single study, at rest or stress (exercise or pharmacologic) | CPT4 78453 | 40757133 | 20 | stress_test |

#### PET heart scan · `stress_pet`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Myocardial imaging, positron emission tomography (PET), perfusion study (including ventricular wall motion[s] and/or ejection fraction[s], when performed); multiple studies at rest and stress (exercise or pharmacologic), with concurrently acquired comp... | CPT4 78431 | 709987 | 535 | stress_test |
| — | Absolute quantitation of myocardial blood flow (AQMBF), positron emission tomography (PET), rest and pharmacologic stress (List separately in addition to code for primary procedure) | CPT4 78434 | 709990 | 407 | stress_test |
| — | Myocardial imaging, positron emission tomography (PET), perfusion study (including ventricular wall motion[s] and/or ejection fraction[s], when performed); multiple studies at rest and stress (exercise or pharmacologic) | CPT4 78492 | 2211998 | 381 | stress_test |
| — | Myocardial imaging, positron emission tomography (PET), combined perfusion with metabolic evaluation study (including ventricular wall motion[s] and/or ejection fraction[s], when performed), dual radiotracer (eg, myocardial viability); with concurrentl... | CPT4 78433 | 709989 | 9 | stress_test |
| — | PET myocardial metabolism study | SNOMED 16545811000119100 | 37109083 | 9 | — |
| — | Myocardial imaging, positron emission tomography (PET), metabolic evaluation study (including ventricular wall motion[s] and/or ejection fraction[s], when performed), single study; with concurrently acquired computed tomography transmission scan | CPT4 78429 | 709985 | 7 | stress_test |
| — | Myocardial imaging, positron emission tomography (PET), perfusion study (including ventricular wall motion[s] and/or ejection fraction[s], when performed); single study, at rest or stress (exercise or pharmacologic) | CPT4 78491 | 2211997 | 3 | stress_test |
| — | Myocardial imaging, positron emission tomography (PET), perfusion study (including ventricular wall motion[s] and/or ejection fraction[s], when performed); single study, at rest or stress (exercise or pharmacologic), with concurrently acquired computed... | CPT4 78430 | 709986 | 2 | stress_test |

#### Heart MRI (CMR) · `cmr`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Cardiac magnetic resonance imaging for morphology and function without contrast material(s), followed by contrast material(s) and further sequences | CPT4 75561 | 2211577 | 644 | — |
| — | Cardiac magnetic resonance imaging for morphology and function without contrast material(s), followed by contrast material(s) and further sequences; with stress imaging | CPT4 75563 | 2211579 | 59 | — |

#### Coronary CT angiogram (CCTA) · `ccta`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Computed tomographic angiography, heart, coronary arteries and bypass grafts (when present), with contrast material, including 3D image postprocessing (including evaluation of cardiac structure and morphology, assessment of cardiac function, and evalua... | CPT4 75574 | 40756829 | 5,054 | — |

#### Coronary calcium score (CAC) · `cac_score`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | CT of heart without contrast with calcium scoring | SNOMED 504981000119108 | 42535629 | 1,790 | — |

#### CT-based flow estimate for artery narrowing (FFR-CT) · `ffr_ct`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Noninvasive estimate of coronary fractional flow reserve (FFR) derived from augmentative software analysis of the data set from a coronary computed tomography angiography, with interpretation and report by a physician or other qualified health care pro... | CPT4 75580 | 724752 | 238 | — |
| — | Noninvasive estimated coronary fractional flow reserve (FFR) derived from coronary computed tomography angiography data using computation fluid dynamics physiologic simulation software analysis of functional data to assess the severity of ... (Deprecated) | CPT4 0504T | 725130 | 47 | — |
| — | Noninvasive estimated coronary fractional flow reserve (FFR) derived from coronary computed tomography angiography data using computation fluid dynamics physiologic simulation software analysis of functional data to assess the severity of ... (Deprecated) | CPT4 0503T | 725129 | 41 | — |
| — | Noninvasive estimated coronary fractional flow reserve (FFR) derived from coronary computed tomography angiography data using computation fluid dynamics physiologic simulation software analysis of functional data to assess the severity of ... (Deprecated) | CPT4 0502T | 725128 | 35 | — |
| — | Noninvasive estimated coronary fractional flow reserve (FFR) derived from coronary computed tomography angiography data using computation fluid dynamics physiologic simulation software analysis of functional data to assess the severity of ... (Deprecated) | CPT4 0501T | 725127 | 10 | — |

#### Invasive coronary angiogram (catheterisation) (ICA) · `coronary_angio`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation; with left heart catheterization including intraprocedural injection(s) for left... | CPT4 93458 | 40756950 | 3,980 | — |
| — | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation | CPT4 93454 | 40756852 | 562 | — |
| — | Intravascular Doppler velocity and/or pressure derived coronary flow reserve measurement (coronary vessel or graft) during coronary angiography including pharmacologically induced stress, when performed; initial vessel (List separately in addition to c... | CPT4 93571 | 2313913 | 369 | — |
| — | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation; with right and left heart catheterization including intraprocedural injection(s)... | CPT4 93460 | 40756944 | 214 | — |
| — | Injection procedure during cardiac catheterization including imaging supervision, interpretation, and report; for supravalvular aortography (List separately in addition to code for primary procedure) | CPT4 93567 | 40756942 | 98 | — |
| — | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation; with left heart catheterization including intraprocedural injection(s) for left... | CPT4 93459 | 40756979 | 68 | — |
| — | Intravascular Doppler velocity and/or pressure derived coronary flow reserve measurement (coronary vessel or graft) during coronary angiography including pharmacologically induced stress, when performed; each additional vessel (List separately in addit... | CPT4 93572 | 2313914 | 59 | — |
| — | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation; with right heart catheterization | CPT4 93456 | 40756899 | 33 | — |
| — | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation; with catheter placement(s) in bypass graft(s) (internal mammary, free arterial,... | CPT4 93455 | 40756911 | 20 | — |
| — | Iliac and/or femoral artery angiography, non-selective, bilateral or ipsilateral to catheter insertion, performed at the same time as cardiac catheterization and/or coronary angiography, includes positioning or placement of the catheter in the distal a... | HCPCS G0278 | 2617361 | 10 | — |
| — | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation; with right and left heart catheterization including intraprocedural injection(s)... | CPT4 93461 | 40756857 | 9 | — |
| — | Injection procedure during cardiac catheterization including imaging supervision, interpretation, and report; for selective right ventricular or right atrial angiography (List separately in addition to code for primary procedure) | CPT4 93566 | 40756983 | 8 | — |
| — | Injection procedure during cardiac catheterization including imaging supervision, interpretation, and report; for selective coronary angiography during congenital heart catheterization (List separately in addition to code for primary procedure) | CPT4 93563 | 40756840 | 3 | — |
| — | Injection procedure during cardiac catheterization including imaging supervision, interpretation, and report; for nonselective pulmonary arterial angiography (List separately in addition to code for primary procedure) | CPT4 93568 | 40756943 | 3 | — |
| — | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation; with catheter placement(s) in bypass graft(s) (internal mammary, free arterial,... | CPT4 93457 | 40757138 | 2 | — |
| — | Catheter placement in coronary artery(ies) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation, with left heart catheterization including intraprocedural injection(s) for lef... | HCPCS C7523 | 1126196 | 1 | — |
| — | Catheter placement in coronary artery(ies) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation, with left heart catheterization including intraprocedural injection(s) for lef... | HCPCS C7524 | 1126197 | 1 | — |
| — | Injection procedure during cardiac catheterization including imaging supervision, interpretation, and report; for selective pulmonary arterial angiography, bilateral (List separately in addition to code for primary procedure) | CPT4 93573 | 1552298 | 1 | — |

#### D-dimer blood test · `d_dimer`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | D-dimer assay, quantitative | SNOMED 103826007 | 4015482 | 24,714 | — |
| — | Fibrin degradation products, D-dimer; qualitative or semiquantitative | CPT4 85378 | 2212698 | 1,481 | — |
| — | Fibrin degradation products, D-dimer; ultrasensitive (eg, for evaluation for venous thromboembolism), qualitative or semiquantitative | CPT4 85380 | 2212700 | 847 | — |

#### Lung ventilation-perfusion scan (V/Q) · `vq_scan`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Pulmonary ventilation (eg, aerosol or gas) and perfusion imaging | CPT4 78582 | 42742555 | 243 | — |
| — | NM Lung Perfusion | LOINC 39697-8 | 3041029 | 176 | — |
| — | Pulmonary ventilation perfusion study | SNOMED 37859006 | 4242700 | 3 | — |

### B. Heart and blood-vessel diagnoses

#### Heart attack or unstable angina diagnosis (ACS) · `acs_mi`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Acute non-ST segment elevation myocardial infarction | SNOMED 401314000 | 4270024 | 1,580 | cad |
| — | Unstable angina co-occurrent and due to coronary arteriosclerosis | SNOMED 15960061000119102 | 36712982 | 892 | cad |
| — | Acute ischemic heart disease | SNOMED 413439005 | 319844 | 773 | cad |
| — | Acute ST segment elevation myocardial infarction | SNOMED 401303003 | 4296653 | 544 | cad |
| — | Acute myocardial infarction | SNOMED 57054005 | 312327 | 258 | cad |
| — | Myocardial infarction due to demand ischemia | SNOMED 16837681000119104 | 37309626 | 254 | cad |
| — | Acute ST segment elevation myocardial infarction involving left anterior descending coronary artery | SNOMED 285981000119103 | 43020460 | 107 | cad |
| — | Acute ST segment elevation myocardial infarction due to right coronary artery occlusion | SNOMED 15713121000119105 | 46270163 | 91 | cad |
| — | Myocardial infarction | SNOMED 22298006 | 4329847 | 28 | cad |
| — | Subsequent non-ST segment elevation myocardial infarction | SNOMED 703360004 | 45766241 | 20 | cad |
| — | Acute ST segment elevation myocardial infarction due to left coronary artery occlusion | SNOMED 15713081000119108 | 46270162 | 15 | cad |
| — | Subsequent myocardial infarction of anterior wall | SNOMED 194857001 | 4108677 | 6 | cad |
| — | Subsequent ST segment elevation myocardial infarction | SNOMED 703211006 | 45766114 | 5 | cad |
| — | Subsequent myocardial infarction of inferior wall | SNOMED 194858006 | 4108218 | 4 | cad |
| — | Acute anterior ST segment elevation myocardial infarction | SNOMED 703164000 | 45766075 | 3 | cad |
| — | Acute ST segment elevation myocardial infarction of inferior wall | SNOMED 703213009 | 45766116 | 2 | cad |

#### Old heart attack diagnosis (MI) · `old_mi`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Old myocardial infarction | SNOMED 1755008 | 314666 | 1,823 | cad |

#### Angina diagnosis (stable or other) · `angina_stable`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Angina pectoris | SNOMED 194828000 | 321318 | 3,931 | — |
| — | Angina co-occurrent and due to coronary arteriosclerosis | SNOMED 15960141000119102 | 36712983 | 1,998 | cad |
| — | Refractory angina | SNOMED 315025001 | 4201629 | 38 | — |
| — | Post infarct angina | SNOMED 314116003 | 4198141 | 5 | — |

#### Coronary artery disease diagnosis (chronic) (CAD) · `cad_chronic`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Atherosclerosis of coronary artery without angina pectoris | SNOMED 451041000124103 | 764123 | 9,566 | — |
| — | Coronary atherosclerosis | SNOMED 443502000 | 40481919 | 1,246 | — |
| — | Chronic ischemic heart disease | SNOMED 413838009 | 315286 | 512 | cad |
| — | Coronary arteriosclerosis in artery of transplanted heart | SNOMED 792842004 | 37312532 | 10 | cad |

#### Angina with open arteries (small-vessel disease or spasm) (INOCA) · `inoca_cmd`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Coronary artery spasm | SNOMED 23687008 | 4127089 | 249 | — |
| — | Coronary microvascular dysfunction | SNOMED 697976003 | 44783791 | 36 | — |

#### Aortic dissection or aortic aneurysm diagnosis · `aortic_syndrome`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Thoracic aortic aneurysm without rupture | SNOMED 74883004 | 441051 | 713 | — |
| — | Dissection of aorta | SNOMED 308546005 | 320739 | 50 | — |
| — | Thoracic aortic aneurysm which has ruptured | SNOMED 195258006 | 441875 | 11 | — |

#### Blood clot in the lung diagnosis (PE) · `pe`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Pulmonary embolism | SNOMED 59282003 | 440417 | 1,731 | — |
| — | Chronic pulmonary embolism | SNOMED 133971000119108 | 44782732 | 179 | — |
| — | Septic pulmonary embolism | SNOMED 441557008 | 40479606 | 49 | — |

#### Inflammation of the heart sac or heart muscle diagnosis · `pericarditis_myocarditis`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Pericardial effusion - noninflammatory | SNOMED 194970009 | 4108814 | 513 | — |
| — | Acute pericarditis | SNOMED 15555002 | 320116 | 349 | — |
| — | Acute idiopathic pericarditis | SNOMED 266235007 | 315293 | 157 | — |
| — | Myocarditis | SNOMED 50920009 | 314383 | 124 | — |
| — | Acute myocarditis | SNOMED 46701001 | 312653 | 56 | — |
| — | Infectious pericarditis | SNOMED 41739008 | 4217075 | 56 | — |
| — | Myocarditis due to infectious agent | SNOMED 22653005 | 4331309 | 36 | — |
| — | Viral pericarditis | SNOMED 70189005 | 4289908 | 29 | — |
| — | Cardiac tamponade | SNOMED 35304003 | 318450 | 25 | — |
| — | Isolated (Fiedler's) myocarditis | SNOMED 266238009 | 4143969 | 23 | — |
| — | Pericarditis | SNOMED 3238004 | 4138837 | 21 | — |
| — | Post-infarction pericarditis | SNOMED 233885007 | 4121477 | 16 | — |
| — | Viral myocarditis | SNOMED 89141000 | 4231274 | 16 | — |
| — | Chronic constrictive pericarditis | SNOMED 52535005 | 4203625 | 13 | — |
| — | Chronic adhesive pericarditis | SNOMED 42999000 | 4181182 | 12 | — |
| — | Myocarditis caused by influenza virus | SNOMED 78046005 | 4299935 | 4 | — |

#### Heart valve disease diagnosis · `valvular_hd`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Mitral valve prolapse | SNOMED 409712001 | 4252872 | 1,105 | — |
| — | Aortic valve stenosis | SNOMED 60573004 | 4189343 | 361 | — |
| — | Aortic valve stenosis with insufficiency | SNOMED 194987006 | 4111099 | 55 | — |
| — | Rheumatic mitral regurgitation | SNOMED 31085000 | 318776 | 47 | — |
| — | Non-rheumatic mitral valve stenosis | SNOMED 194727002 | 4110937 | 25 | — |
| — | Rheumatic aortic regurgitation | SNOMED 78031003 | 439834 | 9 | — |
| — | Rheumatic aortic stenosis | SNOMED 72011007 | 313221 | 6 | — |
| — | Rheumatic aortic stenosis with regurgitation | SNOMED 17759006 | 320429 | 3 | — |
| — | Supravalvar aortic stenosis | SNOMED 268185002 | 4147787 | 3 | — |

#### Heart muscle disease diagnosis · `cardiomyopathy`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Cardiomyopathy | SNOMED 85898001 | 321319 | 1,263 | — |
| — | Dilated cardiomyopathy | SNOMED 399020009 | 4163710 | 400 | — |
| — | Hypertrophic cardiomyopathy | SNOMED 233873004 | 4124693 | 206 | — |
| — | Postpartum cardiomyopathy | SNOMED 62377009 | 312383 | 78 | — |
| — | Cardiomyopathy associated with another disorder | SNOMED 195029002 | 320746 | 76 | — |
| — | Takotsubo cardiomyopathy | SNOMED 441541008 | 40479589 | 76 | — |
| — | Hypertrophic obstructive cardiomyopathy | SNOMED 45227007 | 316428 | 66 | — |
| — | Alcoholic cardiomyopathy | SNOMED 1234750000 | 37164777 | 24 | — |
| — | Cardiomyopathy due to viral infection | SNOMED 204981000119101 | 45757557 | 23 | — |
| — | Cardiomyopathy caused by drug | SNOMED 16228931000119102 | 35615148 | 20 | — |
| — | Restrictive cardiomyopathy | SNOMED 415295002 | 4190773 | 17 | — |
| — | Primary eosinophilic endomyocardial restrictive cardiomyopathy | SNOMED 33258008 | 4141588 | 1 | — |

#### Heart failure diagnosis · `heart_failure`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Hypertensive heart disease without congestive heart failure | SNOMED 60899001 | 319034 | 3,072 | — |
| — | Congestive heart failure | SNOMED 42343007 | 319835 | 1,827 | — |
| — | Heart failure | SNOMED 84114007 | 316139 | 1,631 | — |
| — | Hypertensive heart failure | SNOMED 46113002 | 444101 | 1,555 | — |
| — | Chronic congestive heart failure | SNOMED 88805009 | 4229440 | 649 | — |
| — | Hypertensive heart and renal disease with (congestive) heart failure | SNOMED 194779001 | 439696 | 307 | — |
| — | Left heart failure | SNOMED 85232009 | 439846 | 114 | — |
| — | Hypertensive heart and renal disease with both (congestive) heart failure and renal failure | SNOMED 194781004 | 439694 | 65 | — |
| — | Biventricular congestive heart failure | SNOMED 92506005 | 4242669 | 22 | — |
| — | Chronic right-sided heart failure | SNOMED 10335000 | 4014159 | 13 | — |
| — | Acute right-sided heart failure | SNOMED 359617009 | 4233424 | 13 | — |
| — | Acute on chronic right-sided congestive heart failure | SNOMED 16838951000119100 | 37309625 | 8 | — |
| — | High output heart failure | SNOMED 10091002 | 4004279 | 4 | — |
| — | Right heart failure secondary to left heart failure | SNOMED 44313006 | 4195785 | 4 | — |
| — | Low output heart failure due to and following Fontan operation | SNOMED 871617000 | 3656094 | 1 | — |

#### Abnormal heart rhythm diagnosis (AF) · `arrhythmia`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Supraventricular tachycardia | SNOMED 6456007 | 4275423 | 2,920 | — |
| — | Atrial fibrillation | SNOMED 49436004 | 313217 | 2,831 | — |
| — | Paroxysmal atrial fibrillation | SNOMED 282825002 | 4154290 | 2,476 | — |
| — | Ventricular tachycardia | SNOMED 25569003 | 4103295 | 846 | — |
| — | Atrial flutter | SNOMED 5370000 | 314665 | 614 | — |
| — | Persistent atrial fibrillation | SNOMED 440059007 | 4232697 | 406 | — |
| — | Chronic atrial fibrillation | SNOMED 426749004 | 4141360 | 334 | — |
| — | Typical atrial flutter | SNOMED 720448006 | 36714994 | 281 | — |
| — | Longstanding persistent atrial fibrillation | SNOMED 706923002 | 45768480 | 117 | — |
| — | Atypical atrial flutter | SNOMED 15964901000119107 | 36712986 | 92 | — |
| — | Ventricular fibrillation | SNOMED 71908006 | 437894 | 73 | — |
| — | Permanent atrial fibrillation | SNOMED 440028005 | 4232691 | 66 | — |

### B. Other diagnoses that can explain chest pain

#### Pneumonia or fluid around the lung diagnosis · `pneumonia_pleural`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Pneumonia | SNOMED 233604007 | 255848 | 7,161 | — |
| — | Pleurisy | SNOMED 196075003 | 78786 | 1,719 | — |
| — | Pneumonia caused by SARS-CoV-2 | SNOMED 882784691000119100 | 3661408 | 1,635 | — |
| — | Pleural effusion | SNOMED 60046008 | 254061 | 1,156 | — |
| — | Viral pneumonia | SNOMED 75570004 | 261326 | 876 | — |
| — | Lobar pneumonia | SNOMED 278516003 | 4133224 | 749 | — |
| — | Bacterial pneumonia | SNOMED 53084003 | 257315 | 550 | — |
| — | Bronchopneumonia | SNOMED 396285007 | 256722 | 286 | — |
| — | Pneumonia and influenza | SNOMED 195878008 | 256723 | 237 | — |
| — | Pneumonia caused by Severe acute respiratory syndrome coronavirus | SNOMED 441590008 | 40479642 | 156 | — |
| — | Empyema of pleura | SNOMED 58554001 | 4238808 | 80 | — |
| — | Pneumonia caused by Influenza A virus | SNOMED 772839003 | 36676238 | 48 | — |
| — | Pneumonia caused by Gram negative bacteria | SNOMED 430395005 | 258180 | 42 | — |
| — | Pneumococcal pneumonia | SNOMED 233607000 | 258785 | 41 | — |
| — | Abscess of lung with pneumonia | SNOMED 196112005 | 4025165 | 34 | — |
| — | Pneumonia caused by methicillin resistant Staphylococcus aureus | SNOMED 124691000119101 | 46270027 | 29 | — |
| — | Parainfluenza virus pneumonia | SNOMED 64917006 | 439857 | 27 | — |
| — | Pneumonia caused by respiratory syncytial virus | SNOMED 195881003 | 436145 | 24 | — |
| — | Pneumonia caused by Human metapneumovirus | SNOMED 445096001 | 40482061 | 23 | — |
| — | Pneumonia caused by methicillin susceptible Staphylococcus aureus | SNOMED 128711000119106 | 46274035 | 22 | — |
| — | Ventilator associated pneumonia | SNOMED 429271009 | 259992 | 21 | — |
| — | Pneumonia caused by Streptococcus | SNOMED 34020007 | 261324 | 19 | — |
| — | Empyema with fistula | SNOMED 271503005 | 261883 | 16 | — |
| — | Haemophilus influenzae pneumonia | SNOMED 70036007 | 260754 | 13 | — |
| — | Staphylococcal pneumonia | SNOMED 22754005 | 259852 | 9 | — |
| — | Pneumonia caused by Histoplasma capsulatum | SNOMED 38699009 | 4299862 | 9 | — |
| — | Pneumonia caused by Pseudomonas | SNOMED 41381004 | 252351 | 8 | — |
| — | Pneumonia caused by Chlamydiaceae | SNOMED 233609002 | 254066 | 7 | — |
| — | Adenoviral pneumonia | SNOMED 41207000 | 254677 | 6 | — |
| — | Group B streptococcal pneumonia | SNOMED 195886008 | 252655 | 5 | — |
| — | Pneumonia caused by Escherichia coli | SNOMED 51530003 | 260430 | 5 | — |
| — | Hypostatic pneumonia | SNOMED 85469005 | 4310964 | 5 | — |
| — | Cryptogenic organizing pneumonia | SNOMED 719218000 | 36714118 | 5 | — |
| — | Pneumonia in typhoid fever | SNOMED 45312009 | 4166072 | 2 | — |

#### Collapsed lung or blood in the chest cavity diagnosis · `pneumothorax`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Pneumothorax | SNOMED 36118008 | 253796 | 285 | — |
| — | Traumatic pneumothorax | SNOMED 90070003 | 4234083 | 182 | — |
| — | Hemothorax | SNOMED 31892009 | 4135466 | 77 | — |
| — | Primary spontaneous pneumothorax | SNOMED 328561000119107 | 762337 | 58 | — |
| — | Traumatic pneumohemothorax | SNOMED 42434002 | 4174885 | 52 | — |
| — | Traumatic hemothorax | SNOMED 42458003 | 4175167 | 47 | — |
| — | Pneumothorax due to and following procedure | SNOMED 871586006 | 3656064 | 36 | — |
| — | Spontaneous tension pneumothorax | SNOMED 196102003 | 258787 | 17 | — |
| — | Secondary spontaneous pneumothorax | SNOMED 328571000119101 | 762338 | 11 | — |
| — | Chronic pneumothorax | SNOMED 599006 | 4243667 | 7 | — |

#### Acid reflux or heartburn diagnosis (GERD) · `gerd`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Gastroesophageal reflux disease without esophagitis | SNOMED 266435005 | 4144111 | 43,120 | — |
| — | Gastro-esophageal reflux disease with esophagitis | SNOMED 266433003 | 30437 | 9,684 | — |
| — | Heartburn | SNOMED 16331000 | 23325 | 6,298 | — |
| — | Gastroesophageal reflux disease | SNOMED 235595009 | 318800 | 2 | — |

#### Stomach or food-pipe irritation, ulcer or hernia diagnosis · `peptic_ulcer_gastritis`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Gastritis | SNOMED 4556007 | 201340 | 10,078 | — |
| — | Chronic gastritis | SNOMED 8493009 | 4225273 | 5,539 | — |
| — | Esophagitis | SNOMED 16761005 | 30753 | 3,777 | — |
| — | Acute gastritis | SNOMED 25458004 | 199866 | 2,834 | — |
| — | Nonulcer dyspepsia | SNOMED 3696007 | 4289526 | 2,729 | — |
| — | Gastric ulcer without hemorrhage AND without perforation | SNOMED 73481001 | 4248429 | 1,547 | — |
| — | Eosinophilic esophagitis | SNOMED 235599003 | 27918 | 1,059 | — |
| — | Peptic ulcer | SNOMED 13200003 | 4027663 | 724 | — |
| — | Chronic superficial gastritis | SNOMED 196735001 | 4057513 | 716 | — |
| — | Acute gastric ulcer without hemorrhage AND without perforation | SNOMED 67964002 | 4195231 | 226 | — |
| — | Atrophic gastritis | SNOMED 84568007 | 192667 | 221 | — |
| — | Alcoholic gastritis | SNOMED 2043009 | 195300 | 141 | — |
| — | Chronic gastric ulcer with hemorrhage | SNOMED 57246001 | 4211001 | 121 | — |
| — | Chronic gastric ulcer without hemorrhage AND without perforation | SNOMED 76796008 | 4296611 | 120 | — |
| — | Acute hemorrhagic gastritis | SNOMED 2367005 | 193249 | 95 | — |
| — | Congenital hiatus hernia | SNOMED 47028006 | 198246 | 57 | — |
| — | Chronic duodenal ulcer with hemorrhage | SNOMED 89469000 | 4232181 | 50 | — |
| — | Acute duodenal ulcer without hemorrhage AND without perforation | SNOMED 32490005 | 4138962 | 48 | — |
| — | Acute peptic ulcer without hemorrhage AND without perforation | SNOMED 45485004 | 4163865 | 40 | — |
| — | Acute gastric ulcer with hemorrhage | SNOMED 89748001 | 4231580 | 39 | — |
| — | Chronic gastric ulcer with perforation | SNOMED 31301004 | 4150681 | 27 | — |
| — | Acute gastric ulcer with perforation | SNOMED 19850005 | 4057953 | 24 | — |
| — | Chronic peptic ulcer with hemorrhage | SNOMED 49232000 | 4174044 | 21 | — |
| — | Acute peptic ulcer with hemorrhage | SNOMED 12274003 | 4046500 | 18 | — |
| — | Chronic peptic ulcer without hemorrhage AND without perforation | SNOMED 5492000 | 4204555 | 18 | — |
| — | Acute duodenal ulcer with hemorrhage | SNOMED 12847006 | 4027729 | 17 | — |
| — | Chronic duodenal ulcer without hemorrhage AND without perforation | SNOMED 40214005 | 4222896 | 15 | — |
| — | Gastric hemorrhage due to alcoholic gastritis | SNOMED 40241000119109 | 45757783 | 15 | — |
| — | Gastric hemorrhage due to chronic superficial gastritis | SNOMED 1085121000119107 | 46269837 | 15 | — |
| — | Chronic duodenal ulcer with perforation | SNOMED 49916007 | 4173408 | 10 | — |
| — | Chronic peptic ulcer with perforation | SNOMED 3483000 | 4146517 | 9 | — |
| — | Acute duodenal ulcer with perforation | SNOMED 61347001 | 4265479 | 7 | — |
| — | Gastric hemorrhage due to atrophic gastritis | SNOMED 150721000119102 | 46270145 | 5 | — |
| — | Acute peptic ulcer with perforation | SNOMED 79118000 | 4194543 | 4 | — |
| — | Chronic duodenal ulcer with hemorrhage AND perforation | SNOMED 36975000 | 4289830 | 4 | — |
| — | Acute gastric ulcer with hemorrhage and perforation | SNOMED 48974009 | 4169592 | 3 | — |
| — | Chronic gastric ulcer with hemorrhage and with perforation | SNOMED 76181002 | 4294973 | 3 | — |
| — | Acute duodenal ulcer with hemorrhage AND perforation | SNOMED 86895006 | 4336230 | 1 | — |

#### Gallbladder or pancreas diagnosis · `biliary_pancreatic`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Gallstone | SNOMED 235919008 | 196456 | 3,814 | — |
| — | Calculus of gallbladder with cholecystitis | SNOMED 25924004 | 443785 | 1,596 | — |
| — | Acute pancreatitis | SNOMED 197456007 | 199074 | 1,206 | — |
| — | Acute cholecystitis | SNOMED 65275009 | 198809 | 1,031 | — |
| — | Cholecystitis | SNOMED 76581006 | 192956 | 800 | — |
| — | Chronic cholecystitis | SNOMED 20824003 | 200765 | 783 | — |
| — | Gallbladder calculus with acute cholecystitis and no obstruction | SNOMED 197377009 | 196726 | 743 | — |
| — | Calculus of gallbladder with acute and chronic cholecystitis | SNOMED 699050007 | 44783016 | 408 | — |
| — | Cholelithiasis without obstruction | SNOMED 70342003 | 444367 | 400 | — |
| — | Chronic pancreatitis | SNOMED 235494005 | 195596 | 340 | — |
| — | Gallstone acute pancreatitis | SNOMED 235941008 | 4341763 | 238 | — |
| — | Calculus of bile duct with cholecystitis | SNOMED 36483003 | 201614 | 235 | — |
| — | Alcohol-induced acute pancreatitis | SNOMED 235942001 | 4340493 | 207 | — |
| — | Idiopathic acute pancreatitis | SNOMED 235943006 | 4340960 | 197 | — |
| — | Acute and chronic cholecystitis | SNOMED 396335001 | 4288676 | 145 | — |
| — | Cholelithiasis AND cholecystitis with obstruction | SNOMED 50450007 | 195587 | 84 | — |
| — | Gallbladder calculus with acute cholecystitis and obstruction | SNOMED 197378004 | 201352 | 78 | — |
| — | Cholelithiasis with obstruction | SNOMED 77528005 | 4300203 | 77 | — |
| — | Alcohol-induced chronic pancreatitis | SNOMED 235952002 | 4340964 | 74 | — |
| — | Bile duct calculus with acute cholecystitis | SNOMED 197389006 | 4026144 | 71 | — |
| — | Calculus of gallbladder without cholecystitis or cholangitis | SNOMED 722869007 | 36716712 | 56 | — |
| — | Drug-induced acute pancreatitis | SNOMED 235944000 | 4340961 | 38 | — |
| — | Calculus of bile duct with chronic cholecystitis | SNOMED 91316003 | 444420 | 33 | — |
| — | Bile duct calculus with acute cholecystitis and obstruction | SNOMED 197391003 | 197924 | 32 | — |
| — | Gallstone ileus | SNOMED 37976006 | 198475 | 20 | — |
| — | Calculus of gallbladder with acute cholecystitis | SNOMED 59771005 | 194991 | 15 | — |
| — | Calculus of bile duct with chronic cholecystitis with obstruction | SNOMED 15082003 | 443889 | 5 | — |
| — | Calculus of gallbladder and bile duct with cholecystitis | SNOMED 435121000124109 | 763023 | 4 | — |
| — | Cytomegaloviral pancreatitis | SNOMED 235947007 | 4340962 | 3 | — |
| — | Biliary acute pancreatitis | SNOMED 811431000000107 | 44806251 | 2 | — |

#### Rib-cartilage inflammation diagnosis (costochondritis) · `costochondritis`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Tietze's disease | SNOMED 30128009 | 134461 | 4,506 | — |

#### Chest wall injury or strain diagnosis · `chest_wall`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Closed fracture of one rib | SNOMED 45356009 | 75941 | 822 | — |
| — | Fracture of one rib | SNOMED 20274005 | 4066613 | 195 | — |
| — | Closed fracture of sternum | SNOMED 66112004 | 436832 | 122 | — |
| — | Fracture of sternum | SNOMED 78516000 | 4302740 | 56 | — |
| — | Open fracture of one rib | SNOMED 44932007 | 80229 | 10 | — |
| — | Closed flail chest | SNOMED 311408004 | 4148331 | 9 | — |
| — | Open fracture of sternum | SNOMED 87225004 | 434499 | 2 | — |
| — | Flail chest | SNOMED 78011002 | 434769 | 1 | — |

#### Shingles diagnosis · `herpes_zoster`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Herpes zoster | SNOMED 4740000 | 443943 | 3,220 | — |
| — | Disseminated herpes zoster | SNOMED 55560002 | 4205455 | 47 | — |

#### Anxiety diagnosis · `anxiety`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Anxiety disorder | SNOMED 197480006 | 442077 | 40,081 | — |
| — | Generalized anxiety disorder | SNOMED 21897009 | 434613 | 23,394 | — |
| — | Adjustment disorder with mixed anxiety and depressed mood | SNOMED 782501005 | 36684319 | 5,359 | — |
| — | Organic anxiety disorder | SNOMED 17496003 | 381537 | 407 | — |
| — | Dream anxiety disorder | SNOMED 111487009 | 4009184 | 250 | — |
| — | Organic anxiety disorder caused by psychoactive substance | SNOMED 50026000 | 4178114 | 39 | — |
| — | Cannabis-induced anxiety disorder | SNOMED 39951001 | 4221077 | 22 | — |
| — | Anxiety disorder caused by alcohol | SNOMED 34938008 | 4146660 | 13 | — |
| — | Anxiety | SNOMED 48694002 | 441542 | 8 | — |
| — | Separation anxiety disorder of childhood | SNOMED 11806006 | 4039212 | 8 | — |
| — | Sedative, hypnotic AND/OR anxiolytic-induced anxiety disorder | SNOMED 1686006 | 4056690 | 7 | — |
| — | Anxiety disorder caused by cocaine | SNOMED 51493001 | 4198826 | 1 | — |

#### Panic disorder diagnosis · `panic_attack`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Panic disorder | SNOMED 371631005 | 436074 | 6,473 | — |

#### Depression or somatic-symptom disorder diagnosis · `depression_somatic`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Depressive disorder | SNOMED 35489007 | 440383 | 11,435 | — |
| — | Major depressive disorder | SNOMED 370143000 | 4152280 | 10,173 | — |
| — | Moderate recurrent major depression | SNOMED 18818009 | 4077577 | 8,115 | — |
| — | Mild recurrent major depression | SNOMED 40379007 | 4228802 | 3,745 | — |
| — | Severe recurrent major depression without psychotic features | SNOMED 36474008 | 435220 | 3,155 | — |
| — | Moderate major depression, single episode | SNOMED 15639000 | 4049623 | 3,126 | — |
| — | Recurrent major depression | SNOMED 66344007 | 4282316 | 2,763 | — |
| — | Mild major depression, single episode | SNOMED 79298009 | 4195572 | 2,112 | — |
| — | Recurrent major depression in partial remission | SNOMED 33135002 | 4141454 | 1,149 | — |
| — | Severe major depression, single episode, without psychotic features | SNOMED 76441001 | 441534 | 1,148 | — |
| — | Recurrent major depression in full remission | SNOMED 46244001 | 4263748 | 875 | — |
| — | Single episode of major depression in full remission | SNOMED 19527009 | 4025677 | 804 | — |
| — | Major depression single episode, in partial remission | SNOMED 70747007 | 4323418 | 460 | — |
| — | Recurrent major depression in remission | SNOMED 68019004 | 433991 | 331 | — |
| — | Recurrent depression | SNOMED 191616006 | 4098302 | 324 | — |
| — | Recurrent major depressive episodes, severe, with psychosis | SNOMED 191613003 | 434911 | 313 | — |
| — | Severe major depression, single episode, with psychotic features | SNOMED 430852001 | 438406 | 126 | — |
| — | Hypochondriasis | SNOMED 18193002 | 434920 | 107 | — |
| — | Somatization disorder | SNOMED 397923000 | 441545 | 56 | — |
| — | Mild major depression | SNOMED 87512008 | 4336957 | 14 | — |
| — | Moderate major depression | SNOMED 832007 | 4307111 | 8 | — |
| — | Major depression in remission | SNOMED 42810003 | 4176002 | 2 | — |
| — | Major depression, single episode | SNOMED 36923009 | 4282096 | 2 | — |
| — | Severe major depression without psychotic features | SNOMED 75084000 | 4327337 | 2 | — |
| — | Recurrent major depressive episodes, moderate | SNOMED 191611001 | 432883 | 1 | — |

#### Hyperventilation diagnosis · `hyperventilation`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Hyperventilation | SNOMED 68978004 | 316814 | 267 | — |

#### Sickle cell disease diagnosis · `sickle_cell`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Sickle cell-hemoglobin C disease with crisis | SNOMED 417517009 | 443721 | 33 | — |
| — | Sickle cell-hemoglobin C disease without crisis | SNOMED 417683006 | 443726 | 27 | — |
| — | Sickle cell-hemoglobin SS disease | SNOMED 127040003 | 22281 | 20 | — |
| — | Sickle cell-thalassemia disease with crisis | SNOMED 416826005 | 443738 | 18 | — |
| — | Sickle cell-thalassemia disease without crisis | SNOMED 417048006 | 321263 | 14 | — |
| — | Acute sickle cell splenic sequestration crisis | SNOMED 444108000 | 40485018 | 3 | — |
| — | Sickle cell-hemoglobin C disease | SNOMED 35434009 | 24006 | 1 | — |
| — | Sickle cell beta plus thalassemia | SNOMED 127042006 | 4130678 | 1 | — |

#### Cocaine or methamphetamine use diagnosis · `cocaine_meth`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Harmful pattern of use of cocaine | SNOMED 78267003 | 432303 | 376 | — |
| — | Organic mental disorder caused by cocaine | SNOMED 46975003 | 4264766 | 216 | — |
| — | Cocaine dependence | SNOMED 31956009 | 436389 | 180 | — |
| — | Nondependent harmful pattern of use of cocaine in remission | SNOMED 191920007 | 436098 | 60 | — |
| — | Cocaine dependence in remission | SNOMED 191833002 | 432302 | 58 | — |
| — | Accidental poisoning by cocaine | SNOMED 216583009 | 4314247 | 24 | — |
| — | Cocaine intoxication | SNOMED 27956007 | 4101256 | 6 | — |
| — | Poisoning by cocaine | SNOMED 9982009 | 4322698 | 3 | — |
| — | Cocaine-induced mood disorder | SNOMED 10327003 | 4012869 | 2 | — |
| — | Cocaine withdrawal | SNOMED 80868005 | 4216493 | 1 | — |
| — | Cocaine intoxication delirium | SNOMED 70328006 | 4290062 | 1 | — |

### B. Risk factors and history

#### High blood pressure diagnosis (HTN) · `htn`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Essential hypertension | SNOMED 59621000 | 320128 | 59,378 | — |
| — | Hypertensive heart and chronic kidney disease | SNOMED 8501000119104 | 44784621 | 188 | — |
| — | Benign essential hypertension | SNOMED 1201005 | 312648 | 2 | — |

#### High cholesterol or blood fat diagnosis · `hyperlipidemia`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Hyperlipidemia | SNOMED 55822004 | 432867 | 44,958 | — |
| — | Mixed hyperlipidemia | SNOMED 267434003 | 438720 | 29,452 | — |
| — | Pure hypercholesterolemia | SNOMED 267432004 | 437827 | 18,605 | — |
| — | Familial hypercholesterolemia | SNOMED 398036000 | 4134862 | 878 | — |
| — | Familial hypercholesterolemia - heterozygous | SNOMED 238079002 | 4029259 | 20 | — |
| — | Familial hypercholesterolemia - homozygous | SNOMED 238078005 | 4079885 | 2 | — |

#### Tobacco or nicotine use diagnosis · `tobacco`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Nicotine dependence in remission | SNOMED 836439001 | 3654548 | 17,648 | — |
| — | Nicotine dependence | SNOMED 56294008 | 4209423 | 15,851 | — |
| — | Tobacco dependence in remission | SNOMED 191889006 | 4103418 | 272 | — |
| — | Tobacco dependence syndrome | SNOMED 89765005 | 437264 | 5 | — |

#### Type 2 diabetes diagnosis (T2DM) · `t2dm`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Type 2 diabetes mellitus | SNOMED 44054006 | 201826 | 18,961 | — |
| — | Proliferative retinopathy due to type 2 diabetes mellitus | SNOMED 1501000119109 | 43530685 | 145 | — |
| — | Type 2 diabetes mellitus with ulcer | SNOMED 190389009 | 4099651 | 94 | — |
| — | Hyperosmolar coma due to type 2 diabetes mellitus | SNOMED 190331003 | 201530 | 16 | — |
| — | Type II diabetes mellitus in remission | SNOMED 703138006 | 45766052 | 15 | — |
| — | Pre-existing type 2 diabetes mellitus in pregnancy | SNOMED 609567009 | 43531010 | 2 | — |

#### HbA1c blood test · `hba1c`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Hemoglobin A1c measurement | SNOMED 43396009 | 4184637 | 72,635 | — |

#### Chronic kidney disease or dialysis (CKD) · `ckd_dialysis`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Chronic kidney disease due to hypertension | SNOMED 104931000119100 | 44782429 | 2,233 | — |
| — | Chronic kidney disease stage 2 | SNOMED 431856006 | 443601 | 1,831 | — |
| — | Chronic kidney disease | SNOMED 709044004 | 46271022 | 1,802 | — |
| — | Chronic kidney disease stage 3A | SNOMED 700378005 | 45763854 | 1,446 | — |
| — | Chronic kidney disease stage 3 | SNOMED 433144002 | 443597 | 1,276 | — |
| — | Chronic kidney disease stage 3B | SNOMED 700379002 | 45763855 | 422 | — |
| — | Anemia in chronic kidney disease | SNOMED 707323002 | 45768812 | 378 | — |
| — | Chronic kidney disease stage 1 | SNOMED 431855005 | 443614 | 363 | — |
| — | End-stage renal disease | SNOMED 46177005 | 193782 | 208 | — |
| — | Chronic kidney disease stage 4 | SNOMED 431857002 | 443612 | 207 | — |
| — | Chronic kidney disease stage 5 | SNOMED 433146000 | 443611 | 77 | — |
| — | Hemodialysis procedure with single evaluation by a physician or other qualified health care professional | CPT4 90935 | 2213572 | 77 | — |
| — | Hemodialysis procedure requiring repeated evaluation(s) with or without substantial revision of dialysis prescription | CPT4 90937 | 2213573 | 19 | — |
| — | End-stage renal disease (ESRD) related services monthly, for patients 20 years of age and older; with 4 or more face-to-face visits by a physician or other qualified health care professional per month | CPT4 90960 | 2213587 | 0 | — |
| — | End-stage renal disease (ESRD) related services monthly, for patients 20 years of age and older; with 2-3 face-to-face visits by a physician or other qualified health care professional per month | CPT4 90961 | 2213588 | 0 | — |
| — | End-stage renal disease (ESRD) related services monthly, for patients 20 years of age and older; with 1 face-to-face visit by a physician or other qualified health care professional per month | CPT4 90962 | 2213589 | 0 | — |
| — | End-stage renal disease (ESRD) related services for home dialysis per full month, for patients 20 years of age and older | CPT4 90966 | 2213593 | 0 | — |
| — | End-stage renal disease (ESRD) related services for dialysis less than a full month of service, per day; for patients 20 years of age and older | CPT4 90970 | 2213597 | 0 | — |
| — | Dialysis care | SNOMED 385971003 | 4301680 | 0 | — |

#### Prior heart bypass or stent procedure (CABG / PCI) · `prior_revasc`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Percutaneous transcatheter placement of intracoronary stent(s), with coronary angioplasty when performed, single major coronary artery and/or its branch(es); 1 lesion involving 1 or more coronary segments | CPT4 92928 | 43527998 | 641 | — |
| — | Percutaneous transcatheter placement of drug eluting intracoronary stent(s), with coronary angioplasty when performed; single major coronary artery or branch | HCPCS C9600 | 43533247 | 220 | — |
| — | Percutaneous transluminal revascularization of acute total/subtotal occlusion during acute myocardial infarction, any combination of intracoronary stent, atherectomy and angioplasty, including aspiration thrombectomy when performed, single major corona... | CPT4 92941 | 43528002 | 186 | — |
| — | Coronary artery bypass, using arterial graft(s); single arterial graft | CPT4 33533 | 2107231 | 92 | — |
| — | Percutaneous transluminal coronary angioplasty, single major coronary artery and/or its branch(es) | CPT4 92920 | 43527994 | 68 | — |
| — | Percutaneous transluminal revascularization of chronic total occlusion, single coronary artery, coronary artery branch, or coronary artery bypass graft, and/or subtended major coronary artery branches of the bypass graft, any combination of intracorona... | CPT4 92943 | 43528003 | 46 | — |
| — | Percutaneous transcatheter placement of intracoronary stent(s), with coronary angioplasty when performed; each additional branch of a major coronary artery (List separately in addition to code for primary procedure) (Deprecated) | CPT4 92929 | 43527999 | 43 | — |
| — | Coronary artery bypass, using venous graft(s) and arterial graft(s); 2 venous grafts (List separately in addition to code for primary procedure) | CPT4 33518 | 2107223 | 37 | — |
| — | Coronary artery bypass, using venous graft(s) and arterial graft(s); 3 venous grafts (List separately in addition to code for primary procedure) | CPT4 33519 | 2107224 | 32 | — |
| — | Coronary artery bypass, using arterial graft(s); 2 coronary arterial grafts | CPT4 33534 | 2107242 | 32 | — |
| — | Percutaneous transluminal coronary angioplasty; each additional branch of a major coronary artery (List separately in addition to code for primary procedure) (Deprecated) | CPT4 92921 | 43527995 | 30 | — |
| — | Coronary artery bypass, using venous graft(s) and arterial graft(s); single vein graft (List separately in addition to code for primary procedure) | CPT4 33517 | 2107222 | 26 | — |
| — | Percutaneous transluminal coronary lithotripsy (List separately in addition to code for primary procedure) | CPT4 92972 | 724768 | 22 | — |
| — | Percutaneous transluminal coronary atherectomy, with intracoronary stent, with coronary angioplasty when performed, single major coronary artery and/or its branch(es) | CPT4 92933 | 43527908 | 19 | — |
| — | Percutaneous transluminal coronary mechanical aspiration thrombectomy (List separately in addition to code for primary procedure) | CPT4 92973 | 2313795 | 18 | — |
| — | Percutaneous transcatheter placement of drug-eluting intracoronary stent(s), with coronary angioplasty when performed; each additional branch of a major coronary artery (list separately in addition to code for primary procedure) | HCPCS C9601 | 43533352 | 18 | — |
| — | Percutaneous transluminal revascularization of chronic total occlusion, coronary artery, coronary artery branch, or coronary artery bypass graft, any combination of drug-eluting intracoronary stent, atherectomy and angioplasty; single vessel | HCPCS C9607 | 43533354 | 14 | — |
| — | Percutaneous transluminal revascularization of or through coronary artery bypass graft (internal mammary, free arterial, venous), any combination of intracoronary stent, atherectomy and angioplasty, including distal protection when performed, single ma... | CPT4 92937 | 43528000 | 11 | — |
| — | Reoperation, coronary artery bypass procedure or valve procedure, more than 1 month after original operation (List separately in addition to code for primary procedure) | CPT4 33530 | 2107230 | 7 | — |
| — | Percutaneous transluminal coronary atherectomy, with drug eluting intracoronary stent, with coronary angioplasty when performed; single major coronary artery or branch | HCPCS C9602 | 43533353 | 7 | — |
| — | Coronary artery bypass, using venous graft(s) and arterial graft(s); 4 venous grafts (List separately in addition to code for primary procedure) | CPT4 33521 | 2107226 | 6 | — |
| — | Percutaneous transluminal coronary lithotripsy (List separately in addition to code for primary procedure) (Deprecated) | CPT4 0715T | 1552138 | 5 | — |
| — | Coronary artery bypass, vein only; single coronary venous graft | CPT4 33510 | 2107216 | 5 | — |
| — | Percutaneous transluminal revascularization of chronic total occlusion, coronary artery, coronary artery branch, or coronary artery bypass graft, any combination of intracoronary stent, atherectomy and angioplasty; each additional coronary... (Deprecated) | CPT4 92944 | 43528004 | 5 | — |
| — | Coronary endarterectomy, open, any method, of left anterior descending, circumflex, or right coronary artery performed in conjunction with coronary artery bypass graft procedure, each vessel (List separately in addition to primary procedure) | CPT4 33572 | 2107250 | 4 | — |
| — | Percutaneous transluminal revascularization of acute total/subtotal occlusion during acute myocardial infarction, coronary artery or coronary artery bypass graft, any combination of drug-eluting intracoronary stent, atherectomy and angioplasty, includi... | HCPCS C9606 | 43533187 | 4 | — |
| — | Coronary artery bypass, using arterial graft(s); 3 coronary arterial grafts | CPT4 33535 | 2107243 | 3 | — |
| — | Coronary artery bypass, using arterial graft(s); 4 or more coronary arterial grafts | CPT4 33536 | 2107244 | 3 | — |
| — | Percutaneous transluminal coronary atherectomy, with coronary angioplasty when performed, single major coronary artery and/or its branch(es) | CPT4 92924 | 43527996 | 3 | — |
| — | Percutaneous transluminal revascularization of or through coronary artery bypass graft (internal mammary, free arterial, venous), any combination of drug-eluting intracoronary stent, atherectomy and angioplasty, including distal protection when perform... | HCPCS C9604 | 43533186 | 3 | — |
| — | Coronary artery bypass, vein only; 3 coronary venous grafts | CPT4 33512 | 2107218 | 2 | — |
| — | Coronary artery bypass, using venous graft(s) and arterial graft(s); 5 venous grafts (List separately in addition to code for primary procedure) | CPT4 33522 | 2107227 | 1 | — |
| — | Percutaneous transluminal coronary atherectomy, with intracoronary stent, with coronary angioplasty when performed; each additional branch of a major coronary artery (List separately in addition to code for primary procedure) (Deprecated) | CPT4 92934 | 43527909 | 1 | — |

#### Nerve damage (neuropathy) diagnosis · `neuropathy`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Polyneuropathy | SNOMED 42345000 | 4174262 | 4,255 | — |
| — | Neuropathy | SNOMED 386033004 | 4301699 | 1,043 | — |
| — | Mononeuropathy of lower limb | SNOMED 609592007 | 43531028 | 962 | — |
| — | Mononeuropathy | SNOMED 128189008 | 4134455 | 525 | — |
| — | Idiopathic peripheral autonomic neuropathy | SNOMED 86489003 | 194913 | 513 | — |
| — | Mononeuropathy of upper limb | SNOMED 609591000 | 43531027 | 386 | — |
| — | Idiopathic progressive polyneuropathy | SNOMED 33209009 | 380394 | 277 | — |
| — | Recurrent painful ophthalmoplegic neuropathy | SNOMED 49605003 | 4175786 | 230 | — |
| — | Polyneuropathy associated with another disorder | SNOMED 193186008 | 376686 | 187 | — |
| — | Lumbosacral plexus neuropathy | SNOMED 230617009 | 4044404 | 124 | — |
| — | Intercostal neuropathy | SNOMED 230646002 | 4046351 | 118 | — |
| — | Post-herpetic polyneuropathy | SNOMED 76462000 | 192239 | 96 | — |
| — | Alcoholic polyneuropathy | SNOMED 7916009 | 378421 | 62 | — |
| — | Hereditary motor and sensory neuropathy | SNOMED 398100001 | 4134552 | 62 | — |
| — | Ischemic optic neuropathy | SNOMED 14357004 | 373487 | 59 | — |
| — | Polyneuropathy caused by drug | SNOMED 7339009 | 381551 | 54 | — |
| — | Femoral neuropathy | SNOMED 25690000 | 439807 | 54 | — |
| — | Chronic inflammatory demyelinating polyradiculoneuropathy | SNOMED 128209004 | 381009 | 42 | — |
| — | Autonomic neuropathy | SNOMED 277879009 | 4080146 | 25 | — |
| — | Polyneuropathy in rheumatoid arthritis | SNOMED 193180002 | 4102493 | 25 | — |
| — | Critical illness polyneuropathy | SNOMED 230594005 | 374032 | 22 | — |
| — | Toxic polyneuropathy | SNOMED 45600000 | 373470 | 19 | — |
| — | Motor neuropathy with multiple conduction block | SNOMED 230591002 | 4046338 | 11 | — |
| — | Familial amyloid polyneuropathy | SNOMED 42295001 | 4173311 | 6 | — |
| — | Neuropathy in association with hereditary ataxia | SNOMED 193165008 | 4102492 | 5 | — |
| — | Radiation polyneuropathy | SNOMED 16053951000119108 | 42539208 | 4 | — |
| — | Paraneoplastic neuropathy | SNOMED 77659000 | 378420 | 3 | — |
| — | Serum neuropathy | SNOMED 193203006 | 4105020 | 3 | — |
| — | Polyneuropathy due to systemic sclerosis | SNOMED 322461000119108 | 46270482 | 3 | — |
| — | Nutritional optic neuropathy | SNOMED 82108004 | 380410 | 2 | — |
| — | Polyneuropathy due to infectious mononucleosis | SNOMED 1090231000119107 | 46274079 | 2 | — |
| — | Toxic optic neuropathy | SNOMED 26125006 | 377570 | 1 | — |

### B. Medicines and visits

#### Angina medicines (nitrates, ranolazine) · `nitrate_antianginal`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | nitroglycerin 0.4 MG Sublingual Tablet | RxNorm 198039 | 19019336 | 880 | — |
| — | nitroglycerin Injection | RxNorm 1868493 | 1593968 | 365 | — |
| — | 24 HR isosorbide mononitrate 30 MG Extended Release Oral Tablet | RxNorm 317110 | 19082350 | 188 | — |
| — | nitroglycerin 0.3 MG Sublingual Tablet | RxNorm 198038 | 19019335 | 74 | — |
| — | 12 HR ranolazine 500 MG Extended Release Oral Tablet | RxNorm 616749 | 1337111 | 67 | — |
| — | 24 HR nitroglycerin 0.2 MG/HR Transdermal System | RxNorm 486148 | 1362360 | 32 | — |
| — | 24 HR nitroglycerin 0.1 MG/HR Transdermal System | RxNorm 861657 | 40163938 | 27 | — |
| — | 24 HR isosorbide mononitrate 60 MG Extended Release Oral Tablet | RxNorm 353538 | 1383869 | 21 | — |
| — | isosorbide dinitrate 10 MG Oral Tablet | RxNorm 381056 | 19100691 | 13 | — |
| — | 12 HR ranolazine 1000 MG Extended Release Oral Tablet | RxNorm 728231 | 1337145 | 12 | — |
| — | isosorbide dinitrate 5 MG Oral Tablet | RxNorm 314055 | 19080095 | 12 | — |
| — | nitroglycerin 0.4 MG Sublingual Tablet [Nitrostat] | RxNorm 207346 | 19035279 | 9 | — |
| — | 24 HR nitroglycerin 0.4 MG/HR Transdermal System | RxNorm 486152 | 1362392 | 7 | — |
| — | isosorbide dinitrate 30 MG Oral Tablet | RxNorm 197839 | 1383930 | 7 | — |
| — | isosorbide dinitrate 20 MG Oral Tablet | RxNorm 206842 | 19033627 | 5 | — |
| — | nitroglycerin 0.4 MG/ACTUAT Mucosal Spray | RxNorm 705129 | 19126352 | 5 | — |
| — | 12 HR ranolazine 1000 MG Extended Release Oral Tablet [Ranexa] | RxNorm 860737 | 40163877 | 5 | — |
| — | isosorbide mononitrate 10 MG Oral Tablet | RxNorm 311192 | 1383849 | 4 | — |
| — | nitroglycerin 0.6 MG Sublingual Tablet | RxNorm 198040 | 19019337 | 4 | — |
| — | 24 HR isosorbide mononitrate 120 MG Extended Release Oral Tablet | RxNorm 311196 | 1383850 | 3 | — |
| — | 12 HR ranolazine 500 MG Extended Release Oral Tablet [Ranexa] | RxNorm 860738 | 40163878 | 2 | — |
| — | isosorbide dinitrate 40 MG Oral Tablet | RxNorm 197840 | 19019078 | 1 | — |
| — | nitroglycerin 2.5 MG Extended Release Oral Capsule | RxNorm 312013 | 19079057 | 1 | — |
| — | nitroglycerin 6.5 MG Extended Release Oral Capsule | RxNorm 312018 | 19079082 | 1 | — |

#### Antiplatelet medicines · `antiplatelet`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | aspirin 81 MG Delayed Release Oral Tablet | RxNorm 308416 | 19073712 | 2,687 | — |
| — | aspirin 81 MG Chewable Tablet | RxNorm 318272 | 1113346 | 879 | — |
| — | clopidogrel 75 MG Oral Tablet | RxNorm 309362 | 19075601 | 350 | — |
| — | ticagrelor 90 MG Oral Tablet [Brilinta] | RxNorm 1116639 | 40241189 | 43 | — |
| — | prasugrel 10 MG Oral Tablet | RxNorm 855812 | 40163720 | 24 | — |
| — | aspirin 81 MG Chewable Tablet [Bayer Aspirin] | RxNorm 825180 | 19133088 | 15 | — |
| — | aspirin 81 MG Delayed Release Oral Tablet [Bayer Aspirin] | RxNorm 794229 | 1113617 | 13 | — |
| — | ticagrelor 90 MG Oral Tablet | RxNorm 1116635 | 40241188 | 12 | — |
| — | aspirin 81 MG Delayed Release Oral Tablet [Aspir-Low] | RxNorm 1293665 | 42799212 | 8 | — |
| — | ticagrelor 60 MG Oral Tablet [Brilinta] | RxNorm 1666334 | 46287540 | 5 | — |
| — | clopidogrel 75 MG Oral Tablet [Plavix] | RxNorm 213169 | 1322185 | 3 | — |
| — | aspirin 81 MG Delayed Release Oral Tablet [Ecotrin] | RxNorm 1189781 | 40243310 | 3 | — |
| — | aspirin 81 MG Chewable Tablet [St. Joseph Aspirin] | RxNorm 211832 | 1112960 | 2 | — |
| — | clopidogrel 300 MG Oral Tablet | RxNorm 749196 | 1322189 | 2 | — |
| — | prasugrel 5 MG Oral Tablet | RxNorm 855818 | 40163724 | 2 | — |
| — | ticagrelor 60 MG Oral Tablet | RxNorm 1666332 | 46287538 | 2 | — |
| — | aspirin 81 MG Oral Capsule [Vazalore] | RxNorm 2563431 | 1537535 | 1 | — |

#### Beta-blocker medicines · `beta_blocker`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | 24 HR metoprolol succinate 25 MG Extended Release Oral Tablet | RxNorm 866427 | 40166828 | 3,273 | — |
| — | propranolol hydrochloride 10 MG Oral Tablet | RxNorm 856448 | 40163312 | 2,471 | — |
| — | 24 HR metoprolol succinate 50 MG Extended Release Oral Tablet | RxNorm 866436 | 40166830 | 1,826 | — |
| — | metoprolol tartrate 25 MG Oral Tablet | RxNorm 866924 | 40167213 | 1,681 | — |
| — | propranolol hydrochloride 20 MG Oral Tablet | RxNorm 856457 | 40163333 | 1,479 | — |
| — | metoprolol tartrate 50 MG Oral Tablet | RxNorm 866514 | 40167218 | 917 | — |
| — | atenolol 25 MG Oral Tablet | RxNorm 197380 | 19018811 | 665 | — |
| — | 24 HR metoprolol succinate 100 MG Extended Release Oral Tablet | RxNorm 866412 | 40166824 | 635 | — |
| — | 24 HR propranolol hydrochloride 60 MG Extended Release Oral Capsule | RxNorm 856535 | 40162436 | 586 | — |
| — | carvedilol 6.25 MG Oral Tablet | RxNorm 200031 | 19022749 | 481 | — |
| — | propranolol hydrochloride 40 MG Oral Tablet | RxNorm 856519 | 40163342 | 429 | — |
| — | carvedilol 12.5 MG Oral Tablet | RxNorm 200032 | 19022750 | 413 | — |
| — | atenolol 50 MG Oral Tablet | RxNorm 197381 | 1314008 | 366 | — |
| — | carvedilol 3.125 MG Oral Tablet | RxNorm 686924 | 1346990 | 338 | — |
| — | 24 HR propranolol hydrochloride 80 MG Extended Release Oral Capsule | RxNorm 856569 | 40162438 | 277 | — |
| — | carvedilol 25 MG Oral Tablet | RxNorm 200033 | 19022781 | 258 | — |
| — | metoprolol tartrate 100 MG Oral Tablet | RxNorm 866511 | 40167202 | 229 | — |
| — | metoprolol Injection | RxNorm 1740909 | 35605509 | 186 | — |
| — | bisoprolol fumarate 5 MG Oral Tablet | RxNorm 854905 | 40162878 | 147 | — |
| — | 24 HR propranolol hydrochloride 120 MG Extended Release Oral Capsule | RxNorm 856460 | 40162431 | 118 | — |
| — | atenolol 100 MG Oral Tablet | RxNorm 197379 | 1314006 | 88 | — |
| — | bisoprolol fumarate 5 MG / hydrochlorothiazide 6.25 MG Oral Tablet | RxNorm 854919 | 40162875 | 75 | — |
| — | propranolol hydrochloride 60 MG Oral Tablet | RxNorm 856556 | 40163350 | 69 | — |
| — | atenolol 50 MG / chlorthalidone 25 MG Oral Tablet | RxNorm 197383 | 1395060 | 60 | — |
| — | 24 HR metoprolol succinate 200 MG Extended Release Oral Tablet | RxNorm 866419 | 40166826 | 57 | — |
| — | propranolol hydrochloride 80 MG Oral Tablet | RxNorm 856578 | 40163361 | 55 | — |
| — | 24 HR metoprolol succinate 25 MG Extended Release Oral Tablet [Toprol] | RxNorm 866429 | 40166829 | 45 | — |
| — | bisoprolol fumarate 10 MG Oral Tablet | RxNorm 854901 | 40162867 | 42 | — |
| — | bisoprolol fumarate 10 MG / hydrochlorothiazide 6.25 MG Oral Tablet | RxNorm 854908 | 40162864 | 36 | — |
| — | 24 HR metoprolol succinate 50 MG Extended Release Oral Tablet [Toprol] | RxNorm 866438 | 40166831 | 32 | — |
| — | bisoprolol fumarate 2.5 MG / hydrochlorothiazide 6.25 MG Oral Tablet | RxNorm 854916 | 40162871 | 31 | — |
| — | 24 HR propranolol hydrochloride 160 MG Extended Release Oral Capsule | RxNorm 856481 | 40162434 | 30 | — |
| — | metoprolol tartrate 75 MG Oral Tablet | RxNorm 1606349 | 46221724 | 28 | — |
| — | atenolol 100 MG / chlorthalidone 25 MG Oral Tablet | RxNorm 197382 | 1314009 | 21 | — |
| — | 24 HR carvedilol phosphate 20 MG Extended Release Oral Capsule | RxNorm 860516 | 40163950 | 19 | — |
| — | 24 HR metoprolol succinate 25 MG Extended Release Oral Capsule [Kapspargo] | RxNorm 2047772 | 1510810 | 17 | — |
| — | 24 HR metoprolol succinate 100 MG Extended Release Oral Tablet [Toprol] | RxNorm 866414 | 40166825 | 16 | — |
| — | 24 HR carvedilol phosphate 10 MG Extended Release Oral Capsule | RxNorm 860510 | 40163948 | 15 | — |
| — | hydrochlorothiazide 25 MG / metoprolol tartrate 50 MG Oral Tablet | RxNorm 866482 | 40167091 | 15 | — |
| — | 24 HR carvedilol phosphate 40 MG Extended Release Oral Capsule | RxNorm 860522 | 40163952 | 12 | — |
| — | carvedilol 12.5 MG Oral Tablet [Coreg] | RxNorm 212389 | 1346828 | 7 | — |
| — | 24 HR metoprolol succinate 50 MG Extended Release Oral Capsule [Kapspargo] | RxNorm 2047775 | 1510811 | 7 | — |
| — | 24 HR carvedilol phosphate 80 MG Extended Release Oral Capsule | RxNorm 860532 | 40163954 | 4 | — |
| — | propranolol Injection | RxNorm 1789973 | 42629333 | 4 | — |
| — | propranolol hydrochloride 4 MG/ML Oral Solution | RxNorm 856724 | 40163340 | 3 | — |
| — | 24 HR carvedilol phosphate 20 MG Extended Release Oral Capsule [Coreg] | RxNorm 860518 | 40163951 | 3 | — |
| — | carvedilol 6.25 MG Oral Tablet [Coreg] | RxNorm 212388 | 1346827 | 2 | — |
| — | bisoprolol fumarate 5 MG / hydrochlorothiazide 6.25 MG Oral Tablet [Ziac] | RxNorm 854921 | 40162876 | 2 | — |
| — | 24 HR carvedilol phosphate 10 MG Extended Release Oral Capsule [Coreg] | RxNorm 860512 | 40163949 | 2 | — |
| — | hydrochlorothiazide 25 MG / metoprolol tartrate 100 MG Oral Tablet | RxNorm 866479 | 40167087 | 2 | — |
| — | metoprolol tartrate 37.5 MG Oral Tablet | RxNorm 1606347 | 46221722 | 2 | — |
| — | atenolol 50 MG Oral Tablet [Tenormin] | RxNorm 152414 | 1314005 | 1 | — |
| — | atenolol 25 MG Oral Tablet [Tenormin] | RxNorm 150750 | 19012417 | 1 | — |
| — | metoprolol tartrate 12.5 MG Oral Tablet | RxNorm 2723025 | 37354111 | 1 | — |
| — | 24 HR propranolol hydrochloride 120 MG Extended Release Oral Capsule [Inderal] | RxNorm 856462 | 40162432 | 1 | — |
| — | bisoprolol fumarate 10 MG / hydrochlorothiazide 6.25 MG Oral Tablet [Ziac] | RxNorm 854910 | 40162865 | 1 | — |
| — | hydrochlorothiazide 25 MG / propranolol hydrochloride 40 MG Oral Tablet | RxNorm 856422 | 40163112 | 1 | — |
| — | propranolol hydrochloride 10 MG Oral Tablet [Inderal] | RxNorm 856450 | 40163313 | 1 | — |
| — | propranolol hydrochloride 40 MG Oral Tablet [Inderal] | RxNorm 856521 | 40163343 | 1 | — |
| — | propranolol hydrochloride 8 MG/ML Oral Solution | RxNorm 856733 | 40163354 | 1 | — |
| — | 24 HR carvedilol phosphate 40 MG Extended Release Oral Capsule [Coreg] | RxNorm 860524 | 40163953 | 1 | — |
| — | bisoprolol fumarate 2.5 MG Oral Tablet | RxNorm 865155 | 40166188 | 1 | — |
| — | 24 HR hydrochlorothiazide 12.5 MG / metoprolol succinate 25 MG Extended Release Oral Tablet [Dutoprol] | RxNorm 866464 | 40166820 | 1 | — |
| — | 24 HR hydrochlorothiazide 12.5 MG / metoprolol succinate 50 MG Extended Release Oral Tablet [Dutoprol] | RxNorm 866475 | 40166822 | 1 | — |
| — | metoprolol tartrate 50 MG Oral Tablet [Lopressor] | RxNorm 866516 | 40167219 | 1 | — |

#### Statin medicines · `statin`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | atorvastatin 20 MG Oral Tablet | RxNorm 617310 | 19123592 | 5,289 | — |
| — | rosuvastatin calcium 10 MG Oral Tablet | RxNorm 859747 | 40165245 | 3,928 | — |
| — | atorvastatin 10 MG Oral Tablet | RxNorm 617312 | 1545997 | 3,779 | — |
| — | atorvastatin 40 MG Oral Tablet | RxNorm 617311 | 1545996 | 3,650 | — |
| — | rosuvastatin calcium 20 MG Oral Tablet | RxNorm 859751 | 40165253 | 2,630 | — |
| — | rosuvastatin calcium 5 MG Oral Tablet | RxNorm 859424 | 40165261 | 2,431 | — |
| — | atorvastatin 80 MG Oral Tablet | RxNorm 259255 | 1545959 | 836 | — |
| — | rosuvastatin calcium 40 MG Oral Tablet | RxNorm 859419 | 40165257 | 815 | — |
| — | simvastatin 20 MG Oral Tablet | RxNorm 312961 | 1539411 | 762 | — |
| — | pravastatin sodium 20 MG Oral Tablet | RxNorm 904467 | 40175394 | 629 | — |
| — | pravastatin sodium 40 MG Oral Tablet | RxNorm 904475 | 40175400 | 554 | — |
| — | simvastatin 40 MG Oral Tablet | RxNorm 198211 | 1539407 | 417 | — |
| — | simvastatin 10 MG Oral Tablet | RxNorm 314231 | 1539463 | 373 | — |
| — | pravastatin sodium 10 MG Oral Tablet | RxNorm 904458 | 40175390 | 323 | — |
| — | pravastatin sodium 80 MG Oral Tablet | RxNorm 904481 | 40175404 | 118 | — |
| — | simvastatin 5 MG Oral Tablet | RxNorm 312962 | 1539462 | 59 | — |
| — | simvastatin 80 MG Oral Tablet | RxNorm 200345 | 19023563 | 39 | — |
| — | atorvastatin 20 MG Oral Tablet [Lipitor] | RxNorm 617318 | 1545999 | 32 | — |
| — | rosuvastatin calcium 10 MG Oral Tablet [Crestor] | RxNorm 859749 | 40165246 | 31 | — |
| — | rosuvastatin calcium 20 MG Oral Tablet [Crestor] | RxNorm 859753 | 40165254 | 29 | — |
| — | ezetimibe 10 MG / simvastatin 40 MG Oral Tablet | RxNorm 476350 | 19112569 | 19 | — |
| — | ezetimibe 10 MG / simvastatin 20 MG Oral Tablet | RxNorm 476349 | 1526479 | 16 | — |
| — | atorvastatin 10 MG Oral Tablet [Lipitor] | RxNorm 617314 | 1545998 | 15 | — |
| — | rosuvastatin calcium 5 MG Oral Tablet [Crestor] | RxNorm 859426 | 40165262 | 15 | — |
| — | atorvastatin 40 MG Oral Tablet [Lipitor] | RxNorm 617320 | 19123593 | 10 | — |
| — | amlodipine 10 MG / atorvastatin 20 MG Oral Tablet | RxNorm 597967 | 1332494 | 9 | — |
| — | ezetimibe 10 MG / simvastatin 10 MG Oral Tablet | RxNorm 476345 | 1539469 | 8 | — |
| — | amlodipine 10 MG / atorvastatin 10 MG Oral Tablet | RxNorm 597987 | 1332500 | 7 | — |
| — | amlodipine 5 MG / atorvastatin 20 MG Oral Tablet | RxNorm 597980 | 19122209 | 6 | — |
| — | amlodipine 5 MG / atorvastatin 10 MG Oral Tablet | RxNorm 597977 | 1332497 | 4 | — |
| — | amlodipine 10 MG / atorvastatin 40 MG Oral Tablet | RxNorm 597990 | 19122210 | 4 | — |
| — | rosuvastatin calcium 40 MG Oral Tablet [Crestor] | RxNorm 859421 | 40165258 | 3 | — |
| — | rosuvastatin 20 MG Oral Capsule [Ezallor] | RxNorm 2167567 | 789828 | 2 | — |
| — | pravastatin sodium 20 MG Oral Tablet [Pravachol] | RxNorm 904469 | 40175395 | 2 | — |
| — | atorvastatin 4 MG/ML Oral Suspension [Atorvaliq] | RxNorm 2631867 | 1301873 | 1 | — |
| — | amlodipine 5 MG / atorvastatin 40 MG Oral Tablet | RxNorm 597984 | 1332499 | 1 | — |
| — | ezetimibe 10 MG / simvastatin 80 MG Oral Tablet | RxNorm 476351 | 1526480 | 1 | — |
| — | simvastatin 40 MG Oral Tablet [Zocor] | RxNorm 152923 | 1539406 | 1 | — |
| — | amlodipine 10 MG / atorvastatin 20 MG Oral Tablet [Caduet] | RxNorm 750203 | 19128151 | 1 | — |
| — | ezetimibe 10 MG / rosuvastatin 10 MG Oral Tablet | RxNorm 2535750 | 36026847 | 1 | — |
| — | ezetimibe 10 MG / rosuvastatin 20 MG Oral Tablet [Roszet] | RxNorm 2536062 | 36026856 | 1 | — |
| — | pravastatin sodium 40 MG Oral Tablet [Pravachol] | RxNorm 904477 | 40175401 | 1 | — |
| — | pravastatin sodium 80 MG Oral Tablet [Pravachol] | RxNorm 904483 | 40175405 | 1 | — |

#### Acid-reducing medicines (PPI or H2 blocker) (PPI / H2) · `ppi_h2`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | pantoprazole 40 MG Delayed Release Oral Tablet | RxNorm 314200 | 19080217 | 11,585 | — |
| — | omeprazole 40 MG Delayed Release Oral Capsule | RxNorm 200329 | 19023551 | 9,222 | — |
| — | omeprazole 20 MG Delayed Release Oral Capsule | RxNorm 198051 | 19019418 | 8,429 | — |
| — | famotidine 20 MG Oral Tablet | RxNorm 310273 | 19077241 | 5,603 | — |
| — | famotidine 40 MG Oral Tablet | RxNorm 284245 | 953113 | 3,905 | — |
| — | famotidine Injection | RxNorm 1743827 | 35606550 | 2,355 | — |
| — | pantoprazole 20 MG Delayed Release Oral Tablet | RxNorm 251872 | 948079 | 1,972 | — |
| — | esomeprazole 40 MG Delayed Release Oral Capsule | RxNorm 606730 | 19123105 | 1,443 | — |
| — | pantoprazole 40 MG Injection [Protonix] | RxNorm 885257 | 40168991 | 1,402 | — |
| — | pantoprazole Injection | RxNorm 1737587 | 35604331 | 1,156 | — |
| — | lansoprazole 30 MG Delayed Release Oral Capsule | RxNorm 311277 | 929889 | 669 | — |
| — | ranitidine 150 MG Oral Tablet | RxNorm 198191 | 961050 | 554 | — |
| — | esomeprazole 20 MG Delayed Release Oral Capsule | RxNorm 606726 | 19123103 | 386 | — |
| — | dexlansoprazole 60 MG Delayed Release Oral Capsule [Dexilant] | RxNorm 902626 | 40174235 | 348 | — |
| — | omeprazole 20 MG Delayed Release Oral Tablet | RxNorm 402014 | 19102189 | 335 | — |
| — | rabeprazole sodium 20 MG Delayed Release Oral Tablet | RxNorm 854868 | 40163285 | 309 | — |
| — | dexlansoprazole 60 MG Delayed Release Oral Capsule | RxNorm 833213 | 19039961 | 232 | — |
| — | ranitidine 300 MG Oral Tablet | RxNorm 198193 | 961082 | 222 | — |
| — | omeprazole 10 MG Delayed Release Oral Capsule | RxNorm 199119 | 923647 | 147 | — |
| — | famotidine 26.6 MG / ibuprofen 800 MG Oral Tablet [Duexis] | RxNorm 1100070 | 40239182 | 132 | — |
| — | pantoprazole 40 MG Delayed Release Oral Tablet [Protonix] | RxNorm 284400 | 19071430 | 91 | — |
| — | lansoprazole 15 MG Delayed Release Oral Capsule | RxNorm 596843 | 929953 | 76 | — |
| — | famotidine 10 MG Oral Tablet | RxNorm 199047 | 19021074 | 72 | — |
| — | cimetidine 400 MG Oral Tablet | RxNorm 197507 | 19018875 | 69 | — |
| — | {4 (amoxicillin 500 MG Oral Capsule) / 2 (clarithromycin 500 MG Oral Tablet) / 2 (lansoprazole 30 MG Delayed Release Oral Capsule) } Pack | RxNorm 757968 | 19129191 | 62 | — |
| — | famotidine 20 MG Oral Tablet [Pepcid] | RxNorm 104094 | 19003315 | 60 | — |
| — | dexlansoprazole 30 MG Delayed Release Oral Capsule [Dexilant] | RxNorm 902624 | 40174233 | 60 | — |
| — | amoxicillin 250 MG / omeprazole 10 MG / rifabutin 12.5 MG Delayed Release Oral Capsule [Talicia] | RxNorm 2262032 | 37497626 | 54 | — |
| — | ranitidine 150 MG Oral Capsule | RxNorm 198190 | 19019696 | 50 | — |
| — | famotidine 8 MG/ML Oral Suspension | RxNorm 310274 | 19077242 | 48 | — |
| — | dexlansoprazole 30 MG Delayed Release Oral Capsule | RxNorm 833204 | 19133802 | 45 | — |
| — | esomeprazole 40 MG Delayed Release Oral Capsule [Nexium] | RxNorm 606731 | 19123106 | 39 | — |
| — | famotidine 26.6 MG / ibuprofen 800 MG Oral Tablet | RxNorm 1100066 | 40239181 | 35 | — |
| — | ranitidine 150 MG Oral Capsule [Zantac] | RxNorm 827190 | 19133217 | 34 | — |
| — | cimetidine 200 MG Oral Tablet | RxNorm 197505 | 19018873 | 27 | — |
| — | omeprazole 20 MG Delayed Release Oral Capsule [Prilosec] | RxNorm 207212 | 19034886 | 27 | — |
| — | lansoprazole 30 MG Disintegrating Oral Tablet | RxNorm 351260 | 19098167 | 27 | — |
| — | esomeprazole 20 MG Delayed Release Oral Capsule [Nexium] | RxNorm 606728 | 19123104 | 27 | — |
| — | cimetidine 300 MG Oral Tablet | RxNorm 197506 | 19018874 | 25 | — |
| — | esomeprazole 20 MG / naproxen 500 MG Delayed Release Oral Tablet [Vimovo] | RxNorm 994010 | 40222579 | 24 | — |
| — | cimetidine 800 MG Oral Tablet | RxNorm 197508 | 19018876 | 23 | — |
| — | omeprazole 20 MG Delayed Release Oral Tablet [Prilosec] | RxNorm 608796 | 19123300 | 23 | — |
| — | ranitidine 300 MG Oral Capsule | RxNorm 198192 | 961051 | 22 | — |
| — | ranitidine 25 MG/ML Injection [Zantac] | RxNorm 1859556 | 1718659 | 19 | — |
| — | famotidine 40 MG Oral Tablet [Pepcid] | RxNorm 104095 | 19003316 | 18 | — |
| — | esomeprazole 40 MG Granules for Oral Suspension | RxNorm 692578 | 904492 | 12 | — |
| — | omeprazole 40 MG / sodium bicarbonate 1100 MG Oral Capsule | RxNorm 616541 | 923721 | 10 | — |
| — | omeprazole 40 MG Delayed Release Oral Capsule [Prilosec] | RxNorm 213295 | 923682 | 9 | — |
| — | ranitidine 150 MG Oral Tablet [Zantac] | RxNorm 827189 | 961269 | 9 | — |
| — | ranitidine 15 MG/ML Oral Solution | RxNorm 705610 | 19126405 | 9 | — |
| — | pantoprazole 40 MG Oral Granules | RxNorm 763306 | 19129540 | 9 | — |
| — | pantoprazole 20 MG Delayed Release Oral Tablet [Protonix] | RxNorm 352125 | 948107 | 8 | — |
| — | cimetidine 200 MG Oral Tablet [Tagamet] | RxNorm 104062 | 19003220 | 8 | — |
| — | esomeprazole 20 MG / naproxen 500 MG Delayed Release Oral Tablet | RxNorm 994008 | 40222578 | 8 | — |
| — | omeprazole 40 MG / sodium bicarbonate 1680 MG Powder for Oral Suspension | RxNorm 753557 | 923756 | 7 | — |
| — | esomeprazole 20 MG Delayed Release Oral Tablet [Nexium] | RxNorm 1743279 | 35606348 | 7 | — |
| — | ranitidine 75 MG Oral Tablet | RxNorm 312773 | 961168 | 6 | — |
| — | omeprazole 20 MG / sodium bicarbonate 1100 MG Oral Capsule | RxNorm 616539 | 923720 | 5 | — |
| — | lansoprazole 15 MG Disintegrating Oral Tablet | RxNorm 351261 | 929924 | 5 | — |
| — | lansoprazole 30 MG Delayed Release Oral Capsule [Prevacid] | RxNorm 206206 | 19031629 | 5 | — |
| — | esomeprazole 20 MG Granules for Oral Suspension | RxNorm 692576 | 904490 | 4 | — |
| — | pantoprazole 40 MG Oral Granules [Protonix] | RxNorm 763308 | 19129541 | 4 | — |
| — | rabeprazole sodium 20 MG Delayed Release Oral Tablet [Aciphex] | RxNorm 854870 | 40163286 | 4 | — |
| — | esomeprazole 20 MG / naproxen 375 MG Delayed Release Oral Tablet | RxNorm 994005 | 40222575 | 4 | — |
| — | lansoprazole 15 MG Delayed Release Oral Capsule [Prevacid] | RxNorm 596918 | 929954 | 3 | — |
| — | calcium carbonate 800 MG / famotidine 10 MG / magnesium hydroxide 165 MG Chewable Tablet | RxNorm 283641 | 953112 | 3 | — |
| — | esomeprazole 10 MG Granules for Oral Suspension | RxNorm 861568 | 40165707 | 3 | — |
| — | omeprazole 20 MG Disintegrating Oral Tablet | RxNorm 2003656 | 42543965 | 3 | — |
| — | omeprazole 40 MG / sodium bicarbonate 1100 MG Oral Capsule [Zegerid Reformulated Aug 2006] | RxNorm 646352 | 923755 | 2 | — |
| — | omeprazole 20 MG / sodium bicarbonate 1680 MG Powder for Oral Suspension | RxNorm 753562 | 923757 | 2 | — |
| — | ranitidine 300 MG Oral Tablet [Zantac] | RxNorm 827185 | 961267 | 2 | — |
| — | esomeprazole 20 MG Delayed Release Oral Tablet | RxNorm 433733 | 904457 | 1 | — |
| — | omeprazole 20 MG / sodium bicarbonate 1100 MG Oral Capsule [Zegerid Reformulated Aug 2006] | RxNorm 646344 | 923754 | 1 | — |
| — | pantoprazole 40 MG Injection | RxNorm 283669 | 948080 | 1 | — |
| — | ranitidine 15 MG/ML Oral Solution [Zantac] | RxNorm 755272 | 961263 | 1 | — |
| — | famotidine 10 MG Oral Tablet [Pepcid] | RxNorm 212072 | 19046867 | 1 | — |
| — | ranitidine 75 MG Oral Tablet [Wal-Zan] | RxNorm 643046 | 19124364 | 1 | — |
| — | cimetidine Injectable Solution [Tagamet] | RxNorm 94233 | 40027983 | 1 | — |
| — | esomeprazole 10 MG Granules for Oral Suspension [Nexium] | RxNorm 861570 | 40165708 | 1 | — |
| — | esomeprazole 40 MG Granules for Oral Suspension [Nexium] | RxNorm 861583 | 40165710 | 1 | — |
| — | lansoprazole 30 MG Disintegrating Oral Tablet [Prevacid] | RxNorm 866152 | 40167553 | 1 | — |
| — | esomeprazole strontium 49.3 MG Delayed Release Oral Capsule | RxNorm 1810787 | 40220766 | 1 | — |
| — | esomeprazole 20 MG / naproxen 375 MG Delayed Release Oral Tablet [Vimovo] | RxNorm 994007 | 40222576 | 1 | — |
| — | {4 (amoxicillin 500 MG Oral Capsule) / 2 (clarithromycin 500 MG Oral Tablet) / 2 (omeprazole 20 MG Delayed Release Oral Capsule) } Pack [Omeclamox] | RxNorm 1291987 | 42800263 | 1 | — |
| — | rabeprazole sodium 10 MG Oral Granules | RxNorm 1483318 | 44784921 | 1 | — |

#### SSRI antidepressant medicines · `ssri`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | escitalopram 10 MG Oral Tablet | RxNorm 349332 | 715940 | 6,958 | — |
| — | sertraline 50 MG Oral Tablet | RxNorm 312941 | 739209 | 5,742 | — |
| — | sertraline 25 MG Oral Tablet | RxNorm 312940 | 19079497 | 3,309 | — |
| — | fluoxetine 20 MG Oral Capsule | RxNorm 310385 | 19077463 | 3,025 | — |
| — | escitalopram 20 MG Oral Tablet | RxNorm 351250 | 19098166 | 2,777 | — |
| — | sertraline 100 MG Oral Tablet | RxNorm 312938 | 739207 | 2,725 | — |
| — | escitalopram 5 MG Oral Tablet | RxNorm 351249 | 715962 | 2,583 | — |
| — | fluoxetine 10 MG Oral Capsule | RxNorm 310384 | 19077462 | 1,972 | — |
| — | citalopram 20 MG Oral Tablet | RxNorm 200371 | 19023636 | 1,483 | — |
| — | fluoxetine 40 MG Oral Capsule | RxNorm 313989 | 755739 | 1,308 | — |
| — | citalopram 10 MG Oral Tablet | RxNorm 283672 | 797632 | 1,085 | — |
| — | paroxetine hydrochloride 10 MG Oral Tablet | RxNorm 1738483 | 35604569 | 786 | — |
| — | paroxetine hydrochloride 20 MG Oral Tablet | RxNorm 1738495 | 35604576 | 726 | — |
| — | citalopram 40 MG Oral Tablet | RxNorm 309314 | 19075394 | 674 | — |
| — | fluoxetine 20 MG Oral Tablet | RxNorm 248642 | 755700 | 469 | — |
| — | fluoxetine 10 MG Oral Tablet | RxNorm 313990 | 19079985 | 382 | — |
| — | paroxetine hydrochloride 30 MG Oral Tablet | RxNorm 1738503 | 35604581 | 186 | — |
| — | paroxetine hydrochloride 40 MG Oral Tablet | RxNorm 1738511 | 35604586 | 186 | — |
| — | fluoxetine 60 MG Oral Tablet | RxNorm 1190110 | 40243919 | 106 | — |
| — | escitalopram 10 MG Oral Tablet [Lexapro] | RxNorm 352272 | 715965 | 51 | — |
| — | paroxetine mesylate 7.5 MG Oral Capsule | RxNorm 1430122 | 43532894 | 47 | — |
| — | 24 HR paroxetine hydrochloride 12.5 MG Extended Release Oral Tablet | RxNorm 1738803 | 35604757 | 40 | — |
| — | 24 HR paroxetine hydrochloride 25 MG Extended Release Oral Tablet | RxNorm 1738805 | 35604759 | 37 | — |
| — | fluoxetine 20 MG Oral Capsule [Prozac] | RxNorm 104849 | 19004895 | 34 | — |
| — | escitalopram 20 MG Oral Tablet [Lexapro] | RxNorm 352273 | 715966 | 33 | — |
| — | sertraline 100 MG Oral Tablet [Zoloft] | RxNorm 208149 | 19037642 | 26 | — |
| — | sertraline 50 MG Oral Tablet [Zoloft] | RxNorm 208161 | 19037684 | 25 | — |
| — | PMDD fluoxetine 20 MG Oral Tablet | RxNorm 2532163 | 740118 | 23 | — |
| — | sertraline 150 MG Oral Capsule | RxNorm 410584 | 19103473 | 22 | — |
| — | fluoxetine 4 MG/ML Oral Solution | RxNorm 310386 | 19077464 | 20 | — |
| — | escitalopram 1 MG/ML Oral Solution | RxNorm 351285 | 715964 | 19 | — |
| — | sertraline 20 MG/ML Oral Solution | RxNorm 861064 | 40165282 | 16 | — |
| — | 24 HR paroxetine hydrochloride 37.5 MG Extended Release Oral Tablet | RxNorm 1738807 | 35604761 | 15 | — |
| — | fluoxetine 10 MG Oral Capsule [Prozac] | RxNorm 205535 | 19029479 | 14 | — |
| — | PMDD fluoxetine 10 MG Oral Tablet | RxNorm 2532159 | 740117 | 12 | — |
| — | citalopram 40 MG Oral Tablet [Celexa] | RxNorm 213345 | 797620 | 12 | — |
| — | sertraline 25 MG Oral Tablet [Zoloft] | RxNorm 212233 | 739202 | 11 | — |
| — | citalopram 20 MG Oral Tablet [Celexa] | RxNorm 213344 | 797619 | 10 | — |
| — | citalopram 10 MG Oral Tablet [Celexa] | RxNorm 284591 | 797633 | 7 | — |
| — | sertraline 200 MG Oral Capsule | RxNorm 251201 | 19064370 | 7 | — |
| — | escitalopram 5 MG Oral Tablet [Lexapro] | RxNorm 404408 | 19102734 | 7 | — |
| — | fluoxetine 40 MG Oral Capsule [Prozac] | RxNorm 261287 | 755735 | 5 | — |
| — | paroxetine hydrochloride 20 MG Oral Tablet [Paxil] | RxNorm 207349 | 19035312 | 4 | — |
| — | citalopram 2 MG/ML Oral Solution | RxNorm 309313 | 19075393 | 4 | — |
| — | fluoxetine 25 MG / olanzapine 6 MG Oral Capsule | RxNorm 403969 | 19102552 | 4 | — |
| — | fluoxetine 90 MG Delayed Release Oral Capsule | RxNorm 313995 | 755741 | 3 | — |
| — | fluoxetine 25 MG / olanzapine 3 MG Oral Capsule | RxNorm 721787 | 755855 | 3 | — |
| — | citalopram 30 MG Oral Capsule | RxNorm 2591786 | 1759035 | 2 | — |
| — | paroxetine hydrochloride 30 MG Oral Tablet [Paxil] | RxNorm 207350 | 19035313 | 2 | — |
| — | paroxetine hydrochloride 40 MG Oral Tablet [Paxil] | RxNorm 211700 | 19046308 | 2 | — |
| — | paroxetine hydrochloride 10 MG Oral Tablet [Paxil] | RxNorm 211699 | 722064 | 1 | — |
| — | fluoxetine 50 MG / olanzapine 6 MG Oral Capsule | RxNorm 403972 | 19102555 | 1 | — |
| — | paroxetine mesylate 10 MG Oral Tablet [Pexeva] | RxNorm 541660 | 19113754 | 1 | — |
| — | 24 HR paroxetine hydrochloride 25 MG Extended Release Oral Tablet [Paxil] | RxNorm 1738806 | 35604760 | 1 | — |
| — | 24 HR paroxetine hydrochloride 37.5 MG Extended Release Oral Tablet [Paxil] | RxNorm 1738808 | 35604762 | 1 | — |
| — | paroxetine mesylate 7.5 MG Oral Capsule [Brisdelle] | RxNorm 1430128 | 43532895 | 1 | — |

#### Benzodiazepine (sedative) medicines · `benzodiazepine`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | alprazolam 0.5 MG Oral Tablet | RxNorm 308048 | 19072934 | 3,849 | — |
| — | diazepam 5 MG Oral Tablet | RxNorm 197591 | 723042 | 3,739 | — |
| — | alprazolam 0.25 MG Oral Tablet | RxNorm 308047 | 19072933 | 3,050 | — |
| — | lorazepam 0.5 MG Oral Tablet | RxNorm 197900 | 19019112 | 3,010 | — |
| — | lorazepam Injectable Solution [Ativan] | RxNorm 91878 | 40000859 | 2,999 | — |
| — | lorazepam 1 MG Oral Tablet | RxNorm 197901 | 19019113 | 2,212 | — |
| — | clonazepam 0.5 MG Oral Tablet | RxNorm 197527 | 798875 | 2,202 | — |
| — | diazepam 10 MG Oral Tablet | RxNorm 197589 | 723020 | 1,856 | — |
| — | alprazolam 1 MG Oral Tablet | RxNorm 197321 | 781062 | 1,288 | — |
| — | diazepam 5 MG/ML Injectable Solution [Valium] | RxNorm 200938 | 19024263 | 949 | — |
| — | clonazepam 1 MG Oral Tablet | RxNorm 197528 | 798876 | 841 | — |
| — | diazepam 2 MG Oral Tablet | RxNorm 197590 | 19018909 | 778 | — |
| — | lorazepam 2 MG Oral Tablet | RxNorm 197902 | 19019114 | 338 | — |
| — | temazepam 15 MG Oral Capsule | RxNorm 198241 | 836718 | 336 | — |
| — | alprazolam 2 MG Oral Tablet | RxNorm 197322 | 781063 | 192 | — |
| — | temazepam 30 MG Oral Capsule | RxNorm 198242 | 836719 | 178 | — |
| — | clonazepam 2 MG Oral Tablet | RxNorm 197529 | 798877 | 124 | — |
| — | clonazepam 0.25 MG Disintegrating Oral Tablet | RxNorm 349195 | 798914 | 120 | — |
| — | alprazolam 0.5 MG Oral Tablet [Xanax] | RxNorm 141928 | 781041 | 74 | — |
| — | 24 HR alprazolam 0.5 MG Extended Release Oral Tablet | RxNorm 433798 | 781126 | 69 | — |
| — | diazepam 5 MG Oral Tablet [Valium] | RxNorm 104700 | 19004471 | 66 | — |
| — | temazepam 7.5 MG Oral Capsule | RxNorm 198243 | 836720 | 63 | — |
| — | 24 HR alprazolam 1 MG Extended Release Oral Tablet | RxNorm 433800 | 19107912 | 62 | — |
| — | alprazolam 0.25 MG Oral Tablet [Xanax] | RxNorm 141927 | 781040 | 56 | — |
| — | clonazepam 0.5 MG Disintegrating Oral Tablet | RxNorm 349198 | 798917 | 56 | — |
| — | alprazolam 1 MG Oral Tablet [Xanax] | RxNorm 214003 | 19048247 | 41 | — |
| — | diazepam 10 MG Oral Tablet [Valium] | RxNorm 104701 | 19004472 | 40 | — |
| — | alprazolam 0.5 MG Disintegrating Oral Tablet | RxNorm 485415 | 781152 | 32 | — |
| — | lorazepam 1 MG Oral Tablet [Ativan] | RxNorm 104719 | 19004541 | 32 | — |
| — | clonazepam 0.5 MG Oral Tablet [Klonopin] | RxNorm 206157 | 19031562 | 32 | — |
| — | lorazepam 0.5 MG Oral Tablet [Ativan] | RxNorm 206821 | 19033566 | 31 | — |
| — | alprazolam 0.25 MG Disintegrating Oral Tablet | RxNorm 485413 | 781130 | 24 | — |
| — | clonazepam 0.125 MG Disintegrating Oral Tablet | RxNorm 349194 | 798913 | 21 | — |
| — | clonazepam 1 MG Disintegrating Oral Tablet | RxNorm 349196 | 798915 | 20 | — |
| — | clonazepam 1 MG Oral Tablet [Klonopin] | RxNorm 206159 | 19031564 | 18 | — |
| — | 24 HR alprazolam 2 MG Extended Release Oral Tablet | RxNorm 433799 | 781127 | 16 | — |
| — | alprazolam 2 MG Oral Tablet [Xanax] | RxNorm 214004 | 19048248 | 15 | — |
| — | 2 ML diazepam 5 MG/ML Auto-Injector | RxNorm 1807452 | 40221326 | 14 | — |
| — | alprazolam 1 MG Disintegrating Oral Tablet | RxNorm 485414 | 781131 | 10 | — |
| — | temazepam 22.5 MG Oral Capsule | RxNorm 485489 | 836739 | 10 | — |
| — | diazepam 2 MG Oral Tablet [Valium] | RxNorm 104699 | 19004330 | 10 | — |
| — | lorazepam 2 MG Oral Tablet [Ativan] | RxNorm 206828 | 19033603 | 9 | — |
| — | clonazepam 2 MG Disintegrating Oral Tablet | RxNorm 349197 | 798916 | 8 | — |
| — | clonazepam 2 MG Oral Tablet [Klonopin] | RxNorm 206160 | 19031565 | 6 | — |
| — | 2 ML diazepam 5 MG/ML Rectal Gel | RxNorm 801961 | 19131441 | 5 | — |
| — | temazepam 30 MG Oral Capsule [Restoril] | RxNorm 208465 | 19038579 | 4 | — |
| — | diazepam 1 MG/ML Oral Solution | RxNorm 309843 | 19076372 | 3 | — |
| — | diazepam | RxNorm 3322 | 723013 | 2 | — |
| — | 24 HR alprazolam 3 MG Extended Release Oral Tablet | RxNorm 433801 | 19107913 | 2 | — |
| — | {2 (0.1 ML) (diazepam 100 MG/ML Nasal Spray [Valtoco]) } Pack [Valtoco 20 MG Dose Kit] | RxNorm 2272624 | 37499636 | 2 | — |
| — | 2 ML diazepam 5 MG/ML Cartridge | RxNorm 1807459 | 40221329 | 2 | — |
| — | 24 HR lorazepam 1 MG Extended Release Oral Capsule [Loreev] | RxNorm 2569571 | 702603 | 1 | — |
| — | 24 HR lorazepam 2 MG Extended Release Oral Capsule [Loreev] | RxNorm 2569575 | 702605 | 1 | — |
| — | 24 HR lorazepam 1.5 MG Extended Release Oral Capsule [Loreev] | RxNorm 2594603 | 780210 | 1 | — |
| — | alprazolam 2 MG Disintegrating Oral Tablet | RxNorm 485416 | 781153 | 1 | — |
| — | lorazepam 2 MG/ML Oral Solution | RxNorm 311376 | 792000 | 1 | — |
| — | temazepam 7.5 MG Oral Capsule [Restoril] | RxNorm 208463 | 19038577 | 1 | — |
| — | temazepam 15 MG Oral Capsule [Restoril] | RxNorm 208464 | 19038578 | 1 | — |
| — | 24 HR alprazolam 1 MG Extended Release Oral Tablet [Xanax] | RxNorm 687024 | 19125456 | 1 | — |
| — | 4 ML diazepam 5 MG/ML Rectal Gel | RxNorm 801966 | 19131446 | 1 | — |
| — | {1 (0.1 ML) (diazepam 100 MG/ML Nasal Spray [Valtoco]) } Pack [Valtoco 10 MG Dose Kit] | RxNorm 2272622 | 37499634 | 1 | — |
| — | {1 (0.1 ML) (diazepam 50 MG/ML Nasal Spray [Valtoco]) } Pack [Valtoco 5 MG Dose Kit] | RxNorm 2272630 | 37499638 | 1 | — |
| — | 1 ML lorazepam 2 MG/ML Injection | RxNorm 1665188 | 46287372 | 1 | — |

#### Psychiatric evaluation or psychotherapy visit · `psych_eval_therapy`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Psychiatric diagnostic evaluation | CPT4 90791 | 43527984 | 15,695 | — |
| — | Psychotherapy, 60 minutes with patient | CPT4 90837 | 43527905 | 13,907 | — |
| — | Psychotherapy, 45 minutes with patient | CPT4 90834 | 43527904 | 7,728 | — |
| — | Psychiatric diagnostic evaluation with medical services | CPT4 90792 | 43527985 | 5,513 | — |
| — | Psychotherapy, 30 minutes with patient when performed with an evaluation and management service (List separately in addition to the code for primary procedure) | CPT4 90833 | 43527987 | 4,686 | — |
| — | Psychotherapy, 30 minutes with patient | CPT4 90832 | 43527986 | 3,636 | — |
| — | Family psychotherapy (conjoint psychotherapy) (with patient present), 50 minutes | CPT4 90847 | 2213546 | 1,833 | — |
| — | Psychotherapy, 45 minutes with patient when performed with an evaluation and management service (List separately in addition to the code for primary procedure) | CPT4 90836 | 43527988 | 1,327 | — |
| — | Group psychotherapy (other than of a multiple-family group) | CPT4 90853 | 2213548 | 746 | — |
| — | Psychotherapy, 60 minutes with patient when performed with an evaluation and management service (List separately in addition to the code for primary procedure) | CPT4 90838 | 43527989 | 424 | — |
| — | Psychotherapy for crisis; first 60 minutes | CPT4 90839 | 43527990 | 355 | — |
| — | Family psychotherapy (without the patient present), 50 minutes | CPT4 90846 | 2213545 | 330 | — |
| — | Initial psychiatric collaborative care management, first 70 minutes in the first calendar month of behavioral health care manager activities, in consultation with a psychiatric consultant, and directed by the treating physician or other qualified healt... | CPT4 99492 | 725122 | 259 | — |
| — | Subsequent psychiatric collaborative care management, first 60 minutes in a subsequent month of behavioral health care manager activities, in consultation with a psychiatric consultant, and directed by the treating physician or other qualified health c... | CPT4 99493 | 725123 | 190 | — |
| — | Initial or subsequent psychiatric collaborative care management, each additional 30 minutes in a calendar month of behavioral health care manager activities, in consultation with a psychiatric consultant, and directed by the treating physician or other... | CPT4 99494 | 725124 | 166 | — |

#### Brief mental-health screening · `psych_screen`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Brief emotional/behavioral assessment (eg, depression inventory, attention-deficit/hyperactivity disorder [ADHD] scale), with scoring and documentation, per standardized instrument | CPT4 96127 | 46257498 | 19,572 | — |

#### Emergency department visit (ED) · `ed_visit`

| Plain detail | Verbatim OMOP concept name | Code | OMOP ID | Patients | Also in |
| :---- | :---- | :---- | ----: | ----: | :---- |
| — | Emergency Room and Inpatient Visit | Visit ERIP | 262 | 0 | — |

### B. Combined lists (umbrellas)

#### Any heart stress test (combined list) · `stress_test`

19 codes, all of them listed under: `stress_ecg`, `stress_echo`, `stress_spect`, `stress_pet`.

#### Any coronary artery disease or heart attack diagnosis (combined list) (CAD) · `cad`

20 codes, all of them listed under: `acs_mi`, `old_mi`, `angina_stable`, `cad_chronic`.

<!-- ANNEX:END -->
