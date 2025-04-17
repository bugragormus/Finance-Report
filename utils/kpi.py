"""
kpi.py - KPI (Anahtar Performans Göstergeleri) panelini yönetir.

Bu modül, finansal performans metriklerinin hesaplanmasını ve 
gösterilmesini sağlayan fonksiyonları içerir.
"""

import streamlit as st
from typing import Dict, Any
from utils.error_handler import handle_error, display_friendly_error


def calculate_kpi_metrics(df) -> Dict[str, float]:
    """
    Tüm KPI metriklerini hesaplar ve döndürür.
    
    Parameters:
        df (DataFrame): İşlenecek veri çerçevesi
        
    Returns:
        Dict[str, float]: Hesaplanan metrikler
    """
    total_budget = df["Kümüle Bütçe"].sum()
    total_actual = df["Kümüle Fiili"].sum()
    total_be = (
        df["Kümüle BE Bakiye"].sum()
        if "Kümüle BE Bakiye" in df.columns
        else 0
    )
    total_karsilik = df["Kümüle Fiili Karşılık Masrafı"].sum() if "Kümüle Fiili Karşılık Masrafı" in df.columns else 0

    variance = total_budget - total_actual
    variance_pct = (variance / total_budget * 100) if total_budget != 0 else 0
    usage_pct = (total_actual / total_budget * 100) if total_budget != 0 else 0
    be_ratio = (total_be / total_actual * 100) if total_actual != 0 else 0
    karsilik_ratio = (
        (total_karsilik / total_actual * 100) if total_actual != 0 else 0
    )
    
    return {
        "total_budget": total_budget,
        "total_actual": total_actual,
        "total_be": total_be,
        "total_karsilik": total_karsilik,
        "variance": variance,
        "variance_pct": variance_pct,
        "usage_pct": usage_pct,
        "be_ratio": be_ratio,
        "karsilik_ratio": karsilik_ratio
    }


def _display_budget_warning(usage_pct: float) -> None:
    """
    Bütçe kullanım durumuna göre uyarı gösterir.
    
    Parameters:
        usage_pct (float): Bütçe kullanım yüzdesi
    """
    if usage_pct > 110:
        st.error("🚨 Bütçe %110'dan fazla aşıldı! Acil müdahale gerekebilir.")
    elif usage_pct > 90:
        st.warning("⚠️ Bütçeye çok yaklaşıldı (%90 üzeri).")
    else:
        st.success("✅ Bütçe kullanımı güvenli seviyede.")


@handle_error
def show_kpi_panel(df) -> None:
    """
    KPI metriklerini gösterge panelinde gösterir.
    
    Parameters:
        df (DataFrame): İşlenecek veri çerçevesi
    """
    if "Kümüle Bütçe" not in df.columns or "Kümüle Fiili" not in df.columns:
        display_friendly_error(
            "Tabloda Kümüle Değerler Bulunamadı!",
            "Kümüle Bütçe ve Kümüle Fiili sütunlarının varlığını kontrol edin."
        )
        return
    
    metrics = calculate_kpi_metrics(df)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Toplam Bütçe", f"{metrics['total_budget']:,.0f} ₺")
        st.metric("💼 Toplam Fiili", f"{metrics['total_actual']:,.0f} ₺")
    with col2:
        delta_color = "inverse" if metrics['variance'] < 0 else "normal"
        st.metric(
            "📊 Bütçe Farkı",
            f"{metrics['variance']:,.0f} ₺",
            delta=f"{metrics['variance_pct']:.2f} %",
            delta_color=delta_color,
        )
        st.metric("⚙️ Kullanım Oranı", f"{metrics['usage_pct']:.2f} %")
    with col3:
        st.metric("🧾 Karşılık / Fiili", f"{metrics['karsilik_ratio']:.1f} %")
        st.metric("📘 BE / Fiili", f"{metrics['be_ratio']:.1f} %")

    _display_budget_warning(metrics['usage_pct'])
    st.markdown("---")
