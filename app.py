import streamlit as st
import duckdb

st.set_page_config(page_title="Lakehouse Analytics Dashboard", layout="wide")
st.title("📊 Lakehouse Data Mart Dashboard")

@st.cache_data(ttl=60)
def load_dbt_marts():
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    
    # MinIO S3 configuration
    con.execute("""
        SET s3_endpoint='127.0.0.1:9000';
        SET s3_access_key_id='minioadmin';
        SET s3_secret_access_key='minioadminpassword';
        SET s3_use_ssl=false;
        SET s3_url_style='path';
    """)
    
    # Querying partitioned Parquet transformed through staging rules
    query = """
        WITH sales AS (
            SELECT 
                TRIM(product) AS product_name,
                CAST(amount AS DOUBLE) AS amount_usd
            FROM read_parquet('s3://warehouse/partitioned_sales/*/*/*.parquet')
        )
        SELECT 
            product_name,
            COUNT(*) AS total_orders,
            SUM(amount_usd) AS total_revenue,
            AVG(amount_usd) AS avg_order_value
        FROM sales
        GROUP BY product_name
        ORDER BY total_revenue DESC
    """
    return con.execute(query).df()

# Load data
df = load_dbt_marts()

# Metrics Display
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${df['total_revenue'].sum():,.2f}")
col2.metric("Total Orders", f"{df['total_orders'].sum():,}")
col3.metric("Top Product", df.iloc[0]['product_name'] if not df.empty else "N/A")

st.markdown("---")

# Product Performance Table & Chart
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📦 Product Performance Mart (`fct_product_performance`)")
    st.dataframe(df, use_container_width=True)

with col_right:
    st.subheader("📈 Revenue by Product")
    st.bar_chart(data=df, x="product_name", y="total_revenue")