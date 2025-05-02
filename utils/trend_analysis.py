"""
trend_analysis.py

Bu modül, finansal verilerin aylık bazda zaman içindeki trendlerini analiz eder 
ve interaktif grafiklerle görselleştirir. Kullanıcılar, seçilen aylar için bütçe, fiili ve 
aradaki farkları aynı grafik üzerinde görüntüleyebilir, ayrıca bu grafikleri PNG formatında dışa aktarabilir.

Ana Özellikler:
---------------
- Seçilen aylar için toplam bütçe ve fiili değerlerin hesaplanması
- Bütçe ve fiili değerlerin çubuk grafikle, farkların ise çizgi grafikle gösterimi
- Grafiklerin PNG formatında dışa aktarılabilmesi
- Hata yönetimi ve kullanıcı dostu uyarılar

Kütüphaneler:
-------------
- streamlit: Kullanıcı arayüzü için
- pandas: Veri işleme ve tablo oluşturma
- plotly.graph_objects: Gelişmiş grafik oluşturma
- io.BytesIO: Grafik çıktısını bellekte tutma ve indirme işlemleri
- datetime: Dosya adlarında zaman damgası kullanımı
- utils.error_handler: Hata yakalama ve kullanıcıya dostça gösterme
"""


import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
from typing import Optional, List
from utils.error_handler import handle_error, display_friendly_error


@handle_error
def show_trend_analysis(
    df: pd.DataFrame, 
    selected_months: List[str], 
    budget_color: str = "#636EFA", 
    actual_color: str = "#EF553B", 
    difference_color: str = "#00CC96"
) -> Optional[BytesIO]:
    """
    Aylık finansal trendleri görselleştirir.
    
    Parameters:
        df (DataFrame): İşlenecek veri çerçevesi
        selected_months (List[str]): Grafikte gösterilecek aylar
        budget_color (str): Bütçe çubuklarının rengi
        actual_color (str): Fiili çubuklarının rengi
        difference_color (str): Fark çizgisinin rengi
        
    Returns:
        Optional[BytesIO]: Grafik görüntüsü buffer'ı veya None
    """
    st.subheader("📈 Aylık Trend Analizi")

    trend_data = []
    for month in selected_months:
        b_col, a_col = f"{month} Bütçe", f"{month} Fiili"
        if b_col in df.columns and a_col in df.columns:
            budget_val = df[b_col].sum()
            actual_val = df[a_col].sum()
            trend_data.append(
                {
                    "Ay": month,
                    "Bütçe": budget_val,
                    "Fiili": actual_val,
                    "Fark": budget_val - actual_val,
                }
            )

    if not trend_data:
        display_friendly_error(
            "Trend analizi için yeterli veri yok.",
            "Lütfen farklı aylar veya veri türleri seçin."
        )
        return None

    df_trend = pd.DataFrame(trend_data)
    
    try:
        fig = go.Figure()
        fig.add_bar(
            x=df_trend["Ay"], y=df_trend["Bütçe"], name="Bütçe", marker_color=budget_color
        )
        fig.add_bar(
            x=df_trend["Ay"], y=df_trend["Fiili"], name="Fiili", marker_color=actual_color
        )
        fig.add_trace(
            go.Scatter(
                x=df_trend["Ay"],
                y=df_trend["Fark"],
                name="Fark",
                line=dict(color=difference_color),
            )
        )
        
        # Grafik düzenleme
        fig.update_layout(
            legend=dict(orientation="h", yanchor="top", y=1.1, xanchor="center", x=0.5),
            margin=dict(t=30, b=0, l=0, r=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # PNG export
        img_buffer = BytesIO()
        fig.write_image(img_buffer, format="png")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            "⬇ İndir (PNG)",
            data=img_buffer.getvalue(),
            file_name=f"trend_analizi_{timestamp}.png",
            mime="image/png",
        )

        return img_buffer
        
    except Exception as e:
        display_friendly_error(
            f"Grafik oluşturma hatası: {str(e)}",
            "Veri setini kontrol edin ve tekrar deneyin."
        )
        return None
