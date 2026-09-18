WITH src AS (
    SELECT c.concept_id, c.concept_code
    FROM ethos_production.omop_54.omop_concept c
    WHERE c.vocabulary_id = 'ICD10CM'
      AND c.invalid_reason IS NULL
      AND c.concept_code IN ('R07.89', 'R07.9', 'R07.2', 'R07.8', 'R07.82')
),
std AS (
    SELECT DISTINCT t.concept_id AS std_concept_id
    FROM src
    JOIN ethos_production.omop_54.concept_relationship cr
      ON cr.concept_id_1 = src.concept_id
     AND cr.relationship_id = 'Maps to'
     AND cr.invalid_reason IS NULL
    JOIN ethos_production.omop_54.omop_concept t
      ON t.concept_id = cr.concept_id_2
     AND t.standard_concept = 'S'
     AND t.invalid_reason IS NULL
),
hits AS (
    SELECT co.person_id,
           co.condition_occurrence_id,
           co.condition_start_date
    FROM ethos_production.omop_54.condition_occurrence co
    WHERE co.condition_concept_id IN (SELECT std_concept_id FROM std)
       OR co.condition_source_concept_id IN (SELECT concept_id FROM src)
       OR REPLACE(co.condition_source_value, '.', '') IN
          (SELECT REPLACE(concept_code, '.', '') FROM src)
)
SELECT person_id,
       -- MIN(condition_start_date) AS first_chest_pain_date,
       -- MAX(condition_start_date) AS last_chest_pain_date,
       -- COUNT(DISTINCT condition_occurrence_id) AS occurrence_ct,
       COUNT(DISTINCT condition_start_date) AS distinct_date_ct
FROM hits
GROUP BY person_id
ORDER BY person_id;