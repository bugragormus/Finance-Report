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
- Verilerin orijinal sırasını koruma ve ayların kronolojik sırada gösterimi

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

from utils.data_preview import show_column_totals
from utils.error_handler import handle_error, display_friendly_error
from config.constants import REPORT_BASE_COLUMNS, MONTHS, CUMULATIVE_COLUMNS

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
    - Değer alanı (REPORT_BASE_COLUMNS değerleri)
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
        - Veriler orijinal sırasını korur, aylar kronolojik sırada gösterilir.
    """

    st.subheader("📊 Dinamik Pivot Tablo Oluşturucu")

    # Sütunları numerik ve kategorik olarak ayır
    non_numeric_cols = [col for col in df.columns if col not in df.select_dtypes(include="number").columns]

    # Kullanıcı seçimleri
    row_col = st.multiselect("🧱 Satır Alanları", non_numeric_cols)
    
    # Sidebar'dan seçilen ayları al
    selected_months = st.session_state.get("month_filter", ["Hepsi"])
    if "Hepsi" in selected_months:
        selected_months = MONTHS

    # Değer türü seçimi
    value_type = st.radio(
        "📊 Değer Türü",
        ["Aylık Değerler", "Kümüle Değerler"],
        horizontal=True
    )

    # Değer alanı seçimi
    value_options = []
    if value_type == "Aylık Değerler":
        for base_col in REPORT_BASE_COLUMNS:
            # Seçilen aylardan en az birinde bu değer varsa ekle
            for month in selected_months:
                col_name = f"{month} {base_col}"
                if col_name in df.columns:
                    value_options.append(base_col)
                    break
    else:  # Kümüle Değerler
        for base_col in CUMULATIVE_COLUMNS:
            col_name = f"Kümüle {base_col}"
            if col_name in df.columns:
                value_options.append(base_col)

    if not value_options:
        display_friendly_error(
            f"Seçilen tür için değerler bulunamadı",
            "Farklı bir değer türü seçin veya veri formatını kontrol edin."
        )
        return None, None

    val_col = st.selectbox("🔢 Değer Alanı", value_options)

    # Sütun seçimi artık opsiyonel
    col_col = st.multiselect("📏 Sütun Alanları (Opsiyonel)", non_numeric_cols)

    agg_func = st.selectbox(
        "🔧 Toplama Fonksiyonu", ["sum", "mean", "max", "min", "count"]
    )

    if row_col and val_col:
        try:
            # Seçilen değer için veri sütunlarını belirle
            if value_type == "Aylık Değerler":
                # Ayları MONTHS listesindeki sıraya göre sırala
                value_columns = []
                for month in MONTHS:
                    col_name = f"{month} {val_col}"
                    if col_name in df.columns and month in selected_months:
                        value_columns.append(col_name)
            else:  # Kümüle Değerler
                value_columns = [f"Kümüle {val_col}"]
            
            if not value_columns:
                display_friendly_error(
                    f"Seçilen değer için veri bulunamadı",
                    "Farklı bir değer seçin veya veri formatını kontrol edin."
                )
                return None, None

            # Pivot tablo oluştur
            if col_col:
                # Eğer sütun seçilmişse, normal pivot tablo oluştur
                pivot = pd.pivot_table(
                    df,
                    index=row_col,
                    columns=col_col,
                    values=value_columns,
                    aggfunc=agg_func,
                    fill_value=0,
                    sort=False  # Sıralamayı devre dışı bırak
                )
            else:
                # Sütun seçilmemişse, değer sütunlarını kullan
                pivot = pd.pivot_table(
                    df,
                    index=row_col,
                    values=value_columns,
                    aggfunc=agg_func,
                    fill_value=0,
                    sort=False  # Sıralamayı devre dışı bırak
                )
                
                # Aylık değerler için sütunları MONTHS sırasına göre düzenle
                if value_type == "Aylık Değerler":
                    # Mevcut sütun isimlerini al
                    current_columns = pivot.columns.tolist()
                    # MONTHS sırasına göre sırala
                    ordered_columns = []
                    for month in MONTHS:
                        for col in current_columns:
                            if col.startswith(month):
                                ordered_columns.append(col)
                    # Sütunları yeniden sırala
                    pivot = pivot[ordered_columns]

            # Satırları orijinal sırada tut
            if row_col:
                # Orijinal veri setindeki sırayı koru
                original_order = df[row_col].drop_duplicates().reset_index(drop=True)
                pivot = pivot.reindex(original_order)

            # Pivot tabloyu göster
            st.dataframe(pivot, use_container_width=True)

            # Satır toplamlarını hesapla ve göster
            row_totals = pivot.sum(axis=1)
            row_totals_df = pd.DataFrame(row_totals, columns=["Toplam"])
            st.markdown("#### ➕ Satır Toplamları")
            st.dataframe(row_totals_df, use_container_width=True)

            # Excel export
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                pivot.to_excel(writer, sheet_name="Pivot Tablo")
                row_totals_df.to_excel(writer, sheet_name="Satır Toplamları")
            st.download_button(
                label="⬇ İndir (Excel)",
                data=excel_buffer.getvalue(),
                file_name="pivot_tablo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            return excel_buffer

        except Exception as e:
            display_friendly_error(
                f"Pivot tablo oluşturma hatası: {str(e)}",
                "Veri setinin yapısını kontrol edin veya farklı sütunlar seçin."
            )
            return None, None
    else:
        st.info("Lütfen satır ve değer alanlarını seçin.")
        return None, None
