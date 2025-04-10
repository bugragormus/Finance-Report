import streamlit as st
import pandas as pd
import plotly.express as px

def show_category_charts(df):
    st.subheader("📊 Kategori Bazlı Harcama Dağılımı")

    # Kategorik grup alanları (objeler ve düşük unique sayılılar)
    group_candidates = [col for col in df.columns if df[col].dtype == 'object' and df[col].nunique() <= 50]
    selected_group = st.selectbox("🧩 Gruplama Alanı Seçin", group_candidates, index=group_candidates.index("Masraf Çeşidi Grubu 1") if "Masraf Çeşidi Grubu 1" in group_candidates else 0)

    # Ay seçimi
    month_cols = [col for col in df.columns if any(ay in col for ay in [
        "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
        "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
    ]) and "Fiili" in col]

    if month_cols:
        selected_month = st.selectbox("📅 Ay Seçimi (İsteğe Bağlı)", ["Kümüle Fiili"] + month_cols)
    else:
        selected_month = "Kümüle Fiili"

    # İlk N gösterimi
    top_n = st.slider("🔢 Gösterilecek Grup Sayısı", min_value=1, max_value=4, value=2, step=1)

    if selected_group not in df.columns or selected_month not in df.columns:
        st.warning("Gerekli sütunlar eksik!")
        return

    grouped = df.groupby(selected_group)[selected_month].sum().reset_index()
    grouped = grouped.sort_values(by=selected_month, ascending=False).head(top_n)

    fig_pie = px.pie(grouped, names=selected_group, values=selected_month,
                     title=f"{selected_group} Bazında Harcamalar ({selected_month})")
    st.plotly_chart(fig_pie, use_container_width=True)

    fig_bar = px.bar(grouped, x=selected_group, y=selected_month,
                     title=f"{selected_group} Bazında {selected_month}")
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)
