import streamlit as st
import plotly.express as px
from io import BytesIO
import plotly.io as pio
from PIL import Image

from utils.warning_system import style_overused_rows

# Grafik export ayarları
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 1000
pio.kaleido.scope.default_height = 600
pio.kaleido.scope.default_colorway = px.colors.qualitative.Plotly
pio.kaleido.scope.default_paper_bgcolor = "white"
pio.kaleido.scope.default_plot_bgcolor = "white"

from config.constants import MONTHS


def show_comparative_analysis(df, group_by_col="İlgili 1"):
    st.subheader(f"📊 {group_by_col} Bazında Harcama Karşılaştırması")

    if group_by_col not in df.columns:
        st.warning(f"{group_by_col} sütunu bulunamadı!")
        return

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
            st.warning(f"{selected_month} için Bütçe veya Fiili verisi eksik.")
            return

        group_cols = [month_budget_col, month_actual_col]

    for col in group_cols:
        if col not in df.columns:
            st.warning(f"{col} sütunu eksik.")
            return

    grouped = df.groupby(group_by_col)[group_cols].sum().reset_index()

    # Kullanım yüzdesi
    grouped["Kullanım (%)"] = (grouped[group_cols[1]] / grouped[group_cols[0]]) * 100

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

    # Save the bar chart to an image in memory using plotly.io
    bar_img_buffer = BytesIO()
    pio.write_image(fig, bar_img_buffer, format="png", width=800, height=600)
    bar_img_buffer.seek(0)  # Go to the beginning of the buffer
    bar_img = Image.open(bar_img_buffer)

    # Add a download button for the combined image
    st.download_button(
        label="⬇ İndir (PNG)",
        data=bar_img_buffer,
        file_name="comparative_analysis.png",
        mime="image/png",
        key="download_image",  # Added unique key here
    )

    st.markdown("---")

    # Tablo gösterimi
    styled_grouped = style_overused_rows(
        grouped.sort_values(group_cols[1], ascending=False)
    )
    st.dataframe(styled_grouped, use_container_width=True)

    excel_buffer = BytesIO()
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
        key="download_excel",  # Added unique key here
    )

    return excel_buffer  # ZIP için main.py'ye döndür
