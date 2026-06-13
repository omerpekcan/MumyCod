from core.agent import MumyCodAgent

def test_memory():
    # Ajanı başlat
    agent = MumyCodAgent()
    
    print("--- 1. Soru ---")
    question1 = "Benim adım Mumy, sen kimsin?"
    print(f"Soru: {question1}")
    response1 = agent.ask(question1)
    print(f"Cevap: {response1}\n")
    
    print("--- 2. Soru ---")
    question2 = "Az önce sana adımı ne olarak söylemiştim?"
    print(f"Soru: {question2}")
    response2 = agent.ask(question2)
    print(f"Cevap: {response2}")

if __name__ == "__main__":
    test_memory()
