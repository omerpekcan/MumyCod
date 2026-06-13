import os
import time
from dotenv import load_dotenv
from google import genai
from groq import Groq
from openai import OpenAI

class ProviderManager:
    def __init__(self):
        load_dotenv()
        print("[DEBUG] .env dosyası yükleniyor...")
        
        self.blacklist = set()
        self.providers = [
            {"name": "gemini", "api_key": os.environ.get("GEMINI_API_KEY")},
            {"name": "groq", "api_key": os.environ.get("GROQ_API_KEY")},
            {"name": "openrouter", "api_key": os.environ.get("OPENROUTER_API_KEY")}
        ]
        
        # API anahtarlarının varlığını kontrol et ve log bas
        print("[DEBUG] API anahtarları kontrol ediliyor:")
        for provider in self.providers:
            if provider["api_key"]:
                print(f"  ✓ {provider['name'].upper()}: API anahtarı bulundu (ilk 10 karakter: {provider['api_key'][:10]}...)")
            else:
                print(f"  ✗ {provider['name'].upper()}: API anahtarı bulunamadı")
        
        # İstemcileri __init__ içinde başlatıyoruz
        print("[DEBUG] İstemciler başlatılıyor...")
        self.client_gemini = genai.Client(api_key=os.environ.get("GEMINI_API_KEY")) if os.environ.get("GEMINI_API_KEY") else None
        if self.client_gemini:
            print("[DEBUG] Gemini istemcisi başarıyla başlatıldı")
        else:
            print("[DEBUG] Gemini istemcisi başlatılamadı (API anahtarı yok)")
            
        self.client_groq = Groq(api_key=os.environ.get("GROQ_API_KEY")) if os.environ.get("GROQ_API_KEY") else None
        if self.client_groq:
            print("[DEBUG] Groq istemcisi başarıyla başlatıldı")
        else:
            print("[DEBUG] Groq istemcisi başlatılamadı (API anahtarı yok)")
            
        self.client_openrouter = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ.get("OPENROUTER_API_KEY")) if os.environ.get("OPENROUTER_API_KEY") else None
        if self.client_openrouter:
            print("[DEBUG] OpenRouter istemcisi başarıyla başlatıldı")
        else:
            print("[DEBUG] OpenRouter istemcisi başlatılamadı (API anahtarı yok)")

    def _handle_error(self, e, provider_name):
        """Hata türünü analiz eder ve aksiyon belirler."""
        status_code = getattr(e, 'status_code', getattr(e, 'code', 0))
        
        # 429 ve 503 hatalarında hemen bir sonrakine geçmek istiyoruz (retry yok)
        if status_code in [429, 503]:
            print(f"[DEBUG] {provider_name} {status_code} hatası verdi. Bir sonraki sağlayıcıya geçiliyor.")
            return "NEXT"
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
        print("[DEBUG] Prompt işlenmek üzere sağlayıcılara gönderiliyor...")
        
        for provider in self.providers:
            if provider["name"] in self.blacklist:
                print(f"[DEBUG] {provider['name']} blacklist'te, atlaniyor.")
                continue
            
            if not provider["api_key"]:
                print(f"[DEBUG] {provider['name']} için API anahtarı yok, atlaniyor.")
                continue
            
            try:
                print(f"[DEBUG] {provider['name']} ile deneniyor...")
                
                if provider["name"] == "gemini":
                    print(f"[DEBUG] Gemini API'sine istek gönderiliyor (model: gemini-3.5-flash)...")
                    response = self.client_gemini.models.generate_content(
                        model="models/gemini-3.5-flash",
                        contents=prompt
                    )
                    print(f"[DEBUG] Gemini başarıyla yanıt verdi")
                    return response.text
                    
                elif provider["name"] == "groq":
                    print(f"[DEBUG] Groq API'sine istek gönderiliyor (model: llama-3.3-70b-versatile)...")
                    chat_completion = self.client_groq.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                    )
                    print(f"[DEBUG] Groq başarıyla yanıt verdi")
                    return chat_completion.choices[0].message.content
                    
                elif provider["name"] == "openrouter":
                    print(f"[DEBUG] OpenRouter API'sine istek gönderiliyor (model: google/gemini-2.0-flash-lite-preview:free)...")
                    completion = self.client_openrouter.chat.completions.create(
                        model="google/gemini-2.0-flash-lite-preview:free",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    print(f"[DEBUG] OpenRouter başarıyla yanıt verdi")
                    return completion.choices[0].message.content
            
            except Exception as e:
                print(f"[DEBUG] {provider['name']} hata fırlattı: {type(e).__name__}")
                action = self._handle_error(e, provider["name"])
                # Hata durumunda döngü bir sonraki sağlayıcıya devam eder
                continue
        
        print("[DEBUG] Tüm sağlayıcılar başarısız oldu.")
        raise Exception("Tüm sağlayıcılar başarısız oldu.")
