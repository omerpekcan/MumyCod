import os
from dotenv import load_dotenv
from google import genai
from tenacity import retry, stop_after_attempt, wait_fixed

class ProviderManager:
    def __init__(self):
        load_dotenv()
        self.providers = [
            {"name": "gemini", "api_key": os.environ.get("GEMINI_API_KEY")},
            {"name": "groq", "api_key": os.environ.get("GROQ_API_KEY")},
            {"name": "openrouter", "api_key": os.environ.get("OPENROUTER_API_KEY")}
        ]
        self.model_name = "gemini/gemini-3.1-flash-lite"

    def _call_gemini(self, api_key, prompt):
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

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
                # Diğer sağlayıcılar için buraya ekleme yapılabilir
                
            except Exception as e:
                # 429 hatası veya diğer hatalar durumunda bir sonrakine geç
                print(f"[DEBUG] {provider['name']} başarısız oldu: {str(e)}")
                continue
        
        raise Exception("Tüm sağlayıcılar başarısız oldu.")
