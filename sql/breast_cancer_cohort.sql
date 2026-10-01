----------------------------------------------------
-- v0.2
-- Female breast cancer (ICD9CM 174*, ICD10CM C50*, SNOMED 4162253) persons in OMOP,
-- limited to persons with a policy (POLICY_ERA -> PCP) whose DIM_UNDERWRITING_PROCESS != 'TBD'.
WITH src AS (
    SELECT c.concept_id, c.concept_code
    FROM ethos_production.omop_54.concept c
    WHERE c.vocabulary_id = 'ICD9CM'
      AND c.invalid_reason IS NULL
      AND (
            -- c.concept_code ILIKE ('N97%')          -- exact infertility codes
            -- OR c.concept_code IN (--'Z31.41',
            -- 'Z31.83')          -- exact infertility codes
            -- OR 
            c.concept_code LIKE '174%'                    -- C50 category + all subtypes
        )
    UNION ALL
    SELECT c.concept_id, c.concept_code
    FROM ethos_production.omop_54.concept c
    WHERE c.vocabulary_id = 'ICD10CM'
      AND c.invalid_reason IS NULL
      AND (
            -- c.concept_code ILIKE ('N97%')          -- exact infertility codes
            -- OR c.concept_code IN (--'Z31.41',
            -- 'Z31.83')          -- exact infertility codes
            -- OR 
            c.concept_code LIKE 'C50%'                    -- C50 category + all subtypes
        )
    UNION ALL
    SELECT c.concept_id, c.concept_code
    FROM ethos_production.omop_54.concept c
    WHERE c.vocabulary_id = 'SNOMED'
      AND c.invalid_reason IS NULL
      AND (
            -- c.concept_id = 201909       -- exact infertility codes
            -- OR c.concept_id = 4272937   -- assisted fertilization
            -- OR
            c.concept_id = 4162253   -- C50 category + all subtypes
        )
),
std AS (
    SELECT DISTINCT t.concept_id AS std_concept_id
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
eligible_persons AS (
    -- Persons linked to at least one PCP policy with a non-TBD underwriting process
    SELECT DISTINCT era.PERSON_ID
    FROM ethos_production.omop_54.policy_era era
    JOIN ethos_production.dbt_mart_transformation.m_policy_carrier_product pcp
      ON era.POLICY_ID = pcp.BK_POLICY_ID
    WHERE era.PERSON_ID IS NOT NULL
      AND pcp.DIM_UNDERWRITING_PROCESS != 'TBD'
),
hits AS (
    SELECT co.person_id,
           co.condition_occurrence_id,
           co.condition_start_date
    FROM ethos_production.omop_54.condition_occurrence co
    JOIN eligible_persons ep ON ep.PERSON_ID = co.person_id
    WHERE co.condition_concept_id IN (SELECT std_concept_id FROM std)
       OR co.condition_source_concept_id IN (SELECT concept_id FROM src)
       OR REPLACE(co.condition_source_value, '.', '') IN
          (SELECT REPLACE(concept_code, '.', '') FROM src)
)
SELECT h.person_id,
       -- MIN(condition_start_date) AS first_chest_pain_date,
       -- MAX(condition_start_date) AS last_chest_pain_date,
       -- COUNT(DISTINCT condition_occurrence_id) AS occurrence_ct,
       COUNT(DISTINCT h.condition_start_date) AS distinct_date_ct
FROM hits h
JOIN ethos_production.omop_54.person p ON p.person_id = h.person_id
WHERE p.gender_source_value ILIKE 'female'
GROUP BY h.person_id
ORDER BY h.person_id;
