from core.agent import MumyCodAgent

def test_agent_workflow():
    # Ajanı başlat
    agent = MumyCodAgent()
    
    print("--- Ajan İş Akışı Testi: Çok Adımlı Yazılım Geliştirme ---")
    prompt = (
        "Lütfen 'workspace' dizini altında 'todo_app.py' adında bir Python dosyası oluştur. "
        "İçine görev ekleme, listeleme ve silme özelliklerine sahip çalışan bir CLI Todo uygulaması kodu yaz. "
        "Ardından 'execute_command' aracını kullanarak bu yeni dosyayı çalıştır ve uygulamanın hatasız çalıştığını bana raporla."
    )
    
    print(f"Soru: {prompt}\n")
    response = agent.ask(prompt)
    print(f"Cevap:\n{response}")

if __name__ == "__main__":
    test_agent_workflow()
