# Infertility Predicate Engine

*Working Draft — July 2026*

---

## Overview

This document describes the design, implementation, and validation of the infertility predicate engine for LGA Term Life underwriting. The engine distinguishes letrozole fertility use from cancer-adjuvant use using prescription patterns, prescriber specialty, and diagnosis history drawn from the Ethos OMOP clinical database. It was backtested against all decisioned LGA Term Life policies from June – July 2026 (n=92,829).

---

## Predicates and Composites

This section defines the building blocks of the infertility predicate engine. It covers the atomic predicates — individual clinical checks against the applicant's medical history — and the composites that combine them into named clinical patterns. This section contains no underwriting logic. It is intended for clinical and medical review to validate that the definitions accurately reflect established treatment protocols.

### Atomic Predicates

A predicate answers one question about the applicant's medical history and returns true or false. Atomic predicates check directly against raw data attributes.

**Letrozole present.** The applicant has at least one letrozole fill in their prescription history. Presence alone is not diagnostic — letrozole is used for both ovulation induction and breast cancer adjuvant therapy. Downstream predicates resolve the indication.

`letrozole_present = drug IS letrozole`

**Letrozole short supply.** The applicant has a letrozole fill with a 5 or 6 day supply. Fertility letrozole is prescribed as a 5-day course taken on specific days of the menstrual cycle. Cancer-adjuvant letrozole is taken daily and continuously, dispensed in 28–90 day supplies.

`letrozole_short_supply = drug IS letrozole AND days_supply IN (5, 6)`

**Letrozole chronic supply.** The applicant has a letrozole fill with a supply of 28 days or more. This is the typical cancer-adjuvant dispensing pattern. Retained as an informational signal only — not used as a hard exclusion in any composite because OB-GYNs routinely dispense 30-day fills for cyclical fertility use, with the patient taking the drug for only 5 of those days.

`letrozole_chronic = drug IS letrozole AND days_supply >= 28`

**Clomiphene present.** The applicant has at least one clomiphene fill. Clomiphene has no oncologic indication in women. In women of reproductive age it is a fertility medication.

`clomiphene_present = drug IS clomiphene`

**Step-up sequence.** The applicant has clomiphene fills that predate letrozole fills in chronological order. Clomiphene is the standard first-line agent for anovulation; letrozole is the preferred second-line alternative when clomiphene fails or is contraindicated. The temporal sequence — clomiphene first, letrozole second — is a clinical treatment protocol fingerprint.

`step_up_sequence = clomiphene_present AND letrozole_present AND first_clomiphene_fill_date < first_letrozole_fill_date`

**Infertility or anovulation diagnosis.** The applicant has a documented diagnosis of female infertility or anovulation in their condition history.

`infertility_or_anovulation_dx = condition IS IN (anovulation, tubal infertility, uterine infertility, unexplained infertility)`

**Oncologist prescriber.** Letrozole or tamoxifen in the applicant's prescription history was written by a medical oncologist, hematology/oncologist, or gynecologic oncologist.

`oncologist_prescriber = (drug IS letrozole OR drug IS tamoxifen) AND prescriber_specialty IS IN (medical oncology, hematology/oncology, gynecologic oncology)`

**Breast cancer history.** The applicant has a breast cancer diagnosis anywhere in their condition history.

`breast_cancer_history = condition IS breast cancer (any subtype)`

**OB-GYN or REI prescriber.** The prescription in question was written by an Obstetrician-Gynecologist or Reproductive Endocrinologist. Treated as a confidence-upgrading signal rather than a hard requirement.

`obgyn_or_rei_prescriber = prescriber_specialty IS IN (obstetrics and gynecology, reproductive endocrinology and infertility)`

---

### Composites

A composite combines atomic predicates — or other composites — into a named clinical pattern. It asserts that a recognizable combination of evidence is present in the applicant's history. Composites are organized in tiers: fertility patterns first, the cancer-adjuvant pattern, and the unclassified residual last.

**Letrozole fertility.** Letrozole with a short supply, no cancer exclusion signals.

`composite_letrozole_fertility = letrozole_short_supply AND NOT oncologist_prescriber AND NOT breast_cancer_history`

**Letrozole fertility OBGYN prescriber.** Letrozole with a short supply, prescribed by an OB-GYN or REI, no cancer exclusion signals.

`composite_letrozole_fertility_obgyn_prescriber = letrozole_short_supply AND obgyn_or_rei_prescriber AND NOT oncologist_prescriber AND NOT breast_cancer_history`

**Letrozole fertility diagnosis confirmed.** Letrozole present at any supply length, plus a documented infertility or anovulation diagnosis, no cancer exclusion signals.

`composite_letrozole_fertility_dx_confirmed = letrozole_present AND infertility_or_anovulation_dx AND NOT oncologist_prescriber AND NOT breast_cancer_history`

**Clomiphene fertility.** Clomiphene present, no cancer exclusion signals.

`composite_clomiphene_fertility = clomiphene_present AND NOT oncologist_prescriber AND NOT breast_cancer_history`

**Clomiphene fertility OBGYN prescriber.** Clomiphene present, prescribed by an OB-GYN or REI, no cancer exclusion signals.

`composite_clomiphene_fertility_obgyn_prescriber = clomiphene_present AND obgyn_or_rei_prescriber AND NOT oncologist_prescriber AND NOT breast_cancer_history`

**Anovulation step-up.** Clomiphene fills chronologically preceding letrozole fills, no cancer exclusion signals.

`composite_anovulation_step_up = step_up_sequence AND NOT oncologist_prescriber AND NOT breast_cancer_history`

**Any fertility.** Any fertility composite fires, and the case is not unclassified.

`composite_any_fertility = (composite_letrozole_fertility OR composite_letrozole_fertility_obgyn_prescriber OR composite_letrozole_fertility_dx_confirmed OR composite_clomiphene_fertility OR composite_clomiphene_fertility_obgyn_prescriber OR composite_anovulation_step_up) AND NOT letrozole_unclassified`

**Letrozole chronic cancer adjuvant.** Letrozole with a chronic supply, with an oncologist prescriber or breast cancer history.

`composite_letrozole_chronic_cancer_adjuvant = letrozole_chronic AND (oncologist_prescriber OR breast_cancer_history)`

**Letrozole unclassified.** Letrozole is present but the evidence is insufficient to assert either a fertility or cancer pattern. No short supply, no confirming specialty, no infertility diagnosis, and no cancer signals present.

`letrozole_unclassified = letrozole_present AND NOT letrozole_short_supply AND NOT obgyn_or_rei_prescriber AND NOT infertility_or_anovulation_dx AND NOT oncologist_prescriber AND NOT breast_cancer_history`

---

### References

- [ASRM — Ovulation Induction for the General Gynecologist](https://pmc.ncbi.nlm.nih.gov/articles/PMC6046677/)  
- [ASRM — Fertility Drugs and Cancer: A Guideline (2024)](https://www.asrm.org/practice-guidance/practice-committee-documents/fertility-drugs-and-cancer-a-guideline-2024/)  
- [ASRM — Clomiphene vs Letrozole Step-up in PCOS (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10375350/)  
- [ASCO — Adjuvant Endocrine Therapy for Hormone Receptor–Positive Breast Cancer: Clinical Practice Guideline](https://ascopubs.org/doi/10.1200/JCO.18.01160)  
- [FACE Trial — Letrozole vs Anastrozole in Adjuvant Breast Cancer Therapy](https://ascopubs.org/doi/10.1200/JCO.2016.69.2871)

---

## OMOP Implementation

This section specifies how each atomic predicate is implemented as a SQL query against the Ethos OMOP database. Each predicate is written as a CTE returning a distinct set of policy IDs for which the predicate evaluates true. Absent from the result set means false.

Drug identification uses the concept ancestor table to roll up from any formulation or NDC to the ingredient level, ensuring all dispensed forms of a drug are captured regardless of how they are recorded in the source data. Diagnosis identification uses direct concept matching against standard SNOMED concepts confirmed via OMOP vocabulary mapping. Prescriber specialty matching covers both mapped specialty concept IDs and raw specialty source value strings to handle unmapped provider records.

All CTEs reference the `ethos_production.omop_54` schema with `master_` prefixed clinical tables, which include a `policy_id` column for joining to the underwriting policy universe.

### Atomic Predicates

**letrozole\_present.**

```sql
SELECT DISTINCT de.policy_id
FROM ethos_production.omop_54.master_drug_exposure de
JOIN ethos_production.omop_54.concept_ancestor ca
    ON ca.descendant_concept_id = de.drug_concept_id
    AND ca.ancestor_concept_id = 1315946
WHERE de.drug_concept_id != 0
```

**letrozole\_short\_supply.**

```sql
SELECT DISTINCT de.policy_id
FROM ethos_production.omop_54.master_drug_exposure de
JOIN ethos_production.omop_54.concept_ancestor ca
    ON ca.descendant_concept_id = de.drug_concept_id
    AND ca.ancestor_concept_id = 1315946
WHERE de.drug_concept_id != 0
  AND de.days_supply IN (5, 6)
```

**letrozole\_chronic.**

```sql
SELECT DISTINCT de.policy_id
FROM ethos_production.omop_54.master_drug_exposure de
JOIN ethos_production.omop_54.concept_ancestor ca
    ON ca.descendant_concept_id = de.drug_concept_id
    AND ca.ancestor_concept_id = 1315946
WHERE de.drug_concept_id != 0
  AND de.days_supply >= 28
```

**clomiphene\_present.**

```sql
SELECT DISTINCT de.policy_id
FROM ethos_production.omop_54.master_drug_exposure de
JOIN ethos_production.omop_54.concept_ancestor ca
    ON ca.descendant_concept_id = de.drug_concept_id
    AND ca.ancestor_concept_id = 1598819
WHERE de.drug_concept_id != 0
```

**step\_up\_sequence.**

```sql
SELECT DISTINCT de_c.policy_id
FROM ethos_production.omop_54.master_drug_exposure de_c
JOIN ethos_production.omop_54.concept_ancestor ca_c
    ON ca_c.descendant_concept_id = de_c.drug_concept_id
    AND ca_c.ancestor_concept_id = 1598819
JOIN ethos_production.omop_54.master_drug_exposure de_l
    ON de_l.policy_id = de_c.policy_id
JOIN ethos_production.omop_54.concept_ancestor ca_l
    ON ca_l.descendant_concept_id = de_l.drug_concept_id
    AND ca_l.ancestor_concept_id = 1315946
WHERE de_c.drug_concept_id != 0
  AND de_l.drug_concept_id != 0
  AND de_c.drug_exposure_start_date < de_l.drug_exposure_start_date
```

**infertility\_or\_anovulation\_dx.** Standard SNOMED concepts confirmed via OMOP vocabulary mapping from ICD-10 source codes. No ancestry rollup required — these are terminal leaf concepts.

| ICD-10 | Description | SNOMED Concept ID |
| :---- | :---- | :---- |
| N97.0 | Female infertility associated with anovulation | 197044 |
| N97.1 | Female infertility of tubal origin | 197606 |
| N97.2 | Female infertility of uterine origin | 201635 |
| N97.9 | Female infertility, unspecified | 201909 |

```sql
SELECT DISTINCT co.policy_id
FROM ethos_production.omop_54.master_condition_occurrence co
WHERE co.condition_concept_id IN (197044, 197606, 201635, 201909)
```

**oncologist\_prescriber.** Specialty matching covers both mapped specialty concept IDs and raw source value strings. The same note on source value matching applies here as for `obgyn_or_rei_prescriber` below — string matching is an interim measure pending full specialty concept mapping.

```sql
SELECT DISTINCT de.policy_id
FROM ethos_production.omop_54.master_drug_exposure de
JOIN ethos_production.omop_54.concept_ancestor ca
    ON ca.descendant_concept_id = de.drug_concept_id
    AND ca.ancestor_concept_id IN (1315946, 1436678)
JOIN ethos_production.omop_54.provider p
    ON p.provider_id = de.provider_id
    AND (
        p.specialty_concept_id IN (45756764, 45756811, 45756799)
        OR LOWER(p.specialty_source_value) IN (
            'oncology',
            'hematology/oncology',
            'medical oncology',
            'gynecology/oncology'
        )
    )
WHERE de.drug_concept_id != 0
```

**breast\_cancer\_history.**

```sql
SELECT DISTINCT co.policy_id
FROM ethos_production.omop_54.master_condition_occurrence co
JOIN ethos_production.omop_54.concept_ancestor ca
    ON ca.descendant_concept_id = co.condition_concept_id
    AND ca.ancestor_concept_id = 4162253
```

**obgyn\_or\_rei\_prescriber.** Specialty matching covers both mapped specialty concept IDs and raw source value strings. The source value fallback is required in the current implementation because "Obstetrics and Gynecology" maps to concept\_id \= 0 in the provider table for a significant portion of records, indicating the specialty is present in the source data but has not yet been mapped to a standard concept.

> **Note:** Source value string matching is an interim measure. Standard concept matching is the preferred approach for a production implementation — it is vocabulary-controlled, case-insensitive by design, and not brittle to source system text variation. An outstanding item is to map the unmapped specialty source values in the provider table to their correct standard concepts and retire the string matching fallback.

```sql
SELECT DISTINCT de.policy_id
FROM ethos_production.omop_54.master_drug_exposure de
JOIN ethos_production.omop_54.provider p
    ON p.provider_id = de.provider_id
    AND (
        p.specialty_concept_id IN (38004461, 38003902, 38003905, 45756826)
        OR LOWER(p.specialty_source_value) IN (
            'obstetrics and gynecology',
            'obstetrics & gynecology',
            'obstetrics',
            'gynecology',
            'reproductive endocrinology',
            'reproductive endocrinology and infertility'
        )
    )
WHERE de.drug_concept_id != 0
```

---

### Predicate and Composite Validation — Hit Rates Against LGA Term Life (n=92,829)

The table below reports how frequently each predicate and composite fires across all decisioned LGA Term Life policies in the two-month backtest window (June 1 – July 31, 2026, n=92,829). See the Validation Query section below for the full query used to generate these results.

**Atomic Predicates**

| Predicate | n | % of total |
| :---- | :---- | :---- |
| letrozole\_present | 630 | 0.679% |
| letrozole\_short\_supply | 502 | 0.541% |
| letrozole\_chronic | 136 | 0.147% |
| clomiphene\_present | 805 | 0.867% |
| step\_up\_sequence | 117 | 0.126% |
| infertility\_or\_anovulation\_dx | 768 | 0.827% |
| obgyn\_or\_rei\_prescriber | 225 | 0.242% |
| oncologist\_prescriber | 16 | 0.017% |
| breast\_cancer\_history | 80 | 0.086% |

**Composites**

| Composite | n | % of total |
| :---- | :---- | :---- |
| composite\_letrozole\_fertility | 502 | 0.541% |
| composite\_letrozole\_fertility\_obgyn\_prescriber | 185 | 0.199% |
| composite\_letrozole\_fertility\_dx\_confirmed | 229 | 0.247% |
| composite\_clomiphene\_fertility | 805 | 0.867% |
| composite\_clomiphene\_fertility\_obgyn\_prescriber | 141 | 0.152% |
| composite\_anovulation\_step\_up | 117 | 0.126% |
| composite\_any\_fertility | 1,218 | 1.312% |

> **Note:** The cancer exclusion predicates fire at low rates — 16 oncologist prescriber cases and 80 breast cancer histories across the full two-month population. These rates are expected to understate true prevalence. Prescription data is ordered later in the underwriting funnel, and cases with a clear cancer signal are likely re-routed before an rx order is placed. The population reaching this stage is already pre-filtered toward lower-risk applicants.

---

### Reference Concept IDs

| Concept | Type | Concept ID |
| :---- | :---- | :---- |
| Letrozole | Drug ingredient | 1315946 |
| Clomiphene | Drug ingredient | 1598819 |
| Tamoxifen | Drug ingredient | 1436678 |
| Breast cancer | Condition ancestor | 4162253 |
| OB-GYN (Medicare Specialty) | Provider specialty | 38004461 |
| Gynecology Physician (NUCC) | Provider specialty | 38003902 |
| Obstetrics Physician (NUCC) | Provider specialty | 38003905 |
| Reproductive Endocrinology (ABMS) | Provider specialty | 45756826 |
| Gynecologic Oncology (ABMS) | Provider specialty | 45756764 |

---

## Validation Query

This section contains the full validation query used to backtest the infertility predicate engine against the LGA Term Life population. The query evaluates all atomic predicates and composites for every policy in scope and returns one row per policy with binary flags for each predicate and composite.

### Backtest Population

- Carrier: LGA  
- Product: Term Life Insurance  
- Window: `TS_POLICY_CREATED_AT >= '2026-06-01' AND TS_POLICY_CREATED_AT < '2026-08-01'`  
- Scope: All decisioned policies (excludes TBD)

### Query

```sql
WITH base_policies AS (
    SELECT
        CAST(pcp.BK_POLICY_ID AS VARCHAR) AS policy_id,
        CASE
            WHEN pcp.DIM_UNDERWRITING_PROCESS = 'TBD'    THEN 'TBD'
            WHEN pcp.DIM_UNDERWRITING_PROCESS = 'Manual' THEN 'RUW'
            WHEN pcp.TS_POLICY_APPROVED_AT IS NOT NULL    THEN 'Approved'
            WHEN pcp.TS_POLICY_DECLINED_AT IS NOT NULL    THEN 'Declined'
            ELSE 'error'
        END AS underwriting_decision
    FROM ethos_production.dbt_mart_transformation.m_policy_carrier_product pcp
    WHERE pcp.dim_carrier = 'LGA'
      AND pcp.dim_product = 'Term Life Insurance'
      AND pcp.DIM_UNDERWRITING_PROCESS != 'TBD'
      AND pcp.TS_POLICY_CREATED_AT >= '2026-06-01'
      AND pcp.TS_POLICY_CREATED_AT < '2026-08-01'
),
letrozole_present AS (
    SELECT DISTINCT de.policy_id
    FROM ethos_production.omop_54.master_drug_exposure de
    JOIN ethos_production.omop_54.concept_ancestor ca
        ON ca.descendant_concept_id = de.drug_concept_id
        AND ca.ancestor_concept_id = 1315946
    WHERE de.drug_concept_id != 0
),
letrozole_short_supply AS (
    SELECT DISTINCT de.policy_id
    FROM ethos_production.omop_54.master_drug_exposure de
    JOIN ethos_production.omop_54.concept_ancestor ca
        ON ca.descendant_concept_id = de.drug_concept_id
        AND ca.ancestor_concept_id = 1315946
    WHERE de.drug_concept_id != 0
      AND de.days_supply IN (5, 6)
),
letrozole_chronic AS (
    SELECT DISTINCT de.policy_id
    FROM ethos_production.omop_54.master_drug_exposure de
    JOIN ethos_production.omop_54.concept_ancestor ca
        ON ca.descendant_concept_id = de.drug_concept_id
        AND ca.ancestor_concept_id = 1315946
    WHERE de.drug_concept_id != 0
      AND de.days_supply >= 28
),
clomiphene_present AS (
    SELECT DISTINCT de.policy_id
    FROM ethos_production.omop_54.master_drug_exposure de
    JOIN ethos_production.omop_54.concept_ancestor ca
        ON ca.descendant_concept_id = de.drug_concept_id
        AND ca.ancestor_concept_id = 1598819
    WHERE de.drug_concept_id != 0
),
step_up_sequence AS (
    SELECT DISTINCT de_c.policy_id
    FROM ethos_production.omop_54.master_drug_exposure de_c
    JOIN ethos_production.omop_54.concept_ancestor ca_c
        ON ca_c.descendant_concept_id = de_c.drug_concept_id
        AND ca_c.ancestor_concept_id = 1598819
    JOIN ethos_production.omop_54.master_drug_exposure de_l
        ON de_l.policy_id = de_c.policy_id
    JOIN ethos_production.omop_54.concept_ancestor ca_l
        ON ca_l.descendant_concept_id = de_l.drug_concept_id
        AND ca_l.ancestor_concept_id = 1315946
    WHERE de_c.drug_concept_id != 0
      AND de_l.drug_concept_id != 0
      AND de_c.drug_exposure_start_date < de_l.drug_exposure_start_date
),
infertility_or_anovulation_dx AS (
    SELECT DISTINCT co.policy_id
    FROM ethos_production.omop_54.master_condition_occurrence co
    WHERE co.condition_concept_id IN (197044, 197606, 201635, 201909)
),
breast_cancer_history AS (
    SELECT DISTINCT co.policy_id
    FROM ethos_production.omop_54.master_condition_occurrence co
    JOIN ethos_production.omop_54.concept_ancestor ca
        ON ca.descendant_concept_id = co.condition_concept_id
        AND ca.ancestor_concept_id = 4162253
),
letrozole_specialty_confirmed AS (
    SELECT DISTINCT de.policy_id
    FROM ethos_production.omop_54.master_drug_exposure de
    JOIN ethos_production.omop_54.concept_ancestor ca
        ON ca.descendant_concept_id = de.drug_concept_id
        AND ca.ancestor_concept_id = 1315946
    JOIN ethos_production.omop_54.provider p
        ON p.provider_id = de.provider_id
        AND (
            p.specialty_concept_id IN (38004461, 38003902, 38003905, 45756826)
            OR LOWER(p.specialty_source_value) IN (
                'obstetrics and gynecology', 'obstetrics & gynecology',
                'obstetrics', 'gynecology',
                'reproductive endocrinology',
                'reproductive endocrinology and infertility'
            )
        )
    WHERE de.drug_concept_id != 0
),
clomiphene_specialty_confirmed AS (
    SELECT DISTINCT de.policy_id
    FROM ethos_production.omop_54.master_drug_exposure de
    JOIN ethos_production.omop_54.concept_ancestor ca
        ON ca.descendant_concept_id = de.drug_concept_id
        AND ca.ancestor_concept_id = 1598819
    JOIN ethos_production.omop_54.provider p
        ON p.provider_id = de.provider_id
        AND (
            p.specialty_concept_id IN (38004461, 38003902, 38003905, 45756826)
            OR LOWER(p.specialty_source_value) IN (
                'obstetrics and gynecology', 'obstetrics & gynecology',
                'obstetrics', 'gynecology',
                'reproductive endocrinology',
                'reproductive endocrinology and infertility'
            )
        )
    WHERE de.drug_concept_id != 0
),
oncologist_prescriber AS (
    SELECT DISTINCT de.policy_id
    FROM ethos_production.omop_54.master_drug_exposure de
    JOIN ethos_production.omop_54.concept_ancestor ca
        ON ca.descendant_concept_id = de.drug_concept_id
        AND ca.ancestor_concept_id IN (1315946, 1436678)
    JOIN ethos_production.omop_54.provider p
        ON p.provider_id = de.provider_id
        AND (
            p.specialty_concept_id IN (45756764, 45756811, 45756799)
            OR LOWER(p.specialty_source_value) IN (
                'oncology', 'hematology/oncology',
                'medical oncology', 'gynecology/oncology'
            )
        )
    WHERE de.drug_concept_id != 0
)
SELECT
    bp.policy_id,
    bp.underwriting_decision,
    CASE WHEN lp.policy_id  IS NOT NULL THEN 1 ELSE 0 END AS letrozole_present,
    CASE WHEN ls.policy_id  IS NOT NULL THEN 1 ELSE 0 END AS letrozole_short_supply,
    CASE WHEN lc.policy_id  IS NOT NULL THEN 1 ELSE 0 END AS letrozole_chronic,
    CASE WHEN cp.policy_id  IS NOT NULL THEN 1 ELSE 0 END AS clomiphene_present,
    CASE WHEN su.policy_id  IS NOT NULL THEN 1 ELSE 0 END AS step_up_sequence,
    CASE WHEN dx.policy_id  IS NOT NULL THEN 1 ELSE 0 END AS infertility_or_anovulation_dx,
    CASE WHEN lsc.policy_id IS NOT NULL THEN 1 ELSE 0 END AS letrozole_specialty_confirmed,
    CASE WHEN csc.policy_id IS NOT NULL THEN 1 ELSE 0 END AS clomiphene_specialty_confirmed,
    CASE WHEN onc.policy_id IS NOT NULL THEN 1 ELSE 0 END AS oncologist_prescriber,
    CASE WHEN bc.policy_id  IS NOT NULL THEN 1 ELSE 0 END AS breast_cancer_history,
    -- Composites
    CASE WHEN ls.policy_id IS NOT NULL
          AND onc.policy_id IS NULL AND bc.policy_id IS NULL
         THEN 1 ELSE 0 END AS composite_letrozole_fertility,
    CASE WHEN ls.policy_id IS NOT NULL AND lsc.policy_id IS NOT NULL
          AND onc.policy_id IS NULL AND bc.policy_id IS NULL
         THEN 1 ELSE 0 END AS composite_letrozole_fertility_obgyn_prescriber,
    CASE WHEN lp.policy_id IS NOT NULL AND dx.policy_id IS NOT NULL
          AND onc.policy_id IS NULL AND bc.policy_id IS NULL
         THEN 1 ELSE 0 END AS composite_letrozole_fertility_dx_confirmed,
    CASE WHEN cp.policy_id IS NOT NULL
          AND onc.policy_id IS NULL AND bc.policy_id IS NULL
         THEN 1 ELSE 0 END AS composite_clomiphene_fertility,
    CASE WHEN cp.policy_id IS NOT NULL AND csc.policy_id IS NOT NULL
          AND onc.policy_id IS NULL AND bc.policy_id IS NULL
         THEN 1 ELSE 0 END AS composite_clomiphene_fertility_obgyn_prescriber,
    CASE WHEN su.policy_id IS NOT NULL
          AND onc.policy_id IS NULL AND bc.policy_id IS NULL
         THEN 1 ELSE 0 END AS composite_anovulation_step_up,
    CASE WHEN (ls.policy_id IS NOT NULL
               OR cp.policy_id IS NOT NULL
               OR su.policy_id IS NOT NULL
               OR (lp.policy_id IS NOT NULL AND dx.policy_id IS NOT NULL))
          AND onc.policy_id IS NULL AND bc.policy_id IS NULL
         THEN 1 ELSE 0 END AS composite_any_fertility
FROM base_policies bp
LEFT JOIN letrozole_present lp              ON lp.policy_id  = bp.policy_id
LEFT JOIN letrozole_short_supply ls         ON ls.policy_id  = bp.policy_id
LEFT JOIN letrozole_chronic lc              ON lc.policy_id  = bp.policy_id
LEFT JOIN clomiphene_present cp             ON cp.policy_id  = bp.policy_id
LEFT JOIN step_up_sequence su               ON su.policy_id  = bp.policy_id
LEFT JOIN infertility_or_anovulation_dx dx  ON dx.policy_id  = bp.policy_id
LEFT JOIN letrozole_specialty_confirmed lsc ON lsc.policy_id = bp.policy_id
LEFT JOIN clomiphene_specialty_confirmed csc ON csc.policy_id = bp.policy_id
LEFT JOIN oncologist_prescriber onc         ON onc.policy_id = bp.policy_id
LEFT JOIN breast_cancer_history bc          ON bc.policy_id  = bp.policy_id
ORDER BY bp.policy_id;
```

