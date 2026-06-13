import sys
import os
import time

# core klasörünü import yoluna ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.agent import MumyCodAgent

# Ajan nesnesini global tanımlıyoruz
agent = MumyCodAgent()

def test_final():
    print("--- Ajan başlatılıyor... ---")
    
    # Test fonksiyonu: Hata kontrolü yapan yardımcı
    def run_test(prompt, description):
        print(f"\n--- [Test] {description} ---")
        print(f"Soru: {prompt}")
        
        # Ajanın ask metodunu çağırıyoruz
        response = agent.ask(prompt)
        
        # Hata kontrolü
        if response.startswith("HATA:"):
            print(f"\n!!! HATA ALINDI !!!")
            print(f"Ajanın döndürdüğü hata mesajı: {response}")
            print("Not: Hatanın kaynağını (sağlayıcı ve kod) yukarıdaki [DEBUG] loglarında görebilirsiniz.")
        else:
            print("\nAJANDAN GELEN CEVAP:")
            print("="*30)
            print(response)
            print("="*30)
        return response

    # 1. Dosya okuma testi
    run_test("[TOOL:read_file(tools/terminal_tools.py)] Bu dosyanın içeriğini ve amacını bana Türkçe özetle.", "Dosya okuma")
    
    time.sleep(2) 

    # 2. Git yeteneği testi
    run_test("[TOOL:git_commit('Ajanıma git yeteneği kazandırdım')]", "Git yeteneği testi")
    
    time.sleep(2) 

    # 3. Yazma testi
    run_test("[TOOL:write_file(test_dosyasi.txt, 'Ajanım artık kendi dosyalarını yazabiliyor!')]", "Yazma testi")

if __name__ == "__main__":
    test_final()
