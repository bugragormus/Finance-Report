"""
warning_system.py - Veri stillemesi ve uyarı işlemlerini yönetir.

Bu modül, veri çerçevelerinin biçimlendirilmesi ve görsel uyarıların
eklenmesi için fonksiyonlar içerir.
"""

import pandas as pd
from typing import List
from config.constants import MONTHS
from utils.error_handler import handle_error


@handle_error
def style_warning_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Uyarı gerektiren satırları stillendirir.
    
    Parameters:
        df (DataFrame): Stillendirilecek veri çerçevesi
        
    Returns:
        DataFrame: Stillendirilmiş veri çerçevesi
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
def style_negatives_red(df: pd.DataFrame) -> pd.DataFrame:
    """
    Negatif değerleri kırmızı renkle stillendirir.
    
    Parameters:
        df (DataFrame): Stillendirilecek veri çerçevesi
        
    Returns:
        DataFrame: Stillendirilmiş veri çerçevesi
    """
    return df.style.map(
        lambda x: "color: red" if isinstance(x, (int, float)) and x < 0 else "",
        subset=[col for col in df.columns if "Fark Bakiye" in col],
    )


@handle_error
def style_overused_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bütçesi aşılan satırları stillendirir.
    
    Parameters:
        df (DataFrame): Stillendirilecek veri çerçevesi
        
    Returns:
        DataFrame: Stillendirilmiş veri çerçevesi
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
