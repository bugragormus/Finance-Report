"""
metrics.py - Finansal metrik hesaplama fonksiyonlarını içerir.

Bu modül, finansal performans metriklerinin hesaplanmasını sağlayan
fonksiyonları içerir.

Fonksiyonlar:
    - calculate_metrics: Temel finansal metrikleri hesaplar
    - calculate_variance: Bütçe-fiili farkını hesaplar
    - calculate_performance: Performans metriklerini hesaplar

Özellikler:
    - Bütçe-fiili karşılaştırması
    - Varyans analizi
    - Performans hesaplamaları
    - Hata yönetimi
    - Tip güvenliği

Kullanım:
    from utils.metrics import calculate_metrics
    
    total_budget, total_actual, variance, variance_pct = calculate_metrics(df)
    print(f"Bütçe: {total_budget}, Fiili: {total_actual}")
    print(f"Fark: {variance} ({variance_pct:.2f}%)")
"""

from typing import Tuple
from utils.error_handler import handle_error


@handle_error
def calculate_metrics(df):
    """
    Temel finansal metrikleri hesaplar.
    
    Bu fonksiyon:
    1. Toplam bütçeyi hesaplar
    2. Toplam fiili tutarı hesaplar
    3. Bütçe-fiili farkını hesaplar
    4. Fark yüzdesini hesaplar
    
    Parameters:
        df (DataFrame): İşlenecek veri çerçevesi
        
    Returns:
        Tuple[float, float, float, float]: (
            toplam_bütçe, 
            toplam_fiili, 
            fark, 
            fark_yüzdesi
        )
        
    Hata durumunda:
    - Sıfır değerler döndürülür
    - Hata loglanır
    - Kullanıcıya bilgi verilir
    
    Örnek:
        >>> df = pd.DataFrame({
        ...     "Kümüle Bütçe": [1000, 2000],
        ...     "Kümüle Fiili": [900, 2100]
        ... })
        >>> budget, actual, var, pct = calculate_metrics(df)
        >>> print(f"Bütçe: {budget}, Fiili: {actual}")
        >>> print(f"Fark: {var} ({pct:.2f}%)")
    """
    total_budget = df["Kümüle Bütçe"].sum() if "Kümüle Bütçe" in df.columns else 0
    total_actual = df["Kümüle Fiili"].sum() if "Kümüle Fiili" in df.columns else 0
    variance = total_budget - total_actual
    variance_pct = (variance / total_budget * 100) if total_budget != 0 else 0
    return total_budget, total_actual, variance, variance_pct
