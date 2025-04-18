"""
data_preview.py - Veri önizleme ve görüntüleme işlemlerini yönetir.

Bu modül, veri çerçevelerinin görüntülenmesi, özetlenmesi ve
çeşitli formatlarda dışa aktarılması için fonksiyonlar içerir.

Fonksiyonlar:
    - show_filtered_data: DataFrame'i gösterir ve Excel çıktısı verir
    - show_grouped_summary: Gruplandırılmış veri özetini gösterir
    - calculate_group_totals: Grup toplamlarını hesaplar
    - show_column_totals: Sütun toplamlarını gösterir

Özellikler:
    - Sayfalama desteği
    - Stil uygulama
    - Sabit sütun desteği
    - Excel dışa aktarım
    - Hata yönetimi

Kullanım:
    from utils.data_preview import show_filtered_data
    
    excel_buffer = show_filtered_data(
        df,
        filename="rapor.xlsx",
        style_func=style_warning_rows,
        title="Filtrelenmiş Veri"
    )
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from typing import Optional, List, Callable, Union
from utils.error_handler import handle_error, display_friendly_error


@handle_error
def show_filtered_data(
    df: pd.DataFrame, 
    filename: str = "filtrelenmis_rapor.xlsx", 
    style_func: Optional[Callable] = None, 
    title: Optional[str] = None,
    sticky_column: Optional[Union[str, int]] = None,
    page_size: int = 1000
) -> BytesIO:
    """
    DataFrame'i gösterir, istenirse stil uygular, Excel çıktısı verir.
    
    Bu fonksiyon:
    1. Veri çerçevesini sayfalar
    2. Stil uygulama seçeneği sunar
    3. Sütun yapılandırmasını ayarlar
    4. Sabit sütun desteği sağlar
    5. Excel çıktısı oluşturur
    
    Parameters:
        df (DataFrame): Görüntülenecek veri çerçevesi
        filename (str): İndirme için dosya adı
        style_func (Callable, optional): Veri çerçevesine uygulanacak stil fonksiyonu
        title (str, optional): Görüntüleme başlığı
        sticky_column (Union[str, int], optional): Sabit kalacak sütun adı veya pozisyonu
        page_size (int): Sayfa başına gösterilecek satır sayısı
        
    Returns:
        BytesIO: Excel dosyası buffer'ı
        
    Hata durumunda:
    - Hata loglanır
    - Kullanıcıya hata mesajı gösterilir
    - Boş buffer döndürülür
    
    Örnek:
        >>> df = pd.DataFrame({
        ...     "Masraf Yeri": ["A", "B", "C"],
        ...     "Bütçe": [1000, 2000, 3000]
        ... })
        >>> buffer = show_filtered_data(
        ...     df,
        ...     filename="rapor.xlsx",
        ...     style_func=style_warning_rows,
        ...     sticky_column="Masraf Yeri"
        ... )
    """
    if title:
        st.markdown(title)
    
    # Sabit sütun belirleme
    column_to_stick = None
    if sticky_column is not None:
        if isinstance(sticky_column, str) and sticky_column in df.columns:
            column_to_stick = sticky_column
        elif isinstance(sticky_column, int) and 0 <= sticky_column < len(df.columns):
            column_to_stick = df.columns[sticky_column]
    
    # Stil uygulama seçeneği
    apply_style = False
    if style_func and len(df) > page_size:
        apply_style = st.checkbox("⚠️ Stil Uygula (Performansı Etkileyebilir)", value=False)
    
    # Sayfalama
    total_pages = (len(df) + page_size - 1) // page_size
    if total_pages > 1:
        page = st.number_input("📄 Sayfa", min_value=1, max_value=total_pages, value=1)
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(df))
        display_df = df.iloc[start_idx:end_idx]
    else:
        display_df = df
    
    # Sütun yapılandırması
    column_config = {}
    for col in display_df.columns:
        if pd.api.types.is_numeric_dtype(display_df[col]):
            column_config[col] = st.column_config.NumberColumn(
                col,
                format="%.2f",
                help=f"{col} değerleri"
            )
        else:
            column_config[col] = st.column_config.TextColumn(
                col,
                help=f"{col} değerleri"
            )
    
    # Sabit sütun yapılandırması
    if column_to_stick:
        column_config[column_to_stick] = st.column_config.Column(
            column_to_stick,
            width="medium",
            help="Bu sütun sabit kalacak",
            pinned=True
        )
    
    # Benzersiz anahtar oluştur
    unique_key = f"data_editor_{filename}_{page if total_pages > 1 else 1}"
    
    # Stil fonksiyonu varsa ve seçilmişse uygula
    if style_func and apply_style:
        styled_df = style_func(display_df.copy())
        # Stil uygulanmış DataFrame'i göster
        st.data_editor(
            styled_df,
            column_config=column_config,
            use_container_width=True,
            disabled=True,  # Düzenleme devre dışı
            #hide_index=True,
            key=unique_key
        )
    else:
        # Normal DataFrame'i göster
        st.data_editor(
            display_df,
            column_config=column_config,
            use_container_width=True,
            disabled=True,  # Düzenleme devre dışı
            #hide_index=True,
            key=unique_key
        )

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
    style_func: Optional[Callable] = None,
    sticky_column: Optional[Union[str, int]] = None,
    page_size: int = 1000
) -> Optional[BytesIO]:
    """
    Gruplandırılmış veri özetini gösterir ve Excel çıktısı verir.
    
    Bu fonksiyon:
    1. Veriyi belirtilen sütuna göre gruplar
    2. Hedef sütunlar için özet istatistikler hesaplar
    3. Sonuçları görüntüler
    4. Excel çıktısı oluşturur
    
    Parameters:
        df (DataFrame): İşlenecek veri çerçevesi
        group_column (str): Gruplama yapılacak sütun
        target_columns (List[str]): Özetlenecek sütunlar
        filename (str): İndirme için dosya adı
        title (str, optional): Görüntüleme başlığı
        style_func (Callable, optional): Uygulanacak stil fonksiyonu
        sticky_column (Union[str, int], optional): Sabit kalacak sütun
        page_size (int): Sayfa başına satır sayısı
        
    Returns:
        Optional[BytesIO]: Excel dosyası buffer'ı veya None
        
    Hata durumunda:
    - Hata loglanır
    - Kullanıcıya hata mesajı gösterilir
    - None döndürülür
    
    Örnek:
        >>> df = pd.DataFrame({
        ...     "Kategori": ["A", "A", "B"],
        ...     "Bütçe": [1000, 2000, 3000]
        ... })
        >>> buffer = show_grouped_summary(
        ...     df,
        ...     group_column="Kategori",
        ...     target_columns=["Bütçe"],
        ...     filename="ozet.xlsx"
        ... )
    """
    # Gerçekten var olan kolonları filtrele
    existing_columns = [col for col in target_columns if col in df.columns]

    if group_column in df.columns and existing_columns:
        if title:
            st.markdown(title)

        # Tüm sayısal sütunları topla
        numeric_columns = [col for col in existing_columns if pd.api.types.is_numeric_dtype(df[col])]
        grouped_df = df.groupby(group_column)[numeric_columns].sum().reset_index()
        
        return show_filtered_data(
            grouped_df, 
            filename=filename, 
            style_func=style_func,
            sticky_column=sticky_column,
            page_size=page_size
        )
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
    Grup toplamlarını hesaplar.
    
    Bu fonksiyon:
    1. Veriyi belirtilen sütuna göre gruplar
    2. Seçili aylar için metrikleri hesaplar
    3. Toplamları hesaplar
    4. Sonuçları DataFrame olarak döndürür
    
    Parameters:
        df (DataFrame): İşlenecek veri çerçevesi
        group_column (str): Gruplama yapılacak sütun
        selected_months (List[str]): İşlenecek aylar
        metrics (List[str]): Hesaplanacak metrikler
        
    Returns:
        DataFrame: Hesaplanmış toplamlar
        
    Hata durumunda:
    - Hata loglanır
    - Boş DataFrame döndürülür
    
    Örnek:
        >>> df = pd.DataFrame({
        ...     "Kategori": ["A", "A", "B"],
        ...     "Ocak Bütçe": [1000, 2000, 3000]
        ... })
        >>> totals = calculate_group_totals(
        ...     df,
        ...     group_column="Kategori",
        ...     selected_months=["Ocak"],
        ...     metrics=["Bütçe"]
        ... )
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
    Sütun toplamlarını gösterir ve Excel çıktısı verir.
    
    Bu fonksiyon:
    1. Sayısal sütunların toplamlarını hesaplar
    2. Sonuçları görüntüler
    3. Excel çıktısı oluşturur
    
    Parameters:
        df (DataFrame): İşlenecek veri çerçevesi
        filename (str): İndirme için dosya adı
        title (str, optional): Görüntüleme başlığı
        
    Returns:
        BytesIO: Excel dosyası buffer'ı
        
    Hata durumunda:
    - Hata loglanır
    - Kullanıcıya hata mesajı gösterilir
    - Boş buffer döndürülür
    
    Örnek:
        >>> df = pd.DataFrame({
        ...     "Bütçe": [1000, 2000, 3000],
        ...     "Fiili": [900, 2100, 2900]
        ... })
        >>> buffer = show_column_totals(
        ...     df,
        ...     filename="toplamlar.xlsx"
        ... )
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

