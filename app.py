import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
import zipfile
from datetime import datetime
from fpdf import FPDF

# Veri yükleme fonksiyonu
@st.cache_data(show_spinner="Veri yükleniyor...")
def load_data(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        df.columns = [str(col).strip() for col in df.columns]

        # Zorunlu sütun kontrolü
        mandatory_columns = ["Masraf Yeri Adı", "Kümüle Bütçe", "Kümüle Fiili"]
        missing_columns = [col for col in mandatory_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Eksik sütunlar: {', '.join(missing_columns)}. Lütfen geçerli bir ZFMR0003 raporu yükleyin.")
            return None

        return df
    except Exception as e:
        st.error(f"Veri yükleme hatası: {str(e)}")
        # Hata detayını logla (opsiyonel)
        with open("error_log.txt", "a") as f:
            f.write(f"{datetime.now()}: {str(e)}\n")
        return None

# Metrik hesaplama fonksiyonu
def calculate_metrics(_df):
    total_budget = _df["Kümüle Bütçe"].sum() if "Kümüle Bütçe" in _df.columns else 0
    total_actual = _df["Kümüle Fiili"].sum() if "Kümüle Fiili" in _df.columns else 0
    variance = total_budget - total_actual
    variance_pct = (variance / total_budget) * 100 if total_budget != 0 else 0
    return total_budget, total_actual, variance, variance_pct


# Dinamik filtreleme fonksiyonu
def apply_filters(df, columns, key_prefix):
    selected_filters = {}
    for col in columns:
        if col not in df.columns:
            continue
        temp_df = df.copy()
        for other_col in columns:
            if other_col == col:
                continue
            if f"{key_prefix}_{other_col}" in st.session_state:
                selected = st.session_state[f"{key_prefix}_{other_col}"]
                if selected:
                    temp_df = temp_df[temp_df[other_col].isin(selected)]
        options = sorted(temp_df[col].dropna().unique().tolist(), key=lambda x: str(x))

        selected = st.multiselect(
            f"🔍 {col}",
            options,
            key=f"{key_prefix}_{col}",
            default=st.session_state.get(f"{key_prefix}_{col}", []),
            help=f"{col} için filtre seçin",
        )
        selected_filters[col] = selected


# Filtre uygulama
    filtered_df = df.copy()
    for col, selected in selected_filters.items():
        if selected:
            filtered_df = filtered_df[filtered_df[col].isin(selected)]
    return filtered_df


# PDF rapor oluşturma fonksiyonu
def generate_pdf_report(
    total_budget, total_actual, variance, variance_pct, img_buffer=None
):
    pdf = FPDF()
    pdf.add_page()

    # ₺ sembolü için font ayarları
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)

    # Başlık için bold font kullanımı
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "Finansal Performans Raporu", ln=True, align="C")
    pdf.ln(10)

    # Normal font ile metin ekleme
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(0, 10, f"Toplam Bütçe: {total_budget:,.0f} ₺", ln=True)
    pdf.cell(0, 10, f"Toplam Fiili: {total_actual:,.0f} ₺", ln=True)
    pdf.cell(0, 10, f"Fark: {variance:,.0f} ₺ ({variance_pct:.1f}%)", ln=True)
    pdf.ln(10)

    # Eğer trend grafiği varsa, geçici dosyaya kaydedip PDF'e ekleyin
    if img_buffer:
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
            tmp_img.write(img_buffer.getvalue())
            tmp_img.flush()
            pdf.image(tmp_img.name, w=pdf.w - 40)

    pdf_data = pdf.output(dest="S")
    return bytes(pdf_data)


def main():

    st.set_page_config(layout="wide", page_title="Finansal Performans Analiz Paneli")
    st.title("🏦 Finansal Performans Analiz Paneli")

    st.markdown("""
        <style>
            .stAlert { background-color: #ffebee; border-left: 4px solid #ff5252; }
            .stMultiSearch [data-baseweb="input"] { border-radius: 12px !important; }
        </style>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=["xlsx", "xls"])
    if uploaded_file:
        df = load_data(uploaded_file)
    else:
        st.info("Lütfen ZFMR0003 raporunun Excel dosyasını yükleyin")
        return

    # Yan panelde ek görselleştirme ayarları
    with st.sidebar:
        st.header("🔧 Filtre & Grafik Ayarları")
        st.markdown("<hr style='border-top: 1px solid #ccc; margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True)
        # Mevcut filtreler

        general_columns = [
            "İlgili 1",
            "İlgili 2",
            "İlgili 3",
            "Masraf Yeri",
            "Masraf Yeri Adı",
            "Masraf Çeşidi",
            "Masraf Çeşidi Adı",
            "Masraf Çeşidi Grubu 1",
            "Masraf Çeşidi Grubu 2",
            "Masraf Çeşidi Grubu 3",
        ]
        filtered_df = apply_filters(df, general_columns, "filter")

        st.markdown("<hr style='border-top: 1px solid #ccc; margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True)
        st.header("📊 Gösterilecek Sütunlar")
        st.markdown("<hr style='border-top: 1px solid #ccc; margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True)

        # Ay seçimi
        all_months = [
            "Ocak",
            "Şubat",
            "Mart",
            "Nisan",
            "Mayıs",
            "Haziran",
            "Temmuz",
            "Ağustos",
            "Eylül",
            "Ekim",
            "Kasım",
            "Aralık",
        ]
        all_months_with_all = ["Hepsi"] + all_months  # Yeni seçenek ekle
        selected_months = st.multiselect(
            "📅 Görüntülenecek Aylar:",
            all_months_with_all,
            default=st.session_state.get("month_filter", ["Hepsi"]),  # Güncellendi
            key="month_filter",
        )

        if "Hepsi" in selected_months:
            selected_months = all_months
        else:
            selected_months = [m for m in selected_months if m != "Hepsi"]

        # Veri türü seçimi
        report_base_columns = [
            "Bütçe",
            "Bütçe ÇKG",
            "Bütçe Karşılık Masrafı",
            "Bütçe Bakiye",
            "Fiili",
            "Fiili ÇKG",
            "Fiili Karşılık Masrafı",
            "Fiili Bakiye",
            "Bütçe-Fiili Fark Bakiye",
            "BE",
            "BE-Fiili Fark Bakiye",
        ]
        report_base_columns_with_all = ["Hepsi"] + report_base_columns  # Yeni seçenek ekle
        selected_report_bases = st.multiselect(
            "📉 Görüntülenecek Veri Türleri:",
            report_base_columns_with_all,
            default=st.session_state.get("report_base_filter", ["Hepsi"]),  # Güncellendi
            key="report_base_filter",
        )

        # "Hepsi" seçiliyse tüm veri türlerini seç
        if "Hepsi" in selected_report_bases:
            selected_report_bases = report_base_columns
        else:
            selected_report_bases = [b for b in selected_report_bases if b != "Hepsi"]

        # Kümülatif veri seçimi
        cumulative_columns = ["Kümüle " + col for col in report_base_columns]
        cumulative_columns_with_all = ["Hepsi"] + cumulative_columns  # Yeni seçenek ekle
        selected_cumulative = st.multiselect(
            "📈 Kümülatif Veriler:",
            cumulative_columns_with_all,
            default=st.session_state.get("cumulative_filter", ["Hepsi"]),  # Güncellendi
            key="cumulative_filter",
        )

        # "Hepsi" seçiliyse tüm kümülatifleri seç
        if "Hepsi" in selected_cumulative:
            selected_cumulative = cumulative_columns
        else:
            selected_cumulative = [c for c in selected_cumulative if c != "Hepsi"]

        # Grafik renk ayarları
        st.markdown("<hr style='border-top: 1px solid #ccc; margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True)
        st.markdown("### Grafik Renk Ayarları")
        st.markdown("<hr style='border-top: 1px solid #ccc; margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True)
        budget_color = st.color_picker("Bütçe Rengi", "#636EFA")
        actual_color = st.color_picker("Fiili Rengi", "#EF553B")
        difference_color = st.color_picker("Fark Rengi", "#00CC96")
        show_grid = st.checkbox("Grafik Grid Göster", value=True)

        st.markdown("<hr style='border-top: 1px solid #ccc; margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True)
        if st.button("🗑️ Tüm Filtreleri Temizle"):
            # Tüm filtre anahtarlarını temizle
            for key in list(st.session_state.keys()):
                if key.startswith("filter_") or key in [
                    "month_filter",
                    "report_base_filter",
                    "cumulative_filter",
                ]:
                    del st.session_state[key]

            # Varsayılan "Hepsi" seçimlerini yeniden ata
            st.session_state["month_filter"] = ["Hepsi"]
            st.session_state["report_base_filter"] = ["Hepsi"]
            st.session_state["cumulative_filter"] = ["Hepsi"]

            st.cache_data.clear()
            st.rerun()

    # Sütun tanımlamaları ve veri hazırlığı
    report_base_columns = report_base_columns  # yeniden tanımlandı
    cumulative_columns = ["Kümüle " + col for col in report_base_columns]
    selected_columns = general_columns.copy()

    for month in selected_months:
        for base_col in selected_report_bases:
            month_col_name = f"{month} {base_col}"
            if month_col_name in df.columns:
                selected_columns.append(month_col_name)

    for cum_col in selected_cumulative:
        if cum_col in df.columns:
            selected_columns.append(cum_col)

    final_df = filtered_df[selected_columns]

    # Metrikleri önbellekten alma
    total_budget, total_actual, variance, variance_pct = calculate_metrics(final_df)

    # Metrikler
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Toplam Bütçe", f"{total_budget:,.0f} ₺")
    with col2:
        st.metric("Toplam Fiili", f"{total_actual:,.0f} ₺")
    with col3:
        st.metric(
            "Bütçe Fazlası",
            f"{variance:,.0f} ₺ ({variance_pct:.3f}%)",
            delta_color="off"
        )

    # Sekmeler
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📊 Orijinal Rapor",
            "📈 Trend Analizi",
            "🗂️ Tüm Raporu İndir",
            "📄 PDF Rapor",
        ]
    )

    # Tab1: Excel İndirme ve veri görüntüleme
    with tab1:
        st.subheader("Filtrelenmiş Rapor Verisi")
        st.write(f"Toplam kayıt: {len(final_df)}")
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            final_df.to_excel(writer, index=False, sheet_name="Filtrelenmiş Veri")
            metrics_df = pd.DataFrame(
                {
                    "Metrik": ["Toplam Bütçe", "Toplam Fiili", "Fark"],
                    "Değer (₺)": [total_budget, total_actual, variance],
                    "Yüzde (%)": ["-", "-", f"{variance_pct:.1f}%"],
                }
            )
            metrics_df.to_excel(writer, index=False, sheet_name="Performans Metrikleri")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            "📥 Excel Olarak İndir",
            data=excel_buffer.getvalue(),
            file_name=f"filtrelenmis_rapor_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.dataframe(final_df, use_container_width=True, height=400)

    # Tab2: Trend Analizi ve grafik indirme
    with tab2:
        st.subheader("Aylık Bütçe-Fiili Performans Trendi")
        img_buffer = None
        if selected_months:
            trend_data = []
            for month in selected_months:
                budget_col = f"{month} Bütçe"
                actual_col = f"{month} Fiili"
                if budget_col in final_df.columns and actual_col in final_df.columns:
                    monthly_budget = final_df[budget_col].sum()
                    monthly_actual = final_df[actual_col].sum()
                    trend_data.append(
                        {
                            "Ay": month,
                            "Bütçe": monthly_budget,
                            "Fiili": monthly_actual,
                            "Fark": monthly_actual - monthly_budget,
                        }
                    )
            if trend_data:
                df_trend = pd.DataFrame(trend_data)
                fig = go.Figure()
                fig.add_trace(
                    go.Bar(
                        x=df_trend["Ay"],
                        y=df_trend["Bütçe"],
                        name="Bütçe",
                        marker_color=budget_color,
                        opacity=0.7,
                    )
                )
                fig.add_trace(
                    go.Bar(
                        x=df_trend["Ay"],
                        y=df_trend["Fiili"],
                        name="Fiili",
                        marker_color=actual_color,
                        opacity=0.7,
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=df_trend["Ay"],
                        y=df_trend["Fark"],
                        name="Fark",
                        line=dict(color=difference_color, width=3),
                        yaxis="y2",
                    )
                )
                fig.update_layout(
                    barmode="group",
                    yaxis=dict(title="Tutar (₺)", showgrid=show_grid),
                    yaxis2=dict(
                        title="Fark (₺)", overlaying="y", side="right", showgrid=False
                    ),
                    hovermode="x unified",
                    height=500,
                )
                st.plotly_chart(fig, use_container_width=True)
                img_buffer = BytesIO()
                fig.write_image(img_buffer, format="png", engine="kaleido")
                st.download_button(
                    "📸 Trend Grafiğini İndir (PNG)",
                    data=img_buffer.getvalue(),
                    file_name=f"trend_analizi_{timestamp}.png",
                    mime="image/png",
                )
            else:
                st.warning("Seçilen aylara ait veri bulunamadı")
        else:
            st.info("Lütfen en az bir ay seçin")

        # Tab5: Tüm Raporu ZIP olarak indirme
        with tab3:
            st.subheader("Tüm Rapor Verilerini İndir")
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                zip_file.writestr("filtrelenmis_veri.xlsx", excel_buffer.getvalue())
                if img_buffer:
                    zip_file.writestr(
                        f"trend_analizi_{timestamp}.png", img_buffer.getvalue()
                    )
                #if "roi_json" in locals():
                    #zip_file.writestr(f"roi_analizi_{timestamp}.json", roi_json)
                metrics_str = f"""Toplam Bütçe: {total_budget:,.0f} ₺
    Toplam Fiili: {total_actual:,.0f} ₺
    Fark: {variance:,.0f} ₺ ({variance_pct:.1f}%)"""
                zip_file.writestr("metrikler.txt", metrics_str.encode())
            st.download_button(
                "⬇️ Tüm Raporu ZIP Olarak İndir",
                data=zip_buffer.getvalue(),
                file_name=f"full_report_{timestamp}.zip",
                mime="application/zip",
                help="Tüm veri, grafik ve metrikleri içeren tam rapor",
            )

        # Tab6: PDF Rapor Oluşturma
        with tab4:
            st.subheader("PDF Rapor Oluşturma")
            if st.button("PDF Raporunu Oluştur ve İndir"):
                pdf_data = generate_pdf_report(
                    total_budget, total_actual, variance, variance_pct, img_buffer
                )
                st.download_button(
                    "📄 PDF Olarak İndir",
                    data=pdf_data,
                    file_name=f"rapor_{timestamp}.pdf",
                    mime="application/pdf",
                )

if __name__ == "__main__":
    main()
