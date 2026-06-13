from core.agent import MumyCodAgent

def test_file_operations():
    # Ajanı başlat
    agent = MumyCodAgent()
    
    print("--- 1. Dosya Okuma Testi ---")
    prompt1 = "Bana 'test_output.txt' dosyasının içeriğini oku."
    print(f"Soru: {prompt1}")
    response1 = agent.ask(prompt1)
    print(f"Cevap: {response1}\n")
    
    print("--- 2. Dosya Güncelleme Testi ---")
    prompt2 = "'test_output.txt' dosyasının içeriğini 'Yeni otonom okuma ve yazma testi başarılı!' olarak güncelle."
    print(f"Soru: {prompt2}")
    response2 = agent.ask(prompt2)
    print(f"Cevap: {response2}\n")
    
    print("--- 3. Terminal Komut Testi ---")
    prompt3 = "Bana projenin kök dizinindeki (C:\\Users\\Mumy\\MumyCod) dosyaları listele."
    print(f"Soru: {prompt3}")
    response3 = agent.ask(prompt3)
    print(f"Cevap: {response3}")

if __name__ == "__main__":
    test_file_operations()
