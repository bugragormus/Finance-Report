import streamlit as st
import plotly.express as px

def show_comparative_analysis(df, group_by_col="İlgili 1"):
    st.subheader(f"📊 {group_by_col} Bazında Harcama Karşılaştırması")

    if group_by_col not in df.columns:
        st.warning(f"{group_by_col} sütunu bulunamadı!")
        return

    group_cols = ["Kümüle Bütçe", "Kümüle Fiili"]
    for col in group_cols:
        if col not in df.columns:
            st.warning(f"{col} sütunu eksik.")
            return

    grouped = df.groupby(group_by_col)[group_cols].sum().reset_index()
    grouped["Kullanım (%)"] = (grouped["Kümüle Fiili"] / grouped["Kümüle Bütçe"]) * 100

    fig = px.bar(grouped.sort_values("Kümüle Fiili", ascending=False),
                 x=group_by_col, y=["Kümüle Bütçe", "Kümüle Fiili"],
                 barmode="group", title=f"{group_by_col} Bazında Kümüle Karşılaştırma")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(grouped.sort_values("Kümüle Fiili", ascending=False), use_container_width=True)
