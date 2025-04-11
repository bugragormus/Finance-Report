import streamlit as st
import pandas as pd
from io import BytesIO

from utils.warning_system import style_warning_rows


def show_filtered_data(df, filename="filtrelenmis_rapor.xlsx"):
    st.subheader("📋 Filtrelenmiş Veriler")

    # Uyarı stili uygulanmış dataframe
    styled_df = style_warning_rows(df.copy())
    st.dataframe(styled_df, use_container_width=True)

    # Excel çıktısı
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    st.download_button(
        "⬇ İndir (Excel)",
        data=excel_buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    return excel_buffer  # Diğer yerlerde kullanmak üzere çıktı
