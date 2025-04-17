"""
insight_generator.py - Veri analizine dayalı öngörü oluşturma işlemlerini yönetir.

Bu modül, finansal verileri analiz ederek anlamlı öngörüler 
(insights) oluşturan fonksiyonlar içerir.
"""

import pandas as pd
from typing import List, Optional
from utils.error_handler import handle_error


@handle_error
def generate_insights(df: pd.DataFrame) -> List[str]:
    """
    Finansal verilerden anlamlı öngörüler üretir.
    
    Parameters:
        df (DataFrame): Analiz edilecek veri çerçevesi
        
    Returns:
        List[str]: Öngörü metinleri listesi
    """
    insights = []

    # En fazla harcama yapan masraf yeri
    if "Kümüle Fiili" in df.columns and "Masraf Yeri Adı" in df.columns:
        try:
            masraf_sums = (
                df.groupby("Masraf Yeri Adı")["Kümüle Fiili"]
                .sum()
                .sort_values(ascending=False)
            )
            if not masraf_sums.empty:
                top_yer = masraf_sums.index[0]
                top_val = masraf_sums.iloc[0]
                insights.append(
                    f"📌 En fazla harcama yapan masraf yeri: **{top_yer}** ({top_val:,.0f} ₺)"
                )
        except Exception:
            # Bu öngörü üretilemezse sessizce devam et
            pass

    # Bütçeyi aşan masraf yerleri
    if "Kümüle Bütçe" in df.columns and "Kümüle Fiili" in df.columns:
        try:
            df_copy = df.copy()
            df_copy["Fark"] = df_copy["Kümüle Bütçe"] - df_copy["Kümüle Fiili"]
            sapmalar = (
                df_copy[["Masraf Yeri Adı", "Fark"]]
                .groupby("Masraf Yeri Adı")
                .sum()
                .sort_values(by="Fark")
            )
            if not sapmalar.empty:
                en_cok_asan = sapmalar[sapmalar["Fark"] < 0]
                if not en_cok_asan.empty:
                    en_cok_asan_row = en_cok_asan.iloc[0]
                    insights.append(
                        f"⚠️ Bütçeyi en fazla aşan masraf yeri: **{en_cok_asan_row.name}** ({en_cok_asan_row['Fark']:,.0f} ₺ fark)"
                    )
        except Exception:
            # Bu öngörü üretilemezse sessizce devam et
            pass

        # Hiç harcama yapılmayan masraf yerleri
        try:
            en_az_kullanan = df[df["Kümüle Fiili"] == 0]
            if not en_az_kullanan.empty:
                yerler = en_az_kullanan["Masraf Yeri Adı"].dropna().unique().tolist()
                if yerler:
                    yerler_str = ", ".join(yerler[:5])
                    insights.append(f"❗ Hiç harcama yapılmayan masraf yerleri: {yerler_str}")
        except Exception:
            pass

        # En az harcama yapan aktif masraf yerleri
        try:
            active = df[df["Kümüle Fiili"] > 0]
            if not active.empty:
                min_row = (
                    active.groupby("Masraf Yeri Adı")["Kümüle Fiili"]
                    .sum()
                    .sort_values()
                    .head(1)
                )
                if not min_row.empty:
                    insights.append(
                        f"🔍 En az harcama yapan (aktif) masraf yeri: **{min_row.index[0]}** ({min_row.iloc[0]:,.0f} ₺)"
                    )
        except Exception:
            pass

        # Bütçesinin yarısından azını kullanan masraf yerleri
        if "Masraf Yeri Adı" in df.columns:
            try:
                df_copy = df.copy()
                df_copy["Kullanım Oranı"] = df_copy["Kümüle Fiili"] / df_copy["Kümüle Bütçe"].replace(
                    0, pd.NA
                )
                az_kullananlar = (
                    df_copy[df_copy["Kullanım Oranı"] < 0.5]["Masraf Yeri Adı"].dropna().unique()
                )
                if len(az_kullananlar) > 0:
                    insights.append(
                        f"🧊 Bütçesinin yarısından azını kullanan masraf yerleri: {', '.join(az_kullananlar[:5])}"
                    )
            except Exception:
                pass

            # En yüksek bütçe kullanım oranı
            try:
                kullanim_df = df[df["Kümüle Bütçe"] > 0].copy()
                kullanim_df["Kullanım Oranı"] = (
                    kullanim_df["Kümüle Fiili"] / kullanim_df["Kümüle Bütçe"]
                )
                if not kullanim_df.empty:
                    max_row = kullanim_df.sort_values(
                        "Kullanım Oranı", ascending=False
                    ).head(1)
                    if not max_row.empty:
                        oran = max_row["Kullanım Oranı"].values[0] * 100
                        ad = max_row["Masraf Yeri Adı"].values[0]
                        insights.append(
                            f"🔥 En yüksek bütçe kullanım oranı: **{ad}** (%{oran:.1f})"
                        )
            except Exception:
                pass

    # En çok harcama yapılan masraf grubu
    if "Masraf Çeşidi Grubu 1" in df.columns and "Kümüle Fiili" in df.columns:
        try:
            top_grup = (
                df.groupby("Masraf Çeşidi Grubu 1")["Kümüle Fiili"]
                .sum()
                .sort_values(ascending=False)
                .head(1)
            )
            if not top_grup.empty:
                insights.append(
                    f"🏷️ En çok harcama yapılan masraf grubu: **{top_grup.index[0]}** ({top_grup.iloc[0]:,.0f} ₺)"
                )
        except Exception:
            pass

    return insights
