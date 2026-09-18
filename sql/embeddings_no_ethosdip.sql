-- Random patient: all observations, measurements, conditions
-- flagged by whether the row originates from the ethos_dip (disclosure) vocabulary
-- Snowflake / ethos_production.omop_54

WITH dip_concepts AS (          -- every custom disclosure concept
    SELECT concept_id
    FROM ethos_production.omop_54.omop_concept
    WHERE vocabulary_id = 'ethos_dip'
       OR concept_id >= 2000000001
),

-- ---------------------------------------------------------------
-- Pick the patient. Set has_disclosures = TRUE to force a person
-- who actually has at least one ethos_dip row (random patients
-- frequently have none).
-- ---------------------------------------------------------------
candidates AS (
    SELECT p.person_id,
           EXISTS (
               SELECT 1
               FROM ethos_production.omop_54.observation o
               WHERE o.person_id = p.person_id
                 AND (o.observation_concept_id IN (SELECT concept_id FROM dip_concepts)
                   OR o.observation_source_concept_id IN (SELECT concept_id FROM dip_concepts))
           ) AS has_disclosures
    FROM ethos_production.omop_54.person p
),
picked_person AS (
    SELECT person_id
    FROM candidates
    WHERE 
        has_disclosures = TRUE      -- <<< flip to FALSE, or drop this line, for a truly random person
        and person_id=3955878
    ORDER BY RANDOM()
    LIMIT 1
),

-- ---------------------------------------------------------------
-- Events, one normalized shape per domain
-- ---------------------------------------------------------------
events AS (

    SELECT 'OBSERVATION'                      AS domain_table,
           o.observation_id::VARCHAR          AS event_id,
           o.person_id,
           o.observation_date                 AS event_date,
           o.observation_concept_id           AS concept_id,
           o.observation_source_value         AS source_value,
    FROM ethos_production.omop_54.master_observation o
    JOIN picked_person pp USING (person_id)

    UNION ALL

    SELECT 'MEASUREMENT',
           m.measurement_id::VARCHAR,
           m.person_id,
           m.measurement_date,
           m.measurement_concept_id,
           m.measurement_source_value,
    FROM ethos_production.omop_54.master_measurement m
    JOIN picked_person pp USING (person_id)

    UNION ALL

    SELECT 'CONDITION_OCCURRENCE',
           c.condition_occurrence_id::VARCHAR,
           c.person_id,
           c.condition_start_date,
           c.condition_concept_id,
           c.condition_source_value,
    FROM ethos_production.omop_54.master_condition_occurrence c
    JOIN picked_person pp USING (person_id)
)

SELECT
    e.domain_table,
    e.person_id,
    e.event_id,
    e.event_date,

    -- provenance flag
    CASE
        WHEN std.vocabulary_id = 'ethos_dip' THEN 'DISCLOSURE'
        ELSE 'NON_DISCLOSURE'
    END                                       AS record_origin,

    -- standard (analysis) concept
    e.concept_id,
    std.concept_name                          AS concept_name,
    std.vocabulary_id                         AS concept_vocabulary,
    std.domain_id                             AS concept_domain,
    std.standard_concept,

    -- unmapped detection
    CASE
        WHEN e.concept_id = 0 OR e.concept_id IS NULL THEN TRUE
        ELSE FALSE
    END                                       AS is_unmapped

FROM events e
LEFT JOIN ethos_production.omop_54.concept std  ON std.concept_id  = e.concept_id
-- belt-and-braces: also drops any dip row that slipped past the source filters
WHERE std.vocabulary_id IS DISTINCT FROM 'ethos_dip'
ORDER BY e.event_date, e.domain_table, e.event_id;