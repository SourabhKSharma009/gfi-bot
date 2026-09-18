import duckdb

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("""
    SET s3_endpoint='127.0.0.1:9000';
    SET s3_access_key_id='minioadmin';
    SET s3_secret_access_key='minioadminpassword';
    SET s3_use_ssl=false;
    SET s3_url_style='path';
""")

# Querying with Hive Partition Auto-detection
print("--- Querying Entire Partitioned Lakehouse ---")
df_all = con.execute("""
    SELECT product, SUM(amount) as total_revenue
    FROM 's3://warehouse/partitioned_sales/*/*/*.parquet'
    GROUP BY product
""").df()
print(df_all)

print("\n--- Querying Specific Partition (Partition Pruning) ---")
df_sept = con.execute("""
    SELECT * 
    FROM 's3://warehouse/partitioned_sales/year=2026/month=9/*.parquet'
""").df()
print(df_sept)