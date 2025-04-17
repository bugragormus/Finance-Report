"""
metrics.py - Finansal metrik hesaplama fonksiyonlarını içerir.

Bu modül, finansal performans metriklerinin hesaplanmasını sağlayan
fonksiyonları içerir.
"""

from typing import Tuple
from utils.error_handler import handle_error


@handle_error
def calculate_metrics(df):
    """
    Temel finansal metrikleri hesaplar.
    
    Parameters:
        df (DataFrame): İşlenecek veri çerçevesi
        
    Returns:
        Tuple[float, float, float, float]: (
            toplam_bütçe, 
            toplam_fiili, 
            fark, 
            fark_yüzdesi
        )
    """
    total_budget = df["Kümüle Bütçe"].sum() if "Kümüle Bütçe" in df.columns else 0
    total_actual = df["Kümüle Fiili"].sum() if "Kümüle Fiili" in df.columns else 0
    variance = total_budget - total_actual
    variance_pct = (variance / total_budget * 100) if total_budget != 0 else 0
    return total_budget, total_actual, variance, variance_pct
