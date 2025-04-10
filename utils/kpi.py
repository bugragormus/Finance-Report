import streamlit as st

def show_kpi_panel(total_budget, total_actual, variance, variance_pct):
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📦 Toplam Bütçe", f"{total_budget:,.0f} ₺")
    col2.metric("💸 Toplam Fiili", f"{total_actual:,.0f} ₺")

    # Farkı ve yüzdeyi göster, renkleri dinamik olarak belirle
    delta_color = "inverse" if variance < 0 else "normal"  # Negatifse yeşil, pozitifse kırmızı
    col3.metric("📊 Fark", f"{variance:,.0f} ₺", delta=f"{variance_pct:.2f} %", delta_color=delta_color)

    # Kullanım oranı hesaplama ve gösterme
    usage_pct = (total_actual / total_budget * 100) if total_budget != 0 else 0
    col4.metric("⚙️ Kullanım Oranı", f"{usage_pct:.2f} %")
