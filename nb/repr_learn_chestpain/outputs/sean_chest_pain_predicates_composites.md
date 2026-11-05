# Chest Pain Predicate Engine

*Working Draft — November 2026*

---

## Overview

This document defines the predicates and composites of the chest pain underwriting view of Sean. It turns the Chest Pain Workflow Draft into yes-or-no questions about the claims history of an applicant. The claims history comes from the Ethos clinical database in the Observational Medical Outcomes Partnership (OMOP) common data model. The document gives the OMOP implementation of each predicate, with the concept identifiers (IDs) of each code set. It reports how often each predicate and composite is true for 150,664 applicants with a chest pain event on or before the application date. The counts are a first look at the data and not a validation.

---

## Predicates and Composites

This section defines the building blocks of the chest pain predicate engine. It covers the predicates, which are individual checks against the claims history of an applicant. It covers the composites, which combine predicates and time into the rows of the draft of Sean. This section contains no underwriting logic. The underwriter reviews it to check that the definitions match the draft.

### Index Date and Anchors

Every predicate reads the claims history of the applicant up to one index date. The index date R is the application date of the applicant. An applicant with several policies has one application date, the latest interview start of the policies. The method ignores every event after R.

The anchor is the chest pain event. C is the date of the last chest pain event on or before R. F is the date of the first chest pain event. Months out is the time from C to R, in months of 30.4375 days.

**Chest pain present.** The applicant has at least one chest pain event on or before R. The list holds chest pain, precordial pain, chest pain on breathing, and pain of the space between the ribs. Every count in this document covers the 150,664 applicants with this predicate.

`chest_pain = condition IS chest pain AND event_date <= R`

`C = MAX(event_date) over chest pain events up to R`

`F = MIN(event_date) over chest pain events up to R`

`months_out = (R - C) / 30.4375`

---

### Atomic Predicates

A predicate answers one question about the claims history of an applicant. It returns true or false. Atomic predicates check directly against the code sets. Derived predicates combine other predicates. The order follows the groups of the draft: high-risk features, low-risk features, features coded later, and derived predicates.

The rule of a predicate says which events count. *Up to R* means events on or before R. *On or before C* means events on or before C. *After C* means events after C and up to R. Age and sex come from the date C.

**Age and sex in the high-risk range.** The applicant is a man older than 45, or a woman older than 55, on the date C. Age counts in completed years, so the applicant is 46 or more, or 56 or more. Sean wrote more than 45 and more than 55, and the limits are strict. The draft item is `Male > 45, Female > 55`.

`age_sex_high_risk = (sex IS male AND age_at_C > 45) OR (sex IS female AND age_at_C > 55)`

**Previous coronary artery disease (CAD) diagnosis.** The applicant has at least one CAD diagnosis on or before the date C. The list holds angina, old and acute heart attack, and coronary atherosclerosis. The list has no history-status code and no procedure code, such as bypass or stent. The draft item is `Previous Dx of CAD`.

`hx_cad = condition IS IN CAD diagnoses AND event_date <= C`

**Abnormal electrocardiogram (EKG) code present.** The applicant has at least one coded finding of an abnormal EKG on or before R. The code is a finding, not the test. It comes from the diagnosis code R94.31. Specific findings, such as bundle branch block, are not in the list. The draft item is `Abnormal EKG`.

`abnormal_ekg = condition IS abnormal EKG finding AND event_date <= R`

**Additional cardiac testing after C.** The applicant has at least one cardiac test after the date C. The list holds echocardiography (heart ultrasound), stress tests, heart scans, coronary computed tomography angiography, and cardiac catheterization. The first-line EKG and troponin tests are not in the list. The data shows the test and not the result. The draft item is `Additional cardiac testing`.

`extra_cardiac_testing = procedure IS IN additional cardiac tests AND event_date > C`

**Nitrate prescription present.** The applicant has at least one nitrate drug on or before R. Nitrates are heart drugs that widen blood vessels. The list holds nitroglycerin, isosorbide mononitrate, and isosorbide dinitrate, in every dose form. The dose forms include tablets under the tongue, patches, ointment, and injection, but no rectal ointment. The draft item is `Rx nitrates`.

`rx_nitrates = drug IS IN nitrates AND event_date <= R`

**Troponin test present.** The applicant has at least one troponin test on or before R. Troponin is a blood test for injury to the heart muscle. The data does not show the type of test or the result. The draft item is `Troponin testing`.

`troponin = measurement IS troponin test AND event_date <= R`

**EKG test present.** The applicant has at least one EKG test on or before R. An EKG records the electrical signal of the heart. The list holds the routine 12-lead EKG and 2 screening codes. The data shows that the test happened and not the result. The draft item is `EKG`.

`ekg = procedure IS EKG test AND event_date <= R`

**Gastroesophageal reflux disease (GERD) diagnosis present.** The applicant has at least one GERD diagnosis on or before R. GERD is acid reflux from the stomach into the food pipe. The list holds 4 diagnosis codes. Heartburn is one of them. The draft item is `GERD`.

`gerd = condition IS GERD AND event_date <= R`

**Anxiety diagnosis present.** The applicant has at least one anxiety diagnosis on or before R. The list holds 12 diagnosis codes. They range from generalized anxiety disorder to anxiety that a substance causes. Some codes are rare. The draft item is `Anxiety`.

`anxiety = condition IS anxiety AND event_date <= R`

**GERD or other gastrointestinal (GI) diagnosis after C.** The applicant has at least one GERD diagnosis or other GI diagnosis after the date C. The other GI diagnoses are gastritis, esophagitis, ulcers, dyspepsia, gallstones, cholecystitis, and pancreatitis. The list has no reflux code in its GI part, because the GERD list holds it. The draft item is `GERD, other GI related Dx, later coded`.

`gi_dx = condition IS IN (GERD, other GI diagnoses) AND C < event_date <= R`

**Anxiety diagnosis after C.** The applicant has at least one anxiety diagnosis after the date C. The list is the anxiety list of the low-risk features. The draft item is `Anxiety, later coded`.

`anxiety_later = condition IS anxiety AND C < event_date <= R`

**Chest wall muscle strain after C.** The applicant has at least one strain or sprain diagnosis of the chest wall after the date C. The 4 codes are sprains of the thoracic back, the sternoclavicular joint, the chondrocostal joint, and the sternum. One code, thoracic back sprain, gives most of the applicants. The draft item is `Muscle strain, later coded`.

`muscle_strain = condition IS chest wall strain or sprain AND C < event_date <= R`

**Costochondritis after C.** The applicant has at least one costochondritis diagnosis after the date C. Costochondritis is a pain of the rib cartilage. The list holds 1 code, Tietze's disease. The draft item is `Costochondritis, later coded`.

`costochondritis = condition IS costochondritis AND C < event_date <= R`

**Intercostal or non-cardiac chest pain after F.** The applicant has a code for pain of the space between the ribs after the date F, the first chest pain event. This code is also a chest pain code, so the test uses F and not C. The list has no code that says non-cardiac chest pain. The draft item is `Later noted as intercostal or non-cardiac chest pain`.

`noncardiac_cp = condition IS intercostal pain AND F < event_date <= R`

**Explained diagnosis coded later.** The applicant meets at least one of 4 predicates. These are anxiety, GI diagnosis, chest wall muscle strain, and costochondritis, all after C. The row of the draft calls these the later coded diagnoses. The draft item is `Later coded as anxiety, GI, muscle strain or costochondritis`.

`explained_dx = anxiety_later OR gi_dx OR muscle_strain OR costochondritis`

**EKG without an abnormal code.** The applicant has an EKG test and no abnormal EKG code on or before R. This is a proxy for a normal EKG. The claims data has no test results, so the data does not show a normal EKG. The draft item is `EKG normal (claims proxy: an EKG and no abnormal-EKG code)`.

`ekg_no_abnormal_code = ekg AND NOT abnormal_ekg`

**No further cardiac testing.** The applicant has no additional cardiac test after the date C. The draft item is `No further cardiac testing`.

`no_further_cardiac_testing = NOT extra_cardiac_testing`

**No firm diagnosis.** None of the diagnoses that the draft lists appears in the history of the applicant on or before R. The diagnoses are CAD, GERD, other GI diagnoses, anxiety, chest wall muscle strain, costochondritis, and intercostal or non-cardiac chest pain. The time of the diagnosis does not matter. The coded abnormal EKG finding is a feature of the draft and not a diagnosis, so it does not count. The draft item is `No firm diagnosis (none of the diagnoses of the draft)`.

`no_firm_dx = NOT (hx_cad OR gerd OR anxiety OR gi_dx OR muscle_strain OR costochondritis OR noncardiac_cp), all events up to R`

---

### Composites

A composite combines predicates and time into one row of the draft. The id of a composite keeps the id of the row in the draft. The first letter of the id names the column of the draft: A, R, or D, from left to right. The draft has no order between its rows, so one applicant sometimes meets rows of more than one column. The signs more than and less than are strict. An applicant at exactly 6 months is in neither row.

**high_risk_any: Any high-risk feature.** The applicant meets at least one of 5 predicates: age and sex, previous CAD diagnosis, abnormal EKG code, additional cardiac testing, and nitrate prescription.

`high_risk_any = age_sex_high_risk OR hx_cad OR abnormal_ekg OR extra_cardiac_testing OR rx_nitrates`

**A1: No high-risk feature and more than 6 months out.** The applicant meets none of the 5 high-risk predicates. The last chest pain event is more than 6 months before R. The draft item is `No high risk features and > 6 months out`.

`A1 = NOT high_risk_any AND months_out > 6`

**A2: EKG without an abnormal code and no CAD history.** The applicant has an EKG test and no abnormal EKG code. The applicant has no previous CAD diagnosis. The draft says any time, so months out does not matter. The draft item is `Any time and EKG normal, no Hx of CAD`.

`A2 = ekg_no_abnormal_code AND NOT hx_cad`

**A3: No further cardiac testing, no CAD history, more than 6 months out.** The applicant has no additional cardiac test after C and no previous CAD diagnosis. The last chest pain event is more than 6 months before R. The draft item is `No further cardiac testing, no Hx of CAD, > 6 months out`.

`A3 = no_further_cardiac_testing AND NOT hx_cad AND months_out > 6`

**A4: Explained diagnosis coded later and no CAD history.** The applicant has an explained diagnosis coded after C. The applicant has no previous CAD diagnosis. The draft says any time, so months out does not matter. The draft item is `No Hx of CAD and later coded as anxiety, GI, strain, costochondritis`.

`A4 = explained_dx AND NOT hx_cad`

**A5: Intercostal or non-cardiac chest pain noted later.** The applicant has a code for pain of the space between the ribs after the first chest pain event F. The draft says any time, so months out does not matter. The draft item is `Later noted as intercostal or non-cardiac chest pain`.

`A5 = noncardiac_cp`

**A6: Coded more than 2 years ago.** The last chest pain event is more than 24 months before R. The row has no other condition. The draft item is `Coded > 2 years ago`.

`A6 = months_out > 24`

**R1: Any high-risk feature and less than 6 months out.** The applicant meets at least one of the 5 high-risk predicates. The last chest pain event is less than 6 months before R. The draft item is `Any high risk features and < 6 months`.

`R1 = high_risk_any AND months_out < 6`

**R2: No firm diagnosis and less than 6 months out.** The applicant meets the predicate no firm diagnosis. The last chest pain event is less than 6 months before R. The draft item is `No firm diagnosis and < 6 months`.

`R2 = no_firm_dx AND months_out < 6`

**D1: CAD history and less than 1 year out.** The applicant has any history of CAD. The last chest pain event is less than 12 months before R. The time runs from the chest pain event to the application date, not from the CAD diagnosis. The draft item is `Hx of CAD and < 1 year`.

`D1 = hx_cad AND months_out < 12`

> **Note:** The draft has items that claims data cannot show. Claims hold codes and dates, with no test result and no rating. The document does not count the current `TO` rating, any abnormal testing, EKG normal, and all cardiac testing within normal limits. One proxy replaces EKG normal: an EKG and no abnormal EKG code.

---

### Decisions and Open Items

The project team settled these items with Zack on 4 November 2026.

- **Age limits.** The limits are strict. The document uses older than 45 for a man and older than 55 for a woman, in completed years.
- **Less than 1 year.** The applicant has any history of CAD. The last chest pain event is less than 12 months before the application date.
- **No firm diagnosis.** None of the diagnoses that the draft lists appears on or before the application date.

Sean must settle these items.

- **Current rating.** The document does not count the current `TO` rating. The claims data holds no rating. Sean must say what `TO` means and where the rating sits.
- **Later coded.** The document counts diagnoses strictly after C. The intercostal code counts after F, because it is a chest pain code.
- **Abnormal EKG.** The document counts only the coded finding. A test code does not show the result.
- **Nitrates.** The list names the 3 drugs in every dose form, injection included. The document does not check where the claims come from.
- **Muscle strain.** The list holds chest wall sprains only. A strain of another body part says nothing about chest pain.

---

### References

- Chest Pain Workflow Draft of Sean, in the block below as written  
- Cohort query `sql/chest_pain_cohort.sql`, version 0.3: the persons and the application date R  
- Notebook `Chestpain_Sean_predicates.ipynb`, version 3.1: the counts of this document  
- Code sets `codesets_sean_v2.yaml`: the concepts behind each predicate  

```
CHEST PAIN WORKFLOW DRAFT (Sean), as written. The ids of the rows are added.

HIGH-RISK FEATURES
    Male > 45, Female >55
    Previous Dx of CAD
    Current TO Rating (not in Banner manual as a comorbid condition)
    Abnormal EKG
    Additional Cardiac Testing (Echo, Cath, CCTA, etc.) – or any abnormal testing
    Rx Nitrates

LOW-RISK FEATURES
    Troponin Testing
    EKG
    GERD
    Anxiety

APPROVE
    A1  No High Risk Features and >6 months out
    A2  Any time and EKG normal – no Hx of CAD
    A3  No further cardiac testing – no Hx of CAD and >6 months out
    A4  Any time, no Hx of CAD and later coded as Anxiety (suggest to rate as anxiety – Discuss with Dr. Z) , GERD, other GI related Dx, muscle strain, costochondritis
    A5  Any time, later noted as intercostal or non-cardiac chest pain
    A6  Coded > 2 years ago
    --  All cardiac testing within normal limits (wnl)

REFER
    R1  Any High Risk Features and < 6 months
    R2  No firm diagnosis and < 6 months

DECLINE
    D1  Hx of CAD and < 1 year
```

---

## OMOP Implementation

This section gives the implementation of each predicate as a Structured Query Language (SQL) query on the Ethos clinical database. Each query returns the distinct person identifiers for which the predicate is true. A person that is absent from the result is false. A derived predicate reads the queries of the predicates it combines, by their names.

Each query lists the concept identifiers of its code sets. A comment names each code set and counts its concepts. A code set is a list of standard concepts for one clinical idea. The Reference Concept IDs below give the name of every concept.

The code sets use concepts of four vocabularies. The list starts with Systematized Nomenclature of Medicine Clinical Terms (SNOMED). It continues with Current Procedural Terminology, fourth edition (CPT4), Healthcare Common Procedure Coding System (HCPCS), and RxNorm.

All queries reference the `ethos_production.omop_54` schema with `master_` prefixed clinical tables. The cohort is a set of persons, so the queries use the person identifier and not the policy identifier. Each query reads the events of a person up to the application date R and ignores later events.

### Cohort

The cohort is the query version 0.3 of the file `sql/chest_pain_cohort.sql`, without change. It returns one row per Ethos person with a chest pain code, with the latest interview start date of the policies of the person. That date is the application date R. The Validation Query holds the same text as its first step, named `cohort`.

```sql
-- v0.3
-- Chest pain cohort: Ethos persons with chest pain (ICD10CM R07.x) in DX evidence, confirmed in OMOP.
-- Same shape as colonoscopy_cohort.sql, ICD10CM source concepts only (no SNOMED expansion),
-- plus latest TS_INTERVIEW_STARTED_AT per person (application anchor).

WITH cp_codes AS (
    SELECT column1 AS code                                       -- ICD10CM, dots removed
    FROM VALUES ('R072'), ('R078'), ('R0782'), ('R0789'), ('R079')
),

-- 1) PCP anchor (one row per policy; PCP grain is policy x carrier x product)
valid_policies AS (
    SELECT TRY_TO_NUMBER(bk_policy_id)::VARCHAR AS policy_id,
           MAX(ts_interview_started_at)         AS interview_started_ts
    FROM ethos_production.dbt_mart_transformation.m_policy_carrier_product
    WHERE dim_underwriting_process IS DISTINCT FROM 'TBD'
      AND bk_product_id IN (1, 5, 14, 15, 21, 25)
    GROUP BY 1
),
policy_person AS (
    SELECT DISTINCT v.policy_id, era.person_id, v.interview_started_ts
    FROM ethos_production.omop_54.policy_era era
    JOIN valid_policies v
      ON v.policy_id = TRY_TO_NUMBER(era.policy_id)::VARCHAR
    WHERE era.person_id IS NOT NULL
),

-- 2) DX evidence -> OMOP person
ethos_persons AS (
    SELECT DISTINCT pp.person_id
    FROM ethos_production.airflow_uw_evidence.dx_evidence_flattened d
    JOIN policy_person pp
      ON pp.policy_id = TRY_TO_NUMBER(d.policy_id)::VARCHAR
    WHERE d.description ILIKE '%chest pain%'
       OR REPLACE(UPPER(TRIM(d.medicalcode)), '.', '') IN (SELECT code FROM cp_codes)
),

-- 3) OMOP concept set: listed ICD10CM codes only
cp_concepts AS (
    SELECT c.concept_id
    FROM ethos_production.omop_54.concept c
    WHERE c.vocabulary_id = 'ICD10CM'
      AND REPLACE(c.concept_code, '.', '') IN (SELECT code FROM cp_codes)
),

-- 4) OMOP hits on source concept, restricted to Ethos persons
omop_persons AS (
    SELECT co.person_id
    FROM ethos_production.omop_54.condition_occurrence co
    JOIN ethos_persons e ON e.person_id = co.person_id
    WHERE co.condition_source_concept_id IN (SELECT concept_id FROM cp_concepts)

    UNION

    SELECT o.person_id
    FROM ethos_production.omop_54.observation o
    JOIN ethos_persons e ON e.person_id = o.person_id
    WHERE o.observation_source_concept_id IN (SELECT concept_id FROM cp_concepts)
)

SELECT op.person_id,
       MAX(pp.interview_started_ts)::DATE AS latest_interview_started_date
FROM omop_persons op
JOIN policy_person pp ON pp.person_id = op.person_id
GROUP BY op.person_id
ORDER BY op.person_id;
```

### Anchor

The table `chest_pain_dates` holds R, F, C, and months out for each person with a chest pain event on or before R. It reads the cohort. A person with chest pain only after R has no row, so every query leaves that person out.

**chest\_pain\_dates.**

```sql
SELECT a.person_id, a.r_date, a.f_date, a.c_date,
       DATEDIFF(day, a.c_date, a.r_date) / 30.4375 AS months_out
FROM (
    SELECT e.person_id, coh.latest_interview_started_date AS r_date,
           MIN(e.condition_start_date) AS f_date,
           MAX(e.condition_start_date) AS c_date
    FROM ethos_production.omop_54.master_condition_occurrence e
    JOIN cohort coh ON coh.person_id = e.person_id
    WHERE e.condition_concept_id IN (77670, 134159, 4168213, 42539051)   -- chest_pain (4 concepts)
      AND e.condition_start_date <= coh.latest_interview_started_date
    GROUP BY e.person_id, coh.latest_interview_started_date
) a
```

### Atomic Predicates

**age\_sex\_high\_risk.**

```sql
-- older than 45 (man) or 55 (woman), in completed years: the 46th or 56th birthday is on or before C
SELECT DISTINCT cp.person_id
FROM chest_pain_dates cp
JOIN ethos_production.omop_54.person p ON p.person_id = cp.person_id
WHERE (p.gender_concept_id = 8507   -- male
     AND cp.c_date >= DATEADD(year, 46, p.birth_datetime))
   OR (p.gender_concept_id = 8532   -- female
     AND cp.c_date >= DATEADD(year, 56, p.birth_datetime))
```

**hx\_cad.**

```sql
SELECT DISTINCT e.person_id
FROM ethos_production.omop_54.master_condition_occurrence e
JOIN chest_pain_dates cp ON cp.person_id = e.person_id
WHERE e.condition_concept_id IN (
        -- uw_cad_dx (22 concepts)
        321318, 36712983, 314666, 4270024, 40481919, 36712982, 319844, 4296653,
        315286, 312327, 37309626, 43020460, 46270163, 4329847, 45766241, 46270162,
        37312532, 45766114, 4108677, 4108218, 45766116, 45766075
    )
  AND e.condition_start_date <= cp.c_date
```

**abnormal\_ekg.**

```sql
SELECT DISTINCT e.person_id
FROM ethos_production.omop_54.master_condition_occurrence e
JOIN chest_pain_dates cp ON cp.person_id = e.person_id
WHERE e.condition_concept_id IN (320536)   -- uw_abnormal_ekg (1 concept)
  AND e.condition_start_date <= cp.r_date
```

**extra\_cardiac\_testing.**

```sql
SELECT DISTINCT e.person_id
FROM ethos_production.omop_54.master_procedure_occurrence e
JOIN chest_pain_dates cp ON cp.person_id = e.person_id
WHERE e.procedure_concept_id IN (
        -- uw_cardiac_testing (55 concepts)
        2313869, 40756833, 2313883, 40756829, 40756950, 2313882, 42535629, 2313871,
        2616271, 2313872, 2313884, 2211577, 40756852, 709987, 709990, 2211998,
        2313913, 40756922, 2616272, 724752, 40756944, 2616270, 2313870, 40756942,
        40756979, 2211579, 2313914, 40757098, 725130, 725129, 2313873, 725128,
        2616266, 2313874, 40756899, 40756911, 40757133, 2616265, 2616267, 725127,
        40756857, 37109083, 2617361, 709989, 709985, 40756983, 40756943, 42628042,
        2211997, 40757138, 1552298, 709986, 1126196, 1126197, 1552297
    )
  AND e.procedure_date > cp.c_date
  AND e.procedure_date <= cp.r_date
```

**rx\_nitrates.**

```sql
SELECT DISTINCT e.person_id
FROM ethos_production.omop_54.master_drug_exposure e
JOIN chest_pain_dates cp ON cp.person_id = e.person_id
WHERE e.drug_concept_id IN (
        -- nitrates (22 concepts)
        19019336, 1593968, 19082350, 19035072, 19019335, 40163938, 1362360, 1383869,
        19080095, 19100691, 1362392, 19035279, 19033627, 1383930, 19126352, 1383849,
        19019337, 1383850, 19019078, 1383851, 19079057, 19079082
    )
  AND e.drug_exposure_start_date <= cp.r_date
```

**troponin.**

```sql
SELECT DISTINCT e.person_id
FROM ethos_production.omop_54.master_measurement e
JOIN chest_pain_dates cp ON cp.person_id = e.person_id
WHERE e.measurement_concept_id IN (2212605, 2212610)   -- troponin (2 concepts)
  AND e.measurement_date <= cp.r_date
```

**ekg.**

```sql
SELECT DISTINCT e.person_id
FROM ethos_production.omop_54.master_procedure_occurrence e
JOIN chest_pain_dates cp ON cp.person_id = e.person_id
WHERE e.procedure_concept_id IN (2313816, 2313814, 2313815, 2617470, 2617471)   -- ekg (5 concepts)
  AND e.procedure_date <= cp.r_date
```

**gerd.**

```sql
SELECT DISTINCT e.person_id
FROM ethos_production.omop_54.master_condition_occurrence e
JOIN chest_pain_dates cp ON cp.person_id = e.person_id
WHERE e.condition_concept_id IN (4144111, 30437, 23325, 318800)   -- gerd (4 concepts)
  AND e.condition_start_date <= cp.r_date
```

**anxiety.**

```sql
SELECT DISTINCT e.person_id
FROM ethos_production.omop_54.master_condition_occurrence e
JOIN chest_pain_dates cp ON cp.person_id = e.person_id
WHERE e.condition_concept_id IN (
        -- anxiety (12 concepts)
        442077, 434613, 36684319, 381537, 4009184, 4178114, 4221077, 4146660,
        4039212, 441542, 4056690, 4198826
    )
  AND e.condition_start_date <= cp.r_date
```

**gi\_dx.**

```sql
SELECT DISTINCT e.person_id
FROM ethos_production.omop_54.master_condition_occurrence e
JOIN chest_pain_dates cp ON cp.person_id = e.person_id
WHERE e.condition_concept_id IN (
        -- gerd (4 concepts)
        4144111, 30437, 23325, 318800,
        -- uw_gi_dx (69 concepts)
        201340, 4225273, 196456, 30753, 199866, 4289526, 443785, 4248429,
        199074, 27918, 198809, 192956, 200765, 196726, 4057513, 4027663,
        44783016, 444367, 195596, 4341763, 201614, 4195231, 192667, 4340493,
        4340960, 195300, 4288676, 4211001, 4296611, 193249, 195587, 4300203,
        201352, 4026144, 36716712, 4340964, 198246, 4232181, 4138962, 4163865,
        4340961, 4231580, 444420, 197924, 4150681, 4057953, 198475, 4174044,
        194991, 4027729, 4204555, 4046500, 45757783, 4222896, 46269837, 4173408,
        4146517, 4265479, 443889, 763023, 4169592, 4289830, 46270145, 4194543,
        44806251, 4294973, 4340962, 4336230, 196628
    )
  AND e.condition_start_date > cp.c_date
  AND e.condition_start_date <= cp.r_date
```

**anxiety\_later.**

```sql
SELECT DISTINCT e.person_id
FROM ethos_production.omop_54.master_condition_occurrence e
JOIN chest_pain_dates cp ON cp.person_id = e.person_id
WHERE e.condition_concept_id IN (
        -- anxiety (12 concepts)
        442077, 434613, 36684319, 381537, 4009184, 4178114, 4221077, 4146660,
        4039212, 441542, 4056690, 4198826
    )
  AND e.condition_start_date > cp.c_date
  AND e.condition_start_date <= cp.r_date
```

**muscle\_strain.**

```sql
SELECT DISTINCT e.person_id
FROM ethos_production.omop_54.master_condition_occurrence e
JOIN chest_pain_dates cp ON cp.person_id = e.person_id
WHERE e.condition_concept_id IN (315947, 4014526, 4016837, 81988)   -- uw_muscle_strain (4 concepts)
  AND e.condition_start_date > cp.c_date
  AND e.condition_start_date <= cp.r_date
```

**costochondritis.**

```sql
SELECT DISTINCT e.person_id
FROM ethos_production.omop_54.master_condition_occurrence e
JOIN chest_pain_dates cp ON cp.person_id = e.person_id
WHERE e.condition_concept_id IN (134461)   -- costochondritis (1 concept)
  AND e.condition_start_date > cp.c_date
  AND e.condition_start_date <= cp.r_date
```

**noncardiac\_cp.**

```sql
SELECT DISTINCT e.person_id
FROM ethos_production.omop_54.master_condition_occurrence e
JOIN chest_pain_dates cp ON cp.person_id = e.person_id
WHERE e.condition_concept_id IN (42539051)   -- uw_noncardiac_cp (1 concept)
  AND e.condition_start_date > cp.f_date
  AND e.condition_start_date <= cp.r_date
```

**explained\_dx.**

```sql
SELECT person_id FROM anxiety_later
UNION
SELECT person_id FROM gi_dx
UNION
SELECT person_id FROM muscle_strain
UNION
SELECT person_id FROM costochondritis
```

**ekg\_no\_abnormal\_code.**

```sql
SELECT person_id FROM ekg
EXCEPT
SELECT person_id FROM abnormal_ekg
```

**no\_further\_cardiac\_testing.**

```sql
SELECT person_id FROM chest_pain_dates
EXCEPT
SELECT person_id FROM extra_cardiac_testing
```

**no\_firm\_dx.**

```sql
SELECT person_id FROM chest_pain_dates
EXCEPT
SELECT DISTINCT e.person_id
FROM ethos_production.omop_54.master_condition_occurrence e
JOIN chest_pain_dates cp ON cp.person_id = e.person_id
WHERE e.condition_concept_id IN (
        -- uw_cad_dx (22 concepts)
        321318, 36712983, 314666, 4270024, 40481919, 36712982, 319844, 4296653,
        315286, 312327, 37309626, 43020460, 46270163, 4329847, 45766241, 46270162,
        37312532, 45766114, 4108677, 4108218, 45766116, 45766075,
        -- gerd (4 concepts)
        4144111, 30437, 23325, 318800,
        -- uw_gi_dx (69 concepts)
        201340, 4225273, 196456, 30753, 199866, 4289526, 443785, 4248429,
        199074, 27918, 198809, 192956, 200765, 196726, 4057513, 4027663,
        44783016, 444367, 195596, 4341763, 201614, 4195231, 192667, 4340493,
        4340960, 195300, 4288676, 4211001, 4296611, 193249, 195587, 4300203,
        201352, 4026144, 36716712, 4340964, 198246, 4232181, 4138962, 4163865,
        4340961, 4231580, 444420, 197924, 4150681, 4057953, 198475, 4174044,
        194991, 4027729, 4204555, 4046500, 45757783, 4222896, 46269837, 4173408,
        4146517, 4265479, 443889, 763023, 4169592, 4289830, 46270145, 4194543,
        44806251, 4294973, 4340962, 4336230, 196628,
        -- anxiety (12 concepts)
        442077, 434613, 36684319, 381537, 4009184, 4178114, 4221077, 4146660,
        4039212, 441542, 4056690, 4198826,
        -- uw_muscle_strain (4 concepts)
        315947, 4014526, 4016837, 81988,
        -- costochondritis (1 concept)
        134461,
        -- uw_noncardiac_cp (1 concept)
        42539051
    )
  AND e.condition_start_date <= cp.r_date
```

---

### Predicate and Composite Validation — Hit Rates Against the Chest Pain Cohort (n=150,664)

The tables below report how often each predicate and composite is true for the 150,664 applicants with a chest pain event on or before R. The cohort query gives 150,697 persons with an application date. The other 33 persons have chest pain events only after R, and every count leaves them out. See the Validation Query section below for the full query.

**Atomic Predicates**

| Predicate | n | % of total |
| :---- | :---- | :---- |
| age\_sex\_high\_risk | 54,376 | 36.091% |
| hx\_cad | 8,187 | 5.434% |
| abnormal\_ekg | 17,072 | 11.331% |
| extra\_cardiac\_testing | 22,818 | 15.145% |
| rx\_nitrates | 1,750 | 1.162% |
| troponin | 61,341 | 40.714% |
| ekg | 123,829 | 82.189% |
| gerd | 50,809 | 33.723% |
| anxiety | 55,507 | 36.842% |
| gi\_dx | 34,427 | 22.850% |
| anxiety\_later | 34,194 | 22.696% |
| muscle\_strain | 740 | 0.491% |
| costochondritis | 1,079 | 0.716% |
| noncardiac\_cp | 1,044 | 0.693% |
| explained\_dx | 56,639 | 37.593% |
| ekg\_no\_abnormal\_code | 107,276 | 71.202% |
| no\_further\_cardiac\_testing | 127,846 | 84.855% |
| no\_firm\_dx | 57,359 | 38.071% |

**Composites**

| Composite | n | % of total |
| :---- | :---- | :---- |
| high\_risk\_any | 75,080 | 49.833% |
| A1 | 68,157 | 45.238% |
| A2 | 101,563 | 67.410% |
| A3 | 108,237 | 71.840% |
| A4 | 53,459 | 35.482% |
| A5 | 1,044 | 0.693% |
| A6 | 91,952 | 61.031% |
| R1 | 8,884 | 5.897% |
| R2 | 5,859 | 3.889% |
| D1 | 2,561 | 1.700% |

**Time Cut-offs**

The time rows depend on months out. The table repeats them at other cut-offs. The rows of the draft use 6 months, 12 months, and 24 months.

| Cut-off (months) | A1 | R1 | R2 | D1 | A6 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| 3 | 72,080 | 4,310 | 2,858 | 669 | 142,850 |
| 6 | 68,157 | 8,884 | 5,859 | 1,360 | 134,353 |
| 12 | 61,102 | 17,275 | 11,426 | 2,561 | 118,907 |
| 24 | 48,510 | 31,638 | 21,396 | 4,377 | 91,952 |

- A1: no high-risk feature and more than the cut-off.  
- R1: any high-risk feature and less than the cut-off.  
- R2: no firm diagnosis and less than the cut-off.  
- D1: CAD history and less than the cut-off.  
- A6: coded more than the cut-off ago.  

> **Note:** The counts come from the notebook `Chestpain_Sean_predicates.ipynb`. A local test of the Validation Query on the same extract, outside Snowflake, gives the same counts for all predicates, composites, and cut-offs. A run in Snowflake is the final check. The counts describe the claims data and do not validate the rules.

---

### Reference Concept IDs

The table lists every concept of every code set, with the concepts of most applicants first. The queries show the same concept identifiers inline. The last two rows are the gender concepts of the age predicate.

| Code set | Concept | Type | Concept ID |
| :---- | :---- | :---- | :---- |
| chest\_pain | Chest pain | Condition · SNOMED | 77670 |
| chest\_pain | Precordial pain | Condition · SNOMED | 134159 |
| chest\_pain | Chest pain on breathing | Condition · SNOMED | 4168213 |
| chest\_pain | Pain of intercostal space | Condition · SNOMED | 42539051 |
| uw\_cad\_dx | Angina pectoris | Condition · SNOMED | 321318 |
| uw\_cad\_dx | Angina co-occurrent and due to coronary arteriosclerosis | Condition · SNOMED | 36712983 |
| uw\_cad\_dx | Old myocardial infarction | Condition · SNOMED | 314666 |
| uw\_cad\_dx | Acute non-ST segment elevation myocardial infarction | Condition · SNOMED | 4270024 |
| uw\_cad\_dx | Coronary atherosclerosis | Condition · SNOMED | 40481919 |
| uw\_cad\_dx | Unstable angina co-occurrent and due to coronary arteriosclerosis | Condition · SNOMED | 36712982 |
| uw\_cad\_dx | Acute ischemic heart disease | Condition · SNOMED | 319844 |
| uw\_cad\_dx | Acute ST segment elevation myocardial infarction | Condition · SNOMED | 4296653 |
| uw\_cad\_dx | Chronic ischemic heart disease | Condition · SNOMED | 315286 |
| uw\_cad\_dx | Acute myocardial infarction | Condition · SNOMED | 312327 |
| uw\_cad\_dx | Myocardial infarction due to demand ischemia | Condition · SNOMED | 37309626 |
| uw\_cad\_dx | Acute ST segment elevation myocardial infarction involving left anterior descending coronary artery | Condition · SNOMED | 43020460 |
| uw\_cad\_dx | Acute ST segment elevation myocardial infarction due to right coronary artery occlusion | Condition · SNOMED | 46270163 |
| uw\_cad\_dx | Myocardial infarction | Condition · SNOMED | 4329847 |
| uw\_cad\_dx | Subsequent non-ST segment elevation myocardial infarction | Condition · SNOMED | 45766241 |
| uw\_cad\_dx | Acute ST segment elevation myocardial infarction due to left coronary artery occlusion | Condition · SNOMED | 46270162 |
| uw\_cad\_dx | Coronary arteriosclerosis in artery of transplanted heart | Condition · SNOMED | 37312532 |
| uw\_cad\_dx | Subsequent ST segment elevation myocardial infarction | Condition · SNOMED | 45766114 |
| uw\_cad\_dx | Subsequent myocardial infarction of anterior wall | Condition · SNOMED | 4108677 |
| uw\_cad\_dx | Subsequent myocardial infarction of inferior wall | Condition · SNOMED | 4108218 |
| uw\_cad\_dx | Acute ST segment elevation myocardial infarction of inferior wall | Condition · SNOMED | 45766116 |
| uw\_cad\_dx | Acute anterior ST segment elevation myocardial infarction | Condition · SNOMED | 45766075 |
| uw\_abnormal\_ekg | Electrocardiogram abnormal | Condition · SNOMED | 320536 |
| uw\_cardiac\_testing | Echocardiography, transthoracic, real-time with image documentation (2D), includes M-mode recording, when performed, complete, with spectral Doppler echocardiography, and with color flow Doppler echocardiography | Procedure · CPT4 | 2313869 |
| uw\_cardiac\_testing | Myocardial perfusion imaging, tomographic (SPECT) (including attenuation correction, qualitative or quantitative wall motion, ejection fraction by first pass or gated technique, additional quantification, when performed); multiple studies, at rest and/... | Procedure · CPT4 | 40756833 |
| uw\_cardiac\_testing | Echocardiography, transthoracic, real-time with image documentation (2D), includes M-mode recording, when performed, during rest and cardiovascular stress test using treadmill, bicycle exercise and/or pharmacologically induced stress, with interpretati... | Procedure · CPT4 | 2313883 |
| uw\_cardiac\_testing | Computed tomographic angiography, heart, coronary arteries and bypass grafts (when present), with contrast material, including 3D image postprocessing (including evaluation of cardiac structure and morphology, assessment of cardiac function, and evalua... | Procedure · CPT4 | 40756829 |
| uw\_cardiac\_testing | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation; with left heart catheterization including intraprocedural injection(s) for left... | Procedure · CPT4 | 40756950 |
| uw\_cardiac\_testing | Echocardiography, transthoracic, real-time with image documentation (2D), includes M-mode recording, when performed, during rest and cardiovascular stress test using treadmill, bicycle exercise and/or pharmacologically induced stress, with interpretati... | Procedure · CPT4 | 2313882 |
| uw\_cardiac\_testing | CT of heart without contrast with calcium scoring | Procedure · SNOMED | 42535629 |
| uw\_cardiac\_testing | Echocardiography, transthoracic, real-time with image documentation (2D), includes M-mode recording, when performed, follow-up or limited study | Procedure · CPT4 | 2313871 |
| uw\_cardiac\_testing | Transthoracic echocardiography with contrast, or without contrast followed by with contrast, real-time with image documentation (2d), includes m-mode recording, when performed, complete, with spectral doppler echocardiography, and with color flow doppl... | Procedure · HCPCS | 2616271 |
| uw\_cardiac\_testing | Echocardiography, transesophageal, real-time with image documentation (2D) (with or without M-mode recording); including probe placement, image acquisition, interpretation and report | Procedure · CPT4 | 2313872 |
| uw\_cardiac\_testing | Use of echocardiographic contrast agent during stress echocardiography (List separately in addition to code for primary procedure) | Procedure · CPT4 | 2313884 |
| uw\_cardiac\_testing | Cardiac magnetic resonance imaging for morphology and function without contrast material(s), followed by contrast material(s) and further sequences | Procedure · CPT4 | 2211577 |
| uw\_cardiac\_testing | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation | Procedure · CPT4 | 40756852 |
| uw\_cardiac\_testing | Myocardial imaging, positron emission tomography (PET), perfusion study (including ventricular wall motion[s] and/or ejection fraction[s], when performed); multiple studies at rest and stress (exercise or pharmacologic), with concurrently acquired comp... | Procedure · CPT4 | 709987 |
| uw\_cardiac\_testing | Absolute quantitation of myocardial blood flow (AQMBF), positron emission tomography (PET), rest and pharmacologic stress (List separately in addition to code for primary procedure) | Procedure · CPT4 | 709990 |
| uw\_cardiac\_testing | Myocardial imaging, positron emission tomography (PET), perfusion study (including ventricular wall motion[s] and/or ejection fraction[s], when performed); multiple studies at rest and stress (exercise or pharmacologic) | Procedure · CPT4 | 2211998 |
| uw\_cardiac\_testing | Intravascular Doppler velocity and/or pressure derived coronary flow reserve measurement (coronary vessel or graft) during coronary angiography including pharmacologically induced stress, when performed; initial vessel (List separately in addition to c... | Procedure · CPT4 | 2313913 |
| uw\_cardiac\_testing | Myocardial perfusion imaging, tomographic (SPECT) (including attenuation correction, qualitative or quantitative wall motion, ejection fraction by first pass or gated technique, additional quantification, when performed); single study, at rest or stres... | Procedure · CPT4 | 40756922 |
| uw\_cardiac\_testing | Transthoracic echocardiography, with contrast, or without contrast followed by with contrast, real-time with image documentation (2d), includes m-mode recording, when performed, during rest and cardiovascular stress test using treadmill, bicycle exerci... | Procedure · HCPCS | 2616272 |
| uw\_cardiac\_testing | Noninvasive estimate of coronary fractional flow reserve (FFR) derived from augmentative software analysis of the data set from a coronary computed tomography angiography, with interpretation and report by a physician or other qualified health care pro... | Procedure · CPT4 | 724752 |
| uw\_cardiac\_testing | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation; with right and left heart catheterization including intraprocedural injection(s)... | Procedure · CPT4 | 40756944 |
| uw\_cardiac\_testing | Transthoracic echocardiography with contrast, or without contrast followed by with contrast, real-time with image documentation (2d), includes m-mode recording, when performed, during rest and cardiovascular stress test using treadmill, bicycle exercis... | Procedure · HCPCS | 2616270 |
| uw\_cardiac\_testing | Echocardiography, transthoracic, real-time with image documentation (2D), includes M-mode recording, when performed, complete, without spectral or color Doppler echocardiography | Procedure · CPT4 | 2313870 |
| uw\_cardiac\_testing | Injection procedure during cardiac catheterization including imaging supervision, interpretation, and report; for supravalvular aortography (List separately in addition to code for primary procedure) | Procedure · CPT4 | 40756942 |
| uw\_cardiac\_testing | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation; with left heart catheterization including intraprocedural injection(s) for left... | Procedure · CPT4 | 40756979 |
| uw\_cardiac\_testing | Cardiac magnetic resonance imaging for morphology and function without contrast material(s), followed by contrast material(s) and further sequences; with stress imaging | Procedure · CPT4 | 2211579 |
| uw\_cardiac\_testing | Intravascular Doppler velocity and/or pressure derived coronary flow reserve measurement (coronary vessel or graft) during coronary angiography including pharmacologically induced stress, when performed; each additional vessel (List separately in addit... | Procedure · CPT4 | 2313914 |
| uw\_cardiac\_testing | Myocardial perfusion imaging, planar (including qualitative or quantitative wall motion, ejection fraction by first pass or gated technique, additional quantification, when performed); multiple studies, at rest and/or stress (exercise or pharmacologic)... | Procedure · CPT4 | 40757098 |
| uw\_cardiac\_testing | Noninvasive estimated coronary fractional flow reserve (FFR) derived from coronary computed tomography angiography data using computation fluid dynamics physiologic simulation software analysis of functional data to assess the severity of ... (Deprecated) | Procedure · CPT4 | 725130 |
| uw\_cardiac\_testing | Noninvasive estimated coronary fractional flow reserve (FFR) derived from coronary computed tomography angiography data using computation fluid dynamics physiologic simulation software analysis of functional data to assess the severity of ... (Deprecated) | Procedure · CPT4 | 725129 |
| uw\_cardiac\_testing | Echocardiography, transesophageal, real-time with image documentation (2D) (with or without M-mode recording); placement of transesophageal probe only | Procedure · CPT4 | 2313873 |
| uw\_cardiac\_testing | Noninvasive estimated coronary fractional flow reserve (FFR) derived from coronary computed tomography angiography data using computation fluid dynamics physiologic simulation software analysis of functional data to assess the severity of ... (Deprecated) | Procedure · CPT4 | 725128 |
| uw\_cardiac\_testing | Transthoracic echocardiography with contrast, or without contrast followed by with contrast, real-time with image documentation (2d), includes m-mode recording, when performed, follow-up or limited study | Procedure · HCPCS | 2616266 |
| uw\_cardiac\_testing | Echocardiography, transesophageal, real-time with image documentation (2D) (with or without M-mode recording); image acquisition, interpretation and report only | Procedure · CPT4 | 2313874 |
| uw\_cardiac\_testing | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation; with right heart catheterization | Procedure · CPT4 | 40756899 |
| uw\_cardiac\_testing | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation; with catheter placement(s) in bypass graft(s) (internal mammary, free arterial,... | Procedure · CPT4 | 40756911 |
| uw\_cardiac\_testing | Myocardial perfusion imaging, planar (including qualitative or quantitative wall motion, ejection fraction by first pass or gated technique, additional quantification, when performed); single study, at rest or stress (exercise or pharmacologic) | Procedure · CPT4 | 40757133 |
| uw\_cardiac\_testing | Transthoracic echocardiography with contrast, or without contrast followed by with contrast, real-time with image documentation (2d), includes m-mode recording, when performed, complete, without spectral or color doppler echocardiography | Procedure · HCPCS | 2616265 |
| uw\_cardiac\_testing | Transesophageal echocardiography (tee) with contrast, or without contrast followed by with contrast, real time with image documentation (2d) (with or without m-mode recording); including probe placement, image acquisition, interpretation and report | Procedure · HCPCS | 2616267 |
| uw\_cardiac\_testing | Noninvasive estimated coronary fractional flow reserve (FFR) derived from coronary computed tomography angiography data using computation fluid dynamics physiologic simulation software analysis of functional data to assess the severity of ... (Deprecated) | Procedure · CPT4 | 725127 |
| uw\_cardiac\_testing | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation; with right and left heart catheterization including intraprocedural injection(s)... | Procedure · CPT4 | 40756857 |
| uw\_cardiac\_testing | PET myocardial metabolism study | Procedure · SNOMED | 37109083 |
| uw\_cardiac\_testing | Iliac and/or femoral artery angiography, non-selective, bilateral or ipsilateral to catheter insertion, performed at the same time as cardiac catheterization and/or coronary angiography, includes positioning or placement of the catheter in the distal a... | Procedure · HCPCS | 2617361 |
| uw\_cardiac\_testing | Myocardial imaging, positron emission tomography (PET), combined perfusion with metabolic evaluation study (including ventricular wall motion[s] and/or ejection fraction[s], when performed), dual radiotracer (eg, myocardial viability); with concurrentl... | Procedure · CPT4 | 709989 |
| uw\_cardiac\_testing | Myocardial imaging, positron emission tomography (PET), metabolic evaluation study (including ventricular wall motion[s] and/or ejection fraction[s], when performed), single study; with concurrently acquired computed tomography transmission scan | Procedure · CPT4 | 709985 |
| uw\_cardiac\_testing | Injection procedure during cardiac catheterization including imaging supervision, interpretation, and report; for selective right ventricular or right atrial angiography (List separately in addition to code for primary procedure) | Procedure · CPT4 | 40756983 |
| uw\_cardiac\_testing | Injection procedure during cardiac catheterization including imaging supervision, interpretation, and report; for nonselective pulmonary arterial angiography (List separately in addition to code for primary procedure) | Procedure · CPT4 | 40756943 |
| uw\_cardiac\_testing | Myocardial contrast perfusion echocardiography, at rest or with stress, for assessment of myocardial ischemia or viability (List separately in addition to code for primary procedure) | Procedure · CPT4 | 42628042 |
| uw\_cardiac\_testing | Myocardial imaging, positron emission tomography (PET), perfusion study (including ventricular wall motion[s] and/or ejection fraction[s], when performed); single study, at rest or stress (exercise or pharmacologic) | Procedure · CPT4 | 2211997 |
| uw\_cardiac\_testing | Catheter placement in coronary artery(s) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation; with catheter placement(s) in bypass graft(s) (internal mammary, free arterial,... | Procedure · CPT4 | 40757138 |
| uw\_cardiac\_testing | Injection procedure during cardiac catheterization including imaging supervision, interpretation, and report; for selective pulmonary arterial angiography, bilateral (List separately in addition to code for primary procedure) | Procedure · CPT4 | 1552298 |
| uw\_cardiac\_testing | Myocardial imaging, positron emission tomography (PET), perfusion study (including ventricular wall motion[s] and/or ejection fraction[s], when performed); single study, at rest or stress (exercise or pharmacologic), with concurrently acquired computed... | Procedure · CPT4 | 709986 |
| uw\_cardiac\_testing | Catheter placement in coronary artery(ies) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation, with left heart catheterization including intraprocedural injection(s) for lef... | Procedure · HCPCS | 1126196 |
| uw\_cardiac\_testing | Catheter placement in coronary artery(ies) for coronary angiography, including intraprocedural injection(s) for coronary angiography, imaging supervision and interpretation, with left heart catheterization including intraprocedural injection(s) for lef... | Procedure · HCPCS | 1126197 |
| uw\_cardiac\_testing | Injection procedure during cardiac catheterization including imaging supervision, interpretation, and report; for selective pulmonary arterial angiography, unilateral (List separately in addition to code for primary procedure) | Procedure · CPT4 | 1552297 |
| nitrates | nitroglycerin 0.4 MG Sublingual Tablet | Drug · RxNorm | 19019336 |
| nitrates | nitroglycerin Injection | Drug · RxNorm | 1593968 |
| nitrates | 24 HR isosorbide mononitrate 30 MG Extended Release Oral Tablet | Drug · RxNorm | 19082350 |
| nitrates | nitroglycerin 0.02 MG/MG Topical Ointment [Nitro-Bid] | Drug · RxNorm | 19035072 |
| nitrates | nitroglycerin 0.3 MG Sublingual Tablet | Drug · RxNorm | 19019335 |
| nitrates | 24 HR nitroglycerin 0.1 MG/HR Transdermal System | Drug · RxNorm | 40163938 |
| nitrates | 24 HR nitroglycerin 0.2 MG/HR Transdermal System | Drug · RxNorm | 1362360 |
| nitrates | 24 HR isosorbide mononitrate 60 MG Extended Release Oral Tablet | Drug · RxNorm | 1383869 |
| nitrates | isosorbide dinitrate 5 MG Oral Tablet | Drug · RxNorm | 19080095 |
| nitrates | isosorbide dinitrate 10 MG Oral Tablet | Drug · RxNorm | 19100691 |
| nitrates | 24 HR nitroglycerin 0.4 MG/HR Transdermal System | Drug · RxNorm | 1362392 |
| nitrates | nitroglycerin 0.4 MG Sublingual Tablet [Nitrostat] | Drug · RxNorm | 19035279 |
| nitrates | isosorbide dinitrate 20 MG Oral Tablet | Drug · RxNorm | 19033627 |
| nitrates | isosorbide dinitrate 30 MG Oral Tablet | Drug · RxNorm | 1383930 |
| nitrates | nitroglycerin 0.4 MG/ACTUAT Mucosal Spray | Drug · RxNorm | 19126352 |
| nitrates | isosorbide mononitrate 10 MG Oral Tablet | Drug · RxNorm | 1383849 |
| nitrates | nitroglycerin 0.6 MG Sublingual Tablet | Drug · RxNorm | 19019337 |
| nitrates | 24 HR isosorbide mononitrate 120 MG Extended Release Oral Tablet | Drug · RxNorm | 1383850 |
| nitrates | isosorbide dinitrate 40 MG Oral Tablet | Drug · RxNorm | 19019078 |
| nitrates | isosorbide mononitrate 20 MG Oral Tablet | Drug · RxNorm | 1383851 |
| nitrates | nitroglycerin 2.5 MG Extended Release Oral Capsule | Drug · RxNorm | 19079057 |
| nitrates | nitroglycerin 6.5 MG Extended Release Oral Capsule | Drug · RxNorm | 19079082 |
| troponin | Troponin, quantitative | Measurement · CPT4 | 2212605 |
| troponin | Troponin, qualitative | Measurement · CPT4 | 2212610 |
| ekg | Electrocardiogram, routine ECG with at least 12 leads; interpretation and report only | Procedure · CPT4 | 2313816 |
| ekg | Electrocardiogram, routine ECG with at least 12 leads; with interpretation and report | Procedure · CPT4 | 2313814 |
| ekg | Electrocardiogram, routine ECG with at least 12 leads; tracing only, without interpretation and report | Procedure · CPT4 | 2313815 |
| ekg | Electrocardiogram, routine ecg with 12 leads; performed as a screening for the initial preventive physical examination with interpretation and report | Procedure · HCPCS | 2617470 |
| ekg | Electrocardiogram, routine ecg with 12 leads; tracing only, without interpretation and report, performed as a screening for the initial preventive physical examination | Procedure · HCPCS | 2617471 |
| gerd | Gastroesophageal reflux disease without esophagitis | Condition · SNOMED | 4144111 |
| gerd | Gastro-esophageal reflux disease with esophagitis | Condition · SNOMED | 30437 |
| gerd | Heartburn | Condition · SNOMED | 23325 |
| gerd | Gastroesophageal reflux disease | Condition · SNOMED | 318800 |
| anxiety | Anxiety disorder | Condition · SNOMED | 442077 |
| anxiety | Generalized anxiety disorder | Condition · SNOMED | 434613 |
| anxiety | Adjustment disorder with mixed anxiety and depressed mood | Condition · SNOMED | 36684319 |
| anxiety | Organic anxiety disorder | Condition · SNOMED | 381537 |
| anxiety | Dream anxiety disorder | Condition · SNOMED | 4009184 |
| anxiety | Organic anxiety disorder caused by psychoactive substance | Condition · SNOMED | 4178114 |
| anxiety | Cannabis-induced anxiety disorder | Condition · SNOMED | 4221077 |
| anxiety | Anxiety disorder caused by alcohol | Condition · SNOMED | 4146660 |
| anxiety | Separation anxiety disorder of childhood | Condition · SNOMED | 4039212 |
| anxiety | Anxiety | Condition · SNOMED | 441542 |
| anxiety | Sedative, hypnotic AND/OR anxiolytic-induced anxiety disorder | Condition · SNOMED | 4056690 |
| anxiety | Anxiety disorder caused by cocaine | Condition · SNOMED | 4198826 |
| uw\_gi\_dx | Gastritis | Condition · SNOMED | 201340 |
| uw\_gi\_dx | Chronic gastritis | Condition · SNOMED | 4225273 |
| uw\_gi\_dx | Gallstone | Condition · SNOMED | 196456 |
| uw\_gi\_dx | Esophagitis | Condition · SNOMED | 30753 |
| uw\_gi\_dx | Acute gastritis | Condition · SNOMED | 199866 |
| uw\_gi\_dx | Nonulcer dyspepsia | Condition · SNOMED | 4289526 |
| uw\_gi\_dx | Calculus of gallbladder with cholecystitis | Condition · SNOMED | 443785 |
| uw\_gi\_dx | Gastric ulcer without hemorrhage AND without perforation | Condition · SNOMED | 4248429 |
| uw\_gi\_dx | Acute pancreatitis | Condition · SNOMED | 199074 |
| uw\_gi\_dx | Eosinophilic esophagitis | Condition · SNOMED | 27918 |
| uw\_gi\_dx | Acute cholecystitis | Condition · SNOMED | 198809 |
| uw\_gi\_dx | Cholecystitis | Condition · SNOMED | 192956 |
| uw\_gi\_dx | Chronic cholecystitis | Condition · SNOMED | 200765 |
| uw\_gi\_dx | Gallbladder calculus with acute cholecystitis and no obstruction | Condition · SNOMED | 196726 |
| uw\_gi\_dx | Chronic superficial gastritis | Condition · SNOMED | 4057513 |
| uw\_gi\_dx | Peptic ulcer | Condition · SNOMED | 4027663 |
| uw\_gi\_dx | Calculus of gallbladder with acute and chronic cholecystitis | Condition · SNOMED | 44783016 |
| uw\_gi\_dx | Cholelithiasis without obstruction | Condition · SNOMED | 444367 |
| uw\_gi\_dx | Chronic pancreatitis | Condition · SNOMED | 195596 |
| uw\_gi\_dx | Gallstone acute pancreatitis | Condition · SNOMED | 4341763 |
| uw\_gi\_dx | Calculus of bile duct with cholecystitis | Condition · SNOMED | 201614 |
| uw\_gi\_dx | Acute gastric ulcer without hemorrhage AND without perforation | Condition · SNOMED | 4195231 |
| uw\_gi\_dx | Atrophic gastritis | Condition · SNOMED | 192667 |
| uw\_gi\_dx | Alcohol-induced acute pancreatitis | Condition · SNOMED | 4340493 |
| uw\_gi\_dx | Idiopathic acute pancreatitis | Condition · SNOMED | 4340960 |
| uw\_gi\_dx | Alcoholic gastritis | Condition · SNOMED | 195300 |
| uw\_gi\_dx | Acute and chronic cholecystitis | Condition · SNOMED | 4288676 |
| uw\_gi\_dx | Chronic gastric ulcer with hemorrhage | Condition · SNOMED | 4211001 |
| uw\_gi\_dx | Chronic gastric ulcer without hemorrhage AND without perforation | Condition · SNOMED | 4296611 |
| uw\_gi\_dx | Acute hemorrhagic gastritis | Condition · SNOMED | 193249 |
| uw\_gi\_dx | Cholelithiasis AND cholecystitis with obstruction | Condition · SNOMED | 195587 |
| uw\_gi\_dx | Cholelithiasis with obstruction | Condition · SNOMED | 4300203 |
| uw\_gi\_dx | Gallbladder calculus with acute cholecystitis and obstruction | Condition · SNOMED | 201352 |
| uw\_gi\_dx | Bile duct calculus with acute cholecystitis | Condition · SNOMED | 4026144 |
| uw\_gi\_dx | Calculus of gallbladder without cholecystitis or cholangitis | Condition · SNOMED | 36716712 |
| uw\_gi\_dx | Alcohol-induced chronic pancreatitis | Condition · SNOMED | 4340964 |
| uw\_gi\_dx | Congenital hiatus hernia | Condition · SNOMED | 198246 |
| uw\_gi\_dx | Chronic duodenal ulcer with hemorrhage | Condition · SNOMED | 4232181 |
| uw\_gi\_dx | Acute duodenal ulcer without hemorrhage AND without perforation | Condition · SNOMED | 4138962 |
| uw\_gi\_dx | Acute peptic ulcer without hemorrhage AND without perforation | Condition · SNOMED | 4163865 |
| uw\_gi\_dx | Drug-induced acute pancreatitis | Condition · SNOMED | 4340961 |
| uw\_gi\_dx | Acute gastric ulcer with hemorrhage | Condition · SNOMED | 4231580 |
| uw\_gi\_dx | Calculus of bile duct with chronic cholecystitis | Condition · SNOMED | 444420 |
| uw\_gi\_dx | Bile duct calculus with acute cholecystitis and obstruction | Condition · SNOMED | 197924 |
| uw\_gi\_dx | Chronic gastric ulcer with perforation | Condition · SNOMED | 4150681 |
| uw\_gi\_dx | Acute gastric ulcer with perforation | Condition · SNOMED | 4057953 |
| uw\_gi\_dx | Gallstone ileus | Condition · SNOMED | 198475 |
| uw\_gi\_dx | Chronic peptic ulcer with hemorrhage | Condition · SNOMED | 4174044 |
| uw\_gi\_dx | Calculus of gallbladder with acute cholecystitis | Condition · SNOMED | 194991 |
| uw\_gi\_dx | Acute duodenal ulcer with hemorrhage | Condition · SNOMED | 4027729 |
| uw\_gi\_dx | Chronic peptic ulcer without hemorrhage AND without perforation | Condition · SNOMED | 4204555 |
| uw\_gi\_dx | Acute peptic ulcer with hemorrhage | Condition · SNOMED | 4046500 |
| uw\_gi\_dx | Gastric hemorrhage due to alcoholic gastritis | Condition · SNOMED | 45757783 |
| uw\_gi\_dx | Chronic duodenal ulcer without hemorrhage AND without perforation | Condition · SNOMED | 4222896 |
| uw\_gi\_dx | Gastric hemorrhage due to chronic superficial gastritis | Condition · SNOMED | 46269837 |
| uw\_gi\_dx | Chronic duodenal ulcer with perforation | Condition · SNOMED | 4173408 |
| uw\_gi\_dx | Chronic peptic ulcer with perforation | Condition · SNOMED | 4146517 |
| uw\_gi\_dx | Acute duodenal ulcer with perforation | Condition · SNOMED | 4265479 |
| uw\_gi\_dx | Calculus of bile duct with chronic cholecystitis with obstruction | Condition · SNOMED | 443889 |
| uw\_gi\_dx | Calculus of gallbladder and bile duct with cholecystitis | Condition · SNOMED | 763023 |
| uw\_gi\_dx | Acute gastric ulcer with hemorrhage and perforation | Condition · SNOMED | 4169592 |
| uw\_gi\_dx | Chronic duodenal ulcer with hemorrhage AND perforation | Condition · SNOMED | 4289830 |
| uw\_gi\_dx | Gastric hemorrhage due to atrophic gastritis | Condition · SNOMED | 46270145 |
| uw\_gi\_dx | Acute peptic ulcer with perforation | Condition · SNOMED | 4194543 |
| uw\_gi\_dx | Biliary acute pancreatitis | Condition · SNOMED | 44806251 |
| uw\_gi\_dx | Chronic gastric ulcer with hemorrhage and with perforation | Condition · SNOMED | 4294973 |
| uw\_gi\_dx | Cytomegaloviral pancreatitis | Condition · SNOMED | 4340962 |
| uw\_gi\_dx | Acute duodenal ulcer with hemorrhage AND perforation | Condition · SNOMED | 4336230 |
| uw\_gi\_dx | Mumps pancreatitis | Condition · SNOMED | 196628 |
| uw\_muscle\_strain | Thoracic back sprain | Condition · SNOMED | 315947 |
| uw\_muscle\_strain | Sternoclavicular sprain | Condition · SNOMED | 4014526 |
| uw\_muscle\_strain | Chondrocostal joint sprain | Condition · SNOMED | 4016837 |
| uw\_muscle\_strain | Sprain of sternum | Condition · SNOMED | 81988 |
| costochondritis | Tietze's disease | Condition · SNOMED | 134461 |
| uw\_noncardiac\_cp | Pain of intercostal space | Condition · SNOMED | 42539051 |
| age\_sex\_high\_risk | Male | Gender · Gender | 8507 |
| age\_sex\_high\_risk | Female | Gender · Gender | 8532 |

---

## Validation Query

This section contains the full query that evaluates all predicates and composites for every person in the cohort. The query returns one row per person. Each predicate and each composite becomes one column, with 1 for true and 0 for false. The columns work like a one-hot encoding. A person with several true predicates has several 1s. The sum of each column is the count in the hit-rate tables above.

### Backtest Population

- Cohort: the cohort query version 0.3 (step `cohort`), Ethos persons with chest pain diagnosis codes R07.2, R07.8, R07.82, R07.89, or R07.9, confirmed in OMOP  
- Policies: policies with a product of the list 1, 5, 14, 15, 21, 25 and an underwriting process other than `TBD`  
- Index date: the latest interview start date over the policies of the person  
- Scope: persons with a chest pain event on or before the index date (n=150,664 of 150,697)  

### Query

```sql
WITH
    cp_codes AS (
        SELECT column1 AS code                                       -- ICD10CM, dots removed
        FROM VALUES ('R072'), ('R078'), ('R0782'), ('R0789'), ('R079')
    ),

    -- 1) PCP anchor (one row per policy; PCP grain is policy x carrier x product)
    valid_policies AS (
        SELECT TRY_TO_NUMBER(bk_policy_id)::VARCHAR AS policy_id,
               MAX(ts_interview_started_at)         AS interview_started_ts
        FROM ethos_production.dbt_mart_transformation.m_policy_carrier_product
        WHERE dim_underwriting_process IS DISTINCT FROM 'TBD'
          AND bk_product_id IN (1, 5, 14, 15, 21, 25)
        GROUP BY 1
    ),
    policy_person AS (
        SELECT DISTINCT v.policy_id, era.person_id, v.interview_started_ts
        FROM ethos_production.omop_54.policy_era era
        JOIN valid_policies v
          ON v.policy_id = TRY_TO_NUMBER(era.policy_id)::VARCHAR
        WHERE era.person_id IS NOT NULL
    ),

    -- 2) DX evidence -> OMOP person
    ethos_persons AS (
        SELECT DISTINCT pp.person_id
        FROM ethos_production.airflow_uw_evidence.dx_evidence_flattened d
        JOIN policy_person pp
          ON pp.policy_id = TRY_TO_NUMBER(d.policy_id)::VARCHAR
        WHERE d.description ILIKE '%chest pain%'
           OR REPLACE(UPPER(TRIM(d.medicalcode)), '.', '') IN (SELECT code FROM cp_codes)
    ),

    -- 3) OMOP concept set: listed ICD10CM codes only
    cp_concepts AS (
        SELECT c.concept_id
        FROM ethos_production.omop_54.concept c
        WHERE c.vocabulary_id = 'ICD10CM'
          AND REPLACE(c.concept_code, '.', '') IN (SELECT code FROM cp_codes)
    ),

    -- 4) OMOP hits on source concept, restricted to Ethos persons
    omop_persons AS (
        SELECT co.person_id
        FROM ethos_production.omop_54.condition_occurrence co
        JOIN ethos_persons e ON e.person_id = co.person_id
        WHERE co.condition_source_concept_id IN (SELECT concept_id FROM cp_concepts)

        UNION

        SELECT o.person_id
        FROM ethos_production.omop_54.observation o
        JOIN ethos_persons e ON e.person_id = o.person_id
        WHERE o.observation_source_concept_id IN (SELECT concept_id FROM cp_concepts)
    ),
    cohort AS (
        SELECT op.person_id,
               MAX(pp.interview_started_ts)::DATE AS latest_interview_started_date
        FROM omop_persons op
        JOIN policy_person pp ON pp.person_id = op.person_id
        GROUP BY op.person_id
    ),
    chest_pain_dates AS (
        SELECT a.person_id, a.r_date, a.f_date, a.c_date,
               DATEDIFF(day, a.c_date, a.r_date) / 30.4375 AS months_out
        FROM (
            SELECT e.person_id, coh.latest_interview_started_date AS r_date,
                   MIN(e.condition_start_date) AS f_date,
                   MAX(e.condition_start_date) AS c_date
            FROM ethos_production.omop_54.master_condition_occurrence e
            JOIN cohort coh ON coh.person_id = e.person_id
            WHERE e.condition_concept_id IN (77670, 134159, 4168213, 42539051)   -- chest_pain (4 concepts)
              AND e.condition_start_date <= coh.latest_interview_started_date
            GROUP BY e.person_id, coh.latest_interview_started_date
        ) a
    ),
    age_sex_high_risk AS (
        -- older than 45 (man) or 55 (woman), in completed years: the 46th or 56th birthday is on or before C
        SELECT DISTINCT cp.person_id
        FROM chest_pain_dates cp
        JOIN ethos_production.omop_54.person p ON p.person_id = cp.person_id
        WHERE (p.gender_concept_id = 8507   -- male
             AND cp.c_date >= DATEADD(year, 46, p.birth_datetime))
           OR (p.gender_concept_id = 8532   -- female
             AND cp.c_date >= DATEADD(year, 56, p.birth_datetime))
    ),
    hx_cad AS (
        SELECT DISTINCT e.person_id
        FROM ethos_production.omop_54.master_condition_occurrence e
        JOIN chest_pain_dates cp ON cp.person_id = e.person_id
        WHERE e.condition_concept_id IN (
                -- uw_cad_dx (22 concepts)
                321318, 36712983, 314666, 4270024, 40481919, 36712982, 319844, 4296653,
                315286, 312327, 37309626, 43020460, 46270163, 4329847, 45766241, 46270162,
                37312532, 45766114, 4108677, 4108218, 45766116, 45766075
            )
          AND e.condition_start_date <= cp.c_date
    ),
    abnormal_ekg AS (
        SELECT DISTINCT e.person_id
        FROM ethos_production.omop_54.master_condition_occurrence e
        JOIN chest_pain_dates cp ON cp.person_id = e.person_id
        WHERE e.condition_concept_id IN (320536)   -- uw_abnormal_ekg (1 concept)
          AND e.condition_start_date <= cp.r_date
    ),
    extra_cardiac_testing AS (
        SELECT DISTINCT e.person_id
        FROM ethos_production.omop_54.master_procedure_occurrence e
        JOIN chest_pain_dates cp ON cp.person_id = e.person_id
        WHERE e.procedure_concept_id IN (
                -- uw_cardiac_testing (55 concepts)
                2313869, 40756833, 2313883, 40756829, 40756950, 2313882, 42535629, 2313871,
                2616271, 2313872, 2313884, 2211577, 40756852, 709987, 709990, 2211998,
                2313913, 40756922, 2616272, 724752, 40756944, 2616270, 2313870, 40756942,
                40756979, 2211579, 2313914, 40757098, 725130, 725129, 2313873, 725128,
                2616266, 2313874, 40756899, 40756911, 40757133, 2616265, 2616267, 725127,
                40756857, 37109083, 2617361, 709989, 709985, 40756983, 40756943, 42628042,
                2211997, 40757138, 1552298, 709986, 1126196, 1126197, 1552297
            )
          AND e.procedure_date > cp.c_date
          AND e.procedure_date <= cp.r_date
    ),
    rx_nitrates AS (
        SELECT DISTINCT e.person_id
        FROM ethos_production.omop_54.master_drug_exposure e
        JOIN chest_pain_dates cp ON cp.person_id = e.person_id
        WHERE e.drug_concept_id IN (
                -- nitrates (22 concepts)
                19019336, 1593968, 19082350, 19035072, 19019335, 40163938, 1362360, 1383869,
                19080095, 19100691, 1362392, 19035279, 19033627, 1383930, 19126352, 1383849,
                19019337, 1383850, 19019078, 1383851, 19079057, 19079082
            )
          AND e.drug_exposure_start_date <= cp.r_date
    ),
    troponin AS (
        SELECT DISTINCT e.person_id
        FROM ethos_production.omop_54.master_measurement e
        JOIN chest_pain_dates cp ON cp.person_id = e.person_id
        WHERE e.measurement_concept_id IN (2212605, 2212610)   -- troponin (2 concepts)
          AND e.measurement_date <= cp.r_date
    ),
    ekg AS (
        SELECT DISTINCT e.person_id
        FROM ethos_production.omop_54.master_procedure_occurrence e
        JOIN chest_pain_dates cp ON cp.person_id = e.person_id
        WHERE e.procedure_concept_id IN (2313816, 2313814, 2313815, 2617470, 2617471)   -- ekg (5 concepts)
          AND e.procedure_date <= cp.r_date
    ),
    gerd AS (
        SELECT DISTINCT e.person_id
        FROM ethos_production.omop_54.master_condition_occurrence e
        JOIN chest_pain_dates cp ON cp.person_id = e.person_id
        WHERE e.condition_concept_id IN (4144111, 30437, 23325, 318800)   -- gerd (4 concepts)
          AND e.condition_start_date <= cp.r_date
    ),
    anxiety AS (
        SELECT DISTINCT e.person_id
        FROM ethos_production.omop_54.master_condition_occurrence e
        JOIN chest_pain_dates cp ON cp.person_id = e.person_id
        WHERE e.condition_concept_id IN (
                -- anxiety (12 concepts)
                442077, 434613, 36684319, 381537, 4009184, 4178114, 4221077, 4146660,
                4039212, 441542, 4056690, 4198826
            )
          AND e.condition_start_date <= cp.r_date
    ),
    gi_dx AS (
        SELECT DISTINCT e.person_id
        FROM ethos_production.omop_54.master_condition_occurrence e
        JOIN chest_pain_dates cp ON cp.person_id = e.person_id
        WHERE e.condition_concept_id IN (
                -- gerd (4 concepts)
                4144111, 30437, 23325, 318800,
                -- uw_gi_dx (69 concepts)
                201340, 4225273, 196456, 30753, 199866, 4289526, 443785, 4248429,
                199074, 27918, 198809, 192956, 200765, 196726, 4057513, 4027663,
                44783016, 444367, 195596, 4341763, 201614, 4195231, 192667, 4340493,
                4340960, 195300, 4288676, 4211001, 4296611, 193249, 195587, 4300203,
                201352, 4026144, 36716712, 4340964, 198246, 4232181, 4138962, 4163865,
                4340961, 4231580, 444420, 197924, 4150681, 4057953, 198475, 4174044,
                194991, 4027729, 4204555, 4046500, 45757783, 4222896, 46269837, 4173408,
                4146517, 4265479, 443889, 763023, 4169592, 4289830, 46270145, 4194543,
                44806251, 4294973, 4340962, 4336230, 196628
            )
          AND e.condition_start_date > cp.c_date
          AND e.condition_start_date <= cp.r_date
    ),
    anxiety_later AS (
        SELECT DISTINCT e.person_id
        FROM ethos_production.omop_54.master_condition_occurrence e
        JOIN chest_pain_dates cp ON cp.person_id = e.person_id
        WHERE e.condition_concept_id IN (
                -- anxiety (12 concepts)
                442077, 434613, 36684319, 381537, 4009184, 4178114, 4221077, 4146660,
                4039212, 441542, 4056690, 4198826
            )
          AND e.condition_start_date > cp.c_date
          AND e.condition_start_date <= cp.r_date
    ),
    muscle_strain AS (
        SELECT DISTINCT e.person_id
        FROM ethos_production.omop_54.master_condition_occurrence e
        JOIN chest_pain_dates cp ON cp.person_id = e.person_id
        WHERE e.condition_concept_id IN (315947, 4014526, 4016837, 81988)   -- uw_muscle_strain (4 concepts)
          AND e.condition_start_date > cp.c_date
          AND e.condition_start_date <= cp.r_date
    ),
    costochondritis AS (
        SELECT DISTINCT e.person_id
        FROM ethos_production.omop_54.master_condition_occurrence e
        JOIN chest_pain_dates cp ON cp.person_id = e.person_id
        WHERE e.condition_concept_id IN (134461)   -- costochondritis (1 concept)
          AND e.condition_start_date > cp.c_date
          AND e.condition_start_date <= cp.r_date
    ),
    noncardiac_cp AS (
        SELECT DISTINCT e.person_id
        FROM ethos_production.omop_54.master_condition_occurrence e
        JOIN chest_pain_dates cp ON cp.person_id = e.person_id
        WHERE e.condition_concept_id IN (42539051)   -- uw_noncardiac_cp (1 concept)
          AND e.condition_start_date > cp.f_date
          AND e.condition_start_date <= cp.r_date
    ),
    explained_dx AS (
        SELECT person_id FROM anxiety_later
        UNION
        SELECT person_id FROM gi_dx
        UNION
        SELECT person_id FROM muscle_strain
        UNION
        SELECT person_id FROM costochondritis
    ),
    ekg_no_abnormal_code AS (
        SELECT person_id FROM ekg
        EXCEPT
        SELECT person_id FROM abnormal_ekg
    ),
    no_further_cardiac_testing AS (
        SELECT person_id FROM chest_pain_dates
        EXCEPT
        SELECT person_id FROM extra_cardiac_testing
    ),
    no_firm_dx AS (
        SELECT person_id FROM chest_pain_dates
        EXCEPT
        SELECT DISTINCT e.person_id
        FROM ethos_production.omop_54.master_condition_occurrence e
        JOIN chest_pain_dates cp ON cp.person_id = e.person_id
        WHERE e.condition_concept_id IN (
                -- uw_cad_dx (22 concepts)
                321318, 36712983, 314666, 4270024, 40481919, 36712982, 319844, 4296653,
                315286, 312327, 37309626, 43020460, 46270163, 4329847, 45766241, 46270162,
                37312532, 45766114, 4108677, 4108218, 45766116, 45766075,
                -- gerd (4 concepts)
                4144111, 30437, 23325, 318800,
                -- uw_gi_dx (69 concepts)
                201340, 4225273, 196456, 30753, 199866, 4289526, 443785, 4248429,
                199074, 27918, 198809, 192956, 200765, 196726, 4057513, 4027663,
                44783016, 444367, 195596, 4341763, 201614, 4195231, 192667, 4340493,
                4340960, 195300, 4288676, 4211001, 4296611, 193249, 195587, 4300203,
                201352, 4026144, 36716712, 4340964, 198246, 4232181, 4138962, 4163865,
                4340961, 4231580, 444420, 197924, 4150681, 4057953, 198475, 4174044,
                194991, 4027729, 4204555, 4046500, 45757783, 4222896, 46269837, 4173408,
                4146517, 4265479, 443889, 763023, 4169592, 4289830, 46270145, 4194543,
                44806251, 4294973, 4340962, 4336230, 196628,
                -- anxiety (12 concepts)
                442077, 434613, 36684319, 381537, 4009184, 4178114, 4221077, 4146660,
                4039212, 441542, 4056690, 4198826,
                -- uw_muscle_strain (4 concepts)
                315947, 4014526, 4016837, 81988,
                -- costochondritis (1 concept)
                134461,
                -- uw_noncardiac_cp (1 concept)
                42539051
            )
          AND e.condition_start_date <= cp.r_date
    ),
    flags AS (
        SELECT cp.person_id, cp.r_date, cp.c_date, cp.f_date, cp.months_out,
        CASE WHEN age_sex_high_risk.person_id IS NOT NULL THEN 1 ELSE 0 END AS age_sex_high_risk,
        CASE WHEN hx_cad.person_id IS NOT NULL THEN 1 ELSE 0 END AS hx_cad,
        CASE WHEN abnormal_ekg.person_id IS NOT NULL THEN 1 ELSE 0 END AS abnormal_ekg,
        CASE WHEN extra_cardiac_testing.person_id IS NOT NULL THEN 1 ELSE 0 END AS extra_cardiac_testing,
        CASE WHEN rx_nitrates.person_id IS NOT NULL THEN 1 ELSE 0 END AS rx_nitrates,
        CASE WHEN troponin.person_id IS NOT NULL THEN 1 ELSE 0 END AS troponin,
        CASE WHEN ekg.person_id IS NOT NULL THEN 1 ELSE 0 END AS ekg,
        CASE WHEN gerd.person_id IS NOT NULL THEN 1 ELSE 0 END AS gerd,
        CASE WHEN anxiety.person_id IS NOT NULL THEN 1 ELSE 0 END AS anxiety,
        CASE WHEN gi_dx.person_id IS NOT NULL THEN 1 ELSE 0 END AS gi_dx,
        CASE WHEN anxiety_later.person_id IS NOT NULL THEN 1 ELSE 0 END AS anxiety_later,
        CASE WHEN muscle_strain.person_id IS NOT NULL THEN 1 ELSE 0 END AS muscle_strain,
        CASE WHEN costochondritis.person_id IS NOT NULL THEN 1 ELSE 0 END AS costochondritis,
        CASE WHEN noncardiac_cp.person_id IS NOT NULL THEN 1 ELSE 0 END AS noncardiac_cp,
        CASE WHEN explained_dx.person_id IS NOT NULL THEN 1 ELSE 0 END AS explained_dx,
        CASE WHEN ekg_no_abnormal_code.person_id IS NOT NULL THEN 1 ELSE 0 END AS ekg_no_abnormal_code,
        CASE WHEN no_further_cardiac_testing.person_id IS NOT NULL THEN 1 ELSE 0 END AS no_further_cardiac_testing,
        CASE WHEN no_firm_dx.person_id IS NOT NULL THEN 1 ELSE 0 END AS no_firm_dx
        FROM chest_pain_dates cp
        LEFT JOIN age_sex_high_risk ON age_sex_high_risk.person_id = cp.person_id
        LEFT JOIN hx_cad ON hx_cad.person_id = cp.person_id
        LEFT JOIN abnormal_ekg ON abnormal_ekg.person_id = cp.person_id
        LEFT JOIN extra_cardiac_testing ON extra_cardiac_testing.person_id = cp.person_id
        LEFT JOIN rx_nitrates ON rx_nitrates.person_id = cp.person_id
        LEFT JOIN troponin ON troponin.person_id = cp.person_id
        LEFT JOIN ekg ON ekg.person_id = cp.person_id
        LEFT JOIN gerd ON gerd.person_id = cp.person_id
        LEFT JOIN anxiety ON anxiety.person_id = cp.person_id
        LEFT JOIN gi_dx ON gi_dx.person_id = cp.person_id
        LEFT JOIN anxiety_later ON anxiety_later.person_id = cp.person_id
        LEFT JOIN muscle_strain ON muscle_strain.person_id = cp.person_id
        LEFT JOIN costochondritis ON costochondritis.person_id = cp.person_id
        LEFT JOIN noncardiac_cp ON noncardiac_cp.person_id = cp.person_id
        LEFT JOIN explained_dx ON explained_dx.person_id = cp.person_id
        LEFT JOIN ekg_no_abnormal_code ON ekg_no_abnormal_code.person_id = cp.person_id
        LEFT JOIN no_further_cardiac_testing ON no_further_cardiac_testing.person_id = cp.person_id
        LEFT JOIN no_firm_dx ON no_firm_dx.person_id = cp.person_id
    )
SELECT
    f.*,
    -- Composites
    CASE WHEN (f.age_sex_high_risk + f.hx_cad + f.abnormal_ekg + f.extra_cardiac_testing + f.rx_nitrates) > 0
         THEN 1 ELSE 0 END AS high_risk_any,
    CASE WHEN NOT ((f.age_sex_high_risk + f.hx_cad + f.abnormal_ekg + f.extra_cardiac_testing + f.rx_nitrates) > 0)
         AND f.months_out > 6
         THEN 1 ELSE 0 END AS A1,
    CASE WHEN f.ekg_no_abnormal_code = 1 AND f.hx_cad = 0
         THEN 1 ELSE 0 END AS A2,
    CASE WHEN f.no_further_cardiac_testing = 1 AND f.hx_cad = 0
         AND f.months_out > 6
         THEN 1 ELSE 0 END AS A3,
    CASE WHEN f.explained_dx = 1 AND f.hx_cad = 0
         THEN 1 ELSE 0 END AS A4,
    CASE WHEN f.noncardiac_cp = 1
         THEN 1 ELSE 0 END AS A5,
    CASE WHEN f.months_out > 24
         THEN 1 ELSE 0 END AS A6,
    CASE WHEN ((f.age_sex_high_risk + f.hx_cad + f.abnormal_ekg + f.extra_cardiac_testing + f.rx_nitrates) > 0)
         AND f.months_out < 6
         THEN 1 ELSE 0 END AS R1,
    CASE WHEN f.no_firm_dx = 1 AND f.months_out < 6
         THEN 1 ELSE 0 END AS R2,
    CASE WHEN f.hx_cad = 1 AND f.months_out < 12
         THEN 1 ELSE 0 END AS D1
FROM flags f
ORDER BY f.person_id;
```
