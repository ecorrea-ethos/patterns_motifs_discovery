----------------------------------------------------
-- v0.2
-- Chest pain (ICD10CM R07.*) persons in OMOP, limited to persons with a policy
-- (POLICY_ERA -> PCP) whose DIM_UNDERWRITING_PROCESS != 'TBD'.
-- WITH src AS (
--     SELECT c.concept_id, c.concept_code
--     FROM ethos_production.omop_54.concept c
--     WHERE c.vocabulary_id = 'ICD10CM'
--       AND c.invalid_reason IS NULL
--       AND c.concept_code IN ('R07.89', 'R07.9', 'R07.2', 'R07.8', 'R07.82')
-- ),
-- std AS (
--     SELECT DISTINCT t.concept_id AS std_concept_id
--     FROM src
--     JOIN ethos_production.omop_54.concept_relationship cr
--       ON cr.concept_id_1 = src.concept_id
--      AND cr.relationship_id = 'Maps to'
--      AND cr.invalid_reason IS NULL
--     JOIN ethos_production.omop_54.concept t
--       ON t.concept_id = cr.concept_id_2
--      AND t.standard_concept = 'S'
--      AND t.invalid_reason IS NULL
-- ),
-- eligible_persons AS (
--     -- Persons linked to at least one PCP policy with a non-TBD underwriting process
--     SELECT DISTINCT era.PERSON_ID
--     FROM ethos_production.omop_54.policy_era era
--     JOIN ethos_production.dbt_mart_transformation.m_policy_carrier_product pcp
--       ON era.POLICY_ID = pcp.BK_POLICY_ID
--     WHERE era.PERSON_ID IS NOT NULL
--       AND pcp.DIM_UNDERWRITING_PROCESS != 'TBD'
-- ),
-- hits AS (
--     SELECT co.person_id,
--            co.condition_occurrence_id,
--            co.condition_start_date
--     FROM ethos_production.omop_54.condition_occurrence co
--     JOIN eligible_persons ep ON ep.PERSON_ID = co.person_id
--     WHERE co.condition_concept_id IN (SELECT std_concept_id FROM std)
--        OR co.condition_source_concept_id IN (SELECT concept_id FROM src)
--        OR REPLACE(co.condition_source_value, '.', '') IN
--           (SELECT REPLACE(concept_code, '.', '') FROM src)
-- )
-- SELECT person_id,
--        -- MIN(condition_start_date) AS first_chest_pain_date,
--        -- MAX(condition_start_date) AS last_chest_pain_date,
--        -- COUNT(DISTINCT condition_occurrence_id) AS occurrence_ct,
--        COUNT(DISTINCT condition_start_date) AS distinct_date_ct
-- FROM hits
-- GROUP BY person_id
-- ORDER BY person_id;


----------------------------------------------------
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