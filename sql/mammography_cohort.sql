
WITH mammo_codes AS (
    SELECT column1 AS code
    FROM VALUES ('77065'), ('77066'), ('77067'),   -- CPT: diagnostic/screening mammography
                ('76090'), ('76091'), ('76092'),   -- CPT: legacy mammography
                ('G0202'), ('G0204'), ('G0206')    -- HCPCS: screening/diagnostic mammography
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
    WHERE d.description ILIKE '%mammogr%'
       OR REPLACE(UPPER(TRIM(d.medicalcode)), '.', '') IN (SELECT code FROM mammo_codes)
),

-- 3) OMOP concept set: listed codes + 4324693 and descendants
mammo_concepts AS (
    SELECT c.concept_id
    FROM ethos_production.omop_54.concept c
    WHERE c.vocabulary_id IN ('CPT4', 'HCPCS')
      AND c.concept_code IN (SELECT code FROM mammo_codes)

    UNION

    SELECT ca.descendant_concept_id
    FROM ethos_production.omop_54.concept_ancestor ca
    WHERE ca.ancestor_concept_id = 4324693          -- SNOMED 'Mammography' (includes itself)
),

-- 4) OMOP hits, restricted to Ethos persons
omop_persons AS (
    SELECT po.person_id
    FROM ethos_production.omop_54.procedure_occurrence po
    JOIN ethos_persons e ON e.person_id = po.person_id
    WHERE po.procedure_concept_id        IN (SELECT concept_id FROM mammo_concepts)
       OR po.procedure_source_concept_id IN (SELECT concept_id FROM mammo_concepts)

    UNION

    SELECT m.person_id
    FROM ethos_production.omop_54.measurement m
    JOIN ethos_persons e ON e.person_id = m.person_id
    WHERE m.measurement_concept_id        IN (SELECT concept_id FROM mammo_concepts)
       OR m.measurement_source_concept_id IN (SELECT concept_id FROM mammo_concepts)

    UNION

    SELECT o.person_id
    FROM ethos_production.omop_54.observation o
    JOIN ethos_persons e ON e.person_id = o.person_id
    WHERE o.observation_concept_id        IN (SELECT concept_id FROM mammo_concepts)
       OR o.observation_source_concept_id IN (SELECT concept_id FROM mammo_concepts)
)

SELECT person_id
FROM omop_persons
ORDER BY person_id;