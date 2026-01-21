import pandas as pd
from sqlalchemy import create_engine

# Read the Parqu et file
df = pd.read_parquet('./green_tripdata_2025-11.parquet')

# Create database connection
engine = create_engine('postgresql://postgres:postgres@db:5432/ny_taxi')

# Import to PostgreSQL
df.to_sql('green_tripdata_2025-11', engine, if_exists='replace', index=False)

print("Import completed!!!")
