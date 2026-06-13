import os
import google.generativeai as genai
from llm.base_provider import BaseProvider

class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-flash-lite"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def chat(self, messages: list) -> str:
        # Gemini formatına dönüştür
        gemini_history = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
        
        # Gemini chat API
        chat = self.model.start_chat(history=gemini_history[:-1])
        response = chat.send_message(gemini_history[-1]["parts"][0])
        return response.text

    def summarize(self, text: str) -> str:
        return self.generate(f"Summarize this: {text}")

    def embed(self, text: str) -> list[float]:
        # Placeholder
        return [0.0]
