"""
report.py - PDF rapor oluşturma işlemlerini yönetir.

Bu modül, uygulama verileri kullanılarak PDF formatında 
raporlar oluşturur.
"""

from fpdf import FPDF
import streamlit as st
import os
import tempfile
from typing import Optional, Union, Any
from io import BytesIO
from utils.error_handler import handle_error, display_friendly_error


@handle_error
def generate_pdf_report(
    total_budget: float,
    total_actual: float,
    variance: float,
    variance_pct: float,
    img_buffer: Optional[BytesIO] = None,
    comparative_img_buffer: Optional[BytesIO] = None,
) -> Optional[bytes]:
    """
    Finansal performans raporu PDF dosyası oluşturur.
    
    Parameters:
        total_budget (float): Toplam bütçe değeri
        total_actual (float): Toplam fiili değeri
        variance (float): Fark değeri
        variance_pct (float): Fark yüzdesi değeri
        img_buffer (BytesIO, optional): Trend grafik görüntüsü
        comparative_img_buffer (BytesIO, optional): Karşılaştırma grafik görüntüsü
        
    Returns:
        Optional[bytes]: PDF içeriği byte cinsinden veya None
    """
    pdf = FPDF()
    pdf.add_page()

    # Font paths for the DejaVu fonts
    font_path_regular = "utils/fonts/DejaVuSans.ttf"
    font_path_bold = "utils/fonts/DejaVuSans-Bold.ttf"

    # Check if font files exist
    if not os.path.exists(font_path_regular) or not os.path.exists(font_path_bold):
        display_friendly_error(
            "Font dosyaları bulunamadı", 
            "Lütfen font dosyalarının doğru konumda olduğundan emin olun."
        )
        return None

    try:
        # Add fonts with the correct paths
        pdf.add_font("DejaVu", "", font_path_regular, uni=True)
        pdf.add_font("DejaVu", "B", font_path_bold, uni=True)
    except Exception as e:
        display_friendly_error(
            f"Font yükleme hatası: {str(e)}",
            "Font dosyalarının formatını kontrol edin."
        )
        return None

    # Title using bold font
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "Finansal Performans Raporu", ln=True, align="C")
    pdf.ln(10)

    # Add text with normal font
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(0, 10, f"Toplam Bütçe: {total_budget:,.0f} ₺", ln=True)
    pdf.cell(0, 10, f"Toplam Fiili: {total_actual:,.0f} ₺", ln=True)
    pdf.cell(0, 10, f"Fark: {variance:,.0f} ₺ ({variance_pct:.1f}%)", ln=True)
    pdf.ln(10)

    # Handle trend image
    if img_buffer:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                tmp_img.write(img_buffer.getvalue())
                tmp_img.flush()
                pdf.image(tmp_img.name, w=pdf.w - 40)
            os.unlink(tmp_img.name)  # Clean up temporary file
        except Exception as e:
            display_friendly_error(
                f"Trend grafiği PDF'e eklenemedi: {str(e)}",
                "Grafik verilerini kontrol edin."
            )

    # Handle comparative analysis image
    if comparative_img_buffer:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                tmp_img.write(comparative_img_buffer.getvalue())
                tmp_img.flush()
                pdf.image(tmp_img.name, w=pdf.w - 40)
            os.unlink(tmp_img.name)  # Clean up temporary file
        except Exception as e:
            display_friendly_error(
                f"Karşılaştırmalı analiz grafiği PDF'e eklenemedi: {str(e)}",
                "Grafik verilerini kontrol edin."
            )

    try:
        pdf_data = pdf.output(dest="S")
        # Ensure the data is bytes (encode if necessary)
        if isinstance(pdf_data, str):
            return pdf_data.encode("latin-1")
        return pdf_data
    except Exception as e:
        display_friendly_error(
            f"PDF oluşturma hatası: {str(e)}",
            "PDF oluşturulurken bir sorun oluştu."
        )
        return None
