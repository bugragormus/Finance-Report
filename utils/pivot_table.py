"""
pivot_table.py

Bu modül, kullanıcıların etkileşimli bir arayüz üzerinden dinamik pivot tablolar oluşturmasını ve bu tabloları 
görselleştirerek dışa aktarmasını sağlar. Streamlit arayüzü kullanılarak kolayca:
- Satır ve sütun alanları seçilebilir
- Sayısal değerler için özet fonksiyonları uygulanabilir (toplam, ortalama, maksimum, minimum, adet)
- Oluşturulan tablo hem Excel hem de PNG formatında indirilebilir

Ana Özellikler:
---------------
- Kategorik ve sayısal sütunların otomatik ayrımı
- Kullanıcı dostu hata mesajları ve validasyon
- Görselleştirilebilir tablo çıktısı (Plotly ile)
- PNG formatında grafik çıktısı ve Excel formatında veri çıktısı

Kütüphaneler:
-------------
- streamlit: Arayüz için
- pandas: Veri işleme ve pivot tablo oluşturma
- plotly.express: Görselleştirme
- io.BytesIO: Bellek içi dosya nesneleriyle çalışma
- openpyxl: Excel yazımı
- utils.error_handler: Hata yakalama ve kullanıcı dostu hata gösterimi
"""


import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import plotly.io as pio
from typing import Tuple, Optional
from utils.error_handler import handle_error, display_friendly_error

# Grafik export ayarları
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 1000
pio.kaleido.scope.default_height = 600
pio.kaleido.scope.default_colorway = px.colors.qualitative.Plotly
pio.kaleido.scope.default_paper_bgcolor = "white"
pio.kaleido.scope.default_plot_bgcolor = "white"


@handle_error
def show_pivot_table(df: pd.DataFrame) -> Tuple[Optional[BytesIO], Optional[BytesIO]]:
    """
    Verilen bir DataFrame'den dinamik bir pivot tablo oluşturur ve görselleştirir.
    Ayrıca oluşturulan pivot tabloyu Excel ve PNG formatlarında indirme seçenekleri sunar.

    Kullanıcı arayüzü üzerinden:
    - Satır ve sütun alanları (kategorik değişkenler)
    - Değer alanı (sayısal değişkenler)
    - Toplama fonksiyonu (sum, mean, max, min, count)

    seçilerek pivot tablo oluşturulur.

    Parametreler:
        df (pd.DataFrame): Pivot tabloya dönüştürülecek veri çerçevesi.

    Döndürür:
        Tuple[Optional[BytesIO], Optional[BytesIO]]:
            - `excel_buffer`: Oluşturulan pivot tablonun Excel dosyası olarak bellekteki temsili.
            - `pivot_buffer`: Pivot tablonun PNG görseli olarak bellekteki temsili (görselleştirme mümkünse).
              Görselleştirme yapılamazsa `None` döner.

    Notlar:
        - Eğer sayısal sütun yoksa veya gerekli seçimler yapılmadıysa, işlem gerçekleştirilmez.
        - Görselleştirme, maksimum 15 sütunla sınırlıdır.
        - Hatalar kullanıcı dostu şekilde arayüzde gösterilir.
    """

    st.subheader("📊 Dinamik Pivot Tablo Oluşturucu")

    # Sütunları numerik ve kategorik olarak ayır
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    non_numeric_cols = [col for col in df.columns if col not in numeric_cols]

    # Kullanıcı seçimleri
    row_col = st.multiselect("🧱 Satır Alanları", non_numeric_cols)
    col_col = st.multiselect("📏 Sütun Alanları", non_numeric_cols)
    
    if not numeric_cols:
        display_friendly_error(
            "Sayısal sütun bulunamadı",
            "Pivot tablo için en az bir sayısal sütun gereklidir."
        )
        return None, None
        
    val_col = st.selectbox("🔢 Değer Alanı", numeric_cols)

    agg_func = st.selectbox(
        "🔧 Toplama Fonksiyonu", ["sum", "mean", "max", "min", "count"]
    )

    if row_col and col_col and val_col:
        try:
            # Pivot tablo oluştur
            pivot = pd.pivot_table(
                df,
                index=row_col,
                columns=col_col,
                values=val_col,
                aggfunc=agg_func,
                fill_value=0,
            )

            st.dataframe(pivot, use_container_width=True)

            # Excel export
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                pivot.to_excel(writer)
            st.download_button(
                label="⬇ İndir (Excel)",
                data=excel_buffer.getvalue(),
                file_name="pivot_tablo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            # Pivot görüntüsü oluştur
            pivot_buffer = None
            if len(pivot.columns) <= 15:
                try:
                    fig = px.imshow(
                        pivot, text_auto=True, aspect="auto", color_continuous_scale="Blues"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    png_bytes = fig.to_image(format="png")
                    pivot_buffer = BytesIO(png_bytes)
                    pivot_buffer.seek(0)

                    st.download_button(
                        label="⬇ İndir (PNG)",
                        data=pivot_buffer,
                        file_name="pivot_grafik.png",
                        mime="image/png",
                    )
                except Exception as e:
                    display_friendly_error(
                        f"Grafik oluşturma hatası: {str(e)}",
                        "Grafik oluşturulamadı, ancak Excel verisi hala mevcut."
                    )
            else:
                st.info("Görselleştirme için sütun sayısı çok fazla (maksimum 15).")

            return excel_buffer, pivot_buffer

        except Exception as e:
            display_friendly_error(
                f"Pivot tablo oluşturma hatası: {str(e)}",
                "Veri setinin yapısını kontrol edin veya farklı sütunlar seçin."
            )
            return None, None
    else:
        st.info("Lütfen satır, sütun ve değer alanlarını seçin.")
        return None, None
