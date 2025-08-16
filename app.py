import streamlit as st
import pandas as pd

st.title("🧹 CRM Data Cleaning Automation")

# Upload CSV
uploaded_file = st.file_uploader("Upload your CRM file (CSV format)", type="csv")

if uploaded_file:
    # Read file
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Original Data (first 10 rows)")
    st.dataframe(df.head(10))

    # Step 1: Drop rows with missing key values if such columns exist
    key_columns = ["CUSTOMERNAME", "CONTACTLASTNAME", "CONTACTFIRSTNAME"]
    existing_keys = [col for col in key_columns if col in df.columns]

    if existing_keys:
        before_missing = len(df)
        df = df.dropna(subset=existing_keys, how="any")
        after_missing = len(df)
        removed_missing = before_missing - after_missing
    else:
        removed_missing = 0

    # Step 2: Remove duplicates
    before_dups = len(df)
    df = df.drop_duplicates()
    after_dups = len(df)
    removed_dups = before_dups - after_dups

    # Final cleaned dataframe
    st.subheader("✅ Cleaned Data (first 10 rows)")
    st.dataframe(df.head(10))

    # Step 3: Cleaning Report
    st.subheader("🧹 Data Cleaning Report")
    st.write(f"- Rows removed due to missing values: **{removed_missing}**")
    st.write(f"- Duplicate rows removed: **{removed_dups}**")
    st.write(f"- Final dataset size: **{len(df)} rows, {len(df.columns)} columns**")

    # Download button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Cleaned CSV",
        data=csv,
        file_name="cleaned_crm_data.csv",
        mime="text/csv"
    )
else:
    st.info("Please upload a CSV file to start cleaning.")
