import sys
import pandas as pd

print("arguments", sys.argv)

month = int(sys.argv[1])
print(f"hello pipeline, month={month}")


df = pd.DataFrame({"day": [1, 2], "no_pssngr": [3, 4]})

df['month'] = month
print(df.head())

df.to_parquet(f"output_day_{sys.argv[1]}.parquet")