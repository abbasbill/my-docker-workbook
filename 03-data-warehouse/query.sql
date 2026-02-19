-- Creating external table referring to gcs path
CREATE OR REPLACE EXTERNAL TABLE `de-project-484923.nytaxi.external_yellow_tripdata`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://bbsbllmn-04-bucket/yellow_tripdata_2019-*.parquet']
);

-- Create a non partitioned table from external table
CREATE OR REPLACE TABLE de-project-484923.nytaxi.yellow_tripdata_non_partitioned AS
SELECT * FROM de-project-484923.nytaxi.external_yellow_tripdata;

-- Record count
SELECT count(*) as trips
FROM de-project-484923.nytaxi.yellow_tripdata_non_partitioned;

--  estimated amount of data that will be read on the External Table - 0 bytes
SELECT DISTINCT(tpep_pickup_datetime)
FROM de-project-484923.nytaxi.external_yellow_tripdata;

--  estimated amount of data that will be read on  the Materialized Table - 155.12 MB
SELECT DISTINCT(tpep_pickup_datetime)
FROM de-project-484923.nytaxi.yellow_tripdata_non_partitioned;

--  retrieve the PULocationID and on the table.
SELECT PULocationID
FROM de-project-484923.nytaxi.yellow_tripdata_non_partitioned;

--  retrieve the PULocationID and DOLocationID on the same table.
SELECT PULocationID, PULocationID
FROM de-project-484923.nytaxi.yellow_tripdata_non_partitioned;

--  record with fareamount of 0.
SELECT count(*)
FROM de-project-484923.nytaxi.yellow_tripdata_non_partitioned
WHERE fare_amount = 0;

-- Creating a partition and cluster table
CREATE OR REPLACE TABLE de-project-484923.nytaxi.yellow_tripdata_partitioned_clustered
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY VendorID AS
SELECT * FROM de-project-484923.nytaxi.external_yellow_tripdata;

-- Partition benefit
SELECT DISTINCT(VendorID)
FROM de-project-484923.nytaxi.yellow_tripdata_non_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2024-03-01' AND '2024-03-15';

-- Partition benefit
SELECT DISTINCT(VendorID)
FROM de-project-484923.nytaxi.yellow_tripdata_partitioned_clustered
WHERE DATE(tpep_pickup_datetime) BETWEEN '2024-03-01' AND '2024-03-15';


