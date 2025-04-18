"""
comparative_analysis.py - Karşılaştırmalı analiz ve görselleştirme işlemlerini yönetir.

Bu modül, farklı kategoriler arasında karşılaştırmalı analizler oluşturmak ve 
görselleştirmek için fonksiyonlar içerir.
"""

import streamlit as st
import plotly.express as px
from io import BytesIO
import plotly.io as pio
import pandas as pd
from typing import Tuple, Optional
from utils.error_handler import handle_error, display_friendly_error
from utils.warning_system import style_overused_rows

# Grafik export ayarları
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 1000
pio.kaleido.scope.default_height = 600
pio.kaleido.scope.default_colorway = px.colors.qualitative.Plotly
pio.kaleido.scope.default_paper_bgcolor = "white"
pio.kaleido.scope.default_plot_bgcolor = "white"

from config.constants import MONTHS


@handle_error
def show_comparative_analysis(
    df: pd.DataFrame, 
    group_by_col: str = "İlgili 1"
) -> Tuple[Optional[BytesIO], Optional[BytesIO]]:
    """
    Seçilen gruplama faktörüne göre karşılaştırmalı analiz gösterir.
    
    Parameters:
        df (DataFrame): İşlenecek veri çerçevesi
        group_by_col (str): Gruplama yapılacak sütun adı
        
    Returns:
        Tuple[Optional[BytesIO], Optional[BytesIO]]: 
            (excel_buffer, görüntü_buffer) tuple
    """
    st.subheader(f"📊 {group_by_col} Bazında Harcama Karşılaştırması")

    if group_by_col not in df.columns:
        display_friendly_error(
            f"{group_by_col} sütunu bulunamadı",
            "Farklı bir gruplama kriteri seçin."
        )
        return None, None

    # Sidebar'dan seçilen ayları al
    selected_months = st.session_state.get("month_filter", ["Hepsi"])
    if "Hepsi" in selected_months:
        selected_months = MONTHS

    # Seçilen ayların toplam bütçe ve fiili verilerini hesapla
    total_budget_cols = [f"{month} Bütçe" for month in selected_months if f"{month} Bütçe" in df.columns]
    total_actual_cols = [f"{month} Fiili" for month in selected_months if f"{month} Fiili" in df.columns]

    if not total_budget_cols or not total_actual_cols:
        display_friendly_error(
            "Seçilen aylar için veri bulunamadı",
            "Farklı aylar seçin veya veri formatını kontrol edin."
        )
        return None, None

    try:
        # Verileri gruplama ve toplama
        grouped = df.groupby(group_by_col)[total_budget_cols + total_actual_cols].sum()
        
        # Toplam bütçe ve fiili hesapla
        grouped["Toplam Bütçe"] = grouped[total_budget_cols].sum(axis=1)
        grouped["Toplam Fiili"] = grouped[total_actual_cols].sum(axis=1)
        
        # Kullanım yüzdesi hesapla
        grouped["Kullanım (%)"] = (grouped["Toplam Fiili"] / grouped["Toplam Bütçe"]) * 100
        
        # NaN değerleri ve sonsuz değerleri temizle
        grouped.replace([float('inf'), -float('inf')], pd.NA, inplace=True)
        
        # Sadece toplam sütunları al
        result_df = grouped[["Toplam Bütçe", "Toplam Fiili", "Kullanım (%)"]].reset_index()
        
        # Grafik oluşturma
        fig = px.bar(
            result_df.sort_values("Toplam Fiili", ascending=False),
            x=group_by_col,
            y=["Toplam Bütçe", "Toplam Fiili"],
            barmode="group",
            title=f"{group_by_col} Bazında Year to Date Toplam Karşılaştırması",
            color_discrete_sequence=["#636EFA", "#EF553B"],
        )

        # Grafik stil ayarları
        fig.update_layout(
            template="plotly_white",
            font=dict(color="black", size=12),
            xaxis=dict(tickangle=-45),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=50, r=50, t=80, b=150),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Grafiği hafızada bir görüntüye kaydet
        comperative_img_buffer = BytesIO()
        pio.write_image(fig, comperative_img_buffer, format="png", width=800, height=600)
        comperative_img_buffer.seek(0)  # Tamponun başına git

        # Görüntü için indirme düğmesi ekle
        st.download_button(
            label="⬇ İndir (PNG)",
            data=comperative_img_buffer,
            file_name="comparative_analysis.png",
            mime="image/png",
            key="download_image",
        )

        st.markdown("---")

        # Tablo gösterimi
        styled_grouped = style_overused_rows(
            result_df.sort_values("Toplam Fiili", ascending=False)
        )
        st.dataframe(styled_grouped, use_container_width=True)

        # Excel dosyası oluştur
        excel_buffer = BytesIO()
        try:
            result_df.sort_values("Toplam Fiili", ascending=False).to_excel(
                excel_buffer, index=False
            )
            excel_buffer.seek(0)

            # Excel indirme butonu
            st.download_button(
                label="⬇ İndir (Excel)",
                data=excel_buffer,
                file_name=f"{group_by_col}_bazinda_veriler.xlsx",
                mime="application/vnd.ms-excel",
                key="download_excel",
            )
        except Exception as e:
            display_friendly_error(
                f"Excel oluşturma hatası: {str(e)}",
                "Excel raporu oluşturulamadı."
            )
            return None, comperative_img_buffer

        return excel_buffer, comperative_img_buffer  # ZIP için main.py'ye döndür
        
    except Exception as e:
        display_friendly_error(
            f"Karşılaştırmalı analiz hatası: {str(e)}",
            "Veri formatını kontrol edin ve tekrar deneyin."
        )
        return None, None
