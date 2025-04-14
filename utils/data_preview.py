import streamlit as st
import pandas as pd
from io import BytesIO

def show_filtered_data(df, filename="filtrelenmis_rapor.xlsx", style_func=None, title=None):
    """
    DataFrame'i gösterir, istenirse stil uygular, Excel çıktısı verir.
    """
    if title:
        st.markdown(title)
    # Stil fonksiyonu varsa uygula
    if style_func:
        styled_df = style_func(df.copy())
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

    # Excel çıktısı oluştur
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    # İndirme butonu
    st.download_button(
        label="⬇ İndir (Excel)",
        data=excel_buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    return excel_buffer


def show_grouped_summary(
    df, group_column, target_columns, filename, title=None, style_func=None
):
    # Gerçekten var olan kolonları filtrele
    existing_columns = [col for col in target_columns if col in df.columns]

    if group_column in df.columns and existing_columns:
        if title:
            st.markdown(title)

        grouped_df = df.groupby(group_column)[existing_columns].sum().reset_index()
        show_filtered_data(grouped_df, filename=filename, style_func=style_func)

    else:
        st.warning(
            f"'{group_column}' bazında özet oluşturulamadı. Gerekli sütunlar eksik olabilir."
        )

def calculate_group_totals(df, group_column, selected_months, metrics):
    """
    Grup bazında seçilen ayların toplamlarını hesaplar
    """
    # Toplanacak sütunları belirle
    columns_to_sum = []
    for month in selected_months:
        for metric in metrics:
            col_name = f"{month} {metric}"
            if col_name in df.columns:
                columns_to_sum.append(col_name)

    # Gruplandırılmış toplamları hesapla
    grouped_totals = df.groupby(group_column)[columns_to_sum].sum()

    # Her metrik için toplam sütun oluştur
    for metric in metrics:
        metric_cols = [col for col in columns_to_sum if metric in col]
        grouped_totals[f"Toplam {metric}"] = grouped_totals[metric_cols].sum(axis=1)

    return grouped_totals[[f"Toplam {metric}" for metric in metrics]]
