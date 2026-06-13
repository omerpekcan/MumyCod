import os
import time
from dotenv import load_dotenv
from google import genai
from groq import Groq
from openai import OpenAI

class ProviderManager:
    def __init__(self):
        load_dotenv()
        self.blacklist = set()
        self.providers = [
            {"name": "gemini", "api_key": os.environ.get("GEMINI_API_KEY")},
            {"name": "groq", "api_key": os.environ.get("GROQ_API_KEY")},
            {"name": "openrouter", "api_key": os.environ.get("OPENROUTER_API_KEY")}
        ]
        
        # İstemcileri __init__ içinde başlatıyoruz
        self.client_gemini = genai.Client(api_key=os.environ.get("GEMINI_API_KEY")) if os.environ.get("GEMINI_API_KEY") else None
        self.client_groq = Groq(api_key=os.environ.get("GROQ_API_KEY")) if os.environ.get("GROQ_API_KEY") else None
        self.client_openrouter = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ.get("OPENROUTER_API_KEY")) if os.environ.get("OPENROUTER_API_KEY") else None

    def _handle_error(self, e, provider_name):
        """Hata türünü analiz eder ve aksiyon belirler."""
        # SDK'lardan gelen hata kodlarını yakalamaya çalışıyoruz
        status_code = getattr(e, 'status_code', getattr(e, 'code', 0))
        
        if status_code == 429:
            print(f"[DEBUG] {provider_name} 429 (Quota) hatası verdi. 2 saniye bekleniyor...")
            time.sleep(2)
            return "RETRY"
        elif status_code in [401, 404]:
            print(f"[DEBUG] {provider_name} {status_code} hatası verdi. Blacklist'e alınıyor.")
            self.blacklist.add(provider_name)
            return "BLACKLIST"
        
        print(f"[DEBUG] {provider_name} beklenmedik hata: {str(e)}")
        return "FAIL"

    def ask(self, prompt: str) -> str:
        """
        Sağlayıcılar arasında döngü kurar ve hata durumunda bir sonrakine geçer.
        """
        for provider in self.providers:
            if provider["name"] in self.blacklist or not provider["api_key"]:
                continue
            
            # 429 hatası için retry mekanizması (en fazla 2 deneme)
            for attempt in range(2):
                try:
                    print(f"[DEBUG] {provider['name']} ile deneniyor...")
                    
                    if provider["name"] == "gemini":
                        response = self.client_gemini.models.generate_content(
                            model="models/gemini-3.5-flash",
                            contents=prompt
                        )
                        return response.text
                        
                    elif provider["name"] == "groq":
                        chat_completion = self.client_groq.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.3-70b-versatile",
                        )
                        return chat_completion.choices[0].message.content
                        
                    elif provider["name"] == "openrouter":
                        completion = self.client_openrouter.chat.completions.create(
                            model="google/gemini-2.0-flash-lite-preview:free",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        return completion.choices[0].message.content
                
                except Exception as e:
                    action = self._handle_error(e, provider["name"])
                    if action == "RETRY":
                        continue # Retry döngüsüne devam et
                    else:
                        break # Blacklist veya Fail durumunda bu sağlayıcıyı bırak
        
        raise Exception("Tüm sağlayıcılar başarısız oldu.")
