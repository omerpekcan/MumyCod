import os
from google import genai
from llm.base_provider import BaseProvider

class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str = None, model_name: str = "gemini-2.5-flash-lite"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

    def chat(self, messages: list) -> str:
        # Gemini formatına dönüştür
        formatted_messages = []
        for msg in messages:
            # Gemini API'de 'system' rolü genellikle 'user' olarak gönderilir veya model konfigürasyonunda belirtilir.
            # Burada basitlik adına tüm rolleri 'user' veya 'model' olarak eşliyoruz.
            role = "user" if msg["role"] in ["user", "system"] else "model"
            formatted_messages.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        # Yeni SDK'da generate_content tüm geçmişi liste olarak kabul eder
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=formatted_messages
        )
        return response.text

    def summarize(self, text: str) -> str:
        return self.generate(f"Summarize this: {text}")

    def embed(self, text: str) -> list[float]:
        # Placeholder
        return [0.0]
