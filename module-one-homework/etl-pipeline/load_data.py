import argparse
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
import sys


def get_file_format(file_path):
    """Determine file format from extension."""
    suffix = Path(file_path).suffix.lower()
    if suffix == '.parquet':
        return 'parquet'
    elif suffix == '.csv':
        return 'csv'
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .parquet or .csv")


def read_data(file_path, chunksize=None):
    """Read data from parquet or CSV file."""
    file_format = get_file_format(file_path)
    
    if file_format == 'parquet':
        print(f"Reading parquet file: {file_path}")
        return pd.read_parquet(file_path)
    
    elif file_format == 'csv':
        print(f"Reading CSV file: {file_path}")
        if chunksize:
            return pd.read_csv(file_path, chunksize=chunksize)
        return pd.read_csv(file_path)


def ingest_data(file_path, table_name, db_url, chunksize=100000):
    """
    Ingest data from parquet or CSV file into PostgreSQL database.
    
    Args:
        file_path: Path to the data file (.parquet or .csv)
        table_name: Name of the target database table
        db_url: PostgreSQL connection URL
        chunksize: Number of rows per chunk (for large files)
    """
    try:
        # Create database engine
        engine = create_engine(db_url)
        
        # Check if file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_format = get_file_format(file_path)
        
        # Handle parquet files
        if file_format == 'parquet':
            df = read_data(file_path)
            print(f"Loaded {len(df)} rows from parquet file")
            print(f"Columns: {list(df.columns)}")
            
            # Insert data
            print(f"Inserting data into table '{table_name}'...")
            df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
            print(f"✓ Successfully inserted {len(df)} rows")
        
        # Handle CSV files with chunking
        elif file_format == 'csv':
            # Read first chunk to get schema
            df_iter = pd.read_csv(file_path, chunksize=chunksize)
            df_first = next(df_iter)
            
            print(f"Loaded first chunk: {len(df_first)} rows")
            print(f"Columns: {list(df_first.columns)}")
            
            # Insert first chunk and create table
            print(f"Creating table '{table_name}' and inserting first chunk...")
            df_first.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
            
            rows_inserted = len(df_first)
            
            # Insert remaining chunks
            for i, chunk in enumerate(df_iter, start=2):
                print(f"Inserting chunk {i}: {len(chunk)} rows...")
                chunk.to_sql(name=table_name, con=engine, if_exists='append', index=False)
                rows_inserted += len(chunk)
            
            print(f"✓ Successfully inserted {rows_inserted} rows in total")
        
        print(f"✓ Data ingestion complete!")
        
    except Exception as e:
        print(f"Error during ingestion: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Ingest parquet or CSV data into PostgreSQL database'
    )
    parser.add_argument(
        '--file',
        required=True,
        help='Path to data file (.parquet or .csv)'
    )
    parser.add_argument(
        '--table',
        required=True,
        help='Name of the database table'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='Database host (default: localhost)'
    )
    parser.add_argument(
        '--port',
        default='5432',
        help='Database port (default: 5432)'
    )
    parser.add_argument(
        '--database',
        required=True,
        help='Database name'
    )
    parser.add_argument(
        '--user',
        required=True,
        help='Database user'
    )
    parser.add_argument(
        '--password',
        required=True,
        help='Database password'
    )
    parser.add_argument(
        '--chunksize',
        type=int,
        default=100000,
        help='Chunk size for CSV processing (default: 100000)'
    )
    
    args = parser.parse_args()
    
    # Build database URL
    db_url = f'postgresql://{args.user}:{args.password}@{args.host}:{args.port}/{args.database}'
    
    # Ingest data
    ingest_data(
        file_path=args.file,
        table_name=args.table,
        db_url=db_url,
        chunksize=args.chunksize
    )


if __name__ == '__main__':
    main()

 

 