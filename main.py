import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
import plotly.graph_objects as go

from utils.loader import load_data
from utils.filters import apply_filters
from utils.metrics import calculate_metrics
from utils.report import generate_pdf_report
from config.constants import MONTHS, GENERAL_COLUMNS, REPORT_BASE_COLUMNS

def main():
    st.set_page_config(layout="wide", page_title="Finansal Performans Analiz Paneli")
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
        selected_months = st.multiselect("📅 Aylar", all_months_with_all, default=["Hepsi"], key="month_filter")
        if "Hepsi" in selected_months:
            selected_months = MONTHS

        report_base_columns_with_all = ["Hepsi"] + REPORT_BASE_COLUMNS
        selected_report_bases = st.multiselect("📉 Veri Türleri", report_base_columns_with_all, default=["Hepsi"], key="report_base_filter")
        if "Hepsi" in selected_report_bases:
            selected_report_bases = REPORT_BASE_COLUMNS

        cumulative_columns = ["Kümüle " + col for col in REPORT_BASE_COLUMNS]
        selected_cumulative = st.multiselect("📈 Kümülatif Veriler", ["Hepsi"] + cumulative_columns, default=["Hepsi"], key="cumulative_filter")
        if "Hepsi" in selected_cumulative:
            selected_cumulative = cumulative_columns

        budget_color = st.color_picker("Bütçe Rengi", "#636EFA")
        actual_color = st.color_picker("Fiili Rengi", "#EF553B")
        difference_color = st.color_picker("Fark Rengi", "#00CC96")
        show_grid = st.checkbox("Grafik Grid Göster", value=True)

        if st.button("🗑️ Tüm Filtreleri Temizle"):
            for key in list(st.session_state.keys()):
                if key.startswith("filter_") or key in ["month_filter", "report_base_filter", "cumulative_filter"]:
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

    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Bütçe", f"{total_budget:,.0f} ₺")
    col2.metric("Toplam Fiili", f"{total_actual:,.0f} ₺")
    col3.metric("Bütçe Fazlası", f"{variance:,.0f} ₺ ({variance_pct:.2f}%)")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Veri", "📈 Trend", "🗂️ ZIP", "📄 PDF"])

    with tab1:
        st.dataframe(final_df, use_container_width=True)
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            final_df.to_excel(writer, index=False)
        st.download_button("📥 Excel İndir", data=excel_buffer.getvalue(), file_name="filtrelenmis_rapor.xlsx")

    with tab2:
        trend_data = []
        for month in selected_months:
            b_col, a_col = f"{month} Bütçe", f"{month} Fiili"
            if b_col in final_df.columns and a_col in final_df.columns:
                trend_data.append({
                    "Ay": month,
                    "Bütçe": final_df[b_col].sum(),
                    "Fiili": final_df[a_col].sum(),
                    "Fark": final_df[a_col].sum() - final_df[b_col].sum(),
                })
        if trend_data:
            df_trend = pd.DataFrame(trend_data)
            fig = go.Figure()
            fig.add_bar(x=df_trend["Ay"], y=df_trend["Bütçe"], name="Bütçe", marker_color=budget_color)
            fig.add_bar(x=df_trend["Ay"], y=df_trend["Fiili"], name="Fiili", marker_color=actual_color)
            fig.add_trace(go.Scatter(x=df_trend["Ay"], y=df_trend["Fark"], name="Fark", line=dict(color=difference_color)))
            fig.update_layout(barmode="group", hovermode="x", yaxis=dict(showgrid=show_grid))
            st.plotly_chart(fig, use_container_width=True)

            img_buffer = BytesIO()
            fig.write_image(img_buffer, format="png")
        else:
            img_buffer = None

    with tab3:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr("veri.xlsx", excel_buffer.getvalue())
            if img_buffer:
                zip_file.writestr("trend.png", img_buffer.getvalue())
        st.download_button("⬇️ ZIP İndir", data=zip_buffer.getvalue(), file_name="rapor.zip")

    with tab4:
        if st.button("📄 PDF Raporu Oluştur"):
            pdf = generate_pdf_report(total_budget, total_actual, variance, variance_pct, img_buffer)
            st.download_button("PDF İndir", data=pdf, file_name="rapor.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()
