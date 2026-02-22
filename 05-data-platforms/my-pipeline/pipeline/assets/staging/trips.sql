/* @bruin

name: staging.trips

type: duckdb.sql

depends:
  - ingestion.trips
  - ingestion.payment_lookup

materialization:
  type: table


# TODO: Add one custom check that validates a staging invariant (uniqueness, ranges, etc.)
# Docs: https://getbruin.com/docs/bruin/quality/custom
custom_checks:
  - name: row_count_positive
    query: |
      SELECT CASE WHEN COUNT(*) > 0 THEN 1 ELSE 0 END
      FROM staging.trips
    value: 1
@bruin */

-- TODO: Write the staging SELECT query.
--
-- Purpose of staging:
-- - Clean and normalize schema from ingestion
-- - Deduplicate records (important if ingestion uses append strategy)
-- - Enrich with lookup tables (JOINs)
-- - Filter invalid rows (null PKs, negative values, etc.)
--
-- Why filter by {{ start_datetime }} / {{ end_datetime }}?
-- When using `time_interval` strategy, Bruin:
--   1. DELETES rows where `incremental_key` falls within the run's time window
--   2. INSERTS the result of your query
-- Therefore, your query MUST filter to the same time window so only that subset is inserted.
-- If you don't filter, you'll insert ALL data but only delete the window's data = duplicates.

SELECT
  -- identifiers
  CAST(t.vendor_id AS INTEGER) AS vendor_id,
  CAST(t.ratecode_id AS INTEGER) AS rate_code_id,
  CAST(t.pu_location_id AS INTEGER) AS pickup_location_id,
  CAST(t.do_location_id AS INTEGER) AS dropoff_location_id,
  
  -- timestamps
  CAST(t.tpep_pickup_datetime AS TIMESTAMP) AS pickup_datetime,
  CAST(t.tpep_dropoff_datetime AS TIMESTAMP) AS dropoff_datetime,
  
  -- trip info
  CAST(t.store_and_fwd_flag AS STRING) AS store_and_fwd_flag,
  CAST(t.passenger_count AS INTEGER) AS passenger_count,
  CAST(t.trip_distance AS NUMERIC) AS trip_distance,
  
  -- payment info
  CAST(t.fare_amount AS NUMERIC) AS fare_amount,
  CAST(t.extra AS NUMERIC) AS extra,
  CAST(t.mta_tax AS NUMERIC) AS mta_tax,
  CAST(t.tip_amount AS NUMERIC) AS tip_amount,
  CAST(t.tolls_amount AS NUMERIC) AS tolls_amount,
  CAST(t.improvement_surcharge AS NUMERIC) AS improvement_surcharge,
  CAST(t.total_amount AS NUMERIC) AS total_amount,
  CAST(t.payment_type AS INTEGER) AS payment_type,
  COALESCE(pl.payment_type_name, 'Unknown') AS payment_type_name

FROM ingestion.trips t
LEFT JOIN ingestion.payment_lookup pl ON t.payment_type = pl.payment_type_id

WHERE t.tpep_pickup_datetime >= '{{ start_datetime }}'
  AND t.tpep_pickup_datetime < '{{ end_datetime }}'

