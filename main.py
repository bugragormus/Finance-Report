"""
main.py - Finansal Performans Analiz Paneli ana uygulaması

Bu uygulama, finansal performans metriklerinin analizi, görselleştirilmesi 
ve raporlanması için kullanılır.

Modüller:
    - loader: Veri yükleme ve doğrulama
    - filters: Veri filtreleme işlemleri
    - metrics: Performans metriklerinin hesaplanması
    - report: PDF rapor oluşturma
    - kpi: KPI paneli görüntüleme
    - category_analysis: Kategori bazlı analizler
    - comparative_analysis: Karşılaştırmalı analizler
    - trend_analysis: Trend analizi
    - pivot_table: Pivot tablo görüntüleme
    - insight_generator: Veri içgörüleri oluşturma
    - data_preview: Veri önizleme
    - warning_system: Uyarı sistemi
    - error_handler: Hata yönetimi

Kullanım:
    streamlit run main.py --theme.base="light" --theme.primaryColor="#2f64b5" --theme.backgroundColor="#dee2e6" --theme.secondaryBackgroundColor="#e9ecef" --theme.textColor="#262730" --theme.font="sans serif"
"""

import streamlit as st
from io import BytesIO
import zipfile
from PIL import Image
import pandas as pd
import numpy as np

from utils.loader import load_data
from utils.filters import apply_filters
from utils.metrics import calculate_metrics
from utils.report import generate_pdf_report
from config.constants import (
    MONTHS,
    GENERAL_COLUMNS,
    REPORT_BASE_COLUMNS,
    CUMULATIVE_COLUMNS, FIXED_METRICS,
)
from utils.kpi import show_kpi_panel
from utils.category_analysis import show_category_charts
from utils.comparative_analysis import show_comparative_analysis
from utils.trend_analysis import show_trend_analysis
from utils.pivot_table import show_pivot_table
from utils.insight_generator import generate_insights
from utils.data_preview import show_filtered_data, show_grouped_summary, calculate_group_totals, show_column_totals
from utils.warning_system import style_negatives_red, style_warning_rows
from utils.error_handler import handle_critical_error, display_friendly_error


def setup_page_config():
    """
    Sayfa yapılandırmasını ayarlar.
    
    Bu fonksiyon:
    1. Favicon'u yükler
    2. Sayfa başlığını ayarlar
    3. Sayfa düzenini belirler
    4. Kenar çubuğu durumunu ayarlar
    
    Hata durumunda:
    - Favicon yüklenemezse varsayılan yapılandırmayı kullanır
    - Hata mesajını kullanıcıya gösterir
    """
    try:
        im = Image.open("assets/favicon.png")
        st.set_page_config(
            layout="wide", 
            page_title="Finansal Performans Analiz Paneli", 
            page_icon=im, 
            initial_sidebar_state="expanded"
        )
    except Exception as e:
        st.warning(f"Favicon yüklenemedi: {str(e)}")
        st.set_page_config(
            layout="wide", 
            page_title="Finansal Performans Analiz Paneli", 
            initial_sidebar_state="expanded"
        )


def load_and_validate_data():
    """
    Veri dosyasını yükler ve doğrular.
    
    Bu fonksiyon:
    1. Kullanıcıdan Excel dosyası yüklemesini bekler
    2. Yüklenen dosyayı işler
    3. Veri doğrulama işlemlerini gerçekleştirir
    
    Returns:
        DataFrame or None: Yüklenen veri çerçevesi veya hata durumunda None
        
    Hata durumunda:
    - Kullanıcıya bilgi mesajı gösterir
    - None döndürür
    """
    uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=["xlsx", "xls"])
    if uploaded_file:
        return load_data(uploaded_file)
    else:
        st.info("Lütfen ZFMR0003 raporunun Excel dosyasını yükleyin")
        return None


def setup_sidebar_filters(df):
    """
    Kenar çubuğundaki filtreleri ayarlar.
    
    Bu fonksiyon:
    1. Filtre başlığını gösterir
    2. Genel filtreleri uygular
    3. Ay filtrelerini ayarlar
    4. Rapor bazı filtrelerini ayarlar
    5. Kümülatif filtreleri ayarlar
    
    Parameters:
        df (DataFrame): Filtrelenecek veri çerçevesi
        
    Returns:
        tuple: (filtered_df, selected_months, selected_report_bases, selected_cumulative)
            - filtered_df: Filtrelenmiş veri çerçevesi
            - selected_months: Seçili aylar
            - selected_report_bases: Seçili rapor bazları
            - selected_cumulative: Seçili kümülatif değerler
            
    Hata durumunda:
    - Varsayılan veriyi kullanır
    - Kullanıcıya hata mesajı gösterir
    """
    with st.sidebar:
        st.header("🔧 Filtre & Grafik Ayarları")
        
        # Veri filtreleme
        try:
            # Veri çerçevesini optimize et
            df = df.copy()
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(0)
            
            filtered_df = apply_filters(df, GENERAL_COLUMNS, "filter")
        except Exception as e:
            display_friendly_error(
                f"Filtreleme sırasında hata oluştu: {str(e)}",
                "Varsayılan veri kullanılacak."
            )
            filtered_df = df

        # Ay filtreleri
        all_months_with_all = ["Hepsi"] + MONTHS
        if "month_filter" not in st.session_state:
            st.session_state["month_filter"] = ["Hepsi"]
        selected_months = st.multiselect(
            "📅 Aylar", all_months_with_all, key="month_filter"
        )
        if "Hepsi" in selected_months:
            selected_months = MONTHS

        # Veri türü filtreleri
        report_base_columns_with_all = ["Hepsi"] + REPORT_BASE_COLUMNS
        if "report_base_filter" not in st.session_state:
            st.session_state["report_base_filter"] = ["Hepsi"]
        selected_report_bases = st.multiselect(
            "📉 Veri Türleri",
            report_base_columns_with_all,
            key="report_base_filter",
        )
        if "Hepsi" in selected_report_bases:
            selected_report_bases = REPORT_BASE_COLUMNS

        # Kümülatif veri filtreleri
        cumulative_columns = ["Kümüle " + col for col in CUMULATIVE_COLUMNS]
        if "cumulative_filter" not in st.session_state:
            st.session_state["cumulative_filter"] = ["Hepsi"]
        selected_cumulative = st.multiselect(
            "📈 Kümülatif Veriler",
            ["Hepsi"] + cumulative_columns,
            key="cumulative_filter",
        )
        if "Hepsi" in selected_cumulative:
            selected_cumulative = cumulative_columns
            
        # Filtre temizleme butonu
        if st.button("🗑️ Tüm Filtreleri Temizle"):
            clear_all_filters()
            
    return filtered_df, selected_months, selected_report_bases, selected_cumulative


def clear_all_filters():
    """
    Tüm filtreleri temizler.
    
    Bu fonksiyon:
    1. Tüm filtre durumlarını sıfırlar
    2. Kullanıcıya bilgi mesajı gösterir
    
    Hata durumunda:
    - Hata mesajını loglar
    - Kullanıcıya bilgi verir
    """
    try:
        for key in list(st.session_state.keys()):
            if key.startswith("filter_") or key in [
                "month_filter",
                "report_base_filter",
                "cumulative_filter",
            ]:
                del st.session_state[key]
        st.session_state["month_filter"] = ["Hepsi"]
        st.session_state["report_base_filter"] = ["Hepsi"]
        st.session_state["cumulative_filter"] = ["Hepsi"]
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        display_friendly_error(
            f"Filtre temizleme sırasında hata oluştu: {str(e)}",
            "Lütfen sayfayı manuel olarak yenileyin."
        )


def prepare_final_dataframe(df, filtered_df, selected_months, selected_report_bases, selected_cumulative):
    """
    Son veri çerçevesini hazırlar.
    """
    # Veri çerçevesini optimize et
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # Sütun seçimi için mapping oluştur
    column_mapping = {
        'general': GENERAL_COLUMNS.copy(),
        'monthly': [
            f"{month} {base_col}"
            for month in selected_months
            for base_col in selected_report_bases
            if f"{month} {base_col}" in df.columns
        ],
        'cumulative': [
            cum_col for cum_col in selected_cumulative
            if cum_col in df.columns
        ]
    }
    
    # Tüm sütunları birleştir
    selected_columns = (
        column_mapping['general'] + 
        column_mapping['monthly'] + 
        column_mapping['cumulative']
    )
            
    return df[selected_columns]


@handle_critical_error
def main():
    """
    Ana uygulama fonksiyonu.
    """
    # Sayfa yapılandırması
    setup_page_config()
    
    pd.set_option("styler.render.max_elements", 500000)
    st.title("🏦 Finansal Performans Analiz Paneli")

    # Veri yükleme
    df = load_and_validate_data()
    if df is None:
        return
        
    # Filtreler
    filtered_df, selected_months, selected_report_bases, selected_cumulative = setup_sidebar_filters(df)
    
    # Final veri çerçevesini hazırlama
    try:
        final_df = prepare_final_dataframe(
            df, filtered_df, selected_months, selected_report_bases, selected_cumulative
        )
        total_budget, total_actual, variance, variance_pct = calculate_metrics(final_df)
    except Exception as e:
        display_friendly_error(
            f"Veri işleme sırasında hata oluştu: {str(e)}",
            "Lütfen filtre seçimlerinizi kontrol edin ve tekrar deneyin."
        )
        return

    st.markdown("---")

    # KPI paneli gösterimi
    show_kpi_panel(final_df)

    # Analiz sekmeleri tanımlamaları
    tab_config = {
        'analiz': [
            "📊 Veri",
            "📈 Trend",
            "📊 Kategori Analizi",
            "📈 Karşılaştırmalı Analiz",
            "📎 Pivot Tablo",
            "💡 Otomatik Özet",
        ],
        'raporlama': ["⬇ İndir (ZIP)", "📄 PDF Raporu"]
    }

    # Sekme gruplarını oluştur
    tabs_analiz = st.tabs(tab_config['analiz'])
    tabs_raporlama = st.tabs(tab_config['raporlama'])

    # Analiz tabları
    with tabs_analiz[0]:
        # 🚧 MASRAF ÇEŞİDİ GRUBU 1 ANALİZİ
        with st.container():
            st.markdown("## 🧾 Masraf Çeşidi Grubu 1 Analizi")
            st.markdown("---")

            with st.expander("📅 Ay Bazlı Tablo Seçimi", expanded=True):
                table_month_options = ["Hepsi"] + MONTHS
                selected_table_months = st.multiselect(
                    "Tabloya Dahil Edilecek Ay(lar)",
                    table_month_options,
                    default=["Hepsi"],
                    key="table_month_filter"
                )
                if "Hepsi" in selected_table_months:
                    selected_table_months = MONTHS

                show_cumulative = st.checkbox("Kümüle Verileri Göster", value=False)

            # İzin verilen metrikleri filtrele
            allowed_metrics = [
                metric for metric in FIXED_METRICS
                if "Hepsi" in selected_report_bases or
                   any(metric in base for base in selected_report_bases)
            ]

            # Sütun oluşturma
            table_columns = {
                'monthly': [
                    f"{month} {metric}"
                    for month in selected_table_months
                    for metric in allowed_metrics
                    if f"{month} {metric}" in df.columns
                ],
                'cumulative': [
                    f"Kümüle {metric}"
                    for metric in allowed_metrics
                    if show_cumulative and f"Kümüle {metric}" in df.columns
                ]
            }

            table_target_columns = table_columns['monthly'] + table_columns['cumulative']
            table_filtered_df = filtered_df[GENERAL_COLUMNS + table_target_columns]

            show_grouped_summary(
                table_filtered_df,
                group_column="Masraf Çeşidi Grubu 1",
                target_columns=table_target_columns,
                filename="masraf_grubu_ozet.xlsx",
                title="#### 📊 Grup Bazında Detaylar",
                style_func=style_negatives_red,
                sticky_column="Masraf Çeşidi Grubu 1",
                page_size=1000
            )

            show_column_totals(
                table_filtered_df,
                filename="masraf_grubu_toplam_sayisal.xlsx",
                title="#### ➕ Sayısal Sütun Toplamları"
            )

        # ➕ Masraf Çeşidi Toplamları
        with st.container():
            st.markdown("### 🧮 Masraf Grubu 1 - Year to Date")
            masraf_totals = calculate_group_totals(
                final_df,
                group_column="Masraf Çeşidi Grubu 1",
                selected_months=selected_months,
                metrics=FIXED_METRICS[:-1]
            )

            show_filtered_data(
                masraf_totals,
                filename="masraf_grubu_toplamlar.xlsx",
                title="#### 📌 Toplamlar",
                style_func=style_negatives_red,
                page_size=1000
            )

            show_column_totals(
                masraf_totals,
                filename="masraf_grubu_toplamlar_sayisal.xlsx",
                title="#### ➕ Genel Toplam"
            )

        st.markdown("---")

        # 👥 İLGİLİ 1 ANALİZİ
        with st.container():
            st.markdown("## 👥 İlgili 1 Analizi")
            st.markdown("---")

            with st.expander("📅 Ay Seçimi", expanded=True):
                ilgili1_month_options = ["Hepsi"] + MONTHS
                selected_ilgili1_months = st.multiselect(
                    "İlgili 1 İçin Ay Seçimi",
                    ilgili1_month_options,
                    default=["Hepsi"],
                    key="ilgili1_month_filter"
                )
                if "Hepsi" in selected_ilgili1_months:
                    selected_ilgili1_months = MONTHS

                show_cumulative_ilgili1 = st.checkbox("Kümüle Verileri Göster", value=False, key="cumulative_ilgili1")

            # İlgili1 sütunları
            ilgili1_columns = {
                'monthly': [
                    f"{month} {metric}"
                    for month in selected_ilgili1_months
                    for metric in FIXED_METRICS
                    if f"{month} {metric}" in df.columns
                ],
                'cumulative': [
                    f"Kümüle {metric}"
                    for metric in FIXED_METRICS
                    if show_cumulative_ilgili1 and f"Kümüle {metric}" in df.columns
                ]
            }

            ilgili1_target_columns = ilgili1_columns['monthly'] + ilgili1_columns['cumulative']
            ilgili1_filtered_df = df[GENERAL_COLUMNS + ilgili1_target_columns]

            show_grouped_summary(
                ilgili1_filtered_df,
                group_column="İlgili 1",
                target_columns=ilgili1_target_columns,
                filename="ilgili1_ozet.xlsx",
                title="#### 📊 İlgili 1 Bazında Detaylar",
                style_func=style_negatives_red,
                sticky_column="İlgili 1"
            )

            show_column_totals(
                ilgili1_filtered_df,
                filename="ilgili1_toplam_sayisal.xlsx",
                title="#### ➕ Sayısal Sütun Toplamları"
            )

        with st.container():
            ilgili1_totals = calculate_group_totals(
                final_df,
                group_column="İlgili 1",
                selected_months=selected_months,
                metrics=FIXED_METRICS[:-1]
            )

            show_filtered_data(
                ilgili1_totals,
                filename="ilgili1_toplamlar.xlsx",
                title="#### 📌 Toplamlar",
                style_func=style_negatives_red
            )

            show_column_totals(
                ilgili1_totals,
                filename="ilgili1_toplamlar_sayisal.xlsx",
                title="#### ➕ Genel Toplam"
            )

        st.markdown("---")

        # 📋 HAM VERİ
        with st.container():
            st.markdown("## 📋 Ham Veri Görünümü")
            st.markdown("---")

            with st.expander("🧩 Görüntülenecek Ana Sütunlar", expanded=True):
                column_options = ["Hepsi"] + GENERAL_COLUMNS[:10]
                selected_table_columns = st.multiselect(
                    "Tabloya Dahil Edilecek Sütun(lar)",
                    options=column_options,
                    default=["Hepsi"],
                    key="visible_columns",
                )

            visible_general_columns = (
                GENERAL_COLUMNS[:10] if "Hepsi" in selected_table_columns else selected_table_columns
            )
            remaining_columns = [col for col in final_df.columns if col not in GENERAL_COLUMNS[:10]]

            visible_df = final_df[visible_general_columns + remaining_columns]

            excel_buffer = show_filtered_data(
                visible_df,
                style_func=style_warning_rows,
                filename="ham_veri.xlsx",
                sticky_column=0,
                page_size=1000
            )

            show_column_totals(
                visible_df,
                filename="ham_veri_toplam_sayisal.xlsx",
                title="#### ➕ Ham Verideki Sayısal Sütun Toplamları"
            )


    with tabs_analiz[1]:
        col1, col2, col3 = st.columns(3)
        with col1:
            budget_color = st.color_picker("Bütçe Rengi", "#636EFA")
        with col2:
            actual_color = st.color_picker("Fiili Rengi", "#EF553B")
        with col3:
            difference_color = st.color_picker("Fark Rengi", "#00CC96")

        trend_img_buffer = show_trend_analysis(
            final_df,
            selected_months=selected_months,
            budget_color=budget_color,
            actual_color=actual_color,
            difference_color=difference_color,
        )

    with tabs_analiz[2]:
        combined_img_buffer = show_category_charts(final_df)

    with tabs_analiz[3]:
        group_by_option = st.selectbox("Gruplama Kriteri", GENERAL_COLUMNS)
        comparative_excel_buffer, comperative_img_buffer = show_comparative_analysis(
            final_df, group_by_col=group_by_option
        )

    with tabs_analiz[4]:
        pivot_excel_buffer, pivot_buffer = show_pivot_table(final_df)

    with tabs_analiz[5]:
        insights = generate_insights(final_df)
        if insights:
            for i, insight in enumerate(insights, 1):
                st.markdown(f"{i}. {insight}")
        else:
            st.info("İçgörü üretilemedi.")

    # Raporlama tabları
    with tabs_raporlama[0]:
        if st.button("📦 ZIP Raporu Oluştur"):
            with st.spinner("Rapor oluşturuluyor..."):
                # Excel dosyaları için mapping
                excel_files = {
                    'masraf_grubu': {
                        'sheets': {
                            'Özet': 'masraf_grubu_ozet',
                            'Sayısal Toplam': 'masraf_grubu_toplam_sayisal',
                            'Toplamlar': 'masraf_grubu_toplamlar',
                            'Genel Toplam': 'masraf_grubu_toplamlar_sayisal'
                        },
                        'filename': 'masraf_cesidi_grubu_1_analizi.xlsx'
                    },
                    'ilgili1': {
                        'sheets': {
                            'Özet': 'ilgili1_ozet',
                            'Sayısal Toplam': 'ilgili1_toplam_sayisal',
                            'Toplamlar': 'ilgili1_toplamlar',
                            'Genel Toplam': 'ilgili1_toplamlar_sayisal'
                        },
                        'filename': 'ilgili_1_analizi.xlsx'
                    },
                    'ham_veri': {
                        'sheets': {
                            'Ham Veri': 'ham_veri',
                            'Sayısal Toplam': 'ham_veri_toplam_sayisal'
                        },
                        'filename': 'ham_veri.xlsx'
                    }
                }

                # Görsel dosyaları için mapping
                image_files = {
                    'trend.png': trend_img_buffer,
                    'kategori_analizi.png': combined_img_buffer,
                    'karsilastirma_analizi.png': comperative_img_buffer,
                    'pivot_analizi.png': pivot_buffer
                }

                # ZIP oluştur
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    # Excel dosyalarını ekle
                    for file_config in excel_files.values():
                        excel_buffer = BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                            for sheet_name, state_key in file_config['sheets'].items():
                                if state_key in st.session_state:
                                    st.session_state[state_key].to_excel(writer, sheet_name=sheet_name, index=False)
                        zip_file.writestr(file_config['filename'], excel_buffer.getvalue())

                    # Görsel dosyalarını ekle
                    for filename, buffer in image_files.items():
                        if buffer:
                            zip_file.writestr(filename, buffer.getvalue())

                # ZIP'i session state'e kaydet
                st.session_state["zip_buffer"] = zip_buffer.getvalue()
                st.success("Rapor oluşturuldu!")

        # ZIP indirme butonu
        if "zip_buffer" in st.session_state:
            st.download_button(
                "⬇ İndir (ZIP)",
                data=st.session_state["zip_buffer"],
                file_name="rapor.zip",
                mime="application/zip"
            )

    with tabs_raporlama[1]:
        if st.button("📄 PDF Raporu Oluştur"):
            with st.spinner("Rapor oluşturuluyor..."):
                pdf = generate_pdf_report(
                    total_budget,
                    total_actual,
                    variance,
                    variance_pct,
                    trend_img_buffer,
                    comperative_img_buffer,
                )
                st.download_button(
                    "⬇ İndir (PDF)", data=pdf, file_name="rapor.pdf", mime="application/pdf"
                )


if __name__ == "__main__":
    main()
