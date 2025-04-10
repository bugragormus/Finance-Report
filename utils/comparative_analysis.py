import streamlit as st
import plotly.express as px
from io import BytesIO
import plotly.io as pio
from PIL import Image

# Grafik export ayarları
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 1000
pio.kaleido.scope.default_height = 600
pio.kaleido.scope.default_colorway = px.colors.qualitative.Plotly
pio.kaleido.scope.default_paper_bgcolor = "white"
pio.kaleido.scope.default_plot_bgcolor = "white"


def show_comparative_analysis(df, group_by_col="İlgili 1"):
    st.subheader(f"📊 {group_by_col} Bazında Harcama Karşılaştırması")

    if group_by_col not in df.columns:
        st.warning(f"{group_by_col} sütunu bulunamadı!")
        return

    group_cols = ["Kümüle Bütçe", "Kümüle Fiili"]
    for col in group_cols:
        if col not in df.columns:
            st.warning(f"{col} sütunu eksik.")
            return

    grouped = df.groupby(group_by_col)[group_cols].sum().reset_index()
    grouped["Kullanım (%)"] = (grouped["Kümüle Fiili"] / grouped["Kümüle Bütçe"]) * 100

    # Grafik oluşturma
    fig = px.bar(
        grouped.sort_values("Kümüle Fiili", ascending=False),
        x=group_by_col,
        y=["Kümüle Bütçe", "Kümüle Fiili"],
        barmode="group",
        title=f"{group_by_col} Bazında Kümüle Karşılaştırma",
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

    # Tablo gösterimi
    st.dataframe(
        grouped.sort_values("Kümüle Fiili", ascending=False), use_container_width=True
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    # Save the bar chart to an image in memory using plotly.io
    bar_img_buffer = BytesIO()
    pio.write_image(fig, bar_img_buffer, format="png", width=800, height=600)
    bar_img_buffer.seek(0)  # Go to the beginning of the buffer
    bar_img = Image.open(bar_img_buffer)

    # Add a download button for the combined image
    with col1:
        st.download_button(
            label="📥 İndir (PNG)",
            data=bar_img_buffer,
            file_name="combined_charts.png",
            mime="image/png",
            key="download_image",  # Added unique key here
        )

    excel_buffer = BytesIO()
    grouped.sort_values("Kümüle Fiili", ascending=False).to_excel(
        excel_buffer, index=False
    )
    excel_buffer.seek(0)

    # Excel indirme butonu
    with col2:
        st.download_button(
            label="⬇️ Excel Dosyasını İndir",
            data=excel_buffer,
            file_name=f"{group_by_col}_bazinda_veriler.xlsx",
            mime="application/vnd.ms-excel",
            key="download_excel",  # Added unique key here
        )
