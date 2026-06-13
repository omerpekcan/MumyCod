import sys
import os
import time

# core klasörünü import yoluna ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.agent import MumyCodAgent

# Ajan nesnesini global tanımlıyoruz
agent = MumyCodAgent()

def run_test(prompt, test_name):
    print(f"\n--- [Test] {test_name} ---")
    print(f"Soru: {prompt}")
    # Ajana soruyu gönder
    cevap = agent.ask(prompt)
    print(f"\nAJANDAN GELEN CEVAP:\n{cevap}")

def test_final():
    # Ajanımıza araçları sadece bu formatta kullanması gerektiğini hatırlatan bir bağlam ekliyoruz
    system_instruction = "ZORUNLU FORMAT: SADECE [TOOL:arac_adi(argumanlar)] formatında cevap ver. Başka hiçbir açıklama metni yazma."

    # 1. Dosya okuma testi
    run_test(f"{system_instruction} [TOOL:read_file(tools/terminal_tools.py)]", "Dosya okuma")
    
    time.sleep(2) 

    # 2. Git yeteneği testi
    run_test(f"{system_instruction} [TOOL:git_commit('Ajanima_git_yeteneği_kazandirdim')]", "Git yeteneği testi")
    
    time.sleep(2) 

    # 3. Yazma testi
    run_test(f"{system_instruction} [TOOL:write_file(test_dosyasi.txt, 'Ajanim_artik_kendi_dosyalarini_yazabiliyor!')]", "Yazma testi")

if __name__ == "__main__":
    test_final()