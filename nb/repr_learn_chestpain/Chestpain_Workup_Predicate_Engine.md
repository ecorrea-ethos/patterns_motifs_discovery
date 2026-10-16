# Chest Pain Work-up Predicate Engine

*Working Draft — October 2026*

> **Superseded by `Chestpain_Workup_Predicate_Engine_v2.md`** (NMF k=8 on the validated AHA/ACC code lists, care pattern c3, plain-English Annex A and B). This k=5 version (care pattern c0) is kept for comparison and is not updated.

---

## Overview

This document describes the design of the chest pain predicate engine for life underwriting. The engine separates chest pain that sits in the acute / ED cardiac work-up pathway (bundle c0 of the chest pain NMF run) from chest pain that other care explains (bundles c1 to c4). The comparison is one versus all: c0 against the four other bundles. Today every `dx_9487` (atypical chest pain) case routes to manual review at RUW; this rule is a candidate for narrowing that routing, and it is not yet validated for it.

The predicates are built on OMOP entities. Each entity is identified by its OMOP concept (verbatim name, vocabulary, code, `concept_id`). The entity registry below is the single place that fixes the names. The first sections contain no underwriting logic. They are intended for clinical and medical review to validate that the definitions agree with the care that the bundle describes. The flag rule has its own section.

Source of the entities and sequences: chest pain cohort of 139,416 patients (`sql/chest_pain_cohort.sql`, any of the five R07.x codes), NMF k=5 on concept-level tokens (`nmf_k5_chestpain_full`), PrefixSpan motifs per bundle, and the PubMed check of the final table (`final_table_chestpain_k5_full_literature_verified.csv`).

---

## Entity registry

An entity is a concept, not an ingredient. A predicate is true only for the concept listed. Concept names are verbatim from the OMOP `concept` table of the extract.

| Predicate key | Verbatim OMOP concept name | Class / domain | Vocabulary code | `concept_id` |
| :---- | :---- | :---- | :---- | ----: |
| `chest_pain` | Chest pain. The predicate matches every concept of the codeset `chest_pain` (SNOMED concepts whose name matches "chest pain", "precordial pain" or "intercostal space"), this is the concept the sequences show. | Clinical Finding / Condition | SNOMED 29857009 | 77670 |
| `ecg_tracing` | Electrocardiogram, routine ECG with at least 12 leads; tracing only, without interpretation and report | CPT4 / Procedure | CPT4 93005 | 2313815 |
| `ecg_interpretation` | Electrocardiogram, routine ECG with at least 12 leads; interpretation and report only | CPT4 / Procedure | CPT4 93010 | 2313816 |
| `troponin` | Troponin, quantitative | CPT4 / Measurement | CPT4 84484 | 2212605 |
| `cxr` | Radiologic examination, chest; single view | CPT4 / Procedure | CPT4 71045 | 725068 |
| `iv_push` | Therapeutic, prophylactic, or diagnostic injection (specify substance or drug); intravenous push, single or initial substance/drug | CPT4 / Procedure | CPT4 96374 | 2314215 |

Three precision points:

* **The chest pain predicate is wider than one concept.** The anchor `first_chest_pain_date` is the earliest event of any concept in the codeset `chest_pain` (`nb/repr_learn_chestpain/codesets.yaml`). The sequences were mined on the concept 77670, which is the concept the three sequences name.
* **One ECG is two billing lines.** CPT4 93005 (tracing) and 93010 (interpretation) are the two halves of one test. The five top loadings of c0 are therefore four clinical entities: ECG, troponin, chest X-ray and IV push. The entity count below counts the ECG once. The sequences keep the two lines apart because the mined patterns name them apart.
* **IV push is not specific to chest pain.** CPT4 96374 marks any IV injection in an ED, a clinic or a procedure. It is the same concept as in the letrozole registry. It is kept because it is the fifth top loading of c0.

---

## Predicates and Composites

### Atomic Predicates

A predicate answers one question about the event history of an applicant. It returns true or false. Atomic predicates check directly against raw event attributes: the OMOP concept and the event date.

**Chest pain present.** The applicant has at least one chest pain event. The predicate defines the scope of the engine and the anchor date. Chest pain is nonspecific, so presence alone does not identify the care pathway.

`chest_pain_present = concept IS IN codeset(chest_pain)`

`first_chest_pain_date = MIN(event_date) over chest pain events`

**Work-up entity present.** Four entities are the highest-loading concepts of bundle c0 (acute / ED cardiac work-up). Each one answers: has the applicant ever had this entity?

`ecg_present = concept IS Electrocardiogram ... tracing only [CPT4 93005] OR concept IS Electrocardiogram ... interpretation and report only [CPT4 93010]`

`troponin_present = concept IS Troponin, quantitative [CPT4 84484]`

`cxr_present = concept IS Radiologic examination, chest; single view [CPT4 71045]`

`iv_push_present = concept IS Therapeutic, prophylactic, or diagnostic injection ... intravenous push, single or initial substance/drug [CPT4 96374]`

**Work-up entity in window.** The applicant has an event of the entity within 1 day, before or after, of a chest pain event. The window is `workup_window_days = 1`.

`<entity>_in_window = <entity>_present AND EXISTS chest pain event date d, entity event date e with |e - d| <= workup_window_days`

The window replaces the letrozole rule "first seen 74 or more days after the anchor". The reason is that c0 is a same-day bundle. For all five entities the bundle median first occurrence is the same day as the first chest pain, and 23%, 19%, 27%, 24% and 32% of the patients who have each entity had it before the first chest pain (ECG tracing, troponin, ECG interpretation, chest X-ray, IV push). A one-sided "late" threshold would remove the care the bundle describes. The window is symmetric because an ED ECG can be dated the day before the claim that carries the chest pain code. The rule uses any occurrence in the window, not the first occurrence ever, so an ECG at an earlier physical does not hide an ECG in the ED. A window of 1 day is a draft value, it is not calibrated (see the evaluation protocol).

---

### Composites

A composite combines atomic predicates, or other composites, into a named clinical pattern.

#### Work-up entity bundle

**Work-up entity count.** The number of the four entities that the applicant had within the window of a chest pain event.

`workup_entity_count = ecg_in_window + troponin_in_window + cxr_in_window + iv_push_in_window`

**Work-up bundle.** Three or more of the four entities, each in the window.

`composite_workup_bundle = workup_entity_count >= 3`

#### Work-up sequences

An ordered sequence is a subsequence of the applicant's event list: the steps appear in this order and need not be adjacent. Every sequence starts at a chest pain event, and its last step falls no later than `workup_window_days` after that chest pain event.

**Chest pain, chest X-ray, troponin.**

`composite_seq_cxr_trop = chest_pain -> cxr -> troponin`

**Chest pain, ECG tracing, troponin.**

`composite_seq_ecg_tracing_trop = chest_pain -> ecg_tracing -> troponin`

**Chest pain, ECG interpretation, troponin.**

`composite_seq_ecg_interp_trop = chest_pain -> ecg_interpretation -> troponin`

**Work-up sequence.** At least one of the three sequences.

`composite_workup_sequence = composite_seq_cxr_trop OR composite_seq_ecg_tracing_trop OR composite_seq_ecg_interp_trop`

#### Same-day order

Claims carry a date, not a time. When two steps fall on the same day, the order is a tie-break from `DOMAIN_ORDER` (condition, procedure, measurement, drug). A same-day chest pain therefore sorts before a same-day ECG or chest X-ray, and these sort before a same-day troponin. The three sequences were mined with this rule (`tie_ordered`). A same-day troponin followed by a chest X-ray does not match, while a same-day chest pain, ECG and troponin do.

This matters more here than for letrozole. c0 is a same-day bundle (final verdict *Suggestive*, not *Solid*): with every step required on a strictly later day, the support of the patterns falls below half of its table value. For c0 the order inside the sequences is mostly the tie-break, not an order shown by dates. Read the sequences as "chest pain, an ECG or chest X-ray, and a troponin in one episode". The evaluation reports the strict-date match next to the `tie_ordered` match, so the share of applicants whose "order" is only a tie-break is visible.

#### Ablation composites

These two composites are not part of the flag. They show what each half of the rule contributes.

`composite_workup_bundle_only = chest_pain_present AND composite_workup_bundle`

`composite_workup_sequence_only = chest_pain_present AND composite_workup_sequence`

---

## Flag rule (draft, underwriting logic)

An applicant with chest pain is flagged **Manual RUW (c0 pattern)** when all three conditions are true. The flag marks an applicant whose chest pain sits in an acute / ED cardiac work-up. It does not diagnose heart disease, and a normal troponin and ECG also meet it, because the predicates test that the tests were done, not their results.

`composite_c0_manual_ruw = chest_pain_present AND composite_workup_bundle AND composite_workup_sequence`

In words: the applicant has at least three of the four work-up entities (ECG, troponin, chest X-ray, IV push), each within 1 day of a chest pain event, and the applicant has at least one of the three chest pain, test, troponin sequences completed within 1 day of the chest pain event.

### How the flag is decided

For the underwriting review: three questions, top to bottom. The first "No" ends the check and the applicant is routine for this rule.

1. Does the applicant have a chest pain event? If no, the rule does not apply.
2. Did the applicant have at least 3 of the 4 work-up entities within 1 day of a chest pain event? If no, routine for this rule.
3. Did the applicant have chest pain, then a chest X-ray or an ECG, then a troponin, all within 1 day of the chest pain event? If no, routine for this rule.

All three "Yes" gives **Manual RUW (c0 pattern)**. The checks run in this order; the first check that fails sends the applicant to *not flagged*.

![Decision flow of the chest pain c0 flag, underwriter version](chestpain_c0_flag_flow.png)

### Underwriter checklist

Tick every line that applies. The flag is **Manual RUW (c0 pattern)** only when sections 1, 2 and 3 are all met. Dates are counted from a chest pain event.

**1. Chest pain**

| ☐ | Check |
| :---: | :---- |
| ☐ | The applicant has at least one chest pain event (Chest pain [SNOMED 29857009] or any other concept of the codeset `chest_pain`) |

**2. At least 3 of the 4 services, each within 1 day of a chest pain event**

| ☐ | Service (verbatim OMOP concept) | Code | Seen within 1 day of chest pain? |
| :---: | :---- | :---- | :---: |
| ☐ | Electrocardiogram, routine ECG with at least 12 leads; tracing only, without interpretation and report **or** interpretation and report only | CPT4 93005 or 93010 | ☐ |
| ☐ | Troponin, quantitative | CPT4 84484 | ☐ |
| ☐ | Radiologic examination, chest; single view | CPT4 71045 | ☐ |
| ☐ | Therapeutic, prophylactic, or diagnostic injection (specify substance or drug); intravenous push, single or initial substance/drug | CPT4 96374 | ☐ |

Section 2 is met when 3 or more of the last-column boxes are ticked. A service seen more than 1 day from every chest pain event does not count.

**3. At least 1 work-up sequence after a chest pain event** (in this order; other events may sit in between; last step within 1 day of the chest pain event)

| ☐ | Sequence |
| :---: | :---- |
| ☐ | A: Chest pain [SNOMED 29857009] → Radiologic examination, chest; single view [CPT4 71045] → Troponin, quantitative [CPT4 84484] |
| ☐ | B: Chest pain [SNOMED 29857009] → Electrocardiogram, routine ECG with at least 12 leads; tracing only [CPT4 93005] → Troponin, quantitative [CPT4 84484] |
| ☐ | C: Chest pain [SNOMED 29857009] → Electrocardiogram, routine ECG with at least 12 leads; interpretation and report only [CPT4 93010] → Troponin, quantitative [CPT4 84484] |

**Result:** sections 1, 2 and 3 all met → **Manual RUW (c0 pattern)**. Anything else → routine for this rule. The flag marks a care pattern, not a diagnosis.

### What the flag is compared against

One versus all. The flag targets c0. Every other bundle is a comparison group, grouped as the notebook groups them. Names and sizes are the saved names of the k=5 run (`nmf_k5_chestpain_full_components.json`); patients are counted in the bundle of their dominant NMF component.

| Group | Bundle | Name | Patients | % of cohort | Draft triage |
| :---- | :---- | :---- | ----: | ----: | :---- |
| **Target** | c0 | acute / ED cardiac workup (ECG, troponin, radiology, injectables, basic labs) | 25,953 | 18.6% | manual UW review (troponin result, ECG, imaging, outcome of the work-up) |
| Cardiac work-up (comparison) | c2 | outpatient cardiometabolic / preventive check-up (lipids, HbA1c, ECG, hypertension, general exam) | 54,581 | 39.1% | routine (preventive care around chest pain) |
| Background | c1 | women's health and genitourinary (gyn exam, cytology, pregnancy test, infectious-agent / urine tests) | 17,669 | 12.7% | routine (care unrelated to the chest pain) |
| Background | c4 | musculoskeletal / physical therapy (PT, chiropractic, low back, neck, shoulder pain) | 14,501 | 10.4% | routine (non-cardiac explanation) |
| Background | | *subtotal* | 32,170 | 23.1% | |
| Drug domain | c3 | acute-illness prescriptions (steroids, antibiotics, NSAIDs, muscle relaxant) | 26,712 | 19.2% | unclear (bundle does not show the clinical context; use other evidence) |

The triage text is a draft inference and needs review by an underwriter. The c2 bundle is the closest competitor: it also holds ECGs, so an applicant with a routine ECG at a check-up is the case the window and the troponin step are meant to separate.

---

## Evaluation protocol

*Defined here, not run. No coverage number below is measured.*

The flag is scored one versus all against the c0 label (`labels` and `pids` of `nmf_k5_chestpain_full.npz`):

* the confusion table, precision, recall, specificity and lift over the 18.6% base rate;
* the same table for each other bundle separately (c1 to c4), then pooled by group (cardiac work-up, background, drug domain);
* the two ablation composites, and the `tie_ordered` against strict-date match of the sequences, each with and without the 1-day span;
* the calibration of the window: for the patients of c0, the share with each entity within 0, 1, 3 and 7 days of a chest pain event. `workup_window_days = 1` stays a draft value until this table is read.

Limits to read the result with:

* **The comparison is circular by construction.** c0 is the NMF assignment, and the four entities are the top loadings of c0. High recall measures how well the rule restates the bundle. It does not validate the rule clinically.
* **External check without the NMF.** The forward outcome `cardiac_workup_outcome()` (stress test, coronary angiography or coronary artery disease diagnosis after the chest pain index date) is independent of the bundle. Report the flag against it with troponin removed from the outcome, because troponin is part of the rule. That outcome partly measures reviewer and clinician behaviour, not true cardiac risk.
* **The rule tests that care happened, not what it found.** Nothing in the predicates reads a troponin value or an ECG result. A normal work-up and an abnormal one both meet the flag. Results are the natural next layer for clinical review.
* **False positives from other acute care.** ECG, chest X-ray and IV push also mark an ED visit for any complaint, for example a respiratory infection or an injury. A candidate refinement for clinical review is to require troponin in the bundle. It is not part of the rule.
* **Only 3 of 4 entities are needed.** An applicant can meet the bundle without a troponin and then needs one for the sequence. Whether the bundle should require troponin is a question for clinical review.
* **Bundle statistics are not applicant statistics.** The window comes from bundle medians (same day). The rule applies it to each applicant's own dates.
* **Literature support is partial.** The PubMed check found titles that fit chest pain evaluation with ECG and troponin (rated *Partly* for the three sequences) and no paper that tests their order. See the references.

---

## Population Coverage

Not measured yet. The table lists what is known at the bundle level, from the k=5 run and the PubMed check of the final table.

| Quantity | Value |
| :---- | :---- |
| Cohort | 139,416 patients (any of the five R07.x chest pain codes) |
| Bundle c0 | 25,953 patients, 18.6% |
| ECG tracing (CPT4 93005) in c0 | 77%, median same day as first chest pain |
| Troponin, quantitative (CPT4 84484) in c0 | 77%, median same day |
| ECG interpretation (CPT4 93010) in c0 | 77%, median same day |
| Chest X-ray (CPT4 71045) in c0 | 66%, median same day |
| Intravenous push injection (CPT4 96374) in c0 | 55%, median same day |

| Pattern of c0 | Share of c0 | Share of the other bundles | Times as common |
| :---- | ----: | ----: | ----: |
| Chest pain → chest X-ray → troponin | 48.1% | 15.9% | 2.9 |
| Chest pain → ECG tracing → troponin | 64.4% | 24.6% | 2.6 |
| Chest pain → ECG interpretation → troponin | 52.0% | 19.7% | 2.6 |

Shares are those of the final table (any time order, no 1-day span). All three patterns passed the held-out check (40 splits). The verdict is *Suggestive*, not *Solid*, because c0 is a same-day bundle.

| Predicate or composite | Policies | % cohort |
| :---- | ----: | ----: |
| `chest_pain_present` | not measured | |
| `composite_workup_bundle` (`workup_entity_count >= 3`) | not measured | |
| `composite_workup_sequence` | not measured | |
| `composite_c0_manual_ruw` | not measured | |

---

## References

* Final table of the chest pain k=5 run with literature search: `nb/repr_learn_chestpain/final_table_chestpain_k5_full.xlsx` and `final_table_chestpain_k5_full_literature_verified.csv`.
* Source of the three sequences: final table section of the fused notebook (`nb/repr_learn_chestpain/Chestpain_NMF_PrefixSpan_full.ipynb`, section 5).
* Entities and concept ids: `nmf_k5_chestpain_full_components.json` and `token_map_chestpain_concept.csv`.
* Matching semantics (`tie_ordered`, `strict_date`, `windowed`): `nb/repr_learn_letrozole/motif_robustness/seqindex.py`.
* Forward outcome: `cardiac_workup_outcome()` in `nb/repr_learn_chestpain/ethos_omop.py`.
* Format and voice: `Letrozole_Rx_Predicate_Engine.md`.
