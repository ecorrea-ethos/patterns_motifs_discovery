----------------------------------------------------
-- v0.1  Application date per policy of the chest pain cohort persons.
--
-- Why: age and "within the last 12 / 24 / 36 / 48 / 60 months" are defined relative to the APPLICATION date (Sean, Zack,
-- review of 2026-10-26). The cohort extract has no such date; `policy_id` is on every event table, and the cohort SQL
-- (chest_pain_cohort.sql) already joins omop_54.policy_era to dbt_mart_transformation.m_policy_carrier_product on it.
--
-- Run order (ethos_omop.extract_policy_dates() does step 2 for you and writes policy.csv next to person.csv):
--   1. Run the DISCOVERY query below once and pick the column that holds the application / submission date.
--      THE COLUMN NAME IN STEP 2 IS A GUESS (APPLICATION_DATE), NOT VERIFIED AGAINST THE SCHEMA.
--   2. eo.extract_policy_dates(OUT_DIR, app_date_col="<the column from step 1>")
--
-- A person can have several policies: policy.csv keeps one row per (person, policy); ethos_omop.load_policy_dates()
-- takes the EARLIEST application date per person. Change that rule there if underwriting means another policy.
----------------------------------------------------

-- ==== DISCOVERY ====
SELECT table_schema, table_name, column_name, data_type
FROM ethos_production.information_schema.columns
WHERE (table_schema = 'OMOP_54'                   AND table_name = 'POLICY_ERA')
   OR (table_schema = 'DBT_MART_TRANSFORMATION'   AND table_name = 'M_POLICY_CARRIER_PRODUCT')
ORDER BY table_name, ordinal_position;

-- ==== EXTRACT ====
-- The two double-brace placeholders below are filled in by extract_policy_dates(): the person ids (comma-separated, in chunks)
-- and the date column picked in step 1. Do not write either placeholder anywhere else in this part of the file.
SELECT era.person_id,
       era.policy_id,
       TRY_TO_DATE(pcp.{{APPLICATION_DATE_COLUMN}}::VARCHAR) AS application_date
FROM ethos_production.omop_54.policy_era era
JOIN ethos_production.dbt_mart_transformation.m_policy_carrier_product pcp
  ON era.POLICY_ID = pcp.BK_POLICY_ID
WHERE era.person_id IN ({{PERSON_IDS}})
  AND pcp.{{APPLICATION_DATE_COLUMN}} IS NOT NULL
ORDER BY era.person_id, application_date
