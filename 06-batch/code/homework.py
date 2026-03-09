#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pyspark
from pyspark.sql import SparkSession


# In[4]:


spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()


# In[5]:


from pyspark.sql import types


# In[12]:


yellow_schema = types.StructType([
types.StructField('VendorID', types.IntegerType(), True), 
types.StructField('tpep_pickup_datetime', types.TimestampType(), True), 
types.StructField('tpep_dropoff_datetime', types.TimestampType(), True), 
types.StructField('passenger_count', types.IntegerType(), True), 
types.StructField('trip_distance', types.DoubleType(), True), 
types.StructField('RatecodeID', types.IntegerType(), True), 
types.StructField('store_and_fwd_flag', types.StringType(), True), 
types.StructField('PULocationID', types.IntegerType(), True), 
types.StructField('DOLocationID', types.IntegerType(), True), 
types.StructField('payment_type', types.IntegerType(), True), 
types.StructField('fare_amount', types.DoubleType(), True), 
types.StructField('extra', types.DoubleType(), True), 
types.StructField('mta_tax', types.DoubleType(), True), 
types.StructField('tip_amount', types.DoubleType(), True), 
types.StructField('tolls_amount', types.DoubleType(), True), 
types.StructField('improvement_surcharge', types.DoubleType(), True), 
types.StructField('total_amount', types.DoubleType(), True), 
types.StructField('congestion_surcharge', types.DoubleType(), True), 
types.StructField('Airport_fee', types.DoubleType(), True), 
types.StructField('cbd_congestion_fee', types.DoubleType(), True)
])


# In[6]:


df_yellow = spark.read \
    .parquet('yellow_tripdata_2025-11.parquet')


# In[8]:


df_yellow.schema


# In[9]:


path = 'y_tripdata_2025-11'


# In[10]:


df_yellow \
        .repartition(4) \
        .write.parquet(path, mode='overwrite')




df_yellow = spark.read.parquet('y_tripdata_2025-11/')


df_yellow.select('VendorID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime', 'trip_distance').show(10)



df_yellow.registerTempTable('trips_data')


spark.sql("""
SELECT
    count(1)
FROM
    trips_data
WHERE
    DATE(tpep_pickup_datetime) = '2025-11-15'
""").show()


spark.sql("""
SELECT ROUND(
    MAX(
        (UNIX_TIMESTAMP(tpep_dropoff_datetime) -
         UNIX_TIMESTAMP(tpep_pickup_datetime)) / 3600
    ), 1
) AS longest_trip_hours
FROM trips_data
""").show()



get_ipython().system('mkdir -p ./taxi_zone')


get_ipython().system('wget https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv -O ./taxi_zone/taxi_zone_lookup.csv')


df_zones = spark.read \
    .option("header", True) \
    .csv("taxi_zone/taxi_zone_lookup.csv", inferSchema=True)



df_zones.printSchema()


df_zones.createOrReplaceTempView('taxi_zones')

spark.sql("""
SELECT 
    z.Zone,
    y.PULocationID, 
    COUNT(1) as count
FROM trips_data y
JOIN taxi_zones z
      ON y.PULocationID = z.LocationID
GROUP BY z.Zone, y.PULocationID
ORDER BY count
LIMIT 5
    """).show()



