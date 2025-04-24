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
- utils.formatting: Para birimi formatı işlemleri
- config.constants: Sabit değerler
"""


import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import plotly.io as pio
from typing import Tuple, Optional

from utils.data_preview import show_column_totals
from utils.error_handler import handle_error, display_friendly_error
from utils.formatting import format_currency_columns
from config.constants import FIXED_METRICS, MONTHS, CUMULATIVE_COLUMNS, GENERAL_COLUMNS

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
    - Değer alanı (FIXED_METRICS değerleri)
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

    # Sidebar'dan seçilen report base'leri al
    selected_report_bases = st.session_state.get("report_base_filter", ["Hepsi"])
    if "Hepsi" in selected_report_bases:
        selected_report_bases = FIXED_METRICS

    # İzin verilen metrikleri filtrele
    allowed_metrics = [
        metric for metric in FIXED_METRICS
        if "Hepsi" in selected_report_bases or
           any(metric in base for base in selected_report_bases)
    ]

    # Değer alanı seçimi
    value_options = []
    if value_type == "Aylık Değerler":
        for metric in allowed_metrics:
            # Seçilen aylardan en az birinde bu değer varsa ekle
            for month in selected_months:
                col_name = f"{month} {metric}"
                if col_name in df.columns:
                    value_options.append(metric)
                    break
    else:  # Kümüle Değerler
        for metric in allowed_metrics:
            col_name = f"Kümüle {metric}"
            if col_name in df.columns:
                value_options.append(metric)

    if not value_options:
        display_friendly_error(
            f"Seçilen tür için değerler bulunamadı",
            "Farklı bir değer türü seçin veya veri formatını kontrol edin."
        )
        return None, None

    # Otomatik olarak tüm izin verilen metrikleri seç
    val_cols = value_options

    # Sütun seçimi artık opsiyonel
    col_col = st.multiselect("📏 Sütun Alanları (Opsiyonel)", non_numeric_cols)

    agg_func = st.selectbox(
        "🔧 Toplama Fonksiyonu", ["sum", "mean", "max", "min", "count"]
    )

    if row_col and val_cols:
        try:
            # Seçilen değerler için veri sütunlarını belirle
            value_columns = []
            if value_type == "Aylık Değerler":
                # Ayları MONTHS listesindeki sıraya göre sırala
                for month in MONTHS:
                    for val_col in val_cols:
                        col_name = f"{month} {val_col}"
                        if col_name in df.columns and month in selected_months:
                            value_columns.append(col_name)
            else:  # Kümüle Değerler
                for val_col in val_cols:
                    col_name = f"Kümüle {val_col}"
                    if col_name in df.columns:
                        value_columns.append(col_name)
            
            if not value_columns:
                display_friendly_error(
                    f"Seçilen değerler için veri bulunamadı",
                    "Farklı değerler seçin veya veri formatını kontrol edin."
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

            # Pivot tabloyu TL formatında göster
            display_pivot = format_currency_columns(pivot.copy(), [row_col])
            st.dataframe(display_pivot, use_container_width=True)

            # Satır toplamlarını hesapla ve göster
            if value_type == "Aylık Değerler":
                # Her bir değer alanı için ayrı toplam hesapla
                totals_dict = {}
                for val_col in val_cols:
                    # İlgili değer alanına ait sütunları bul
                    val_columns = [col for col in pivot.columns if col.endswith(f" {val_col}")]
                    if val_columns:
                        # Bu değer alanı için toplam hesapla
                        totals_dict[f"Toplam {val_col}"] = pivot[val_columns].sum(axis=1)
                
                # Toplamları DataFrame'e dönüştür
                row_totals_df = pd.DataFrame(totals_dict)
            else:  # Kümüle Değerler
                # Her bir değer alanı için ayrı toplam hesapla
                totals_dict = {}
                for val_col in val_cols:
                    # İlgili değer alanına ait sütunları bul
                    val_columns = [col for col in pivot.columns if col.startswith(f"Kümüle {val_col}")]
                    if val_columns:
                        # Bu değer alanı için toplam hesapla
                        totals_dict[f"Toplam {val_col}"] = pivot[val_columns].sum(axis=1)
                
                # Toplamları DataFrame'e dönüştür
                row_totals_df = pd.DataFrame(totals_dict)

            # Satır toplamlarını TL formatında göster
            display_totals = format_currency_columns(row_totals_df.copy(), [])
            st.markdown("#### ➕ Satır Toplamları")
            st.dataframe(display_totals, use_container_width=True)

            # Excel export
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                display_pivot.to_excel(writer, sheet_name="Pivot Tablo")
                display_totals.to_excel(writer, sheet_name="Satır Toplamları")
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
