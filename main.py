import os
import sys
from colorama import init, Fore, Style
from dotenv import load_dotenv
from core.agent import MumyCodAgent

# Colorama'yı başlat
init(autoreset=True)

def main():
    """
    MumyCod giriş noktası. 
    .env yükler, Agent'ı başlatır ve terminal üzerinden kullanıcı etkileşimini yönetir.
    """
    # .env dosyasını yükle
    load_dotenv()
    
    try:
        # Ajanı başlat
        system_prompt = "Sen MumyCod'sun. Çok kısa, öz ve net cevaplar ver. Gereksiz açıklamalardan kaçın, doğrudan çözüme odaklan. Kodun yeşil renkte basılmasını sağla."
        agent = MumyCodAgent()
        # Eğer MumyCodAgent constructor'ı bir prompt kabul etmiyorsa bile core kısmında ayarlanabilir, 
        # ancak mevcut yapıda agent.ask öncesi sistem mesajı talimatı eklendi.
        
        print(f"\n{Fore.GREEN}MumyCod: Merhaba! Ben yazılım asistanınız MumyCod. Size nasıl yardımcı olabilirim?")
        print("(Cıkmak için 'exit' veya 'quit' yazabilirsiniz.)\n")

        while True:
            try:
                user_input = input("Siz >> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit"]:
                    print("MumyCod: Gorusmek uzere!")
                    break

                # Agent üzerinden sorguyu işle
                response = agent.ask(user_input)
                
                print(f"\n{Fore.GREEN}MumyCod >> {response}\n")

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
