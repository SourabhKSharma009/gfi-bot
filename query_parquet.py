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

print("\n--- Analytical Query directly on Parquet File ---")

# Parquet file par fast aggregation query
df = con.execute("""
    SELECT 
        product,
        COUNT(transaction_id) as total_sold,
        SUM(amount) as revenue
    FROM 's3://warehouse/sales.parquet'
    GROUP BY product
    ORDER BY revenue DESC
""").df()

print(df)