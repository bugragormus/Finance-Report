"""
warning_system.py - Veri stillemesi ve uyarı işlemlerini yönetir.

Bu modül, veri çerçevelerinin biçimlendirilmesi ve görsel uyarıların
eklenmesi için fonksiyonlar içerir.

Fonksiyonlar:
    - style_warning_rows: Uyarı gerektiren satırları stillendirir
    - style_negatives_red: Negatif değerleri kırmızı renkle stillendirir
    - style_overused_rows: Bütçesi aşılan satırları stillendirir

Özellikler:
    - Koşullu stilleme
    - Renk kodlaması
    - Hata yönetimi
    - Performans optimizasyonu
    - Özelleştirilebilir stiller

Kullanım:
    from utils.warning_system import style_warning_rows
    
    styled_df = style_warning_rows(df)
    display(styled_df)
"""

import pandas as pd

from pandas.io.formats.style import Styler

from config.constants import MONTHS
from utils.error_handler import handle_error


@handle_error
def style_warning_rows(df: pd.DataFrame) -> Styler:
    """
    Uyarı gerektiren satırları stillendirir.
    
    Bu fonksiyon:
    1. Kümüle bütçe-fiili karşılaştırması yapar
    2. Aşım durumlarını tespit eder
    3. İlgili hücreleri renklendirir
    4. Aylık bazda kontroller yapar
    
    Parameters:
        df (DataFrame): Stillendirilecek veri çerçevesi
        
    Returns:
        Styler: Stillendirilmiş veri çerçevesi
        
    Hata durumunda:
    - Hata loglanır
    - Orijinal veri çerçevesi döndürülür
    
    Örnek:
        >>> df = pd.DataFrame({
        ...     "Kümüle Bütçe": [1000, 2000],
        ...     "Kümüle Fiili": [1100, 1900]
        ... })
        >>> styled_df = style_warning_rows(df)
        >>> display(styled_df)
    """
    def apply_style(row):
        style = [""] * len(row)

        # Kümüle kontrolü
        if "Kümüle Bütçe" in row and "Kümüle Fiili" in row:
            try:
                budget = row["Kümüle Bütçe"]
                actual = row["Kümüle Fiili"]

                if actual > budget:
                    # Kümüle alanları boyama (kırmızı)
                    for col in ["Kümüle Bütçe", "Kümüle Fiili"]:
                        if col in row.index:
                            style[row.index.get_loc(col)] = "background-color: #ffcccc"

                    # Masraf bilgilerini boyama (kırmızı)
                    if "Masraf Yeri" in row.index:
                        style[
                            row.index.get_loc("Masraf Yeri")
                        ] = "background-color: #ffcccc"
                    if "Masraf Çeşidi" in row.index:
                        style[
                            row.index.get_loc("Masraf Çeşidi")
                        ] = "background-color: #ffcccc"

                    # Aylık bazda fiili > bütçe ise mavi renkle boyama
                    for month in MONTHS:
                        b_col = f"{month} Bütçe"
                        a_col = f"{month} Fiili"
                        if b_col in row.index and a_col in row.index:
                            try:
                                if row[a_col] > row[b_col]:
                                    style[
                                        row.index.get_loc(b_col)
                                    ] = "background-color: #ffcccc"
                                    style[
                                        row.index.get_loc(a_col)
                                    ] = "background-color: #ffcccc"
                            except:
                                continue

            except:
                pass

        return style

    return df.style.apply(apply_style, axis=1)


@handle_error
def style_negatives_red(df: pd.DataFrame) -> Styler:
    """
    Negatif değerleri kırmızı renkle stillendirir.
    
    Bu fonksiyon:
    1. Fark bakiye sütunlarını tespit eder
    2. Negatif değerleri bulur
    3. Kırmızı renkle işaretler
    
    Parameters:
        df (DataFrame): Stillendirilecek veri çerçevesi
        
    Returns:
        Styler: Stillendirilmiş veri çerçevesi
        
    Hata durumunda:
    - Hata loglanır
    - Orijinal veri çerçevesi döndürülür
    
    Örnek:
        >>> df = pd.DataFrame({
        ...     "Fark Bakiye": [100, -50, 200]
        ... })
        >>> styled_df = style_negatives_red(df)
        >>> display(styled_df)
    """
    return df.style.map(
        lambda x: "color: red" if isinstance(x, (int, float)) and x < 0 else "",
        subset=[col for col in df.columns if "Fark Bakiye" in col],
    )


@handle_error
def style_overused_rows(df: pd.DataFrame) -> Styler:
    """
    Bütçesi aşılan satırları stillendirir.
    
    Bu fonksiyon:
    1. Kullanım yüzdesini kontrol eder
    2. %100 ve üzeri değerleri tespit eder
    3. İlgili satırları renklendirir
    
    Parameters:
        df (DataFrame): Stillendirilecek veri çerçevesi
        
    Returns:
        Styler: Stillendirilmiş veri çerçevesi
        
    Hata durumunda:
    - Hata loglanır
    - Orijinal veri çerçevesi döndürülür
    
    Örnek:
        >>> df = pd.DataFrame({
        ...     "Kullanım (%)": [80, 110, 95]
        ... })
        >>> styled_df = style_overused_rows(df)
        >>> display(styled_df)
    """
    def apply_style(row):
        if "Kullanım (%)" in row and pd.notnull(row["Kullanım (%)"]):
            try:
                if row["Kullanım (%)"] >= 100:
                    return ["background-color: #ffcccc"] * len(row)
            except:
                pass
        return [""] * len(row)

    return df.style.apply(apply_style, axis=1)
