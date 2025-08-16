import io
import re
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# ------------------------
# Helpers
# ------------------------
COMMON_DATE_COLS = ["order_date", "orderdate", "order date", "date",
                    "order_purchase_timestamp", "invoice_date", "created_at"]
COMMON_SALES_COLS = ["sales", "revenue", "amount", "payment_value", "total", "price"]
COMMON_PROFIT_COLS = ["profit", "margin", "gross_profit"]
COMMON_ORDERID_COLS = ["order_id", "order id", "order number", "orderno", "invoice", "invoice_id"]
COMMON_CUSTOMER_COLS = ["customer_name", "customer", "customer id", "customer_id", "client", "buyer_id"]

def find_col(columns, candidates):
    cols = [c for c in columns]
    lower_map = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand in lower_map:
            return lower_map[cand]
    # fuzzy: strip non-letters
    norm_map = {re.sub(r"[^a-z]", "", c.lower()): c for c in cols}
    for cand in candidates:
        nc = re.sub(r"[^a-z]", "", cand)
        if nc in norm_map:
            return norm_map[nc]
    return None

def try_read_csv(file_or_bytes):
    # multiple encodings fallback
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            return pd.read_csv(file_or_bytes, encoding=enc)
        except UnicodeDecodeError:
            if hasattr(file_or_bytes, "seek"):
                file_or_bytes.seek(0)
            continue
        except Exception:
            if hasattr(file_or_bytes, "seek"):
                file_or_bytes.seek(0)
            continue
    # last resort: let pandas guess with engine='python'
    try:
        if hasattr(file_or_bytes, "seek"):
            file_or_bytes.seek(0)
        return pd.read_csv(file_or_bytes, engine="python")
    except Exception as e:
        raise e

def parse_dates_inplace(df, date_col):
    if date_col is None:
        return df
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    return df

def safe_float_series(s):
    if np.issubdtype(s.dtype, np.number):
        return s
    return pd.to_numeric(s, errors="coerce")

# ------------------------
# UI
# ------------------------
st.set_page_config(page_title="Finance & CRM Auto-Report", layout="wide")
st.title("Finance & CRM Auto-Report (Streamlit demo)")

st.markdown(
    "Upload your report (CSV) **or** paste a **GitHub raw URL**. "
    "Works great with Kaggle’s *Sample Superstore* (Sales/Profit/Date)."
)

with st.expander("Load data"):
    col1, col2 = st.columns([2, 1])
    with col1:
        url = st.text_input("GitHub RAW CSV URL (optional)", placeholder="https://raw.githubusercontent.com/.../file.csv")
    with col2:
        st.write("")
        st.write("")
        use_url = st.checkbox("Load from URL", value=False)

    uploaded = st.file_uploader("…or upload CSV", type=["csv"])

    df = None
    load_error = None
    if use_url and url:
        try:
            # Streamlit fetches URLs fine via pandas
            df = try_read_csv(url)
        except Exception as e:
            load_error = f"Failed to load from URL: {e}"
    elif uploaded is not None:
        # Turn uploaded file into a BytesIO that we can seek on
        raw = uploaded.read()
        file_like = io.BytesIO(raw)
        try:
            df = try_read_csv(file_like)
        except Exception as e:
            load_error = f"Failed to read uploaded file: {e}"

if load_error:
    st.error(load_error)

if df is None:
    st.info("Please load a CSV file first (URL or Upload).")
    st.stop()

st.success("Data loaded successfully.")
st.caption(f"Detected columns: {list(df.columns)}")

# ------------------------
# Column mapping (auto-detect with manual override)
# ------------------------
auto_date = find_col(df.columns.str.lower(), COMMON_DATE_COLS)
auto_sales = find_col(df.columns.str.lower(), COMMON_SALES_COLS)
auto_profit = find_col(df.columns.str.lower(), COMMON_PROFIT_COLS)
auto_order = find_col(df.columns.str.lower(), COMMON_ORDERID_COLS)
auto_customer = find_col(df.columns.str.lower(), COMMON_CUSTOMER_COLS)

with st.expander("Column mapping (auto-detected, you can override)"):
    c1, c2, c3 = st.columns(3)
    with c1:
        date_col = st.selectbox("Date column", [None] + list(df.columns), index=(list(df.columns).index(auto_date)+1 if auto_date in df.columns else 0))
        order_col = st.selectbox("Order ID column", [None] + list(df.columns), index=(list(df.columns).index(auto_order)+1 if auto_order in df.columns else 0))
    with c2:
        sales_col = st.selectbox("Sales/Revenue column", [None] + list(df.columns), index=(list(df.columns).index(auto_sales)+1 if auto_sales in df.columns else 0))
        profit_col = st.selectbox("Profit column (optional)", [None] + list(df.columns), index=(list(df.columns).index(auto_profit)+1 if auto_profit in df.columns else 0))
    with c3:
        customer_col = st.selectbox("Customer column (optional)", [None] + list(df.columns), index=(list(df.columns).index(auto_customer)+1 if auto_customer in df.columns else 0))

# parse date
df = parse_dates_inplace(df, date_col)

# cast numerics
if sales_col:
    df[sales_col] = safe_float_series(df[sales_col])
if profit_col:
    df[profit_col] = safe_float_series(df[profit_col])

# ------------------------
# Date range filter (if date available)
# ------------------------
if date_col:
    min_d = pd.to_datetime(df[date_col].min())
    max_d = pd.to_datetime(df[date_col].max())
    if pd.isna(min_d) or pd.isna(max_d):
        st.warning("Date parsing produced NaT values. Check your date column.")
    else:
        start, end = st.slider(
            "Filter by date range",
            min_value=min_d.to_pydatetime(),
            max_value=max_d.to_pydatetime(),
            value=(min_d.to_pydatetime(), max_d.to_pydatetime()),
        )
        mask = (df[date_col] >= start) & (df[date_col] <= end)
        df = df.loc[mask].copy()

# ------------------------
# KPIs
# ------------------------
kpi_cols = st.columns(4)
total_sales = float(df[sales_col].sum()) if sales_col else np.nan
orders_count = int(df[order_col].nunique()) if order_col else len(df)
customers_count = int(df[customer_col].nunique()) if customer_col else np.nan
profit_sum = float(df[profit_col].sum()) if profit_col else np.nan
profit_margin = (profit_sum / total_sales * 100.0) if (profit_col and sales_col and total_sales) else np.nan

with kpi_cols[0]:
    st.metric("Revenue", f"{total_sales:,.2f}" if sales_col else "—")
with kpi_cols[1]:
    st.metric("Orders", f"{orders_count:,}")
with kpi_cols[2]:
    st.metric("Customers", f"{customers_count:,}" if not np.isnan(customers_count) else "—")
with kpi_cols[3]:
    st.metric("Profit Margin", f"{profit_margin:.1f}%" if not np.isnan(profit_margin) else "—")

st.divider()

# ------------------------
# Charts
# ------------------------
# 1) Revenue over time (monthly)
if date_col and sales_col:
    df["_month"] = df[date_col].dt.to_period("M").dt.to_timestamp()
    rev_month = df.groupby("_month", dropna=True)[sales_col].sum().reset_index()

    fig_time = px.line(rev_month, x="_month", y=sales_col, markers=True,
                       title="Revenue over time (Monthly)")
    fig_time.update_layout(xaxis_title="Month", yaxis_title="Revenue")
    st.plotly_chart(fig_time, use_container_width=True)

# 2) Top categories/dimensions if present (e.g., Segment/Category/Sub-Category)
with st.expander("Category breakdown (pick any categorical column)"):
    cat_cols = [c for c in df.columns if df[c].dtype == "object" and c not in [customer_col, order_col]]
    if len(cat_cols) == 0:
        st.info("No categorical columns found (object dtype).")
    else:
        ccol = st.selectbox("Choose a categorical column", cat_cols)
        if sales_col and ccol:
            top_cat = (
                df.groupby(ccol, dropna=False)[sales_col]
                .sum()
                .sort_values(ascending=False)
                .head(15)
                .reset_index()
            )
            fig_cat = px.bar(top_cat, x=ccol, y=sales_col, title=f"Revenue by {ccol} (Top 15)")
            st.plotly_chart(fig_cat, use_container_width=True)

# 3) Top customers
with st.expander("Top customers"):
    if customer_col and sales_col:
        top_cust = (
            df.groupby(customer_col, dropna=False)[sales_col]
            .sum()
            .sort_values(ascending=False)
            .head(20)
            .reset_index()
        )
        st.dataframe(top_cust, use_container_width=True)
    else:
        st.info("Customer or Sales column not provided.")

# 4) Simple retention (repeat purchase rate)
with st.expander("Repeat purchase rate"):
    if customer_col and order_col:
        cust_orders = df.groupby(customer_col)[order_col].nunique()
        repeat_rate = (cust_orders.gt(1).sum() / cust_orders.shape[0] * 100) if cust_orders.shape[0] else 0.0
        st.metric("Repeat Purchase Rate", f"{repeat_rate:.1f}%")
    else:
        st.info("Need Customer and Order ID columns to compute repeat rate.")

# 5) Profit by month (if available)
if profit_col and date_col:
    prof_month = df.groupby(df[date_col].dt.to_period("M").dt.to_timestamp())[profit_col].sum().reset_index()
    fig_profit = px.bar(prof_month, x=date_col, y=profit_col, title="Profit over time (Monthly)")
    st.plotly_chart(fig_profit, use_container_width=True)

st.caption("Tip: This template auto-detects columns and lets you override them. Keep calm and ship dashboards.")
