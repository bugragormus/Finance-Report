import streamlit as st


def show_kpi_panel(df):
    try:
        total_budget = df["Kümüle Bütçe"].sum()
        total_actual = df["Kümüle Fiili"].sum()
        total_be = (
            df.get("Kümüle BE Bakiye", 0).sum()
            if "Kümüle BE Bakiye" in df.columns
            else 0
        )
        total_karsilik = df.get("Kümüle Fiili Karşılık Masrafı", 0).sum()

        variance = total_budget - total_actual
        variance_pct = (variance / total_budget * 100) if total_budget != 0 else 0
        usage_pct = (total_actual / total_budget * 100) if total_budget != 0 else 0
        be_ratio = (total_be / total_actual * 100) if total_actual != 0 else 0
        karsilik_ratio = (
            (total_karsilik / total_actual * 100) if total_actual != 0 else 0
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Toplam Bütçe", f"{total_budget:,.0f} ₺")
            st.metric("💼 Toplam Fiili", f"{total_actual:,.0f} ₺")
        with col2:
            delta_color = "inverse" if variance < 0 else "normal"
            st.metric(
                "📊 Bütçe Farkı",
                f"{variance:,.0f} ₺",
                delta=f"{variance_pct:.2f} %",
                delta_color=delta_color,
            )
            st.metric("⚙️ Kullanım Oranı", f"{usage_pct:.2f} %")
        with col3:
            st.metric("🧾 Karşılık / Fiili", f"{karsilik_ratio:.1f} %")
            st.metric("📘 BE / Fiili", f"{be_ratio:.1f} %")

        # Özet Uyarı
        if usage_pct > 110:
            st.error("🚨 Bütçe %110'dan fazla aşıldı! Acil müdahale gerekebilir.")
        elif usage_pct > 90:
            st.warning("⚠️ Bütçeye çok yaklaşıldı (%90 üzeri).")
        else:
            st.success("✅ Bütçe kullanımı güvenli seviyede.")
        st.markdown("---")

    except Exception as e:
        st.warning("Tabloda Kümüle Değerler Bulunamadı!")
