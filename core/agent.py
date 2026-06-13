import os
import re
from typing import List, Dict, Any
from llm.deepseek_provider import DeepSeekProvider
from core.session_manager import SessionManager
from core.planner import Planner
from indexing.symbol_index import SymbolIndexer
from retrieval.retriever import CodeRetriever
from tools.file_reader import FileReader
from tools.file_tools import write_to_file


class MumyCodAgent:
    """
    MumyCod'un ana karar mekanizması (Agent).
    Hafızayı ve LLM sağlayıcısını koordine eder.
    """
    
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        # Yapay zekaya nasıl davranması gerektiğini dikte eden sistem talimatı
        self.system_prompt = (
            "MumyCod: İleri düzeyde, zeki ve yüksek kapasiteli bir AI kodlama asistanısın.\n"
            "Kullanıcıya kodlama yolculuğunda yardım ediyorsun. Yanıtların net, "
            "doğru, üretim için hazır ve çözüm odaklı olmalı. Kod bloklarını her zaman "
            "standart markdown formatında (```csharp vb.) vermeye özen göster. Uzun "
            "ve alakasız açıklamalardan kaçın.\n\n"
            "ARAÇLAR:\n"
            "Dosya oluşturmak veya güncellemek için `write_to_file(filepath, content)` aracını kullanabilirsin.\n"
            "Bunu kullanmak için yanıtında şu formatı kullan: [TOOL:write_to_file(dosya_yolu, içerik)]"
        )
        
        # Hafıza şefini başlatıyoruz
        self.session = SessionManager(system_prompt=self.system_prompt)
        
        # Varsayılan olarak Groq üzerindeki Llama/DeepSeek sağlayıcımızı bağlıyoruz
        self.provider = DeepSeekProvider(model_name=model_name)
        
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
            results = self.retriever.retrieve(user_input)
            
            if results:
                target_file = results[0]
                
                file_content = self.file_reader.read(
                    target_file
                )
                
                context_text = f"""
İLGİLİ DOSYA:
{target_file}

DOSYA İÇERİĞİ:

{file_content[:4000]}
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
        # [TOOL:write_to_file(path, content)] formatını ara
        tool_match = re.search(r"\[TOOL:write_to_file\((.*?),\s*(.*?)\)\]", response, re.DOTALL)
        
        if tool_match:
            path = tool_match.group(1).strip().strip("'").strip('"')
            content = tool_match.group(2).strip().strip("'").strip('"')
            
            # Aracı çalıştır
            tool_result = write_to_file(path, content)
            
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
