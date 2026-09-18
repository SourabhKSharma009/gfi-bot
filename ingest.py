import duckdb
import pandas as pd
from datetime import datetime

# 1. New batch sales data
new_sales = [
    {"transaction_id": 106, "customer_id": "C1004", "product": "Laptop", "amount": 1250.00, "transaction_date": "2026-09-06"},
    {"transaction_id": 107, "customer_id": "C1005", "product": "Monitor", "amount": 320.00, "transaction_date": "2026-09-06"},
    {"transaction_id": 108, "customer_id": "C1001", "product": "Mouse", "amount": 25.00, "transaction_date": "2026-09-07"}
]

new_df = pd.DataFrame(new_sales)

# 2. Connect DuckDB to MinIO
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("""
    SET s3_endpoint='127.0.0.1:9000';
    SET s3_access_key_id='minioadmin';
    SET s3_secret_access_key='minioadminpassword';
    SET s3_use_ssl=false;
    SET s3_url_style='path';
""")

# 3. Read existing data, combine with new batch, and overwrite in MinIO
print("Fetching existing Parquet file from MinIO...")
existing_df = con.execute("SELECT * FROM 's3://warehouse/sales.parquet'").df()

combined_df = pd.concat([existing_df, new_df], ignore_index=True)

print(f"Uploading updated dataset ({len(combined_df)} records) to MinIO...")
con.execute("COPY combined_df TO 's3://warehouse/sales.parquet' (FORMAT PARQUET);")

print("SUCCESS: New batch ingested successfully!")