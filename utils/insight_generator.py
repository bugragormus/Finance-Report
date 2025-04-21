"""
insight_generator.py - Veri analizine dayalı öngörü oluşturma işlemlerini yönetir.

Bu modül, finansal verileri analiz ederek anlamlı öngörüler 
(insights) oluşturan fonksiyonlar içerir.

Fonksiyonlar:
    - generate_insights: Finansal verilerden anlamlı öngörüler üretir
    - analyze_spending_patterns: Harcama kalıplarını analiz eder
    - identify_anomalies: Anomali tespiti yapar

Özellikler:
    - Otomatik öngörü üretimi
    - Harcama analizi
    - Bütçe kullanım analizi
    - Anomali tespiti
    - Hata yönetimi

Kullanım:
    from utils.insight_generator import generate_insights
    
    insights = generate_insights(df)
    for insight in insights:
        print(insight)
"""

import pandas as pd
from typing import List
from utils.error_handler import handle_error


@handle_error
def generate_insights(df: pd.DataFrame) -> List[str]:
    """
    Finansal verilerden anlamlı öngörüler üretir.
    
    Bu fonksiyon:
    1. En fazla harcama yapan masraf yerini tespit eder
    2. Bütçeyi aşan masraf yerlerini belirler
    3. Hiç harcama yapılmayan yerleri tespit eder
    4. En az harcama yapan aktif yerleri belirler
    5. Bütçe kullanım oranlarını analiz eder
    6. En çok harcama yapılan masraf grubunu tespit eder
    
    Parameters:
        df (DataFrame): Analiz edilecek veri çerçevesi
        
    Returns:
        List[str]: Öngörü metinleri listesi
    """
    insights = []
    
    # Veri çerçevesini optimize et
    df = df.copy()
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # Gerekli sütunları kontrol et
    required_cols = {
        'masraf_yeri': ['Masraf Yeri Adı', 'Kümüle Fiili'],
        'butce': ['Masraf Yeri Adı', 'Kümüle Bütçe', 'Kümüle Fiili'],
        'masraf_grubu': ['Masraf Çeşidi Grubu 1', 'Kümüle Fiili']
    }
    
    # En fazla harcama yapan masraf yeri
    if all(col in df.columns for col in required_cols['masraf_yeri']):
        try:
            masraf_sums = df.groupby("Masraf Yeri Adı")["Kümüle Fiili"].sum()
            if not masraf_sums.empty:
                top_yer = masraf_sums.idxmax()
                top_val = masraf_sums.max()
                insights.append(f"📌 En fazla harcama yapan masraf yeri: **{top_yer}** ({top_val:,.0f} ₺)")
        except Exception:
            pass

    # Bütçe analizleri
    if all(col in df.columns for col in required_cols['butce']):
        try:
            # Bütçeyi aşan masraf yerleri
            df['Fark'] = df['Kümüle Bütçe'] - df['Kümüle Fiili']
            sapmalar = df.groupby("Masraf Yeri Adı")['Fark'].sum()
            if not sapmalar.empty:
                en_cok_asan = sapmalar[sapmalar < 0]
                if not en_cok_asan.empty:
                    top_asan = en_cok_asan.idxmin()
                    top_fark = en_cok_asan.min()
                    insights.append(f"⚠️ Bütçeyi en fazla aşan masraf yeri: **{top_asan}** ({top_fark:,.0f} ₺ fark)")

            # Hiç harcama yapılmayan masraf yerleri
            en_az_kullanan = df[df['Kümüle Fiili'] == 0]['Masraf Yeri Adı'].dropna().unique()
            if len(en_az_kullanan) > 0:
                yerler_str = ", ".join(en_az_kullanan[:5])
                insights.append(f"❗ Hiç harcama yapılmayan masraf yerleri: {yerler_str}")

            # En az harcama yapan aktif masraf yerleri
            active = df[df['Kümüle Fiili'] > 0]
            if not active.empty:
                min_row = active.groupby("Masraf Yeri Adı")['Kümüle Fiili'].sum().nsmallest(1)
                if not min_row.empty:
                    insights.append(f"🔍 En az harcama yapan (aktif) masraf yeri: **{min_row.index[0]}** ({min_row.iloc[0]:,.0f} ₺)")

            # Bütçe kullanım oranları
            df['Kullanım Oranı'] = df['Kümüle Fiili'] / df['Kümüle Bütçe'].replace(0, pd.NA)
            
            # Bütçesinin yarısından azını kullananlar
            az_kullananlar = df[df['Kullanım Oranı'] < 0.5]['Masraf Yeri Adı'].dropna().unique()
            if len(az_kullananlar) > 0:
                insights.append(f"🧊 Bütçesinin yarısından azını kullanan masraf yerleri: {', '.join(az_kullananlar[:5])}")

            # En yüksek bütçe kullanım oranı
            kullanim_df = df[df['Kümüle Bütçe'] > 0]
            if not kullanim_df.empty:
                max_row = kullanim_df.loc[kullanim_df['Kullanım Oranı'].idxmax()]
                oran = max_row['Kullanım Oranı'] * 100
                insights.append(f"🔥 En yüksek bütçe kullanım oranı: **{max_row['Masraf Yeri Adı']}** (%{oran:.1f})")

        except Exception:
            pass

    # En çok harcama yapılan masraf grubu
    if all(col in df.columns for col in required_cols['masraf_grubu']):
        try:
            top_grup = df.groupby("Masraf Çeşidi Grubu 1")['Kümüle Fiili'].sum().nlargest(1)
            if not top_grup.empty:
                insights.append(f"🏷️ En çok harcama yapılan masraf grubu: **{top_grup.index[0]}** ({top_grup.iloc[0]:,.0f} ₺)")
        except Exception:
            pass

    return insights
