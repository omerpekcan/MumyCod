import re
import os
import traceback
from llm.provider_manager import ProviderManager
from tools.file_tools import read_file, write_file
from tools.terminal_tools import execute_command
from tools.git_tools import GitTools
from retrieval.retriever import CodeRetriever

class MumyCodAgent:
    def __init__(self):
        print("[DEBUG] MumyCodAgent başlatılıyor...")
        # ProviderManager ile çoklu sağlayıcı desteği aktif
        self.provider_manager = ProviderManager()
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

    def _execute_tool(self, tool_call: str) -> str:
        """
        Basit string ayrıştırma ile araçları çalıştırır.
        tool_call formatı: name(args)
        """
        try:
            # name(args) -> name, args
            if "(" not in tool_call or ")" not in tool_call:
                return "Hata: Geçersiz araç formatı."
            
            tool_name = tool_call.split('(')[0].strip()
            tool_args = tool_call.split('(', 1)[1].rsplit(')', 1)[0].strip()
            
            print(f"[DEBUG] Tetiklenen Araç: {tool_name}")
            print(f"[DEBUG] Temizlenmiş Argümanlar: {tool_args}")
            
            if tool_name == "write_file":
                parts = tool_args.split(',', 1)
                if len(parts) == 2:
                    path = parts[0].strip().strip("'").strip('"')
                    content = parts[1].strip().strip("'").strip('"')
                    return write_file(path, content)
                return "Hata: write_file için dosya_yolu ve içerik gerekli."
            
            elif tool_name == "read_file":
                return read_file(tool_args.strip("'").strip('"'))
            
            elif tool_name == "execute_command":
                return execute_command(tool_args.strip("'").strip('"'))
            
            elif tool_name == "search_codebase":
                results = self.retriever.retrieve_relevant_chunks(tool_args.strip("'").strip('"'))
                return "\n".join([f"Dosya: {r['file_path']}\nİçerik: {r['text']}" for r in results])
            
            elif tool_name == "git_commit":
                return self.git_tools.git_commit(tool_args.strip("'").strip('"'))
            
            elif tool_name == "git_push":
                return self.git_tools.git_push()
            
            return f"Bilinmeyen araç: {tool_name}"
            
        except Exception as e:
            return f"Araç çalıştırılırken hata oluştu: {str(e)}"

    def ask(self, user_query: str) -> str:
        print(f"\n[DEBUG] --- ask() metodu çağrıldı ---")
        print(f"[DEBUG] Soru: {user_query}")
        
        try:
            # 1. LLM'e sor
            print("[DEBUG] LLM'e istek gönderiliyor...")
            response = self.provider_manager.ask(user_query)
            print(f"[DEBUG] LLM'den gelen ham cevap: {response}")
            
            # 2. Araçları basitçe parse et
            if "[TOOL:" in response:
                try:
                    # [TOOL:name(args)] -> name(args)
                    tool_call = response.split("[TOOL:")[1].split("]")[0]
                    
                    # Aracı çalıştır
                    result = self._execute_tool(tool_call)
                    
                    # 3. Sonucu LLM'e geri gönder ve özetlet
                    final_prompt = f"Kullanıcı sorusu: '{user_query}'.\n\nAraç çalıştırıldı. Sonuç:\n{result}\n\nLütfen bu sonucu kullanıcıya özetle."
                    print("[DEBUG] Araç sonucu LLM'e özetletiliyor...")
                    final_response = self.provider_manager.ask(final_prompt)
                    return final_response
                except Exception as e:
                    print(f"[DEBUG] Araç ayrıştırma hatası: {e}")
                    return f"Araç çalıştırılamadı: {str(e)}"
            
            print("[DEBUG] Araç tespit edilmedi, doğrudan yanıt dönülüyor.")
            return response
            
        except Exception as e:
            print("[DEBUG] !!! HATA YAKALANDI !!!")
            traceback.print_exc()
            return f"HATA: {str(e)}"
