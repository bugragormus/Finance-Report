import streamlit as st
from io import BytesIO
import zipfile
from PIL import Image
import pandas as pd

from utils.loader import load_data
from utils.filters import apply_filters
from utils.metrics import calculate_metrics
from utils.report import generate_pdf_report
from config.constants import (
    MONTHS,
    GENERAL_COLUMNS,
    REPORT_BASE_COLUMNS,
    CUMULATIVE_COLUMNS,
)
from utils.kpi import show_kpi_panel
from utils.category_analysis import show_category_charts
from utils.comparative_analysis import show_comparative_analysis
from utils.trend_analysis import show_trend_analysis
from utils.pivot_table import show_pivot_table
from utils.insight_generator import generate_insights
from utils.data_preview import show_filtered_data, show_grouped_summary, calculate_group_totals
from utils.warning_system import style_negatives_red, style_warning_rows


def main():

    im = Image.open("assets/favicon.png")
    st.set_page_config(
        layout="wide", page_title="Finansal Performans Analiz Paneli", page_icon=im, initial_sidebar_state="expanded"
    )
    pd.set_option("styler.render.max_elements", 500000)
    st.title("🏦 Finansal Performans Analiz Paneli")

    uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=["xlsx", "xls"])
    if uploaded_file:
        df = load_data(uploaded_file)
    else:
        st.info("Lütfen ZFMR0003 raporunun Excel dosyasını yükleyin")
        return

    with st.sidebar:
        st.header("🔧 Filtre & Grafik Ayarları")
        filtered_df = apply_filters(df, GENERAL_COLUMNS, "filter")

        all_months_with_all = ["Hepsi"] + MONTHS
        selected_months = st.multiselect(
            "📅 Aylar", all_months_with_all, default=["Hepsi"], key="month_filter"
        )
        if "Hepsi" in selected_months:
            selected_months = MONTHS

        report_base_columns_with_all = ["Hepsi"] + REPORT_BASE_COLUMNS
        selected_report_bases = st.multiselect(
            "📉 Veri Türleri",
            report_base_columns_with_all,
            default=["Hepsi"],
            key="report_base_filter",
        )
        if "Hepsi" in selected_report_bases:
            selected_report_bases = REPORT_BASE_COLUMNS

        cumulative_columns = ["Kümüle " + col for col in CUMULATIVE_COLUMNS]
        selected_cumulative = st.multiselect(
            "📈 Kümülatif Veriler",
            ["Hepsi"] + cumulative_columns,
            default=["Hepsi"],
            key="cumulative_filter",
        )
        if "Hepsi" in selected_cumulative:
            selected_cumulative = cumulative_columns

        if st.button("🗑️ Tüm Filtreleri Temizle"):
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

    selected_columns = GENERAL_COLUMNS.copy()
    for month in selected_months:
        for base_col in selected_report_bases:
            col_name = f"{month} {base_col}"
            if col_name in df.columns:
                selected_columns.append(col_name)
    for cum_col in selected_cumulative:
        if cum_col in df.columns:
            selected_columns.append(cum_col)

    final_df = filtered_df[selected_columns]
    total_budget, total_actual, variance, variance_pct = calculate_metrics(final_df)

    st.markdown("---")

    show_kpi_panel(final_df)

    # Define all the tabs, including the modules
    tab_titles_analiz = [
        "📊 Veri",
        "📈 Trend",
        "📊 Kategori Analizi",
        "📈 Karşılaştırmalı Analiz",
        "📎 Pivot Tablo",
        "💡 Otomatik Özet",
    ]
    tab_titles_raporlama = ["⬇ İndir (ZIP)", "📄 PDF Raporu"]

    # Create two groups of tabs
    tabs_analiz = st.tabs(tab_titles_analiz)
    tabs_raporlama = st.tabs(tab_titles_raporlama)

    # Analiz tabları
    with tabs_analiz[0]:
        # HEDEF SÜTUNLARIN OLUŞTURULMASI
        target_columns = []
        for month in selected_months:
            target_columns.extend([
                f"{month} Bütçe",
                f"{month} Fiili",
                f"{month} BE",
                f"{month} Bütçe-Fiili Fark Bakiye",
                f"{month} BE-Fiili Fark Bakiye",
            ])

        # KÜMÜLATİF SÜTUN FİLTRESİ
        allowed_cumulative = [
            "Kümüle Bütçe",
            "Kümüle Fiili",
            "Kümüle BE Bakiye",
            "Kümüle Bütçe-Fiili Fark Bakiye",
            "Kümüle BE-Fiili Fark Bakiye"
        ]

        cumulative_to_include = [
            col for col in selected_cumulative
            if col in allowed_cumulative and col in df.columns
        ]
        target_columns += cumulative_to_include

        # GRUP BAZINDA ÖZET VE TOPLAMLAR
        st.markdown("### 🧾 Masraf Çeşidi Grubu 1 Analizi")

        # 1. Orijinal Grup Özeti
        show_grouped_summary(
            final_df,
            group_column="Masraf Çeşidi Grubu 1",
            target_columns=target_columns,
            filename="masraf_grubu_ozet.xlsx",
            title="**Grup Bazında Detaylar**",
            style_func=style_negatives_red,
        )

        # 2. Aynı Bölümde Toplamlar
        masraf_totals = calculate_group_totals(
            final_df,
            group_column="Masraf Çeşidi Grubu 1",
            selected_months=selected_months,
            metrics=["Bütçe", "Fiili", "BE", "Bütçe-Fiili Fark Bakiye", "BE-Fiili Fark Bakiye"]
        )
        show_filtered_data(
            masraf_totals,
            filename="masraf_grubu_toplamlar.xlsx",
            title="**Seçilen Ayların Toplamları**",
            style_func=style_negatives_red
        )

        st.markdown("---")

        # İlgili 1 için AYNI MANTIK TEKRARLANIR
        st.markdown("### 👥 İlgili 1 Analizi")
        show_grouped_summary(
            final_df,
            group_column="İlgili 1",
            target_columns=target_columns,
            filename="ilgili1_ozet.xlsx",
            title="**Grup Bazında Detaylar**",
            style_func=style_negatives_red,
        )
        ilgili1_totals = calculate_group_totals(
            final_df,
            group_column="İlgili 1",
            selected_months=selected_months,
            metrics=["Bütçe", "Fiili", "BE", "Bütçe-Fiili Fark Bakiye", "BE-Fiili Fark Bakiye"]
        )
        show_filtered_data(
            ilgili1_totals,
            filename="ilgili1_toplamlar.xlsx",
            title="**Seçilen Ayların Toplamları**",
            style_func=style_negatives_red
        )

        st.markdown("---")

        # HAM VERİ GÖSTERİMİ (Tam Genişlik)
        st.markdown("### 📋 Ham Veri")
        first_10_columns = GENERAL_COLUMNS[:10]
        column_options = ["Hepsi"] + first_10_columns

        selected_table_columns = st.multiselect(
            "🧩 Görüntülenecek Ana Sütunlar",
            options=column_options,
            default=["Hepsi"],
            key="visible_columns",
        )

        visible_general_columns = (
            first_10_columns
            if "Hepsi" in selected_table_columns
            else selected_table_columns
        )

        remaining_columns = [col for col in final_df.columns if col not in first_10_columns]
        visible_df = final_df[visible_general_columns + remaining_columns]

        excel_buffer = show_filtered_data(
            visible_df,
            style_func=style_warning_rows,
            filename="ham_veri.xlsx"
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
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr("veri.xlsx", excel_buffer.getvalue())
            if trend_img_buffer:
                zip_file.writestr("trend.png", trend_img_buffer.getvalue())
            if combined_img_buffer:
                zip_file.writestr(
                    "kategori_analizi.png", combined_img_buffer.getvalue()
                )
            if comperative_img_buffer:
                zip_file.writestr(
                    "karsilastirma_analizi.png", comperative_img_buffer.getvalue()
                )
            if pivot_buffer:
                zip_file.writestr("pivot_analizi.png", pivot_buffer.getvalue())
            if "comparative_excel_buffer" in locals() and comparative_excel_buffer:
                zip_file.writestr(
                    "karsilastirma_analizi.xlsx", comparative_excel_buffer.getvalue()
                )
            if "pivot_excel_buffer" in locals() and pivot_excel_buffer:
                zip_file.writestr("pivot_tablo.xlsx", pivot_excel_buffer.getvalue())
        st.download_button(
            "⬇ İndir (ZIP)", data=zip_buffer.getvalue(), file_name="rapor.zip"
        )

    with tabs_raporlama[1]:
        if st.button("📄 PDF Raporu Oluştur"):
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
