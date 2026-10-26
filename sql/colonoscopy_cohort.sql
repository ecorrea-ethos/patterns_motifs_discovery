-- Colonoscopy cohort: Ethos persons with a colonoscopy. Same shape as mammography_cohort.sql (returns person_id only; the notebook
-- feeds it to ethos_omop.extract_cohort). Written 2026-10-19 by analogy with that file; NOT RUN yet against Snowflake.
-- Check before the first extract: the number of persons returned, and that the code list below matches what the dx evidence uses.

WITH colo_codes AS (
    SELECT column1 AS code
    FROM VALUES ('45378'), ('45379'), ('45380'), ('45381'), ('45382'), ('45384'), ('45385'),   -- CPT: colonoscopy, flexible
                ('45386'), ('45388'), ('45389'), ('45390'), ('45391'), ('45392'), ('45393'), ('45398'),
                ('44388'), ('44389'), ('44390'), ('44391'), ('44392'), ('44394'),               -- CPT: colonoscopy through stoma
                ('44401'), ('44402'), ('44403'), ('44404'), ('44405'), ('44406'), ('44407'), ('44408'),
                ('G0105'), ('G0121')                                                            -- HCPCS: screening colonoscopy, high risk / not high risk
),

-- 1) PCP anchor
valid_policies AS (
    SELECT DISTINCT TRY_TO_NUMBER(bk_policy_id)::VARCHAR AS policy_id
    FROM ethos_production.dbt_mart_transformation.m_policy_carrier_product
    WHERE dim_underwriting_process IS DISTINCT FROM 'TBD'
      AND bk_product_id IN (1, 5, 14, 15, 21, 25)
),
policy_person AS (
    SELECT DISTINCT v.policy_id, era.person_id
    FROM ethos_production.omop_54.policy_era era
    JOIN valid_policies v
      ON v.policy_id = TRY_TO_NUMBER(era.policy_id)::VARCHAR
    WHERE era.person_id IS NOT NULL
),

-- 2) DX evidence -> OMOP person
ethos_persons AS (
    SELECT DISTINCT pp.person_id
    FROM ethos_production.airflow_uw_evidence.dx_evidence_flattened d
    JOIN valid_policies v
      ON v.policy_id = TRY_TO_NUMBER(d.policy_id)::VARCHAR
    JOIN policy_person pp
      ON pp.policy_id = v.policy_id
    WHERE d.description ILIKE '%colonoscop%'
       OR REPLACE(UPPER(TRIM(d.medicalcode)), '.', '') IN (SELECT code FROM colo_codes)
),

-- 3) OMOP concept set: listed codes + SNOMED 'Colonoscopy' (4249893) and 'Screening colonoscopy' (40480729) with their descendants
--    (both ids read from the concept.csv of the existing extracts: 73761001 and 444783004)
colo_concepts AS (
    SELECT c.concept_id
    FROM ethos_production.omop_54.concept c
    WHERE c.vocabulary_id IN ('CPT4', 'HCPCS')
      AND c.concept_code IN (SELECT code FROM colo_codes)

    UNION

    SELECT ca.descendant_concept_id
    FROM ethos_production.omop_54.concept_ancestor ca
    WHERE ca.ancestor_concept_id IN (4249893, 40480729)      -- (includes themselves)
),

-- 4) OMOP hits, restricted to Ethos persons
omop_persons AS (
    SELECT po.person_id
    FROM ethos_production.omop_54.procedure_occurrence po
    JOIN ethos_persons e ON e.person_id = po.person_id
    WHERE po.procedure_concept_id        IN (SELECT concept_id FROM colo_concepts)
       OR po.procedure_source_concept_id IN (SELECT concept_id FROM colo_concepts)

    UNION

    SELECT m.person_id
    FROM ethos_production.omop_54.measurement m
    JOIN ethos_persons e ON e.person_id = m.person_id
    WHERE m.measurement_concept_id        IN (SELECT concept_id FROM colo_concepts)
       OR m.measurement_source_concept_id IN (SELECT concept_id FROM colo_concepts)

    UNION

    SELECT o.person_id
    FROM ethos_production.omop_54.observation o
    JOIN ethos_persons e ON e.person_id = o.person_id
    WHERE o.observation_concept_id        IN (SELECT concept_id FROM colo_concepts)
       OR o.observation_source_concept_id IN (SELECT concept_id FROM colo_concepts)
)

SELECT person_id
FROM omop_persons
ORDER BY person_id;
