import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
from io import BytesIO
from PIL import Image

# Configure Plotly to use a static image export engine
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 800
pio.kaleido.scope.default_height = 600
pio.kaleido.scope.default_colorway = px.colors.qualitative.Plotly
pio.kaleido.scope.default_paper_bgcolor = "white"
pio.kaleido.scope.default_plot_bgcolor = "white"


def show_category_charts(df):
    st.subheader("📊 Kategori Bazlı Harcama Dağılımı")

    # Kategorik grup alanları (objeler ve düşük unique sayılılar)
    group_candidates = [
        col
        for col in df.columns
        if df[col].dtype == "object" and df[col].nunique() <= 50
    ]
    selected_group = st.selectbox(
        "🧩 Gruplama Alanı Seçin",
        group_candidates,
        index=group_candidates.index("Masraf Çeşidi Grubu 1")
        if "Masraf Çeşidi Grubu 1" in group_candidates
        else 0,
    )

    # Ay seçimi
    month_cols = [
        col
        for col in df.columns
        if any(
            ay in col
            for ay in [
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
        )
        and "Fiili" in col
    ]

    if month_cols:
        selected_month = st.selectbox(
            "📅 Ay Seçimi (İsteğe Bağlı)", ["Kümüle Fiili"] + month_cols
        )
    else:
        selected_month = "Kümüle Fiili"

    # İlk N gösterimi
    top_n = st.slider(
        "🔢 Gösterilecek Grup Sayısı", min_value=1, max_value=50, value=10, step=1
    )

    if selected_group not in df.columns or selected_month not in df.columns:
        st.warning("Gerekli sütunlar eksik!")
        return

    grouped = df.groupby(selected_group)[selected_month].sum().reset_index()
    grouped = grouped.sort_values(by=selected_month, ascending=False).head(top_n)

    # Create a pie chart
    fig_pie = px.pie(
        grouped,
        names=selected_group,
        values=selected_month,
        title=f"{selected_group} Bazında Harcamalar ({selected_month})",
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Pie chart styling
    fig_pie = px.pie(
        grouped,
        names=selected_group,
        values=selected_month,
        title=f"{selected_group} Bazında Harcamalar ({selected_month})",
        color_discrete_sequence=px.colors.qualitative.Plotly,  # Renk paleti eklendi
    )

    fig_pie.update_layout(
        template="plotly_white",
        font=dict(color="black", size=12),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(font=dict(color="black"), bgcolor="rgba(255,255,255,0.8)"),
        margin=dict(t=50, b=20, l=20, r=20),
        height=600,  # Sabit yükseklik
    )

    # Create a bar chart
    fig_bar = px.bar(
        grouped,
        x=selected_group,
        y=selected_month,
        title=f"{selected_group} Bazında {selected_month}",
    )
    fig_bar.update_layout(xaxis_tickangle=-45)

    # Bar chart styling
    fig_bar = px.bar(
        grouped,
        x=selected_group,
        y=selected_month,
        title=f"{selected_group} Bazında {selected_month}",
        color=selected_group,
        color_discrete_sequence=px.colors.qualitative.Plotly,  # Renk paleti eklendi
    )

    fig_bar.update_layout(
        template="plotly_white",
        font=dict(color="black", size=12),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(
            tickangle=-45,
            showgrid=False,
            linecolor="black",
            title_font=dict(color="black"),
            tickfont=dict(color="black"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="lightgray",
            linecolor="black",
            title_font=dict(color="black"),
            tickfont=dict(color="black"),
        ),
        margin=dict(l=50, r=50, t=50, b=150),
        height=600,  # Sabit yükseklik
        width=800,  # Sabit genişlik
    )

    fig_bar.update_traces(marker_line_color="black", marker_line_width=0.5, opacity=0.9)

    # Adjust the layout to avoid overflow
    fig_bar.update_layout(
        margin=dict(l=50, r=50, t=50, b=100),  # Adjust margins
        autosize=True,  # Allow auto-sizing for the plot
        xaxis_title=selected_group,  # Ensure proper title for X-axis
        yaxis_title=selected_month,  # Ensure proper title for Y-axis
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # Save the pie chart to an image in memory using plotly.io
    pie_img_buffer = BytesIO()
    pio.write_image(fig_pie, pie_img_buffer, format="png", width=800, height=600)
    pie_img_buffer.seek(0)  # Go to the beginning of the buffer
    pie_img = Image.open(pie_img_buffer)

    # Save the bar chart to an image in memory using plotly.io
    bar_img_buffer = BytesIO()
    pio.write_image(fig_bar, bar_img_buffer, format="png", width=800, height=600)
    bar_img_buffer.seek(0)  # Go to the beginning of the buffer
    bar_img = Image.open(bar_img_buffer)

    # Combine the two images (pie on top of the bar)
    combined_width = max(pie_img.width, bar_img.width)
    combined_height = pie_img.height + bar_img.height

    combined_img = Image.new("RGB", (combined_width, combined_height))

    # Paste the pie and bar charts into the combined image
    combined_img.paste(pie_img, (0, 0))
    combined_img.paste(bar_img, (0, pie_img.height))

    # Save the combined image to a buffer
    combined_img_buffer = BytesIO()
    combined_img.save(combined_img_buffer, format="PNG")
    combined_img_buffer.seek(0)

    # Add a download button for the combined image
    st.download_button(
        label="⬇ İndir (PNG)",
        data=combined_img_buffer,
        file_name="combined_charts.png",
        mime="image/png",
    )

    return combined_img_buffer
