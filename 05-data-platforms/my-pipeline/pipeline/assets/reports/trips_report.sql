/* @bruin

name: reports.trips_report

type: duckdb.sql

# TODO: Declare dependency on the staging asset(s) this report reads from.
depends:
  - staging.trips

materialization:
  type: table


# TODO: Define report columns + primary key(s) at your chosen level of aggregation.
columns:
  - name: vendor_id
    type: INTEGER
    description: The vendor ID for the trip
    primary_key: true
  - name: pickup_date
    type: DATE
    description: The date of the pickup
    primary_key: true
  - name: trip_count
    type: BIGINT
    description: The number of trips for the vendor and date combination
    checks:
      - name: non_negative

@bruin */

-- Purpose of reports:
-- - Aggregate staging data for dashboards and analytics
-- Required Bruin concepts:
-- - Filter using `{{ start_datetime }}` / `{{ end_datetime }}` for incremental runs
-- - GROUP BY your dimension + date columns

SELECT
  vendor_id,
  CAST(pickup_datetime AS DATE) AS pickup_date,
  COUNT(*) AS trip_count,
  COUNT(DISTINCT CAST(pickup_datetime AS DATE)) AS active_days,
  AVG(trip_distance) AS avg_trip_distance,
  SUM(total_amount) AS total_revenue,
  AVG(total_amount) AS avg_fare,
  AVG(passenger_count) AS avg_passengers,
  COUNT(DISTINCT pickup_location_id) AS unique_pickup_locations,
  COUNT(DISTINCT dropoff_location_id) AS unique_dropoff_locations

FROM staging.trips

WHERE pickup_datetime >= '{{ start_datetime }}'
  AND pickup_datetime < '{{ end_datetime }}'
  AND vendor_id IS NOT NULL

GROUP BY vendor_id, CAST(pickup_datetime AS DATE)

ORDER BY vendor_id, pickup_date
