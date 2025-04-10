import streamlit as st
import pandas as pd
import plotly.express as px

def show_pivot_table(df):
    st.subheader("📊 Dinamik Pivot Tablo Oluşturucu")

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    non_numeric_cols = [col for col in df.columns if col not in numeric_cols]

    row_col = st.multiselect("🧱 Satır Alanları", non_numeric_cols)
    col_col = st.multiselect("📏 Sütun Alanları", non_numeric_cols)
    val_col = st.selectbox("🔢 Değer Alanı", numeric_cols)

    agg_func = st.selectbox("🔧 Toplama Fonksiyonu", ["sum", "mean", "max", "min", "count"])

    if row_col and col_col and val_col:
        try:
            pivot = pd.pivot_table(
                df,
                index=row_col,
                columns=col_col,
                values=val_col,
                aggfunc=agg_func,
                fill_value=0
            )
            st.dataframe(pivot, use_container_width=True)

            if len(pivot.columns) <= 15:
                fig = px.imshow(pivot, text_auto=True, aspect="auto", color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Hata oluştu: {e}")
    else:
        st.info("Lütfen satır, sütun ve değer alanlarını seçin.")
