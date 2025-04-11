import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime

def show_trend_analysis(df, selected_months, budget_color, actual_color, difference_color):
    st.subheader("📈 Aylık Trend Analizi")

    trend_data = []
    for month in selected_months:
        b_col, a_col = f"{month} Bütçe", f"{month} Fiili"
        if b_col in df.columns and a_col in df.columns:
            trend_data.append({
                "Ay": month,
                "Bütçe": df[b_col].sum(),
                "Fiili": df[a_col].sum(),
                "Fark": df[a_col].sum() - df[b_col].sum(),
            })

    if not trend_data:
        st.warning("Trend analizi için yeterli veri yok.")
        return None  # img_buffer yerine None döner

    df_trend = pd.DataFrame(trend_data)
    fig = go.Figure()
    fig.add_bar(x=df_trend["Ay"], y=df_trend["Bütçe"], name="Bütçe", marker_color=budget_color)
    fig.add_bar(x=df_trend["Ay"], y=df_trend["Fiili"], name="Fiili", marker_color=actual_color)
    fig.add_trace(go.Scatter(x=df_trend["Ay"], y=df_trend["Fark"], name="Fark", line=dict(color=difference_color)))
    st.plotly_chart(fig, use_container_width=True)

    # PNG export
    img_buffer = BytesIO()
    fig.write_image(img_buffer, format="png")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button(
        "⬇ İndir (PNG)",
        data=img_buffer.getvalue(),
        file_name=f"trend_analizi_{timestamp}.png",
        mime="image/png"
    )

    return img_buffer
