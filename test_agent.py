from core.agent import MumyCodAgent

def test_agent_workflow():
    # Ajanı başlat
    agent = MumyCodAgent()
    
    print("--- Ajan İş Akışı Testi: Kod Analizi ve İyileştirme ---")
    prompt = (
        "Projedeki 'tools/terminal_tools.py' dosyasını oku. "
        "İçindeki kod yapısını incele, Windows encoding (karakter kodlama) yönetiminin "
        "doğru yapılıp yapılmadığını kontrol et ve eğer kodda iyileştirilecek bir yer varsa "
        "dosyayı 'write_to_file' kullanarak güncelle. Sonucu bana raporla."
    )
    
    print(f"Soru: {prompt}\n")
    response = agent.ask(prompt)
    print(f"Cevap:\n{response}")

if __name__ == "__main__":
    test_agent_workflow()
