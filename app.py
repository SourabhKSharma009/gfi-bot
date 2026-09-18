import streamlit as st
import duckdb
import plotly.express as px

st.set_page_config(page_title="Partitioned Lakehouse Dashboard", layout="wide")

st.title("📊 MinIO + DuckDB Partitioned Lakehouse Dashboard")
st.markdown("Querying **Partitioned Parquet** files directly from **MinIO S3**")

@st.cache_resource
def get_duckdb_connection():
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("""
        SET s3_endpoint='127.0.0.1:9000';
        SET s3_access_key_id='minioadmin';
        SET s3_secret_access_key='minioadminpassword';
        SET s3_use_ssl=false;
        SET s3_url_style='path';
    """)
    return con

con = get_duckdb_connection()

@st.cache_data(ttl=5)
def load_partitioned_data():
    return con.execute("""
        SELECT 
            transaction_id,
            customer_id,
            product,
            amount,
            transaction_date,
            year,
            month
        FROM 's3://warehouse/partitioned_sales/*/*/*.parquet'
    """).df()

try:
    df = load_partitioned_data()

    # Sidebar Controls
    st.sidebar.header("🔍 Filter Data")
    
    products = ["All"] + list(df["product"].unique())
    selected_product = st.sidebar.selectbox("Select Product", products)

    # Filter Logic
    filtered_df = df.copy()
    if selected_product != "All":
        filtered_df = filtered_df[filtered_df["product"] == selected_product]

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Filtered Transactions", len(filtered_df))
    col2.metric("Total Revenue", f"${filtered_df['amount'].sum():,.2f}")
    col3.metric("Avg Transaction Value", f"${filtered_df['amount'].mean():,.2f}")

    st.divider()

    # Visualizations
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Revenue Distribution")
        fig_bar = px.bar(
            filtered_df, 
            x="product", 
            y="amount", 
            color="product", 
            text_auto=True,
            title="Revenue by Selected Product"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Filtered Dataset View")
        st.dataframe(filtered_df, use_container_width=True)

except Exception as e:
    st.error(f"Error connecting to MinIO Partitioned Lakehouse: {e}")