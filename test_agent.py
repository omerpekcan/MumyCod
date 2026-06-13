from core.agent import MumyCodAgent

def test_file_writing():
    # Ajanı başlat
    agent = MumyCodAgent()
    
    print("--- Dosya Yazma Testi ---")
    prompt = "Bana 'test_output.txt' adında bir dosya oluştur ve içine 'Merhaba Mumy, bu dosya otonom MumyCod ajanı tarafından yazıldı!' metnini kaydet."
    print(f"Soru: {prompt}")
    response = agent.ask(prompt)
    print(f"Cevap: {response}")

if __name__ == "__main__":
    test_file_writing()
