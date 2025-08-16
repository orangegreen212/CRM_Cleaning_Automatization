# app1.py

import streamlit as st
import pandas as pd
import re
import plotly.express as px

def is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", str(email)))

def main():
    st.title("CRM")

    uploaded = st.file_uploader("Please upload CSV file", type=["csv"])
    if not uploaded:
        st.info("Please upload CSV file, example, from Lead Scoring Dataset.")
        return

    df = pd.read_csv(uploaded)

    st.subheader("Первые строки")
    st.write(df.head())

    # Validation email
    df["valid_email"] = df["Email"].apply(is_valid_email)
    email_stats = df["valid_email"].value_counts()

    fig1 = px.pie(
        names=email_stats.index.map({True: "Valid", False: "Invalid"}),
        values=email_stats.values,
        title="Valid vs Invalid e-mails"
    )
    st.plotly_chart(fig1)

    # Lead
    if "Lead Stage" in df.columns:
        stage_counts = df["Lead Stage"].value_counts()
        fig2 = px.bar(x=stage_counts.index, y=stage_counts.values, labels={'x': 'Lead Stage', 'y': 'Count'}, title="Лиды по стадиям")
        st.plotly_chart(fig2)

    # Source Lead
    if "Lead Origin" in df.columns:
        origin_counts = df["Lead Origin"].value_counts().nlargest(10)
        fig3 = px.bar(x=origin_counts.index, y=origin_counts.values, labels={'x': 'Lead Origin', 'y': 'Count'}, title="Топ-10 источников лидов")
        st.plotly_chart(fig3)

    st.markdown("— DONE. —")

if __name__ == "__main__":
    main()
