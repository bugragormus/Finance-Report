"""
report.py - PDF rapor oluşturma işlemlerini yönetir.

Bu modül, uygulama verileri kullanılarak PDF formatında 
raporlar oluşturur.

Fonksiyonlar:
    - generate_pdf_report: Finansal performans raporu PDF dosyası oluşturur
    - add_chart_to_pdf: PDF'e grafik ekler
    - format_currency: Para birimini formatlar

Özellikler:
    - Özelleştirilebilir rapor şablonları
    - Grafik entegrasyonu
    - Çoklu dil desteği
    - Hata yönetimi
    - Geçici dosya yönetimi

Kullanım:
    from utils.report import generate_pdf_report
    
    pdf_data = generate_pdf_report(
        total_budget=1000000,
        total_actual=950000,
        variance=50000,
        variance_pct=5.0,
        img_buffer=trend_chart,
        comparative_img_buffer=comparative_chart
    )
    if pdf_data:
        with open("rapor.pdf", "wb") as f:
            f.write(pdf_data)
"""

from fpdf import FPDF
import os
import tempfile
from typing import Optional
from io import BytesIO
from datetime import datetime
from utils.error_handler import handle_error, display_friendly_error


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Sayfa kenar boşlukları
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(True, margin=20)
        
        # Font paths for the DejaVu fonts
        self.font_path_regular = "utils/fonts/DejaVuSans.ttf"
        self.font_path_bold = "utils/fonts/DejaVuSans-Bold.ttf"

        # Check if font files exist
        if not os.path.exists(self.font_path_regular) or not os.path.exists(self.font_path_bold):
            display_friendly_error(
                "Font dosyaları bulunamadı", 
                "Lütfen font dosyalarının doğru konumda olduğundan emin olun."
            )
            return

        try:
            # Add fonts with the correct paths
            self.add_font("DejaVu", "", self.font_path_regular, uni=True)
            self.add_font("DejaVu", "B", self.font_path_bold, uni=True)
        except Exception as e:
            display_friendly_error(
                f"Font yükleme hatası: {str(e)}",
                "Font dosyalarının formatını kontrol edin."
            )

    def header(self):
        # Logo
        try:
            self.image('assets/logo.png', 20, 10, 30)
        except:
            pass
        
        # Başlık
        self.set_font('DejaVu', 'B', 16)
        self.cell(0, 15, 'Finansal Performans Raporu', 0, 1, 'C')
        
        # Tarih
        self.set_font('DejaVu', '', 10)
        self.cell(0, 10, f'Rapor Tarihi: {datetime.now().strftime("%d.%m.%Y")}', 0, 1, 'R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.cell(0, 10, f'Sayfa {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('DejaVu', 'B', 14)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 12, title, 0, 1, 'L', True)
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('DejaVu', '', 11)
        self.multi_cell(0, 6, body)
        self.ln()

    def add_table(self, headers, data, col_widths):
        # Tablo başlığı
        self.set_font('DejaVu', 'B', 11)
        self.set_fill_color(240, 240, 240)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, 1, 0, 'C', True)
        self.ln()
        
        # Tablo içeriği
        self.set_font('DejaVu', '', 10)
        for row in data:
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 10, str(cell), 1, 0, 'C')
            self.ln()

    def add_metric_card(self, title, value, change=None):
        self.set_font('DejaVu', 'B', 11)
        self.cell(0, 10, title, 0, 1, 'L')
        
        self.set_font('DejaVu', '', 12)
        if change:
            self.cell(0, 10, f"{value} ({change})", 0, 1, 'L')
        else:
            self.cell(0, 10, str(value), 0, 1, 'L')
        self.ln(5)


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
    pdf = PDF()
    pdf.add_page()

    # 1. Özet Bölümü
    pdf.chapter_title("1. Özet")
    summary = f"""
    Bu rapor, şirketin finansal performansını detaylı bir şekilde analiz etmektedir. 
    Rapor, bütçe ve fiili harcamalar arasındaki farkları, trend analizlerini ve 
    kategori bazlı performans değerlendirmelerini içermektedir.
    
    Raporun ana bulguları:
    • Toplam bütçe: {total_budget:,.0f} ₺
    • Toplam fiili: {total_actual:,.0f} ₺
    • Fark: {variance:,.0f} ₺ ({variance_pct:.1f}%)
    
    Bu rapor, finansal performansın daha iyi anlaşılması ve gelecekteki bütçe planlaması 
    için önemli içgörüler sunmaktadır. Detaylı analizler ve öneriler, raporun devamında 
    yer almaktadır.
    """
    pdf.chapter_body(summary)

    # 2. Finansal Metrikler
    pdf.chapter_title("2. Finansal Metrikler")
    
    # Metrikler tablosu
    headers = ["Metrik", "Değer", "Değişim"]
    data = [
        ["Toplam Bütçe", f"{total_budget:,.0f} ₺", "-"],
        ["Toplam Fiili", f"{total_actual:,.0f} ₺", "-"],
        ["Fark", f"{variance:,.0f} ₺", f"{variance_pct:.1f}%"]
    ]
    col_widths = [70, 70, 70]
    pdf.add_table(headers, data, col_widths)
    
    # Metrik açıklamaları
    pdf.ln(5)
    metrics_explanation = """
    Finansal metrikler, şirketin bütçe performansını değerlendirmek için kullanılan 
    temel göstergelerdir. Bu metrikler:
    
    • Toplam Bütçe: Planlanan toplam harcama miktarı
    • Toplam Fiili: Gerçekleşen toplam harcama miktarı
    • Fark: Bütçe ile fiili harcamalar arasındaki fark
    
    Bu metrikler, bütçe sapmalarını tespit etmek ve gelecekteki bütçe planlaması için 
    önemli bilgiler sağlar.
    """
    pdf.chapter_body(metrics_explanation)

    # 3. Trend Analizi
    if img_buffer:
        pdf.chapter_title("3. Trend Analizi")
        trend_explanation = """
        Trend analizi, finansal performansın zaman içindeki değişimini gösterir. 
        Bu analiz, harcama kalıplarını ve bütçe sapmalarının nedenlerini anlamak 
        için önemlidir.
        
        Aşağıdaki grafik, seçilen dönemdeki harcama trendlerini göstermektedir:
        """
        pdf.chapter_body(trend_explanation)
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                tmp_img.write(img_buffer.getvalue())
                tmp_img.flush()
                pdf.image(tmp_img.name, w=pdf.w - 40)
            os.unlink(tmp_img.name)
        except Exception as e:
            display_friendly_error(
                f"Trend grafiği PDF'e eklenemedi: {str(e)}",
                "Grafik verilerini kontrol edin."
            )

    # 4. Karşılaştırmalı Analiz
    if comparative_img_buffer:
        pdf.chapter_title("4. Karşılaştırmalı Analiz")
        comparative_explanation = """
        Karşılaştırmalı analiz, farklı kategoriler veya dönemler arasındaki 
        finansal performansı karşılaştırır. Bu analiz, en iyi ve en kötü 
        performans gösteren alanları belirlemek için kullanılır.
        
        Aşağıdaki grafik, seçilen kategoriler arasındaki karşılaştırmalı 
        performansı göstermektedir:
        """
        pdf.chapter_body(comparative_explanation)
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                tmp_img.write(comparative_img_buffer.getvalue())
                tmp_img.flush()
                pdf.image(tmp_img.name, w=pdf.w - 40)
            os.unlink(tmp_img.name)
        except Exception as e:
            display_friendly_error(
                f"Karşılaştırmalı analiz grafiği PDF'e eklenemedi: {str(e)}",
                "Grafik verilerini kontrol edin."
            )

    # 5. Sonuç ve Öneriler
    pdf.chapter_title("5. Sonuç ve Öneriler")
    conclusion = f"""
    Finansal performans analizi sonucunda elde edilen bulgular ve öneriler:
    
    1. Bütçe Performansı
       • Bütçe ve fiili harcamalar arasında {variance_pct:.1f}%'lik bir fark bulunmaktadır.
       • Bu farkın ana nedenleri detaylı olarak incelenmelidir.
       • Gelecek dönemler için bütçe planlaması gözden geçirilmelidir.
    
    2. Trend Analizi
       • Harcama trendlerinin düzenli olarak takip edilmesi
       • Bütçe sapmalarının erken tespiti için alarm sistemlerinin kurulması
       • Kategori bazlı performans değerlendirmelerinin periyodik olarak yapılması
    
    3. İyileştirme Önerileri
       • Bütçe planlama süreçlerinin gözden geçirilmesi
       • Harcama kontrol mekanizmalarının güçlendirilmesi
       • Performans metriklerinin düzenli olarak izlenmesi
       • Kategori bazlı optimizasyon çalışmalarının yapılması
    
    4. Aksiyon Planı
       • Kısa vadeli (1-3 ay):
         - Bütçe sapmalarının detaylı analizi
         - Harcama kontrol mekanizmalarının gözden geçirilmesi
       
       • Orta vadeli (3-6 ay):
         - Bütçe planlama süreçlerinin iyileştirilmesi
         - Performans izleme sisteminin kurulması
       
       • Uzun vadeli (6-12 ay):
         - Kategori bazlı optimizasyon çalışmaları
         - Otomatik raporlama sisteminin geliştirilmesi
    """
    pdf.chapter_body(conclusion)

    try:
        pdf_data = pdf.output(dest="S")
        if isinstance(pdf_data, str):
            return pdf_data.encode("latin-1")
        return pdf_data
    except Exception as e:
        display_friendly_error(
            f"PDF oluşturma hatası: {str(e)}",
            "PDF oluşturulurken bir sorun oluştu."
        )
        return None
