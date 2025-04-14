from fpdf import FPDF


def generate_pdf_report(
    total_budget, total_actual, variance, variance_pct, img_buffer=None, comparative_img_buffer=None
):
    pdf = FPDF()
    pdf.add_page()

    # Font paths for the DejaVu fonts
    font_path_regular = "utils/fonts/DejaVuSans.ttf"
    font_path_bold = "utils/fonts/DejaVuSans-Bold.ttf"

    # Add fonts with the correct paths
    pdf.add_font("DejaVu", "", font_path_regular, uni=True)
    pdf.add_font("DejaVu", "B", font_path_bold, uni=True)

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

    # If the trend image exists, add it to the PDF
    if img_buffer:
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
            tmp_img.write(img_buffer.getvalue())
            tmp_img.flush()
            pdf.image(tmp_img.name, w=pdf.w - 40)

    # If the comparative analysis image exists, add it to the PDF
    if comparative_img_buffer:
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
            tmp_img.write(comparative_img_buffer.getvalue())
            tmp_img.flush()
            pdf.image(tmp_img.name, w=pdf.w - 40)

    pdf_data = pdf.output(dest="S")
    # Ensure the data is bytes (encode if necessary)
    if isinstance(pdf_data, str):
        return pdf_data.encode("latin-1")
    return pdf_data
