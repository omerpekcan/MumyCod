import os
from typing import List, Dict, Any
from llm.deepseek_provider import DeepSeekProvider
from core.session_manager import SessionManager

class MumyCodAgent:
    """
    MumyCod'un ana karar mekanizması (Agent).
    Hafızayı ve LLM sağlayıcısını koordine eder.
    """
    
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        # Yapay zekaya nasıl davranması gerektiğini dikte eden sistem talimatı
        self.system_prompt = (
            "Sen MumyCod adında, terminal tabanlı çalışan otonom bir yazılım ajanısın.\n"
            "Kullanıcıya kodlama yolculuğunda yardım ediyorsun. Yanıtların net, "
            "doğru ve çözüm odaklı olmalı. Kod bloklarını her zaman standart markdown "
            "formatında (```csharp vb.) vermeye özen göster."
        )
        
        # Hafıza şefini başlatıyoruz
        self.session = SessionManager(system_prompt=self.system_prompt)
        
        # Varsayılan olarak Groq üzerindeki Llama/DeepSeek sağlayıcımızı bağlıyoruz
        self.provider = DeepSeekProvider(model_name=model_name)

    def ask(self, user_input: str) -> str:
        """
        Kullanıcıdan gelen soruyu alır, hafıza geçmişiyle harmanlar,
        yapay zekaya sorar ve cevabı döner.
        """
        if not user_input.strip():
            return "Kanka boş mesaj gönderdin, ne yapacağımı bilemedim. 🤔"
            
        # 1. Kullanıcının mesajını anlık hafızaya kaydet
        self.session.add_user_message(user_input)
        
        # 2. Sistem promptu dahil tüm geçmişi paketle
        full_history = self.session.get_messages()
        
        # 3. Sağlayıcı üzerinden yapay zekaya ateşle
        # İleride context_manager yazdığımızda bu geçmişi kırpıp göndereceğiz kanka!
        response = self.provider.generate_response(full_history)
        
        # 4. Yapay zekanın verdiği cevabı da hafızaya kaydet (Süreklilik için çok kritik)
        self.session.add_agent_message(response)
        
        return response

    def clear_memory(self):
        """Ajanın anlık sohbet hafızasını gıcır gıcır sıfırlar."""
        self.session.reset_session()