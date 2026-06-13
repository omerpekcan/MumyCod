import os
import re
from typing import List, Dict, Any
from llm.gemini_provider import GeminiProvider
from core.session_manager import SessionManager
from core.planner import Planner
from indexing.symbol_index import SymbolIndexer
from retrieval.retriever import CodeRetriever
from tools.file_reader import FileReader
from tools.file_tools import write_to_file, read_file
from tools.terminal_tools import execute_command


class MumyCodAgent:
    """
    MumyCod'un ana karar mekanizması (Agent).
    Hafızayı ve LLM sağlayıcısını koordine eder.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        # Yapay zekaya nasıl davranması gerektiğini dikte eden sistem talimatı
        self.system_prompt = (
            "MumyCod: İleri düzeyde, zeki ve yüksek kapasiteli bir AI kodlama asistanısın.\n"
            "Kullanıcıya kodlama yolculuğunda yardım ediyorsun. Yanıtların net, "
            "doğru, üretim için hazır ve çözüm odaklı olmalı. Kod bloklarını her zaman "
            "standart markdown formatında (```csharp vb.) vermeye özen göster. Uzun "
            "ve alakasız açıklamalardan kaçın.\n\n"
            "ARAÇLAR:\n"
            "1. Dosya oluşturmak veya güncellemek için `write_to_file(filepath, content)` aracını kullanabilirsin.\n"
            "2. Mevcut bir dosyayı okumak için `read_file(filepath)` aracını kullanabilirsin.\n"
            "3. Terminal komutu çalıştırmak için `execute_command(command)` aracını kullanabilirsin.\n"
            "4. Kod tabanında arama yapmak için `search_codebase(query)` aracını kullanabilirsin.\n"
            "Bunu kullanmak için yanıtında şu formatı kullan:\n"
            "[TOOL:write_to_file(dosya_yolu, içerik)] veya [TOOL:read_file(dosya_yolu)] veya [TOOL:execute_command(komut)] veya [TOOL:search_codebase(sorgu)]"
        )
        
        # Hafıza şefini başlatıyoruz
        self.session = SessionManager(system_prompt=self.system_prompt)
        
        # Gemini sağlayıcısını başlatıyoruz (API anahtarını ortam değişkeninden alıyoruz)
        api_key = os.getenv("GEMINI_API_KEY")
        self.provider = GeminiProvider(api_key=api_key, model_name=model_name)
        
        # Planlayıcı
        self.planner = Planner()
        
        # Sembol indeksi oluştur
        self.symbol_index = SymbolIndexer().build_symbol_index(".")
        
        # Kod retrieveri
        self.retriever = CodeRetriever(
            self.symbol_index
        )
        
        # Dosya okuyucu
        self.file_reader = FileReader()
        
        # Sohbet geçmişi (Memory)
        self.history = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

    def ask(self, user_input: str) -> str:
        """
        Kullanıcıdan gelen soruyu alır, hafıza geçmişiyle harmanlar,
        yapay zekaya sorar ve cevabı döner.
        """
        if not user_input.strip():
            return "Kanka boş mesaj gönderdin, ne yapacağımı bilemedim. 🤔"
            
        # 1. Kullanıcının mesajını sohbet geçmişine kaydet
        self.history.append(
            {
                "role": "user",
                "content": user_input
            }
        )
        
        # Plan oluştur
        plan = self.planner.plan(user_input)
        
        context_text = ""
        
        if plan["intent"] == "modify_code":
            results = self.retriever.retrieve_relevant_chunks(user_input)
            
            if results:
                # En alakalı sonucu bağlam olarak ekle
                target_file = results[0]["file_path"]
                file_content = results[0]["chunk"]
                
                context_text = f"""
İLGİLİ DOSYA (RAG):
{target_file}

DOSYA İÇERİĞİ:

{file_content}
"""
        
        if context_text:
            self.history.append(
                {
                    "role": "system",
                    "content": context_text
                }
            )
        
        # 2. Sağlayıcı üzerinden yapay zekaya ateşle (Tüm geçmişi gönderiyoruz)
        response = self.provider.chat(self.history)
        
        # 3. Araç kullanımı kontrolü (Tool Calling)
        
        # write_to_file kontrolü
        write_match = re.search(r"\[TOOL:write_to_file\((.*?),\s*(.*?)\)\]", response, re.DOTALL)
        if write_match:
            path = write_match.group(1).strip().strip("'").strip('"')
            content = write_match.group(2).strip().strip("'").strip('"')
            
            # Aracı çalıştır
            tool_result = write_to_file(path, content)
            
            # Sonucu yanıta ekle
            response += f"\n\n[Sistem: {tool_result}]"
            
        # read_file kontrolü
        read_match = re.search(r"\[TOOL:read_file\((.*?)\)\]", response, re.DOTALL)
        if read_match:
            path = read_match.group(1).strip().strip("'").strip('"')
            
            # Aracı çalıştır
            tool_result = read_file(path)
            
            # Sonucu yanıta ekle
            response += f"\n\n[Sistem: {tool_result}]"
            
        # execute_command kontrolü
        cmd_match = re.search(r"\[TOOL:execute_command\((.*?)\)\]", response, re.DOTALL)
        if cmd_match:
            command = cmd_match.group(1).strip().strip("'").strip('"')
            
            # Aracı çalıştır
            tool_result = execute_command(command)
            
            # Sonucu yanıta ekle
            response += f"\n\n[Sistem: {tool_result}]"
            
        # search_codebase kontrolü
        search_match = re.search(r"\[TOOL:search_codebase\((.*?)\)\]", response, re.DOTALL)
        if search_match:
            query = search_match.group(1).strip().strip("'").strip('"')
            
            # Aracı çalıştır
            results = self.retriever.retrieve_relevant_chunks(query)
            
            # Sonuçları formatla
            formatted_results = "\n\n".join([f"Dosya: {r['file_path']}\nİçerik: {r['chunk']}" for r in results])
            tool_result = f"Arama Sonuçları:\n{formatted_results}"
            
            # Sonucu yanıta ekle
            response += f"\n\n[Sistem: {tool_result}]"
        
        # 4. Yapay zekanın verdiği cevabı da sohbet geçmişine kaydet
        self.history.append(
            {
                "role": "assistant",
                "content": response
            }
        )
        
        return response

    def clear_memory(self):
        """Ajanın anlık sohbet hafızasını gıcır gıcır sıfırlar."""
        self.session.reset_session()
        # Geçmişi de sıfırlayalım
        self.history = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]
