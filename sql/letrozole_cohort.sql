WITH src AS (
    -- 1. Identify the Letrozole ingredient concept in RxNorm / RxNorm Extension
    SELECT c.concept_id, c.concept_code, c.concept_name
    FROM ethos_production.omop_54.concept c
    WHERE c.vocabulary_id IN ('RxNorm', 'RxNorm Extension')
      AND LOWER(c.concept_name) = 'letrozole'
      AND c.concept_class_id = 'Ingredient'
      AND c.invalid_reason IS NULL

    UNION ALL

    -- 2. Include any specific NDC source concepts for Letrozole (if applicable)
    SELECT c.concept_id, c.concept_code, c.concept_name
    FROM ethos_production.omop_54.concept c
    WHERE c.vocabulary_id = 'NDC'
      AND LOWER(c.concept_name) LIKE '%letrozole%'
      AND c.invalid_reason IS NULL
),
std AS (
    -- Get all Standard descendant concepts (e.g., Clinical Drugs, Branded Drugs, Dose Forms)
    -- that roll up to the Letrozole ingredient via CONCEPT_ANCESTOR
    SELECT DISTINCT ca.descendant_concept_id AS std_concept_id
    FROM src
    JOIN ethos_production.omop_54.concept_ancestor ca
      ON ca.ancestor_concept_id = src.concept_id
    JOIN ethos_production.omop_54.concept t
      ON t.concept_id = ca.descendant_concept_id
     AND t.standard_concept = 'S'
     AND t.invalid_reason IS NULL

    UNION

    -- Direct 'Maps to' relationship for source non-standard concepts
    SELECT DISTINCT cr.concept_id_2 AS std_concept_id
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
hits AS (
    SELECT de.person_id,
           de.drug_exposure_id,
           de.drug_exposure_start_date
    FROM ethos_production.omop_54.drug_exposure de
    WHERE de.drug_concept_id IN (SELECT std_concept_id FROM std)
       OR de.drug_source_concept_id IN (SELECT concept_id FROM src)
       OR LOWER(de.drug_source_value) LIKE '%letrozole%'
)
SELECT person_id,
       COUNT(DISTINCT drug_exposure_id) AS total_exposures,
       COUNT(DISTINCT drug_exposure_start_date) AS distinct_date_ct
FROM hits
GROUP BY person_id
ORDER BY person_id;