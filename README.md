# Finansal Performans Analiz Paneli

Finansal verilerin analizi, görselleştirilmesi ve raporlanması için geliştirilmiş bir Streamlit uygulaması.

## 🚀 Özellikler

- 📊 Veri Görüntüleme ve Analiz

  - Yüksek performanslı veri görüntüleme (st.data_editor kullanımı)
  - Sayfalama desteği (büyük veri setleri için)
  - İsteğe bağlı stil uygulama
  - Sabit sütun desteği
  - Excel formatında dışa aktarım

- 🔍 Filtreleme ve Gruplama

  - Dinamik filtreleme
  - Çoklu grup analizi
  - Kategori bazlı karşılaştırmalar

- 📈 Görselleştirme

  - Trend analizi
  - Kategori bazlı grafikler
  - Karşılaştırmalı analizler
  - Pivot tablo desteği

- 📑 Raporlama
  - PDF rapor oluşturma
  - ZIP formatında toplu indirme
  - Özelleştirilebilir rapor formatları

## 🛠️ Teknik Özellikler

- **Performans Optimizasyonları**

  - Büyük veri setleri için sayfalama
  - İsteğe bağlı stil uygulama
  - Optimize edilmiş veri görüntüleme
  - Lazy loading desteği

- **Veri İşleme**

  - Pandas DataFrame entegrasyonu
  - Otomatik veri tipi algılama
  - Sayısal değer formatlaması
  - Hata yönetimi

- **Kullanıcı Arayüzü**
  - Responsive tasarım
  - Kolay navigasyon
  - Sezgisel filtreleme
  - Türkçe arayüz

## 📦 Kurulum

1. Gerekli paketleri yükleyin:

```bash
git clone [your-repository-url]
cd Finance-Report
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## 🎯 Kullanım

1. Excel dosyasını yükleyin
2. Filtreleri ayarlayın
3. Analiz seçeneklerini belirleyin
4. Raporları oluşturun ve indirin

## 🔧 Performans İpuçları

- Büyük veri setleri için sayfalama kullanın
- Stil uygulamayı sadece gerektiğinde etkinleştirin
- Gereksiz sütunları filtreleyin
- Önbelleği temizleyin gerektiğinde

## 📝 Lisans

MIT

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

streamlit run main.py --server.port 8080 --theme.base="light" --theme.primaryColor="#6eb52f" --theme.backgroundColor="#f0f0f5" --theme.secondaryBackgroundColor="#e0e0ef" --theme.textColor="#262730" --theme.font="sans serif"
