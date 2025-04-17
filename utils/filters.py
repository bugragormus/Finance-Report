"""
filters.py - Veri filtreleme işlemlerini yönetir.

Bu modül, veri çerçevelerinin filtrelenmesini ve kullanıcı tarafından
seçilen filtre kriterlerinin uygulanmasını sağlar.
"""

import streamlit as st
from utils.error_handler import handle_error, display_friendly_error


@handle_error
def apply_filters(df, columns, key_prefix):
    """
    Streamlit arayüzünde seçilen filtre kriterlerine göre veriyi filtreler.
    
    Parameters:
        df (DataFrame): Filtrelenecek veri çerçevesi
        columns (list): Filtrelenecek sütunlar
        key_prefix (str): Filtre anahtar öneki (session_state anahtarları için)
        
    Returns:
        DataFrame: Filtrelenmiş veri çerçevesi
    """
    selected_filters = {}
    for col in columns:
        if col not in df.columns:
            continue
            
        # Kademeli filtreleme için geçici veri çerçevesi oluştur
        temp_df = df.copy()
        for other_col in columns:
            if other_col == col:
                continue
            if f"{key_prefix}_{other_col}" in st.session_state:
                selected = st.session_state[f"{key_prefix}_{other_col}"]
                if selected:
                    temp_df = temp_df[temp_df[other_col].isin(selected)]
                    
        # Bu sütun için mevcut seçenekleri belirle
        options = sorted(temp_df[col].dropna().unique().tolist(), key=lambda x: str(x))

        # Oturum durumundan mevcut seçimi al
        current_selection = st.session_state.get(f"{key_prefix}_{col}", [])
        
        # Mevcut seçimlerden artık mevcut olmayan değerleri temizle
        valid_defaults = [val for val in current_selection if val in options]
        
        try:
            selected = st.multiselect(
                f"🔍 {col}",
                options,
                key=f"{key_prefix}_{col}",
                default=valid_defaults,
                help=f"{col} için filtre seçin",
            )
        except st.errors.StreamlitAPIException as e:
            display_friendly_error(
                "Filtre değerleri değişti", 
                "Lütfen filtre seçimlerinizi tekrar yapın."
            )
            # Bu filtre için oturum durumunu sıfırla
            st.session_state[f"{key_prefix}_{col}"] = []
            selected = st.multiselect(
                f"🔍 {col}",
                options,
                key=f"{key_prefix}_{col}",
                default=[],
                help=f"{col} için filtre seçin",
            )
        
        selected_filters[col] = selected

    # Filtre uygulama
    filtered_df = df.copy()
    for col, selected in selected_filters.items():
        if selected:
            filtered_df = filtered_df[filtered_df[col].isin(selected)]
    return filtered_df
