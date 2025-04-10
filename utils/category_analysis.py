import streamlit as st
import pandas as pd
import plotly.express as px

def show_category_charts(df):
    st.subheader("🧾 Masraf Çeşidi Grubu 1 Bazında Dağılım")

    if "Masraf Çeşidi Grubu 1" not in df.columns or "Kümüle Fiili" not in df.columns:
        st.warning("Gerekli sütunlar eksik!")
        return

    grouped = df.groupby("Masraf Çeşidi Grubu 1")["Kümüle Fiili"].sum().reset_index()
    grouped = grouped.sort_values(by="Kümüle Fiili", ascending=False)

    fig_pie = px.pie(grouped, names="Masraf Çeşidi Grubu 1", values="Kümüle Fiili", title="Fiili Harcamaların Dağılımı")
    st.plotly_chart(fig_pie, use_container_width=True)

    fig_bar = px.bar(grouped, x="Masraf Çeşidi Grubu 1", y="Kümüle Fiili", title="Masraf Gruplarına Göre Fiili Harcama")
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)
