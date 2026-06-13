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

    def _execute_tool(self, tool_name: str, tool_args: str) -> str:
        """Araçları çalıştıran yardımcı metod."""
        print(f"[DEBUG] Araç çalıştırılıyor: {tool_name}, Argümanlar: {tool_args}")
        
        if tool_name == "write_file":
            # write_file için argümanları virgülle ayır (ilk virgül dosya yolu, sonrası içerik)
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

    def ask(self, user_query: str) -> str:
        print(f"\n[DEBUG] --- ask() metodu çağrıldı ---")
        print(f"[DEBUG] Soru: {user_query}")
        
        try:
            # 1. LLM'e sor
            print("[DEBUG] LLM'e istek gönderiliyor...")
            response_text = self.provider_manager.ask(user_query)
            print(f"[DEBUG] LLM'den yanıt alındı.")
            
            # 2. Araçları parse et
            # Esnek regex: [TOOL:isim(argümanlar)]
            # re.DOTALL ile çok satırlı içerikleri yakalıyoruz
            tool_match = re.search(r"\[TOOL:(\w+)\((.*?)\)\]", response_text, re.DOTALL)
            
            if tool_match:
                tool_name, tool_args = tool_match.groups()
                
                # Argümanları temizle (tırnakları ve olası etiketleri kaldır)
                # Sadece dış tırnakları değil, içerideki olası path= gibi etiketleri de temizlemek için
                # basit bir temizleme yapıyoruz
                cleaned_args = tool_args.strip().strip("'").strip('"')
                
                print(f"[DEBUG] Tetiklenen Araç: {tool_name}")
                print(f"[DEBUG] Temizlenmiş Argümanlar: {cleaned_args}")
                
                # Aracı çalıştır
                tool_result = self._execute_tool(tool_name, cleaned_args)
                print(f"[DEBUG] Araç sonucu: {tool_result[:100]}...")
                
                # 3. Sonucu LLM'e geri gönder ve özetlet
                final_prompt = f"Kullanıcı sorusu: '{user_query}'.\n\nAraç '{tool_name}' çalıştırıldı. Sonuç:\n{tool_result}\n\nLütfen bu sonucu kullanıcıya özetle."
                print("[DEBUG] Araç sonucu LLM'e özetletiliyor...")
                final_response = self.provider_manager.ask(final_prompt)
                return final_response
            
            print("[DEBUG] Araç tespit edilmedi, doğrudan yanıt dönülüyor.")
            return response_text
            
        except Exception as e:
            print("[DEBUG] !!! HATA YAKALANDI !!!")
            traceback.print_exc()
            return f"HATA: {str(e)}"
