import re
import os
import traceback
from llm.gemini_provider import GeminiProvider
from tools.file_tools import read_file, write_to_file
from tools.terminal_tools import execute_command
from retrieval.retriever import CodeRetriever

class MumyCodAgent:
    def __init__(self):
        print("[DEBUG] MumyCodAgent başlatılıyor...")
        self.provider = GeminiProvider()
        # brain.json dosyasının doğru yolda olduğundan emin oluyoruz
        self.retriever = CodeRetriever(brain_path="memory/brain.json")
        self.history = []
        print("[DEBUG] MumyCodAgent başarıyla başlatıldı.")

    def ask(self, user_query: str) -> str:
        print(f"\n[DEBUG] --- ask() metodu çağrıldı ---")
        print(f"[DEBUG] Soru: {user_query}")
        
        try:
            # 1. LLM'e sor
            print("[DEBUG] LLM'e istek gönderiliyor (provider.chat)...")
            response = self.provider.chat(user_query)
            
            # Nesne kontrolü
            text = response.text if hasattr(response, "text") else str(response)
            print(f"[DEBUG] LLM'den yanıt alındı. Yanıt uzunluğu: {len(text)} karakter.")
            
            # 2. Araçları parse et (Daha esnek regex)
            tool_match = re.search(r"\[TOOL:(\w+)\((.*?)\)\]", text)
            if tool_match:
                tool_name, tool_args = tool_match.groups()
                # Argümanlardaki tırnakları temizle
                tool_args = tool_args.strip("'").strip('"')
                
                print(f"[DEBUG] Araç tespit edildi: {tool_name}, Argümanlar: {tool_args}")
                
                # Araçları işle
                if tool_name == "read_file":
                    print(f"[DEBUG] read_file aracı çalıştırılıyor...")
                    res = read_file(tool_args)
                elif tool_name == "execute_command":
                    print(f"[DEBUG] execute_command aracı çalıştırılıyor...")
                    res = execute_command(tool_args)
                elif tool_name == "search_codebase":
                    print(f"[DEBUG] search_codebase aracı çalıştırılıyor...")
                    results = self.retriever.retrieve_relevant_chunks(tool_args)
                    res = "\n".join([f"Dosya: {r['file_path']}\nİçerik: {r['text']}" for r in results])
                else:
                    res = f"Bilinmeyen araç: {tool_name}"
                    print(f"[DEBUG] {res}")
                
                print(f"[DEBUG] Araç sonucu: {res[:100]}...")
                return res
            
            print("[DEBUG] Araç tespit edilmedi, doğrudan yanıt dönülüyor.")
            return text
            
        except Exception as e:
            print("[DEBUG] !!! HATA YAKALANDI !!!")
            traceback.print_exc()
            return f"HATA: {str(e)}"
