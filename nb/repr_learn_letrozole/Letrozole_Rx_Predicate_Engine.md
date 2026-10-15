# Letrozole Rx Predicate Engine

*Working Draft — October 2026*

---

## Overview

This document describes the design of the letrozole predicate engine for life underwriting. The engine separates letrozole use that sits in the peri-operative / oncology pathway (bundle c5 of the letrozole NMF run) from letrozole use that fertility care or background care explains (bundles c0 to c4 and c6). The comparison is one versus all: c5 against the six other bundles.

The predicates are built on OMOP entities. Each entity is identified by its OMOP concept (verbatim name, vocabulary, code, `concept_id`). The entity registry below is the single place that fixes the names. The first sections contain no underwriting logic. They are intended for clinical and medical review to validate that the definitions agree with the care that the bundle describes. The flag rule has its own section.

Source of the entities and sequences: letrozole cohort of 5,238 patients (`sql/letrozole_cohort.sql`, female-only v0.5), NMF k=7 on concept-level tokens (`nmf_k7_letrozole_full`), PrefixSpan motifs per bundle, and the PubMed check of the final table (`final_table_letrozole_k7_full_literature_verified.csv`).

---

## Entity registry

An entity is a concept, not an ingredient. A predicate is true only for the concept listed. Concept names are verbatim from the OMOP `concept` table of the extract.

| Predicate key | Verbatim OMOP concept name | Class / domain | Vocabulary code | `concept_id` |
| :---- | :---- | :---- | :---- | ----: |
| `letrozole` | letrozole 2.5 MG Oral Tablet. The predicate matches every concept of the codeset `letrozole` (all strengths and brands), this is the concept the sequences show. | Clinical Drug / Drug | RxNorm 200064 | 19022830 |
| `ondansetron_inj` | ondansetron Injection | Clinical Drug Form / Drug | RxNorm 1740463 | 35605480 |
| `ketorolac_inj` | ketorolac Injectable Solution [Toradol] | Branded Drug Form / Drug | RxNorm 363077 | 40048832 |
| `dexamethasone_inj` | dexamethasone Injection | Clinical Drug Form / Drug | RxNorm 1812073 | 1719010 |
| `iv_push` | Therapeutic, prophylactic, or diagnostic injection (specify substance or drug); intravenous push, single or initial substance/drug | CPT4 / Procedure | CPT4 96374 | 2314215 |
| `bmp` | Basic metabolic panel (Calcium, total) This panel must include the following: Calcium, total (82310) Carbon dioxide (bicarbonate) (82374) Chloride (82435) Creatinine (82565) Glucose (82947) Potassium (84132) Sodium (84295) Urea nitrogen (BUN) (84520) | CPT4 / Measurement | CPT4 80048 | 2212090 |
| `cbc` | Complete blood count with white cell differential, automated | Procedure / Measurement | SNOMED 9564003 | 4319466 |
| `cmp` | Comprehensive metabolic panel | Procedure / Measurement | SNOMED 371361000119107 | 3661905 |
| `venipuncture` | Venipuncture for blood test | Procedure / Procedure | SNOMED 28520004 | 4102442 |

Two precision points:

* **The ketorolac entity is the branded form.** The concept is `ketorolac Injectable Solution [Toradol]`. Other ketorolac injection concepts do not match unless clinical review adds them to the registry.
* **The letrozole predicate is wider than one concept.** The anchor `first_letrozole_date` is the earliest event of any concept in the codeset `letrozole` (`nb/repr_learn_letrozole/codesets.yaml`). The sequences were mined on the tablet concept 19022830, which is the concept the three sequences name.

---

## Predicates and Composites

### Atomic Predicates

A predicate answers one question about the event history of an applicant. It returns true or false. Atomic predicates check directly against raw event attributes: the OMOP concept and the event date.

**Letrozole present.** The applicant has at least one letrozole fill. The predicate defines the scope of the engine and the anchor date. Letrozole has fertility indications used off-label and an oncology indication, so presence alone does not identify the pathway.

`letrozole_present = concept IS IN codeset(letrozole)`

`first_letrozole_date = MIN(event_date) over letrozole events`

**Peri-operative entity present.** Five entities are the five highest-loading concepts of bundle c5 (peri-operative / oncology). Each one answers: has the applicant ever had this entity?

`ondansetron_inj_present = concept IS ondansetron Injection [RxNorm 1740463]`

`ketorolac_inj_present = concept IS ketorolac Injectable Solution [Toradol] [RxNorm 363077]`

`dexamethasone_inj_present = concept IS dexamethasone Injection [RxNorm 1812073]`

`iv_push_present = concept IS Therapeutic, prophylactic, or diagnostic injection ... intravenous push, single or initial substance/drug [CPT4 96374]`

`bmp_present = concept IS Basic metabolic panel (Calcium, total) ... [CPT4 80048]`

**Peri-operative entity late.** The applicant has the entity and its first occurrence is 74 days or more after the first letrozole fill. The threshold is the median offset of ketorolac and of the basic metabolic panel in c5. An entity seen earlier than that does not count, which removes care that precedes letrozole by weeks and cannot be follow-up care for it.

`<entity>_ge74d = <entity>_present AND (first_<entity>_date - first_letrozole_date) >= 74 days`

For c5 the median first occurrence is +100 d (ondansetron), +74 d (ketorolac), +156 d (dexamethasone), +178 d (IV push) and +74 d (BMP). 46%, 48%, 43%, 42% and 48% of the c5 patients who have each entity had it before the first letrozole fill.

**Blood-work step present.** Three entities form the monitoring sequences.

`cbc_present = concept IS Complete blood count with white cell differential, automated [SNOMED 9564003]`

`cmp_present = concept IS Comprehensive metabolic panel [SNOMED 371361000119107]`

`venipuncture_present = concept IS Venipuncture for blood test [SNOMED 28520004]`

---

### Composites

A composite combines atomic predicates, or other composites, into a named clinical pattern.

#### Peri-operative entity bundle

**Peri-operative entity count.** The number of the five entities that the applicant had 74 days or more after the first letrozole fill.

`periop_entity_count = ondansetron_inj_ge74d + ketorolac_inj_ge74d + dexamethasone_inj_ge74d + iv_push_ge74d + bmp_ge74d`

**Peri-operative bundle.** Three or more of the five entities, each late.

`composite_periop_bundle = periop_entity_count >= 3`

#### Monitoring sequences

An ordered sequence is a subsequence of the applicant's event list: the steps appear in this order and need not be adjacent. Every sequence starts at a letrozole fill.

**Letrozole, CBC, CMP.**

`composite_seq_cbc_cmp = letrozole -> cbc -> cmp`

**Letrozole, CMP, CBC.**

`composite_seq_cmp_cbc = letrozole -> cmp -> cbc`

**Letrozole, venipuncture, CMP, CBC.**

`composite_seq_venip_cmp_cbc = letrozole -> venipuncture -> cmp -> cbc`

**Monitoring sequence.** At least one of the three sequences.

`composite_monitoring_sequence = composite_seq_cbc_cmp OR composite_seq_cmp_cbc OR composite_seq_venip_cmp_cbc`

#### Same-day order

Claims carry a date, not a time. When two steps fall on the same day, the order is a tie-break from `DOMAIN_ORDER` (condition, procedure, measurement, drug). A same-day measurement therefore sorts before a same-day drug. The three sequences were mined with this rule (`tie_ordered`). A same-day letrozole fill followed by a CBC on the same day does not match, while a same-day venipuncture, CMP and CBC after an earlier letrozole fill do. The evaluation reports the strict-date match (every step on a strictly later day) next to the `tie_ordered` match, so the share of applicants whose "order" is only a tie-break is visible.

#### Ablation composites

These two composites are not part of the flag. They show what each half of the rule contributes.

`composite_periop_bundle_only = letrozole_present AND composite_periop_bundle`

`composite_monitoring_sequence_only = letrozole_present AND composite_monitoring_sequence`

---

## Flag rule (draft, underwriting logic)

An applicant who has received letrozole is flagged **Manual RUW (c5 pattern)** when all three conditions are true. The flag marks an applicant whose letrozole use looks like the peri-operative / oncology pathway. It does not diagnose cancer.

`composite_c5_manual_ruw = letrozole_present AND composite_periop_bundle AND composite_monitoring_sequence`

In words: the applicant has at least three of the five peri-operative entities, each first seen 74 days or more after the first letrozole fill, and the applicant has at least one of the three blood-work sequences after a letrozole fill.

### How the flag is decided

For the underwriting review: three questions, top to bottom. The first "No" ends the check and the applicant is routine for this rule.

![Decision flow of the letrozole c5 flag, underwriter version](letrozole_c5_flag_flow.png)

A technical version with the predicate names, bundle shares and `concept_id`s is in [letrozole_c5_flag_flow_technical.png](letrozole_c5_flag_flow_technical.png). The checks run in the same order in both: the first check that fails sends the applicant to *not flagged*.

### Underwriter checklist

Tick every line that applies. The flag is **Manual RUW (c5 pattern)** only when sections 1, 2 and 3 are all met. Dates are counted from the first letrozole fill.

**1. Letrozole**

| ☐ | Check |
| :---: | :---- |
| ☐ | The applicant has at least one letrozole fill (letrozole 2.5 MG Oral Tablet [RxNorm 200064] or any other letrozole product) |

**2. At least 3 of the 5 services, each first seen 74 or more days after the first letrozole fill**

| ☐ | Service (verbatim OMOP concept) | Code | Seen 74+ days after first fill? |
| :---: | :---- | :---- | :---: |
| ☐ | ondansetron Injection | RxNorm 1740463 | ☐ |
| ☐ | ketorolac Injectable Solution [Toradol] | RxNorm 363077 | ☐ |
| ☐ | dexamethasone Injection | RxNorm 1812073 | ☐ |
| ☐ | Therapeutic, prophylactic, or diagnostic injection (specify substance or drug); intravenous push, single or initial substance/drug | CPT4 96374 | ☐ |
| ☐ | Basic metabolic panel (Calcium, total) This panel must include the following: … | CPT4 80048 | ☐ |

Section 2 is met when 3 or more of the last-column boxes are ticked. A service first seen before day 74 does not count.

**3. At least 1 blood-work sequence after a letrozole fill** (in this order; other events may sit in between)

| ☐ | Sequence |
| :---: | :---- |
| ☐ | A: letrozole → Complete blood count with white cell differential, automated [SNOMED 9564003] → Comprehensive metabolic panel [SNOMED 371361000119107] |
| ☐ | B: letrozole → Comprehensive metabolic panel [SNOMED 371361000119107] → Complete blood count with white cell differential, automated [SNOMED 9564003] |
| ☐ | C: letrozole → Venipuncture for blood test [SNOMED 28520004] → Comprehensive metabolic panel [SNOMED 371361000119107] → Complete blood count with white cell differential, automated [SNOMED 9564003] |

**Result:** sections 1, 2 and 3 all met → **Manual RUW (c5 pattern)**. Anything else → routine for this rule. The flag marks a care pattern, not a diagnosis.

### What the flag is compared against

One versus all. The flag targets c5. Every other bundle is a comparison group, grouped as the notebook groups them. Names and sizes are the saved names of the k=7 run (`nmf_k7_letrozole_full_components.json`); patients are counted in the bundle of their dominant NMF component.

| Group | Bundle | Name | Patients | % of cohort | Draft triage |
| :---- | :---- | :---- | ----: | ----: | :---- |
| **Target** | c5 | peri-operative / oncology (breast_cancer loads here) | 486 | 9.3% | manual UW review (stage, treatment status, adjuvant letrozole) |
| Fertility | c2 | fertility treatment and work-up | 637 | 12.2% | routine (letrozole explained by fertility) |
| Fertility | c3 | pregnancy and prenatal care | 858 | 16.4% | routine (letrozole explained by fertility) |
| Fertility | c4 | preconception carrier screening | 273 | 5.2% | routine (letrozole explained by fertility) |
| Fertility | | *subtotal* | 1,768 | 33.8% | |
| Background | c0 | preventive and fertility work-up labs | 775 | 14.8% | routine, indication unclear (use other evidence) |
| Background | c1 | acute-infection and symptomatic pharmacy | 1,768 | 33.8% | routine, indication unclear (use other evidence) |
| Background | c6 | physical therapy / manual and chiropractic care | 441 | 8.4% | routine, indication unclear (use other evidence) |
| Background | | *subtotal* | 2,984 | 57.0% | |

The triage text is a draft inference and needs review by an underwriter.

---

## Evaluation protocol

*Defined here, not run. No coverage number below is measured.*

The flag is scored one versus all against the c5 label (`labels` and `pids` of `nmf_k7_letrozole_full.npz`):

* the confusion table, precision, recall, specificity and lift over the 9.3% base rate;
* the same table for each other bundle separately (c0 to c4, c6), then pooled by group (fertility, background);
* the two ablation composites, and the `tie_ordered` against strict-date match of the sequences.

Limits to read the result with:

* **The comparison is circular by construction.** c5 is the NMF assignment, and the five entities are the top loadings of c5. High recall measures how well the rule restates the bundle. It does not validate the rule clinically.
* **External check without the NMF.** Confirmed breast-cancer diagnosis (ICD-9 174.x, ICD-10 C50.x or SNOMED 4162253, the Mini Table 1 rule of the Day 3 notebook) and the oncology probe label are independent of the bundle. Report the flag against them.
* **False positives from surgery and procedures.** Ondansetron, ketorolac, dexamethasone and IV push also mark any surgery or procedure (for example oocyte retrieval or cesarean delivery). A fertility applicant can meet Rule A. An exclusion composite on the fertility procedure codeset (`art_procedure`) is a candidate for clinical review. It is not part of the rule.
* **Bundle statistics are not applicant statistics.** The 74-day threshold comes from bundle medians. The rule applies it to each applicant's own first occurrence of each entity.

---

## Population Coverage

Not measured yet. The table lists what is known at the bundle level, from the k=7 run and the PubMed check of the final table.

| Quantity | Value |
| :---- | :---- |
| Cohort | 5,238 patients (female, letrozole fill, valid PCP policy) |
| Bundle c5 | 486 patients, 9.3% |
| ondansetron Injection in c5 | 69%, median +100 d after first letrozole |
| ketorolac Injectable Solution [Toradol] in c5 | 63%, median +74 d |
| dexamethasone Injection in c5 | 56%, median +156 d |
| Intravenous push injection (CPT4 96374) in c5 | 54%, median +178 d |
| Basic metabolic panel (CPT4 80048) in c5 | 54%, median +74 d |

| Predicate or composite | Policies | % cohort |
| :---- | ----: | ----: |
| `letrozole_present` | not measured | |
| `periop_entity_count >= 3` (`composite_periop_bundle`) | not measured | |
| `composite_monitoring_sequence` | not measured | |
| `composite_c5_manual_ruw` | not measured | |

---

## References

* Final table of the letrozole k=7 run with literature search: `nb/repr_learn_letrozole/final_table_letrozole_k7_full_literature_verified.csv`.
* Source of the three sequences: Day 3 motif tables of the letrozole k=7 run (`nb/repr_learn_letrozole/Letrozole_NMF_PrefixSpan_full.ipynb`, section 5).
* Matching semantics (`tie_ordered`, `strict_date`): `nb/repr_learn_letrozole/motif_robustness/seqindex.py`.
* Format and voice: `Diabetes_Rx_Predicate_Engine.md`.
