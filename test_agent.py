import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.agent import MumyCodAgent

def test_final():
    print("--- Ajan başlatılıyor... ---")
    agent = MumyCodAgent()
    
    # Burada cevabı alıp bir değişkene atıyoruz
    print("--- Araç çağrılıyor (read_file)... ---")
    output = agent.ask("[TOOL:read_file(tools/terminal_tools.py)] Bu dosyanın içeriğini ve amacını bana Türkçe özetle.")
    
    # İşte burası kritik: Eğer bir çıktı geldiyse bunu terminale ZORLA bastırıyoruz
    print("\n" + "="*30)
    print("AJANDAN GELEN CEVAP:")
    print("="*30)
    print(output)
    print("="*30)

if __name__ == "__main__":
    test_final()

    # Ajanı test etmek için:
print("--- Git yeteneği testi ---")
response = agent.ask("[TOOL:git_commit('Ajanıma git yeteneği kazandırdım')]")
print(f"Git çıktısı: {response}")