from fpdf import FPDF
import streamlit as st
import os
import tempfile


def generate_pdf_report(
    total_budget,
    total_actual,
    variance,
    variance_pct,
    img_buffer=None,
    comparative_img_buffer=None,
):
    try:
        pdf = FPDF()
        pdf.add_page()

        # Font paths for the DejaVu fonts
        font_path_regular = "utils/fonts/DejaVuSans.ttf"
        font_path_bold = "utils/fonts/DejaVuSans-Bold.ttf"

        # Check if font files exist
        if not os.path.exists(font_path_regular) or not os.path.exists(font_path_bold):
            st.error("Font dosyaları bulunamadı. Lütfen font dosyalarının doğru konumda olduğundan emin olun.")
            return None

        try:
            # Add fonts with the correct paths
            pdf.add_font("DejaVu", "", font_path_regular, uni=True)
            pdf.add_font("DejaVu", "B", font_path_bold, uni=True)
        except Exception as e:
            st.error(f"Font yükleme hatası: {str(e)}")
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
                st.warning(f"Trend grafiği PDF'e eklenemedi: {str(e)}")

        # Handle comparative analysis image
        if comparative_img_buffer:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                    tmp_img.write(comparative_img_buffer.getvalue())
                    tmp_img.flush()
                    pdf.image(tmp_img.name, w=pdf.w - 40)
                os.unlink(tmp_img.name)  # Clean up temporary file
            except Exception as e:
                st.warning(f"Karşılaştırmalı analiz grafiği PDF'e eklenemedi: {str(e)}")

        try:
            pdf_data = pdf.output(dest="S")
            # Ensure the data is bytes (encode if necessary)
            if isinstance(pdf_data, str):
                return pdf_data.encode("latin-1")
            return pdf_data
        except Exception as e:
            st.error(f"PDF oluşturma hatası: {str(e)}")
            return None

    except Exception as e:
        st.error(f"Rapor oluşturma sırasında beklenmeyen bir hata oluştu: {str(e)}")
        return None
