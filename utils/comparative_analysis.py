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

    # Kullanıcıya ay seçme seçeneği ekle
    selected_month = st.selectbox(
        "📅 Ay Seçimi (İsteğe Bağlı)", ["Kümüle"] + MONTHS, index=0
    )

    # Bütçe ve Fiili kolonlarının adı
    if selected_month == "Kümüle":
        group_cols = ["Kümüle Bütçe", "Kümüle Fiili"]
    else:
        # Seçilen ay ismi ile uygun Bütçe ve Fiili kolonlarını oluşturuyoruz
        month_budget_col = f"{selected_month} Bütçe"
        month_actual_col = f"{selected_month} Fiili"

        # Kolonların mevcut olup olmadığını kontrol et
        if month_budget_col not in df.columns or month_actual_col not in df.columns:
            display_friendly_error(
                f"{selected_month} için Bütçe veya Fiili verisi eksik",
                "Farklı bir ay veya 'Kümüle' seçebilirsiniz."
            )
            return None, None

        group_cols = [month_budget_col, month_actual_col]

    # Sütunların varlığını kontrol et
    for col in group_cols:
        if col not in df.columns:
            display_friendly_error(
                f"{col} sütunu eksik",
                "Veri formatınızı kontrol edin."
            )
            return None, None

    try:
        # Verileri gruplama
        grouped = df.groupby(group_by_col)[group_cols].sum().reset_index()

        # Kullanım yüzdesi
        grouped["Kullanım (%)"] = (grouped[group_cols[1]] / grouped[group_cols[0]]) * 100

        # NaN değerleri ve sonsuz değerleri temizle
        grouped.replace([float('inf'), -float('inf')], pd.NA, inplace=True)
        
        # Grafik oluşturma
        fig = px.bar(
            grouped.sort_values(group_cols[1], ascending=False),
            x=group_by_col,
            y=group_cols,
            barmode="group",
            title=f"{group_by_col} Bazında {selected_month} Karşılaştırması",
            color_discrete_sequence=["#636EFA", "#EF553B"],
        )  # Mavi ve kırmızı renkler

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
            grouped.sort_values(group_cols[1], ascending=False)
        )
        st.dataframe(styled_grouped, use_container_width=True)

        # Excel dosyası oluştur
        excel_buffer = BytesIO()
        try:
            grouped.sort_values(group_cols[1], ascending=False).to_excel(
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
