import os
import sys
from dotenv import load_dotenv
from core.agent import MumyCodAgent

def main():
    """
    MumyCod giriş noktası. 
    .env yükler, Agent'ı başlatır ve terminal üzerinden kullanıcı etkileşimini yönetir.
    """
    # .env dosyasını yükle
    load_dotenv()
    
    try:
        # Ajanı başlat
        agent = MumyCodAgent()
        print("\n🧟 MumyCod: Merhaba! Ben yazılım asistanınız MumyCod. Size nasıl yardımcı olabilirim?")
        print("(Çıkmak için 'exit' veya 'quit' yazabilirsiniz.)\n")

        while True:
            try:
                user_input = input("Siz >> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit", "çıkış"]:
                    print("MumyCod: Görüşmek üzere! 🧟")
                    break

                # Agent üzerinden sorguyu işle
                response = agent.ask(user_input)
                
                print(f"\nMumyCod >> {response}\n")

            except KeyboardInterrupt:
                print("\n\nMumyCod: İşlem kullanıcı tarafından kesildi. Görüşmek üzere!")
                break
            except Exception as e:
                print(f"\n[SİSTEM HATASI] Bir hata oluştu: {str(e)}\n")

    except Exception as e:
        print(f"Başlatma hatası: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
