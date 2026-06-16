# MumyCod - Otonom Kod Asistanı 🤖

MumyCod, 3 farklı yapay zeka sağlayıcısını (Gemini, Groq, OpenRouter) tek bir çatı altında toplayan, akıllı hata yönetimi ve fallback mekanizmalarına sahip otonom bir kod asistanıdır.

## ✨ Özellikler

- **Çoklu Sağlayıcı Desteği**: Gemini, Groq ve OpenRouter arasında otomatik geçiş
- **Akıllı Hata Yönetimi**: Circuit breaker ve blacklist ile hatalı sağlayıcıları izole eder
- **Rate Limit Yönetimi**: API sınırlarına takıldığında otomatik olarak diğer sağlayıcıya geçer
- **RAG (Retrieval-Augmented Generation)**: Kod tabanınızdan bilgi çekip bağlam sağlar
- **Araç Desteği**: Dosya okuma/yazma, Git işlemleri, terminal komutları, web araması
- **Bellek Yönetimi**: Konuşma geçmişini saklayarak bağlamı korur
- **Web Arayüzü**: Flask ile hazırlanmış kullanıcı dostu arayüz

## 🚀 Başlangıç

### Gereksinimler
- Python 3.8+
- pip (Python paket yöneticisi)
- API anahtarları (Gemini, Groq, OpenRouter)

### Kurulum

1. **Depoyu klonlayın:**
```bash
git clone https://github.com/omerpekcan/MumyCod.git
cd MumyCod

python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
OPENROUTER_API_KEY=your_openrouter_key

python main.py
Tarayıcınızda http://localhost:5000 adresini açın.

MumyCod/
├── llm/                    # Yapay zeka sağlayıcıları
│   ├── base_provider.py    # Temel soyut sınıf
│   ├── gemini_provider.py  # Gemini entegrasyonu
│   ├── groq_provider.py    # Groq entegrasyonu
│   ├── deepseek_provider.py # DeepSeek (Groq üzerinden)
│   └── provider_manager.py # Sağlayıcı yönetimi (fallback, circuit breaker)
├── retrieval/              # RAG sistemi
│   ├── embeddings.py       # Vektör dönüştürme
│   ├── vector_store.py     # Vektör veritabanı
│   ├── retrieve.py         # Bilgi getirme
│   └── reranker.py         # Sonuçları sıralama
├── tools/                  # Araçlar
│   ├── file_tool.py        # Dosya okuma/yazma
│   ├── git_tool.py         # Git işlemleri
│   ├── search_tool.py      # Web araması
│   └── terminal_tool.py    # Terminal komutları
├── memory/                 # Bellek yönetimi
├── ui/                     # Kullanıcı arayüzü
├── templates/              # Flask HTML şablonları
├── main.py                 # Terminal ana uygulaması
├── app.py                  # Web arayüzü uygulaması
├── requirements.txt        # Python bağımlılıkları
├── .env.example            # Örnek ortam değişkenleri
└── README.md               # Bu dosya


🔧 Sağlayıcılar ve Fallback Mekanizması

MumyCod, 3 farklı sağlayıcıyı şu öncelik sırasına göre kullanır:

    Gemini (Birincil)

    Groq (Yedek 1)

    OpenRouter (Yedek 2)

Hata Yönetimi Stratejileri:
Hata Türü	Aksiyon
Rate Limit (429)	Bir sonraki sağlayıcıya geç
Servis Kullanılamıyor (503)	Bir sonraki sağlayıcıya geç
Geçersiz API Anahtarı (401)	Blacklist'e ekle
5'ten fazla hata	Circuit breaker aç (5 dakika bekle)
🛠️ Geliştirme
Test Etme
bash

python test_agent.py       # Ana agent testi
python test_retriever.py   # RAG sistemi testi
python test_groq.py        # Groq bağlantı testi
python debug_system.py     # Sistem debug

Yeni Sağlayıcı Ekleme

    llm/base_provider.py'dan türeyen yeni bir sınıf oluşturun.

    generate(), chat(), summarize(), embed() metotlarını implement edin.

    provider_manager.py'daki providers listesine ekleyin.

🤝 Katkıda Bulunma

    Bu depoyu fork'layın

    Yeni bir branch oluşturun: git checkout -b yeni-ozellik

    Değişikliklerinizi commit'leyin: git commit -m 'Yeni özellik eklendi'

    Branch'inizi push'layın: git push origin yeni-ozellik

    Pull Request oluşturun

📄 Lisans

Bu proje MIT Lisansı ile lisanslanmıştır.
🙏 Teşekkürler

    Google Gemini API

    Groq API

    OpenRouter API

⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!
text



🎯 Neler Ekledim?

    ✅ Proje açıklaması ve özellikler

    ✅ Kurulum adımları (sanal ortam, bağımlılıklar, .env)

    ✅ Kullanım kılavuzu (terminal + web arayüzü)

    ✅ Detaylı proje yapısı (klasör açıklamaları)

    ✅ Sağlayıcı ve hata yönetimi tablosu

    ✅ Test komutları

    ✅ Geliştirme rehberi (yeni provider ekleme)


