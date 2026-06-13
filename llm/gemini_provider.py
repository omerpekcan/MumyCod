import os
from dotenv import load_dotenv
from google import genai
from llm.base_provider import BaseProvider

class GeminiProvider(BaseProvider):
    def __init__(self):
        load_dotenv()
        
        # API anahtarını ortam değişkenlerinden al
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            print("API anahtarı .env dosyasından okunamadı!")
            
        # Yeni google.genai SDK kullanımı
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash"
        
        # Model konfigürasyonu (tools aktif)
        self.config = {
            "tools": [] # Araçlar burada tanımlanabilir
        }

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=self.config
        )
        return response.text

    def chat(self, history_or_prompt) -> str:
        # Eğer gelen veri düz bir string ise direkt üret ve dön
        if isinstance(history_or_prompt, str):
            return self.generate(history_or_prompt)
            
        # Gemini formatına dönüştür
        formatted_contents = []
        for message in history_or_prompt:
            # 'system' veya 'user' rollerini 'user' olarak, 'assistant'ı 'model' olarak eşle
            role = "user" if message.get("role") in ["user", "system"] else "model"
            
            # İçeriği al
            text = message.get("content") or str(message.get("parts", ""))
            formatted_contents.append({"role": role, "parts": [{"text": text}]})
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=formatted_contents,
            config=self.config
        )
        return response.text

    def summarize(self, text: str) -> str:
        return self.generate(f"Summarize this: {text}")

    def embed(self, text: str) -> list[float]:
        # Embedding için ayrı bir model veya endpoint gerekebilir, şimdilik placeholder
        return [0.0]
