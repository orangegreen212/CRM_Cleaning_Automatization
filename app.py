import streamlit as st
import pandas as pd
import plotly.express as px

st.title("CRM Data Cleaning & Visualization")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    # Try reading with different encodings
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(uploaded_file, encoding="latin-1")
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded_file, encoding="cp1252")

    st.subheader("Preview of the dataset")
    st.write(df.head())

    # Missing values
    st.subheader("Missing values per column")
    st.write(df.isnull().sum())

    # Numeric statistics
    st.subheader("Statistics for numeric columns")
    st.write(df.describe())

    # Numeric distribution plot
    numeric_cols = df.select_dtypes(include="number").columns

    if len(numeric_cols) > 0:
        col = st.selectbox("Choose a numeric column for visualization", numeric_cols)
        fig = px.histogram(df, x=col, nbins=30, title=f"Distribution of {col}")
        st.plotly_chart(fig)
    else:
        st.info("No numeric columns found in this dataset.")
