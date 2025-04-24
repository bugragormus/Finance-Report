"""
formatting.py - Formatlama ve sunum yardımcı fonksiyonlarını içerir.

Bu modül, veri formatlamak, sayıları düzenli göstermek ve
tekrar eden formatlama kodlarını merkezileştirmek için kullanılır.
"""

from typing import Union, Optional
import pandas as pd
import numpy as np
from pandas.io.formats.style import Styler


def format_currency(value: Union[int, float], decimal_places: int = 0) -> str:
    """
    Para birimi formatında gösterir.
    
    Parameters:
        value (Union[int, float]): Formatlanacak değer
        decimal_places (int): Ondalık basamak sayısı
        
    Returns:
        str: Formatlanmış metin
    """
    return f"{value:,.{decimal_places}f} ₺"


def format_percentage(value: Union[int, float], decimal_places: int = 2) -> str:
    """
    Yüzde formatında gösterir.
    
    Parameters:
        value (Union[int, float]): Formatlanacak değer
        decimal_places (int): Ondalık basamak sayısı
        
    Returns:
        str: Formatlanmış metin
    """
    return f"{value:.{decimal_places}f} %"


def calculate_percentage(part: Union[int, float], whole: Union[int, float], 
                        default: float = 0.0) -> float:
    """
    Güvenli bir şekilde yüzde hesaplar.
    
    Parameters:
        part (Union[int, float]): Bölünen (pay)
        whole (Union[int, float]): Bölen (payda)
        default (float): Bölen sıfırsa kullanılacak varsayılan değer
        
    Returns:
        float: Hesaplanan yüzde
    """
    return (part / whole * 100) if whole != 0 else default


def format_change(value: Union[int, float], 
                 show_sign: bool = True,
                 use_colors: bool = False) -> str:
    """
    Değişimi formatlar, opsiyonel olarak işaret ve renk ekler.
    
    Parameters:
        value (Union[int, float]): Formatlanacak değişim değeri
        show_sign (bool): Artı işaretini göster/gizle
        use_colors (bool): HTML renk etiketleri ekle/ekleme
        
    Returns:
        str: Formatlanmış metin
    """
    formatted = f"{'+' if value > 0 and show_sign else ''}{value:,.1f}"
    
    if use_colors:
        if value > 0:
            return f"<span style='color:green'>{formatted}</span>"
        elif value < 0:
            return f"<span style='color:red'>{formatted}</span>"
    
    return formatted


def highlight_negatives(df: pd.DataFrame, columns: Optional[list] = None) -> Styler:
    """
    Negatif değerleri vurgulayarak stillendirir.
    
    Parameters:
        df (DataFrame): Stillendirilecek DataFrame
        columns (list, optional): Stillendirilecek sütunlar, None ise sayısal sütunlar kullanılır
        
    Returns:
        DataFrame: Stillendirilmiş DataFrame
    """
    # Eğer sütunlar belirtilmemişse, sayısal sütunları bul
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Stillendirilmiş DataFrame'i döndür
    return df.style.map(
        lambda x: 'color: red' if isinstance(x, (int, float)) and x < 0 else '',
        subset=columns
    )


def round_significant(value: Union[int, float], digits: int = 2) -> float:
    """
    Değeri anlamlı basamaklara yuvarlar.
    
    Parameters:
        value (Union[int, float]): Yuvarlanacak değer
        digits (int): Anlamlı basamak sayısı
        
    Returns:
        float: Yuvarlanmış değer
    """
    if value == 0:
        return 0
    
    import math
    return round(value, digits - 1 - int(math.floor(math.log10(abs(value)))))


def format_currency_columns(df: pd.DataFrame, general_columns: list) -> pd.DataFrame:
    """
    GENERAL_COLUMNS dışındaki tüm sayısal sütunları TL formatında gösterir.
    
    Parameters:
        df (DataFrame): Formatlanacak DataFrame
        general_columns (list): Formatlanmayacak sütunların listesi
        
    Returns:
        DataFrame: Formatlanmış DataFrame
    """
    # Sayısal sütunları bul
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # GENERAL_COLUMNS dışındaki sayısal sütunları formatla
    for col in numeric_cols:
        if col not in general_columns:
            df[col] = df[col].apply(lambda x: format_currency(x) if pd.notnull(x) else x)
    
    return df 