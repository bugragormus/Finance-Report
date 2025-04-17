"""
data_preview.py - Veri önizleme ve görüntüleme işlemlerini yönetir.

Bu modül, veri çerçevelerinin görüntülenmesi, özetlenmesi ve
çeşitli formatlarda dışa aktarılması için fonksiyonlar içerir.
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from typing import Optional, List, Callable
from utils.error_handler import handle_error, display_friendly_error


@handle_error
def show_filtered_data(
    df: pd.DataFrame, 
    filename: str = "filtrelenmis_rapor.xlsx", 
    style_func: Optional[Callable] = None, 
    title: Optional[str] = None
) -> BytesIO:
    """
    DataFrame'i gösterir, istenirse stil uygular, Excel çıktısı verir.
    
    Parameters:
        df (DataFrame): Görüntülenecek veri çerçevesi
        filename (str): İndirme için dosya adı
        style_func (Callable, optional): Veri çerçevesine uygulanacak stil fonksiyonu
        title (str, optional): Görüntüleme başlığı
        
    Returns:
        BytesIO: Excel dosyası buffer'ı
    """
    if title:
        st.markdown(title)
    
    # Stil fonksiyonu varsa uygula
    if style_func:
        styled_df = style_func(df.copy())
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

    # Excel çıktısı oluştur
    excel_buffer = BytesIO()
    try:
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)

        # İndirme butonu
        st.download_button(
            label="⬇ İndir (Excel)",
            data=excel_buffer.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        display_friendly_error(
            f"Excel oluşturma hatası: {str(e)}",
            "Veri formatını kontrol edin."
        )

    return excel_buffer


@handle_error
def show_grouped_summary(
    df: pd.DataFrame, 
    group_column: str, 
    target_columns: List[str], 
    filename: str, 
    title: Optional[str] = None, 
    style_func: Optional[Callable] = None
) -> Optional[BytesIO]:
    """
    Belirtilen sütuna göre gruplandırılmış özet tablo gösterir.
    
    Parameters:
        df (DataFrame): Gruplanacak veri çerçevesi
        group_column (str): Gruplama yapılacak sütun
        target_columns (List[str]): Gruplanacak hedef sütunlar
        filename (str): İndirme için dosya adı
        title (str, optional): Görüntüleme başlığı
        style_func (Callable, optional): Veri çerçevesine uygulanacak stil fonksiyonu
        
    Returns:
        Optional[BytesIO]: Excel dosyası buffer'ı veya None
    """
    # Gerçekten var olan kolonları filtrele
    existing_columns = [col for col in target_columns if col in df.columns]

    if group_column in df.columns and existing_columns:
        if title:
            st.markdown(title)

        # Tüm sayısal sütunları topla
        numeric_columns = [col for col in existing_columns if pd.api.types.is_numeric_dtype(df[col])]
        grouped_df = df.groupby(group_column)[numeric_columns].sum().reset_index()
        
        return show_filtered_data(grouped_df, filename=filename, style_func=style_func)
    else:
        display_friendly_error(
            f"'{group_column}' bazında özet oluşturulamadı", 
            "Gerekli sütunlar eksik olabilir."
        )
        return None


@handle_error
def calculate_group_totals(
    df: pd.DataFrame, 
    group_column: str, 
    selected_months: List[str], 
    metrics: List[str]
) -> pd.DataFrame:
    """
    Grup bazında seçilen ayların toplamlarını hesaplar.
    
    Parameters:
        df (DataFrame): İşlenecek veri çerçevesi
        group_column (str): Gruplama yapılacak sütun
        selected_months (List[str]): Seçilen aylar listesi
        metrics (List[str]): Toplanacak metrik adları
        
    Returns:
        DataFrame: Gruplandırılmış toplamlar
    """
    # Toplanacak sütunları belirle
    columns_to_sum = []
    for month in selected_months:
        for metric in metrics:
            col_name = f"{month} {metric}"
            if col_name in df.columns:
                columns_to_sum.append(col_name)

    if not columns_to_sum:
        display_friendly_error(
            "Toplanacak sütun bulunamadı",
            "Lütfen ay ve metrik seçimlerinizi kontrol edin."
        )
        return pd.DataFrame()

    # Gruplandırılmış toplamları hesapla
    try:
        grouped_totals = df.groupby(group_column)[columns_to_sum].sum()

        # Her metrik için toplam sütun oluştur
        for metric in metrics:
            # Sütun adını "Ay [Metrik]" formatında böl ve tam eşleşme kontrol et
            metric_cols = [
                col for col in columns_to_sum
                if col.split(" ", 1)[-1] == metric
            ]

            # "BE Bakiye" metriği için "Kümüle BE Bakiye" sütununu da kontrol et
            if metric == "BE Bakiye" and not metric_cols:
                # Kümüle BE Bakiye sütunu varsa ekle
                kumule_col = "Kümüle BE Bakiye"
                if kumule_col in df.columns:
                    # Tüm sütunları içeren yeni bir DataFrame oluştur
                    if kumule_col not in grouped_totals.columns:
                        kumule_data = df.groupby(group_column)[kumule_col].sum()
                        # Ayrı bir seri olarak ekle
                        grouped_totals[f"Toplam {metric}"] = kumule_data
                        continue

            # "BE-Fiili Fark Bakiye" metriği için "Kümüle BE-Fiili Fark Bakiye" sütununu da kontrol et
            if metric == "BE-Fiili Fark Bakiye" and not metric_cols:
                # Kümüle BE-Fiili Fark Bakiye sütunu varsa ekle
                kumule_col = "Kümüle BE-Fiili Fark Bakiye"
                if kumule_col in df.columns:
                    # Tüm sütunları içeren yeni bir DataFrame oluştur
                    if kumule_col not in grouped_totals.columns:
                        kumule_data = df.groupby(group_column)[kumule_col].sum()
                        # Ayrı bir seri olarak ekle
                        grouped_totals[f"Toplam {metric}"] = kumule_data
                        continue

            if metric_cols:
                grouped_totals[f"Toplam {metric}"] = grouped_totals[metric_cols].sum(axis=1)

        return grouped_totals[[f"Toplam {metric}" for metric in metrics if f"Toplam {metric}" in grouped_totals.columns]]
    except Exception as e:
        display_friendly_error(
            f"Grup toplamları hesaplanırken hata oluştu: {str(e)}",
            "Veri ve grup sütununu kontrol edin."
        )
        return pd.DataFrame()


@handle_error
def show_column_totals(
    df: pd.DataFrame, 
    filename: str = "sutun_toplamlari.xlsx", 
    title: Optional[str] = None
) -> BytesIO:
    """
    GENERAL_COLUMNS dışında kalan sayısal sütunların toplamlarını gösterir.
    
    Parameters:
        df (DataFrame): İşlenecek veri çerçevesi
        filename (str): İndirme için dosya adı
        title (str, optional): Görüntüleme başlığı
        
    Returns:
        BytesIO: Excel dosyası buffer'ı
    """
    from config.constants import GENERAL_COLUMNS
    
    # Sayısal sütunları filtreleme
    numeric_columns = [
        col for col in df.columns
        if col not in GENERAL_COLUMNS and pd.api.types.is_numeric_dtype(df[col])
    ]
    
    if not numeric_columns:
        display_friendly_error(
            "Sayısal sütun bulunamadı",
            "Veri formatını kontrol edin."
        )
        # Boş bir DataFrame oluştur
        totals_df = pd.DataFrame({"Bilgi": ["Sayısal sütun bulunamadı"]})
    else:
        totals_df = pd.DataFrame(df[numeric_columns].sum()).T
        totals_df.index = ["Toplam"]

    return show_filtered_data(
        totals_df,
        filename=filename,
        title=title or "**Sayısal Sütunların Toplamları**"
    )

