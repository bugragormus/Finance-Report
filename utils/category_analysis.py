"""
category_analysis.py - Kategori bazlı analiz ve görselleştirme işlemlerini yönetir.

Bu modül, kategori bazlı analizler oluşturmak ve görselleştirmek için
fonksiyonlar içerir.
"""

import streamlit as st
import plotly.express as px
import plotly.io as pio
from io import BytesIO
import zipfile
import pandas as pd
from typing import Tuple, Optional, Any
from utils.error_handler import handle_error, display_friendly_error

# Plotly ayarları
pio.kaleido.scope.default_format = "png"
pio.kaleido.scope.default_width = 1200
pio.kaleido.scope.default_height = 800
pio.kaleido.scope.default_colorway = px.colors.qualitative.Pastel
pio.kaleido.scope.default_paper_bgcolor = "#FFFFFF"
pio.kaleido.scope.default_plot_bgcolor = "#FFFFFF"

from config.constants import MONTHS


@handle_error
def create_charts(df: pd.DataFrame, group_col: str, time_period: str, metric: str) -> Tuple[Optional[Any], Optional[Any]]:
    """
    Pasta ve sütun grafiklerini oluşturur.
    
    Parameters:
        df (DataFrame): İşlenecek veri çerçevesi
        group_col (str): Gruplama kolonu
        time_period (str): Zaman periyodu (ay veya Kümüle)
        metric (str): Metrik adı (Bütçe, Fiili, BE, vb.)
        
    Returns:
        Tuple[Optional[Figure], Optional[Figure]]: (pasta_grafik, sütun_grafik) tuple
    """
    # Sütun adını oluştur
    col_name = (
        f"{time_period} {metric}" if time_period != "Kümüle" else f"Kümüle {metric}"
    )

    if col_name not in df.columns:
        return None, None

    try:
        # Veri hazırlama
        df_filtered = df[[group_col, col_name]].copy()
        df_grouped = df_filtered.groupby(group_col)[col_name].sum().reset_index()
        df_sorted = df_grouped.sort_values(col_name, ascending=False)

        # Pasta Grafik
        fig_pie = px.pie(
            df_sorted,
            values=col_name,
            title=f"{metric} Dağılımı - {time_period}",
            names=group_col,
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_pie.update_layout(
            font=dict(size=14, family="Arial"),
            margin=dict(t=60, b=60, l=20, r=150),  # sağ boşluk artırıldı
            showlegend=True,
            legend=dict(
                orientation="v",  # dikey hizalama
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.05  # sağa kaydır
            ),
        )

        # Sütun Grafik
        fig_bar = px.bar(
            df_sorted,
            x=group_col,
            y=col_name,
            text=col_name,
            title=f"{metric} Karşılaştırması - {time_period}",
            color=group_col,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )

        fig_bar.update_layout(
            xaxis=dict(
                title=None,
                tickangle=-60,  # Açıyı artır
                tickfont=dict(size=9, family="Arial"),
                automargin=True,  # Otomatik marj ayarı
                side="bottom",  # X eksenini alta sabitle
            ),
            yaxis=dict(title=None, tickformat=",.0f", automargin=True),
            margin=dict(
                t=80,  # Üst
                b=350,  # Alt (uzun etiketler için)
                l=150,  # Sol (artırıldı)
                r=50,  # Sağ
            ),
        )

        fig_bar.update_traces(
            textposition="auto",
            textangle=0,  # Metin dönüş açısı
            cliponaxis=False,  # Ekseni aşan verilere izin ver
        )

        # Kenar boşluklarını zorla ayarla
        fig_bar.update_layout(autosize=False, width=1400, height=900)  # Genişliği artır

        return fig_pie, fig_bar
    except Exception as e:
        display_friendly_error(
            f"Grafik oluşturma hatası: {str(e)}",
            f"{time_period} {metric} için grafik oluşturulamadı."
        )
        return None, None


@handle_error
def save_figure(fig: Any) -> BytesIO:
    """
    Grafiği buffer'a kaydeder.
    
    Parameters:
        fig (Figure): Kaydedilecek grafik
        
    Returns:
        BytesIO: Grafik görüntüsü buffer'ı
    """
    img_buffer = BytesIO()
    try:
        pio.write_image(
            fig,
            img_buffer,
            format="png",
            width=1400,  # Render genişliğini artır
            height=900,
            scale=2,  # Çözünürlüğü 2x yap
        )
        img_buffer.seek(0)
        return img_buffer
    except Exception as e:
        display_friendly_error(
            f"Grafik kaydetme hatası: {str(e)}",
            "Grafik kaydedilemedi."
        )
        # Boş bir buffer döndür
        img_buffer.seek(0)
        return img_buffer


@handle_error
def show_category_charts(df: pd.DataFrame) -> Optional[BytesIO]:
    """
    Kategori bazlı analiz grafiklerini gösterir ve indirebilir.
    
    Parameters:
        df (DataFrame): İşlenecek veri çerçevesi
        
    Returns:
        Optional[BytesIO]: Tüm grafikleri içeren ZIP buffer'ı veya None
    """
    with st.expander("⚙️ Analiz Ayarları", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            group_options = [
                col
                for col in df.columns
                if df[col].dtype == "object" and df[col].nunique() <= 30
            ]
            if not group_options:
                display_friendly_error(
                    "Gruplama için uygun sütun bulunamadı",
                    "Veri formatını kontrol edin."
                )
                return None
                
            selected_group = st.selectbox(
                "**Gruplama Kriteri**",
                group_options,
                index=group_options.index("Masraf Çeşidi Grubu 1")
                if "Masraf Çeşidi Grubu 1" in group_options
                else 0,
            )

        with col2:
            time_options = ["Kümüle"] + MONTHS
            selected_time = st.selectbox("**Zaman Periyodu**", time_options, index=0)

        with col3:
            top_n = st.slider(
                "**Gösterilecek Grup Sayısı**",
                min_value=1,
                max_value=100,
                value=12,
                step=1,
            )

    # Grafiklerin oluşturulması
    metric_data = {
        "Bütçe": {"color": "#636EFA"},
        "Fiili": {"color": "#EF553B"},
        "BE Bakiye" if selected_time == "Kümüle" else "BE": {"color": "#00CC96"},
    }

    all_images = {}
    has_data = False  # En az bir grafik oluşturuldu mu kontrol et

    for metric in metric_data.keys():
        fig_pie, fig_bar = create_charts(df, selected_group, selected_time, metric)

        if fig_pie and fig_bar:
            has_data = True
            with st.container():
                st.markdown(f"### {metric} Analizi")

                # Pasta Grafik
                st.plotly_chart(fig_pie, use_container_width=True)

                # Boşluk
                st.write("")

                # Sütun Grafik
                st.plotly_chart(fig_bar, use_container_width=True)

                # Grafikleri kaydet
                pie_img = save_figure(fig_pie)
                bar_img = save_figure(fig_bar)
                all_images[f"{metric}_Pasta.png"] = pie_img.getvalue()
                all_images[f"{metric}_Sütun.png"] = bar_img.getvalue()

                # Bölüm ayracı
                st.markdown("---")
        else:
            st.info(f"{selected_time} {metric} verisi bulunamadı", icon="ℹ️")

    # İndirme butonu
    if all_images:
        try:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for name, data in all_images.items():
                    zip_file.writestr(name, data)

            col_dl, _ = st.columns([0.3, 0.7])
            with col_dl:
                st.download_button(
                    label="📥 Tüm Raporları İndir",
                    data=zip_buffer.getvalue(),
                    file_name="Finansal_Analiz_Raporu.zip",
                    mime="application/zip",
                    use_container_width=True,
                    type="primary",
                )
            return zip_buffer
        except Exception as e:
            display_friendly_error(
                f"ZIP oluşturma hatası: {str(e)}",
                "Rapor dosyası oluşturulamadı."
            )
            return None
    elif not has_data:
        display_friendly_error(
            "Hiçbir veri görselleştirilemedi",
            "Seçilen zamanda ve metrikte veri bulunamadı."
        )
        return None
        
    return None
