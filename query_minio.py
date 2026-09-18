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

print("\n--- Querying sales.csv directly from MinIO Lakehouse via DuckDB ---\n")

# read_csv using explicit schema parsing options
df = con.execute("""
    SELECT 
        customer_id, 
        COUNT(transaction_id) as total_orders, 
        SUM(amount) as total_spent 
    FROM read_csv('s3://warehouse/sales.csv', 
                  header=True, 
                  delim=',', 
                  columns={
                      'transaction_id': 'INTEGER',
                      'customer_id': 'VARCHAR',
                      'product': 'VARCHAR',
                      'amount': 'DOUBLE',
                      'transaction_date': 'DATE'
                  }) 
    GROUP BY customer_id 
    ORDER BY total_spent DESC
""").df()

print(df)