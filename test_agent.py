import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.agent import MumyCodAgent

def test_final():
    print("--- Ajan başlatılıyor... ---")
    agent = MumyCodAgent()
    
    # 1. Dosya okuma testi
    print("\n--- Araç çağrılıyor (read_file)... ---")
    output = agent.ask("[TOOL:read_file(tools/terminal_tools.py)] Bu dosyanın içeriğini ve amacını bana Türkçe özetle.")
    
    print("\n" + "="*30)
    print("AJANDAN GELEN CEVAP:")
    print("="*30)
    print(output)
    print("="*30)

    # 2. Git yeteneği testi
    print("\n--- Git yeteneği testi ---")
    response = agent.ask("[TOOL:git_commit('Ajanıma git yeteneği kazandırdım')]")
    print(f"Git çıktısı: {response}")

if __name__ == "__main__":
    test_final()

# Test: Dosyaya yazma yeteneği
response = agent.ask("[TOOL:write_file(test_dosyasi.txt, 'Ajanım artık kendi dosyalarını yazabiliyor!')]")
print(f"Yazma sonucu: {response}")