import streamlit as st
import pandas as pd
import plotly.express as px

# Заголовок
st.title("Автоматизация очистки CRM данных")

# Загрузка датасета
uploaded_file = st.file_uploader("Загрузите CSV файл", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("Первые строки датасета")
    st.write(df.head())

    # Пропуски
    st.subheader("Пропущенные значения")
    st.write(df.isnull().sum())

    # Числовое описание
    st.subheader("Статистика по числовым данным")
    st.write(df.describe())

    # Визуализация: распределение числовых колонок
    numeric_cols = df.select_dtypes(include="number").columns

    if len(numeric_cols) > 0:
        col = st.selectbox("Выберите колонку для графика", numeric_cols)
        fig = px.histogram(df, x=col, nbins=30, title=f"Распределение {col}")
        st.plotly_chart(fig)
    else:
        st.info("Числовых колонок не найдено")
