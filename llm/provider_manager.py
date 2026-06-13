import os
from dotenv import load_dotenv
from google import genai
from groq import Groq
from openai import OpenAI

class ProviderManager:
    def __init__(self):
        load_dotenv()
        # API anahtarlarını çekiyoruz
        self.providers = [
            {"name": "gemini", "api_key": os.environ.get("GEMINI_API_KEY")},
            {"name": "groq", "api_key": os.environ.get("GROQ_API_KEY")},
            {"name": "openrouter", "api_key": os.environ.get("OPENROUTER_API_KEY")}
        ]
        self.model_name = "gemini-3.5-flash"

    def _call_gemini(self, api_key, prompt):
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

    def _call_groq(self, api_key, prompt):
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content

    def _call_openrouter(self, api_key, prompt):
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-lite-preview:free",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content

    def ask(self, prompt: str) -> str:
        """
        Sağlayıcılar arasında döngü kurar ve hata durumunda bir sonrakine geçer.
        """
        for provider in self.providers:
            if not provider["api_key"]:
                continue
            
            try:
                print(f"[DEBUG] {provider['name']} ile deneniyor...")
                if provider["name"] == "gemini":
                    return self._call_gemini(provider["api_key"], prompt)
                elif provider["name"] == "groq":
                    return self._call_groq(provider["api_key"], prompt)
                elif provider["name"] == "openrouter":
                    return self._call_openrouter(provider["api_key"], prompt)
            
            except Exception as e:
                print(f"[DEBUG] {provider['name']} başarısız oldu: {str(e)}")
                continue
        
        raise Exception("Tüm sağlayıcılar başarısız oldu.")