import duckdb
import pandas as pd

# 1. Create dataset locally in memory using Pandas
data = {
    'transaction_id': [101, 102, 103, 104, 105],
    'customer_id': ['C1001', 'C1002', 'C1001', 'C1003', 'C1002'],
    'product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones'],
    'amount': [1200.50, 25.00, 75.00, 300.00, 80.00],
    'transaction_date': ['2026-09-01', '2026-09-02', '2026-09-03', '2026-09-04', '2026-09-05']
}
df = pd.DataFrame(data)

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

print("--- Creating and Uploading Parquet File directly to MinIO ---")

# 3. Export DataFrame directly as Parquet into MinIO warehouse bucket
con.execute("COPY df TO 's3://warehouse/sales.parquet' (FORMAT PARQUET);")

print("SUCCESS: 'sales.parquet' written successfully to MinIO 'warehouse' bucket!")