# Finansal Performans Analiz Paneli

Finansal verilerin analizi, görselleştirilmesi ve raporlanması için geliştirilmiş bir Streamlit uygulaması.

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Teknik Özellikler](#-teknik-özellikler)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [API Dokümantasyonu](#-api-dokümantasyonu)
- [Modül Yapısı](#-modül-yapısı)
- [Performans İpuçları](#-performans-ipuçları)
- [Hata Yönetimi](#-hata-yönetimi)
- [Güvenlik](#-güvenlik)
- [Geliştirme](#-geliştirme)
- [Lisans](#-lisans)

## 🚀 Özellikler

### 📊 Veri Görüntüleme ve Analiz

- **Yüksek Performanslı Veri Görüntüleme**

  - st.data_editor kullanımı
  - Sayfalama desteği (büyük veri setleri için)
  - İsteğe bağlı stil uygulama
  - Sabit sütun desteği
  - Excel formatında dışa aktarım

- **Veri Filtreleme ve Gruplama**
  - Dinamik filtreleme
  - Çoklu grup analizi
  - Kategori bazlı karşılaştırmalar
  - Özel filtre kombinasyonları

### 📈 Görselleştirme

- **Trend Analizi**

  - Zaman serisi grafikleri
  - Hareketli ortalama hesaplamaları
  - Mevsimsellik analizi
  - Anomali tespiti

- **Kategori Bazlı Grafikler**

  - Pasta grafikler
  - Çubuk grafikler
  - Stacked bar grafikler
  - Heatmap görselleştirmeleri

- **Karşılaştırmalı Analizler**
  - Yıl bazlı karşılaştırmalar
  - Kategori bazlı karşılaştırmalar
  - Benchmark analizi
  - Performans metrikleri

### 📑 Raporlama

- **PDF Rapor Oluşturma**

  - Özelleştirilebilir rapor şablonları
  - Otomatik içindekiler tablosu
  - Grafik ve tablo ekleme
  - Çoklu dil desteği

- **Toplu İndirme**
  - ZIP formatında toplu indirme
  - Özelleştirilebilir rapor formatları
  - Otomatik dosya isimlendirme
  - İlerleme göstergesi

## 🛠️ Teknik Özellikler

### Performans Optimizasyonları

- **Veri İşleme**

  - Büyük veri setleri için sayfalama
  - İsteğe bağlı stil uygulama
  - Optimize edilmiş veri görüntüleme
  - Lazy loading desteği

- **Bellek Yönetimi**
  - Verimli veri yapıları
  - Garbage collection optimizasyonu
  - Önbellek yönetimi
  - Kaynak temizleme

### Veri İşleme

- **Pandas Entegrasyonu**

  - DataFrame optimizasyonları
  - Otomatik veri tipi algılama
  - Sayısal değer formatlaması
  - Hata yönetimi

- **Veri Doğrulama**
  - Giriş verisi doğrulama
  - Veri bütünlüğü kontrolü
  - Eksik veri yönetimi
  - Anomali tespiti

## 📦 Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)
- Git

### Adım Adım Kurulum

1. **Repository'yi Klonlayın:**

```bash
git clone [your-repository-url]
cd Finance-Report
```

2. **Sanal Ortam Oluşturun:**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. **Bağımlılıkları Yükleyin:**

```bash
pip install -r requirements.txt
```

4. **Uygulamayı Başlatın:**

```bash
streamlit run main.py
```

## 🎯 Kullanım

### Veri Yükleme

1. Excel dosyasını yükleyin
2. Veri formatını doğrulayın
3. Gerekli sütunları seçin

### Analiz Yapma

1. Filtreleri ayarlayın
2. Analiz türünü seçin
3. Parametreleri belirleyin
4. Sonuçları görüntüleyin

### Rapor Oluşturma

1. Rapor türünü seçin
2. İçeriği özelleştirin
3. Formatı belirleyin
4. İndirin veya paylaşın

## 📚 API Dokümantasyonu

### Ana Modüller

#### utils.loader

- `load_data(file)`: Excel dosyasını yükler ve DataFrame'e dönüştürür
- `validate_data(df)`: Veri bütünlüğünü kontrol eder

#### utils.filters

- `apply_filters(df, columns, filter_type)`: Veri filtreleme işlemlerini gerçekleştirir
- `clear_filters()`: Tüm filtreleri temizler

#### utils.metrics

- `calculate_metrics(df)`: Temel metrikleri hesaplar
- `generate_insights(df)`: Veri içgörüleri oluşturur

### Yardımcı Fonksiyonlar

#### utils.formatting

- `format_numbers(value)`: Sayısal değerleri formatlar
- `style_negatives_red(df)`: Negatif değerleri kırmızı yapar

#### utils.error_handler

- `handle_critical_error(func)`: Kritik hataları yönetir
- `display_friendly_error(message, fallback)`: Kullanıcı dostu hata mesajları gösterir

## 🗂️ Modül Yapısı

```
Finance-Report/
├── main.py              # Ana uygulama dosyası
├── requirements.txt     # Bağımlılıklar
├── README.md           # Dokümantasyon
├── config/             # Yapılandırma dosyaları
│   └── constants.py    # Sabitler
├── utils/              # Yardımcı modüller
│   ├── loader.py       # Veri yükleme
│   ├── filters.py      # Filtreleme
│   ├── metrics.py      # Metrik hesaplama
│   ├── report.py       # Raporlama
│   └── ...            # Diğer modüller
└── assets/            # Statik dosyalar
    └── favicon.png    # Uygulama ikonu
```

## 🔧 Performans İpuçları

### Veri İşleme

- Büyük veri setleri için sayfalama kullanın
- Gereksiz sütunları filtreleyin
- Veri tiplerini optimize edin

### Bellek Yönetimi

- Önbelleği düzenli temizleyin
- Büyük nesneleri bellekten serbest bırakın
- Garbage collection'ı optimize edin

### Arayüz Optimizasyonu

- Gereksiz yeniden render'ları önleyin
- Lazy loading kullanın
- Önbelleğe alma stratejileri uygulayın

## ⚠️ Hata Yönetimi

### Hata Türleri

- Veri yükleme hataları
- Filtreleme hataları
- Hesaplama hataları
- Raporlama hataları

### Hata Yakalama

- Try-except blokları
- Özel hata sınıfları
- Kullanıcı dostu hata mesajları
- Loglama sistemi

## 🔒 Güvenlik

### Veri Güvenliği

- Girdi doğrulama
- XSS koruması
- SQL enjeksiyon koruması
- Dosya yükleme güvenliği

### Erişim Kontrolü

- Kullanıcı yetkilendirme
- Rol tabanlı erişim
- Oturum yönetimi
- Güvenli bağlantılar

## 🛠️ Geliştirme

### Kod Standartları

- PEP 8 uyumluluğu
- Docstring kullanımı
- Tip kontrolü
- Birim testler

### Geliştirme Ortamı

- Virtual environment
- IDE yapılandırması
- Debug araçları
- Test ortamı

## 📝 Lisans

MIT

streamlit run main.py --theme.base="light" --theme.primaryColor="#2f64b5" --theme.backgroundColor="#dee2e6" --theme.secondaryBackgroundColor="#e9ecef" --theme.textColor="#262730" --theme.font="sans serif"