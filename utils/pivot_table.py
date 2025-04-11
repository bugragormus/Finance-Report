import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
from io import BytesIO

# Grafik export ayarları
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 1000
pio.kaleido.scope.default_height = 600
pio.kaleido.scope.default_colorway = px.colors.qualitative.Plotly
pio.kaleido.scope.default_paper_bgcolor = "white"
pio.kaleido.scope.default_plot_bgcolor = "white"

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

            # 🔽 Excel indirme
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                pivot.to_excel(writer)
            st.download_button(
                label="⬇ İndir (Excel)",
                data=excel_buffer.getvalue(),
                file_name="pivot_tablo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # 📊 PNG indirme
            if len(pivot.columns) <= 15:
                fig = px.imshow(pivot, text_auto=True, aspect="auto", color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)

                png_bytes = fig.to_image(format="png")
                st.download_button(
                    label="⬇ İndir (PNG)",
                    data=png_bytes,
                    file_name="pivot_grafik.png",
                    mime="image/png"
                )

        except Exception as e:
            st.error(f"Hata oluştu: {e}")
    else:
        st.info("Lütfen satır, sütun ve değer alanlarını seçin.")
