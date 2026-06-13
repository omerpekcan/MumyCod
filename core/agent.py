import re
import os
import traceback
from llm.gemini_provider import GeminiProvider
from tools.file_tools import read_file, write_file
from tools.terminal_tools import execute_command
from tools.git_tools import GitTools
from retrieval.retriever import CodeRetriever

class MumyCodAgent:
    def __init__(self):
        print("[DEBUG] MumyCodAgent başlatılıyor...")
        self.provider = GeminiProvider()
        # brain.json dosyasının doğru yolda olduğundan emin oluyoruz
        self.retriever = CodeRetriever(brain_path="memory/brain.json")
        self.git_tools = GitTools()
        self.history = []
        
        # Yapay zekaya nasıl davranması gerektiğini dikte eden sistem talimatı
        self.system_prompt = (
            "MumyCod: İleri düzeyde, zeki ve yüksek kapasiteli bir AI kodlama asistanısın.\n"
            "Kullanıcıya kodlama yolculuğunda yardım ediyorsun. Yanıtların net, "
            "doğru, üretim için hazır ve çözüm odaklı olmalı. Kod bloklarını her zaman "
            "standart markdown formatında (```csharp vb.) vermeye özen göster. Uzun "
            "ve alakasız açıklamalardan kaçın.\n\n"
            "ARAÇLAR:\n"
            "1. Dosya oluşturmak veya güncellemek için `write_file(filepath, content)` aracını kullanabilirsin.\n"
            "2. Mevcut bir dosyayı okumak için `read_file(filepath)` aracını kullanabilirsin.\n"
            "3. Terminal komutu çalıştırmak için `execute_command(command)` aracını kullanabilirsin.\n"
            "4. Kod tabanında arama yapmak için `search_codebase(query)` aracını kullanabilirsin.\n"
            "5. Git commit yapmak için `git_commit(message)` aracını kullanabilirsin.\n"
            "6. Git push yapmak için `git_push()` aracını kullanabilirsin.\n"
            "Bunu kullanmak için yanıtında şu formatı kullan:\n"
            "[TOOL:write_file(dosya_yolu, içerik)] veya [TOOL:read_file(dosya_yolu)] veya [TOOL:execute_command(komut)] veya [TOOL:search_codebase(sorgu)] veya [TOOL:git_commit(mesaj)] veya [TOOL:git_push()]"
        )
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
            # write_file için özel regex (iki argümanlı)
            write_match = re.search(r"\[TOOL:write_file\((.*?),\s*(.*?)\)\]", text, re.DOTALL)
            if write_match:
                path, content = write_match.groups()
                path = path.strip("'").strip('"')
                content = content.strip("'").strip('"')
                print(f"[DEBUG] Araç tespit edildi: write_file, Dosya: {path}")
                res = write_file(path, content)
                return res

            # Diğer araçlar için regex
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
                elif tool_name == "git_commit":
                    print(f"[DEBUG] git_commit aracı çalıştırılıyor...")
                    res = self.git_tools.git_commit(tool_args)
                elif tool_name == "git_push":
                    print(f"[DEBUG] git_push aracı çalıştırılıyor...")
                    res = self.git_tools.git_push()
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
