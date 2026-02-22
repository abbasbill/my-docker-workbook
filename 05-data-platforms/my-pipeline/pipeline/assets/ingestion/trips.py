"""@bruin

name: ingestion.trips
connection: duckdb-default

materialization:
  type: table
  strategy: append
image: python:3.11

@bruin"""

import os
import json
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


def materialize():
    """
    Ingest NYC taxi trip data from the public dataset.
    
    Uses Bruin runtime context to:
    - Fetch data for the specified date window
    - Process multiple taxi types (yellow, green, etc.)
    - Return a DataFrame with proper schema and lineage columns
    """
    # Get environment variables from Bruin runtime
    start_date_str = os.getenv('BRUIN_START_DATE')
    end_date_str = os.getenv('BRUIN_END_DATE')
    bruin_vars_str = os.getenv('BRUIN_VARS', '{}')
    
    # Parse variables
    bruin_vars = json.loads(bruin_vars_str)
    taxi_types = bruin_vars.get('taxi_types', ['yellow'])
    
    # Parse dates
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    
    # Define schema for all taxi types (flexible to handle missing columns)
    # Let pandas infer types and we'll convert after loading if needed
    parse_dates = ['tpep_pickup_datetime', 'tpep_dropoff_datetime']
    
    # Collect data for all months in the date range
    all_dfs = []
    current_date = start_date
    
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        
        for taxi_type in taxi_types:
            try:
                # Construct URL for NYC TLC data
                url = (
                    f'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/'
                    f'{taxi_type}/{taxi_type}_tripdata_{year:04d}-{month:02d}.csv.gz'
                )
                
                print(f'Fetching {taxi_type} taxi data for {year:04d}-{month:02d} from: {url}')
                
                # Read CSV with flexible dtypes (infer from data)
                df = pd.read_csv(
                    url,
                    parse_dates=parse_dates,
                    low_memory=False,
                    on_bad_lines='skip'  # Skip problematic rows
                )
                
                # Add metadata columns for lineage
                df['taxi_type'] = taxi_type
                df['extracted_at'] = datetime.utcnow().isoformat()
                
                all_dfs.append(df)
                print(f'Successfully ingested {len(df)} records')
                
            except Exception as e:
                import traceback
                print(f'Error: Could not fetch {taxi_type} taxi for {year:04d}-{month:02d}: {str(e)}')
                traceback.print_exc()
        
        # Move to next month
        current_date += relativedelta(months=1)
    
    if not all_dfs:
        raise ValueError(f'No data was ingested for the date range {start_date_str} to {end_date_str}')
    
    # Combine all DataFrames
    final_df = pd.concat(all_dfs, ignore_index=True)
    
    print(f'Total records ingested: {len(final_df)}')
    
    return final_df
