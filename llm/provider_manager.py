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
        """Hata türünü analiz eder, neden ve aksiyon belirler."""
        status_code = getattr(e, 'status_code', getattr(e, 'code', 0))
        error_type = type(e).__name__
        error_msg = str(e).lower()
        
        print(f"[DEBUG] {provider_name} hata detayı - Tip: {error_type}, Kod: {status_code}")
        
        # 429 (Rate Limit) ve 503 (Service Unavailable) hatalarında
        if status_code in [429, 503]:
            reason = "Rate limit aşıldı" if status_code == 429 else "Servis geçici olarak kullanılamıyor"
            print(f"[DEBUG] {provider_name} {status_code} hatası: {reason}. Bir sonraki sağlayıcıya geçiliyor.")
            return "NEXT"
        
        # 401 (Unauthorized) ve 404 (Not Found) hatalarında blacklist
        elif status_code in [401, 404]:
            reason = "API anahtarı geçersiz veya yanlış" if status_code == 401 else "Endpoint bulunamadı"
            print(f"[DEBUG] {provider_name} {status_code} hatası: {reason}. Blacklist'e alınıyor.")
            self.blacklist.add(provider_name)
            return "BLACKLIST"
        
        # Connection hatalarında
        elif "connectionerror" in error_type.lower() or "timeout" in error_msg:
            print(f"[DEBUG] {provider_name} bağlantı hatası: Ağ problemi veya timeout. Bir sonraki sağlayıcıya geçiliyor.")
            return "NEXT"
        
        # Authentication hatalarında
        elif "authentication" in error_msg or "unauthenticated" in error_msg:
            print(f"[DEBUG] {provider_name} kimlik doğrulama hatası: API anahtarı geçersiz. Blacklist'e alınıyor.")
            self.blacklist.add(provider_name)
            return "BLACKLIST"
        
        # Type hatalarında (model/params yanlış)
        elif "typeerror" in error_type.lower():
            print(f"[DEBUG] {provider_name} tip hatası: Model veya parametreler yanlış. Blacklist'e alınıyor.")
            self.blacklist.add(provider_name)
            return "BLACKLIST"
        
        # Diğer hatalar
        else:
            print(f"[DEBUG] {provider_name} beklenmedik hata: {error_type} - {str(e)}")
            return "FAIL"

    def ask(self, prompt: str) -> str:
        """
        Sağlayıcılar arasında döngü kurar ve hata durumunda bir sonrakine geçer.
        Detaylı hata raporlaması yaparak feedback sağlar.
        """
        print("[DEBUG] Prompt işlenmek üzere sağlayıcılara gönderiliyor...")
        print(f"[DEBUG] Prompt uzunluğu: {len(prompt)} karakter")
        
        last_error = None
        attempted_providers = []
        
        for provider in self.providers:
            if provider["name"] in self.blacklist:
                print(f"[DEBUG] {provider['name']} blacklist'te, atlaniyor.")
                continue
            
            if not provider["api_key"]:
                print(f"[DEBUG] {provider['name']} için API anahtarı yok, atlaniyor.")
                continue
            
            attempted_providers.append(provider["name"])
            
            try:
                print(f"[DEBUG] {provider['name']} ile deneniyor... (Girişim: {len(attempted_providers)}/{len([p for p in self.providers if p['api_key']])})")
                
                if provider["name"] == "gemini":
                    print(f"[DEBUG] Gemini API'sine istek gönderiliyor (model: gemini-3.5-flash)...")
                    response = self.client_gemini.models.generate_content(
                        model="models/gemini-3.5-flash",
                        contents=prompt
                    )
                    print(f"[DEBUG] Gemini başarıyla yanıt verdi (Yanıt uzunluğu: {len(response.text)} karakter)")
                    return response.text
                    
                elif provider["name"] == "groq":
                    print(f"[DEBUG] Groq API'sine istek gönderiliyor (model: llama-3.3-70b-versatile)...")
                    chat_completion = self.client_groq.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                    )
                    response_content = chat_completion.choices[0].message.content
                    print(f"[DEBUG] Groq başarıyla yanıt verdi (Yanıt uzunluğu: {len(response_content)} karakter)")
                    return response_content
                    
                elif provider["name"] == "openrouter":
                    print(f"[DEBUG] OpenRouter API'sine istek gönderiliyor (model: google/gemini-2.0-flash-lite-preview:free)...")
                    completion = self.client_openrouter.chat.completions.create(
                        model="google/gemini-2.0-flash-lite-preview:free",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    response_content = completion.choices[0].message.content
                    print(f"[DEBUG] OpenRouter başarıyla yanıt verdi (Yanıt uzunluğu: {len(response_content)} karakter)")
                    return response_content
            
            except Exception as e:
                last_error = e
                print(f"[DEBUG] {provider['name']} hata fırlattı: {type(e).__name__}")
                action = self._handle_error(e, provider["name"])
                
                if action == "BLACKLIST":
                    print(f"[DEBUG] {provider['name']} blacklist'e eklendi, diğer sağlayıcılar deneniyor...")
                elif action == "NEXT":
                    print(f"[DEBUG] {provider['name']} başarısız, bir sonraki sağlayıcıya geçiliyor...")
                else:
                    print(f"[DEBUG] {provider['name']} başarısız (FAIL), bir sonraki sağlayıcıya geçiliyor...")
                
                continue
        
        print("[DEBUG] Tüm sağlayıcılar başarısız oldu.")
        print(f"[DEBUG] Denenen sağlayıcılar: {', '.join(attempted_providers)}")
        
        if last_error:
            error_msg = f"Tüm sağlayıcılar başarısız oldu. Son hata: {type(last_error).__name__} - {str(last_error)}"
        else:
            error_msg = "Tüm sağlayıcılar başarısız oldu. (Kullanılabilir sağlayıcı yok)"
        
        print(f"[DEBUG] {error_msg}")
        raise Exception(error_msg)
