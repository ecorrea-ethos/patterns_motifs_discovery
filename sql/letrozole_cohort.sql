-- v0.5: v0.4 letrozole cohort restricted to females (OMOP PERSON.GENDER_CONCEPT_ID = 8532).
-- Paths: (1) RxNorm ingredient descendants + NDC "Maps to", (2) ATC L02BG04 descendants,
--        (3) source concept match, (4) free-text LIKE on drug_source_value (letrozole / femara).
-- Valid = person linked to a PCP policy with non-TBD underwriting process, via POLICY_ERA.
-- One row per person; via_* flags show which path caught them.

WITH src AS (
    SELECT c.concept_id
    FROM ethos_production.omop_54.concept c
    WHERE c.vocabulary_id IN ('RxNorm', 'RxNorm Extension')
      AND LOWER(c.concept_name) = 'letrozole'
      AND c.concept_class_id = 'Ingredient'
      AND c.invalid_reason IS NULL

    UNION ALL

    SELECT c.concept_id
    FROM ethos_production.omop_54.concept c
    WHERE c.vocabulary_id = 'NDC'
      AND LOWER(c.concept_name) LIKE '%letrozole%'
      AND c.invalid_reason IS NULL
),
std_ingredient AS (
    SELECT DISTINCT ca.descendant_concept_id AS std_concept_id
    FROM src
    JOIN ethos_production.omop_54.concept_ancestor ca
      ON ca.ancestor_concept_id = src.concept_id
    JOIN ethos_production.omop_54.concept t
      ON t.concept_id = ca.descendant_concept_id
     AND t.standard_concept = 'S'
     AND t.invalid_reason IS NULL

    UNION

    SELECT DISTINCT cr.concept_id_2
    FROM src
    JOIN ethos_production.omop_54.concept_relationship cr
      ON cr.concept_id_1 = src.concept_id
     AND cr.relationship_id = 'Maps to'
     AND cr.invalid_reason IS NULL
    JOIN ethos_production.omop_54.concept t
      ON t.concept_id = cr.concept_id_2
     AND t.standard_concept = 'S'
     AND t.invalid_reason IS NULL
),
std_atc AS (
    SELECT DISTINCT ca.descendant_concept_id AS std_concept_id
    FROM ethos_production.omop_54.concept atc
    JOIN ethos_production.omop_54.concept_ancestor ca
      ON ca.ancestor_concept_id = atc.concept_id
    JOIN ethos_production.omop_54.concept t
      ON t.concept_id = ca.descendant_concept_id
     AND t.standard_concept = 'S'
     AND t.invalid_reason IS NULL
    WHERE atc.vocabulary_id = 'ATC'
      AND atc.concept_code = 'L02BG04'
      AND atc.invalid_reason IS NULL
),
eligible_persons AS (
    SELECT DISTINCT era.PERSON_ID
    FROM ethos_production.omop_54.policy_era era
    JOIN ethos_production.dbt_mart_transformation.m_policy_carrier_product pcp
      ON era.POLICY_ID = pcp.BK_POLICY_ID
    WHERE era.PERSON_ID IS NOT NULL
      AND pcp.DIM_UNDERWRITING_PROCESS != 'TBD'
),
female_persons AS (
    -- v0.5 change: keep only females among eligible persons
    SELECT ep.PERSON_ID
    FROM eligible_persons ep
    JOIN ethos_production.omop_54.person p
      ON p.person_id = ep.PERSON_ID
    WHERE p.gender_concept_id = 8532
),
hits AS (
    SELECT de.person_id,
           de.drug_exposure_id,
           de.drug_exposure_start_date,
           IFF(de.drug_concept_id IN (SELECT std_concept_id FROM std_ingredient), 1, 0) AS via_ingredient,
           IFF(de.drug_concept_id IN (SELECT std_concept_id FROM std_atc), 1, 0)        AS via_atc,
           IFF(de.drug_source_concept_id IN (SELECT concept_id FROM src), 1, 0)         AS via_src,
           IFF(LOWER(de.drug_source_value) LIKE '%letrozole%'
            OR LOWER(de.drug_source_value) LIKE '%femara%', 1, 0)                       AS via_text
    FROM ethos_production.omop_54.drug_exposure de
    JOIN female_persons fp ON fp.PERSON_ID = de.person_id
    WHERE de.drug_concept_id IN (SELECT std_concept_id FROM std_ingredient)
       OR de.drug_concept_id IN (SELECT std_concept_id FROM std_atc)
       OR de.drug_source_concept_id IN (SELECT concept_id FROM src)
       OR LOWER(de.drug_source_value) LIKE '%letrozole%'
       OR LOWER(de.drug_source_value) LIKE '%femara%'
)
SELECT person_id,
       COUNT(DISTINCT drug_exposure_id)         AS total_exposures,
       COUNT(DISTINCT drug_exposure_start_date) AS distinct_date_ct,
       MIN(drug_exposure_start_date)            AS first_exposure_date,
       MAX(drug_exposure_start_date)            AS last_exposure_date,
       MAX(via_ingredient) AS via_ingredient,
       MAX(via_atc)        AS via_atc,
       MAX(via_src)        AS via_src,
       MAX(via_text)       AS via_text
FROM hits
GROUP BY person_id
ORDER BY person_id;