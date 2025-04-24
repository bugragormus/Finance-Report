"""
KPI (Anahtar Performans Göstergeleri) Yönetim Modülü

Bu modül, finansal performans metriklerinin hesaplanmasını ve görselleştirilmesini sağlayan 
fonksiyonları içerir. Temel olarak bütçe, fiili harcamalar, bütçe farkları ve çeşitli 
oranların hesaplanması ve gösterilmesi işlemlerini yönetir.

Ana Fonksiyonlar:
    - calculate_kpi_metrics: Tüm KPI metriklerini hesaplar
    - show_kpi_panel: Hesaplanan metrikleri görsel bir panelde gösterir
    - _display_budget_warning: Bütçe kullanım durumuna göre uyarı mesajları gösterir

Hesaplanan Metrikler:
    - Toplam Bütçe ve Fiili Harcamalar
    - Bütçe Farkı ve Yüzdesi
    - Bütçe Kullanım Oranı
    - BE (Bütçe Eki) / Fiili Oranı
    - Karşılık / Fiili Oranı

Kullanım:
    >>> from utils.kpi import show_kpi_panel
    >>> show_kpi_panel(df)  # DataFrame'de gerekli sütunlar olmalıdır
"""

import streamlit as st
from typing import Dict
from utils.error_handler import handle_error, display_friendly_error
from config.constants import MONTHS


def calculate_kpi_metrics(df) -> Dict[str, float]:
    """
    Tüm KPI metriklerini hesaplar ve döndürür.
    
    Parameters:
        df (DataFrame): İşlenecek veri çerçevesi
        
    Returns:
        Dict[str, float]: Hesaplanan metrikler
    """
    # Sidebar'dan seçilen ayları al
    selected_months = st.session_state.get("month_filter", ["Hepsi"])
    if "Hepsi" in selected_months:
        selected_months = MONTHS

    # Seçilen ayların toplam bütçe ve fiili verilerini hesapla
    total_budget = 0
    total_actual = 0
    total_be = 0
    total_karsilik = 0

    for month in selected_months:
        if f"{month} Bütçe" in df.columns:
            total_budget += df[f"{month} Bütçe"].sum()
        if f"{month} Fiili" in df.columns:
            total_actual += df[f"{month} Fiili"].sum()
        if f"{month} BE Bakiye" in df.columns:
            total_be += df[f"{month} BE Bakiye"].sum()
        if f"{month} Fiili Karşılık Masrafı" in df.columns:
            total_karsilik += df[f"{month} Fiili Karşılık Masrafı"].sum()

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
    # Sidebar'dan seçilen ayları al
    selected_months = st.session_state.get("month_filter", ["Hepsi"])
    if "Hepsi" in selected_months:
        selected_months = MONTHS

    # Seçilen aylar için gerekli sütunların varlığını kontrol et
    required_columns = []
    for month in selected_months:
        required_columns.extend([
            f"{month} Bütçe",
            f"{month} Fiili"
        ])

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        display_friendly_error(
            "Tabloda Gerekli Sütunlar Bulunamadı!",
            f"Eksik sütunlar: {', '.join(missing_columns)}"
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
