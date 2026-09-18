import duckdb

# Connect DuckDB to MinIO
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("""
    SET s3_endpoint='127.0.0.1:9000';
    SET s3_access_key_id='minioadmin';
    SET s3_secret_access_key='minioadminpassword';
    SET s3_use_ssl=false;
    SET s3_url_style='path';
""")

print("Reading full dataset from MinIO...")

# Export data into hive-partitioned Parquet folders on MinIO
con.execute("""
    COPY (
        SELECT 
            transaction_id,
            customer_id,
            product,
            amount,
            transaction_date,
            YEAR(CAST(transaction_date AS DATE)) AS year,
            MONTH(CAST(transaction_date AS DATE)) AS month
        FROM 's3://warehouse/sales.parquet'
    ) 
    TO 's3://warehouse/partitioned_sales' 
    (FORMAT PARQUET, PARTITION_BY (year, month), OVERWRITE_OR_IGNORE);
""")

print("SUCCESS: Partitioned dataset created on MinIO!")