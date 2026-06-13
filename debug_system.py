import sys
import os

print("[1/4] Bileşenler yükleniyor...")
try:
    from core.agent import MumyCodAgent
    from retrieval.retriever import CodeRetriever
    print("-> Bileşenler başarıyla yüklendi.")
except Exception as e:
    print(f"-> HATA: Bileşen yükleme başarısız: {e}")
    sys.exit(1)

print("[2/4] Hafıza kontrol ediliyor...")
try:
    retriever = CodeRetriever()
    print(f"-> Hafıza yüklendi. {len(retriever.data)} blok mevcut.")
except Exception as e:
    print(f"-> HATA: Hafıza yükleme başarısız: {e}")
    sys.exit(1)

print("[3/4] Ajan başlatılıyor...")
try:
    agent = MumyCodAgent()
    print("-> Ajan hazır.")
except Exception as e:
    print(f"-> HATA: Ajan başlatılamadı: {e}")
    sys.exit(1)

print("[4/4] Sorgu testi yapılıyor...")
try:
    result = agent.search_codebase("terminal_tools")
    print(f"-> Arama sonucu: {result[:200]}")
except Exception as e:
    print(f"-> HATA: Arama başarısız: {e}")
    sys.exit(1)

print("\n!!! HER ŞEY TIKIRINDA! MumyCod çalışmaya hazır. !!!")