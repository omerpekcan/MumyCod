import os
from dotenv import load_dotenv
from core.agent import MumyCodAgent

def main():
    # .env dosyasındaki GROQ_API_KEY'i sisteme yüklüyoruz
    load_dotenv()
    
    print("🧟‍♂️ MumyCod Arka Plan Motoru Başlatılıyor...")
    try:
        # Ajanımızı ayağa kaldırıyoruz
        agent = MumyCodAgent()
        print("✅ Motor başarıyla ateşlendi! Groq bağlantısı hazır.")
        print("-" * 50)
        
        # İlk test sorumuzu soruyoruz
        soru = "Selam MumyCod! Ben senin geliştiricin Mumy. Bana C#'ta hızlıca ekrana yazı yazdıran kodu verir misin?"
        print(f"Kullanıcı: {soru}\n")
        
        print("🤖 MumyCod Düşünüyor ve Cevap Üretiyor...\n")
        cevap = agent.ask(soru)
        
        print(f"MumyCod: {cevap}")
        print("-" * 50)
        print("🎉 TEST BAŞARILI! Yapay zeka canavar gibi cevap verdi kanka.")
        
    except Exception as e:
        print(f"🚨 Test Sırasında Hata Çıktı Kanka: {str(e)}")

if __name__ == "__main__":
    main()