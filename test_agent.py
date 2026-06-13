import sys
import os
import time  # API limitine takılmamak için zamanlayıcı ekledik

# core klasörünü import yoluna ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.agent import MumyCodAgent

# Ajan nesnesini global tanımlıyoruz
agent = MumyCodAgent()

def test_final():
    print("--- Ajan başlatılıyor... ---")
    
    # 1. Dosya okuma testi
    print("\n--- [Test 1] Dosya okuma ---")
    output = agent.ask("[TOOL:read_file(tools/terminal_tools.py)] Bu dosyanın içeriğini ve amacını bana Türkçe özetle.")
    print("AJANDAN GELEN CEVAP:\n" + "="*30 + "\n" + output + "\n" + "="*30)
    
    # API'nin nefes alması için kısa bir bekleme
    time.sleep(5) 

    # 2. Git yeteneği testi
    print("\n--- [Test 2] Git yeteneği testi ---")
    response = agent.ask("[TOOL:git_commit('Ajanıma git yeteneği kazandırdım')]")
    print(f"Git çıktısı: {response}")
    
    time.sleep(5) 

    # 3. Yazma testi
    print("\n--- [Test 3] Yazma testi ---")
    response = agent.ask("[TOOL:write_file(test_dosyasi.txt, 'Ajanım artık kendi dosyalarını yazabiliyor!')]")
    print(f"Yazma sonucu: {response}")

if __name__ == "__main__":
    test_final()