import streamlit as st
import pandas as pd
import re
import plotly.express as px

# Проверка валидности телефона (только цифры, длина 7-15)
def is_valid_phone(phone):
    phone_str = str(phone)
    digits = re.sub(r"\D", "", phone_str)
    return 7 <= len(digits) <= 15

def main():
    st.title("CRM Demo Analysis")

    uploaded = st.file_uploader("Upload CSV file", type=["csv"])
    if not uploaded:
        st.info("Please upload your CSV file.")
        return

    # Попробуем разные кодировки
    try:
        df = pd.read_csv(uploaded, encoding="utf-8")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(uploaded, encoding="latin-1")
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded, encoding="cp1252")

    st.subheader("First rows of your data")
    st.write(df.head())

    # Валидация телефонов
    if "PHONE" in df.columns:
        df["valid_phone"] = df["PHONE"].apply(is_valid_phone)
        phone_stats = df["valid_phone"].value_counts()
        fig_phone = px.pie(
            names=phone_stats.index.map({True: "Valid", False: "Invalid"}),
            values=phone_stats.values,
            title="Valid vs Invalid Phones"
        )
        st.plotly_chart(fig_phone)

    # Источники лидов
    if "LEADSOURCE" in df.columns:
        source_counts = df["LEADSOURCE"].value_counts().nlargest(10)
        fig_source = px.bar(
            x=source_counts.index,
            y=source_counts.values,
            labels={'x': 'Lead Source', 'y': 'Count'},
            title="Top 10 Lead Sources"
        )
        st.plotly_chart(fig_source)

    # Потенциальные сделки
    if "POTENTIALDEALSIZE" in df.columns:
        df["POTENTIALDEALSIZE"] = pd.to_numeric(df["POTENTIALDEALSIZE"], errors='coerce')
        top_deals = df.nlargest(10, "POTENTIALDEALSIZE")[["CUSTOMERNAME", "POTENTIALDEALSIZE"]]
        st.subheader("Top 10 Customers by Potential Deal Size")
        st.write(top_deals)

    st.markdown("— DONE. —")

if __name__ == "__main__":
    main()
