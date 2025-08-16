import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="CRM/Finance Report", layout="wide")

st.title("📊 CRM & Finance Automated Report")

# --- Data Upload ---
st.sidebar.header("Data Source")
data_source = st.sidebar.radio("Choose data source:", ["GitHub link", "Upload CSV"])

if data_source == "GitHub link":
    url = st.sidebar.text_input("Paste GitHub raw CSV link:", 
                                "https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv")
    if url:
        df = pd.read_csv(url)
else:
    file = st.sidebar.file_uploader("Upload CSV file", type="csv")
    if file:
        df = pd.read_csv(file)

if 'df' in locals():
    st.subheader("🔎 Raw Data (first 10 rows)")
    st.dataframe(df.head(10))

    # --- Data Cleaning ---
    st.subheader("🧹 Data Cleaning Report")
    initial_shape = df.shape

    # Удаление пропусков
    df_clean = df.dropna(subset=["CUSTOMERNAME", "CONTACTLASTNAME", "CONTACTFIRSTNAME"], how="any")
    removed_nulls = initial_shape[0] - df_clean.shape[0]

    # Удаление дубликатов
    before_dupes = df_clean.shape[0]
    df_clean = df_clean.drop_duplicates()
    removed_dupes = before_dupes - df_clean.shape[0]

    st.markdown(f"""
    - Исходное количество строк: **{initial_shape[0]}**
    - Удалено строк с пропущенными данными: **{removed_nulls}**
    - Удалено дубликатов: **{removed_dupes}**
    - Итоговое количество строк: **{df_clean.shape[0]}**
    """)

    # --- Metrics & Visuals ---
    st.subheader("📈 Key Metrics")
    if "POTENTIALDEALSIZE" in df_clean.columns:
        st.metric("Средний размер сделки", round(df_clean["POTENTIALDEALSIZE"].mean(), 2))
        st.metric("Максимальный размер сделки", round(df_clean["POTENTIALDEALSIZE"].max(), 2))
        st.metric("Количество сделок", df_clean.shape[0])

    st.subheader("🌍 Deals by Country")
    if "COUNTRY" in df_clean.columns:
        country_stats = df_clean["COUNTRY"].value_counts().head(10)
        fig, ax = plt.subplots()
        country_stats.plot(kind="bar", ax=ax)
        ax.set_ylabel("Количество сделок")
        ax.set_xlabel("Страна")
        st.pyplot(fig)

    st.subheader("📌 Средний размер сделки по источнику (LEADSOURCE)")
    if {"LEADSOURCE", "POTENTIALDEALSIZE"}.issubset(df_clean.columns):
        lead_stats = df_clean.groupby("LEADSOURCE")["POTENTIALDEALSIZE"].mean().sort_values(ascending=False)
        fig2, ax2 = plt.subplots()
        lead_stats.plot(kind="bar", ax=ax2)
        ax2.set_ylabel("Средний размер сделки")
        ax2.set_xlabel("Источник")
        st.pyplot(fig2)
