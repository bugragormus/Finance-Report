"""
loader.py - Veri yükleme işlemlerini yönetir.

Bu modül, Excel dosyalarının yüklenmesi, doğrulanması ve işlenmesi için 
gerekli fonksiyonları içerir.
"""

import pandas as pd
import streamlit as st
from utils.error_handler import handle_error, display_friendly_error


@st.cache_data(show_spinner="Veri yükleniyor...")
@handle_error
def load_data(uploaded_file):
    """
    Excel dosyasını yükler ve veri çerçevesine dönüştürür.
    
    Parameters:
        uploaded_file (UploadedFile): Streamlit ile yüklenen Excel dosyası
        
    Returns:
        DataFrame: Yüklenen veriden oluşturulan pandas DataFrame,
                  hata durumunda None döner.
    """
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    df.columns = [str(col).strip() for col in df.columns]

    # Zorunlu sütun kontrolü
    mandatory_columns = ["Masraf Yeri Adı", "Kümüle Bütçe", "Kümüle Fiili"]
    missing_columns = [col for col in mandatory_columns if col not in df.columns]
    if missing_columns:
        missing_cols_str = ', '.join(missing_columns)
        display_friendly_error(
            f"Eksik sütunlar: {missing_cols_str}",
            "Lütfen geçerli bir ZFMR0003 raporu yükleyin."
        )
        return None

    return df
