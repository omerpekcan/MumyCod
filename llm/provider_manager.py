import os
import time
from typing import Optional, Dict
from dotenv import load_dotenv
from google import genai
from groq import Groq
from openai import OpenAI

class ProviderManager:
    def __init__(self):
        load_dotenv()
        print("[DEBUG] .env dosyası yükleniyor...")
        
        self.blacklist = set()
        self.failure_counts: Dict[str, int] = {}
        self.circuit_breakers: Dict[str, float] = {}
        self.MAX_FAILURES = 3
        self.RECOVERY_TIME = 300  # 5 dakika

        self.providers = [
            {"name": "gemini", "api_key": os.environ.get("GEMINI_API_KEY")},
            {"name": "groq", "api_key": os.environ.get("GROQ_API_KEY")},
            {"name": "openrouter", "api_key": os.environ.get("OPENROUTER_API_KEY")}
        ]
        
        # API anahtarlarının varlığını kontrol et ve log bas
        print("[DEBUG] API anahtarları kontrol ediliyor:")
        for provider in self.providers:
            if provider["api_key"]:
                print(f"  [OK] {provider['name'].upper()}: API anahtarı bulundu (ilk 10 karakter: {provider['api_key'][:10]}...)")
            else:
                print(f"  [MISSING] {provider['name'].upper()}: API anahtarı bulunamadı")
        
        # İstemcileri __init__ içinde başlatıyoruz
        print("[DEBUG] İstemciler başlatılıyorum...")
        self.client_gemini: Optional[genai.Client] = genai.Client(api_key=os.environ.get("GEMINI_API_KEY")) if os.environ.get("GEMINI_API_KEY") else None
        if self.client_gemini:
            print("[DEBUG] Gemini istemcisi başarıyla başlatıldı")
        else:
            print("[DEBUG] Gemini istemcisi başlatılamadı (API anahtarı yok)")
            
        self.client_groq: Optional[Groq] = Groq(api_key=os.environ.get("GROQ_API_KEY")) if os.environ.get("GROQ_API_KEY") else None
        if self.client_groq:
            print("[DEBUG] Groq istemcisi başarıyla başlatıldı")
        else:
            print("[DEBUG] Groq istemcisi başlatılamadı (API anahtarı yok)")
            
        self.client_openrouter: Optional[OpenAI] = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ.get("OPENROUTER_API_KEY")) if os.environ.get("OPENROUTER_API_KEY") else None
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
        Circuit Breaker mantığı ile hatalı sağlayıcıları izole eder.
        """
        print("[DEBUG] Prompt işlenmek üzere sağlayıcılara gönderiliyor...")
        
        last_error = None
        attempted_providers = []
        current_time = time.time()
        
        for provider in self.providers:
            p_name = provider["name"]

            # Circuit Breaker Kontrolü
            if p_name in self.circuit_breakers:
                if current_time < self.circuit_breakers[p_name]:
                    print(f"[DEBUG] {p_name} devre dışı (Circuit Open), atlanıyor.")
                    continue
                else:
                    print(f"[DEBUG] {p_name} deneme aşamasında (Circuit Half-Open)...")

            if p_name in self.blacklist:
                print(f"[DEBUG] {p_name} blacklist'te, atlaniyor.")
                continue
            
            if not provider["api_key"]:
                print(f"[DEBUG] {provider['name']} için API anahtarı yok, atlaniyor.")
                continue
            
            attempted_providers.append(provider["name"])
            
            try:
                print(f"[DEBUG] {provider['name']} ile deneniyor... (Girişim: {len(attempted_providers)}/{len([p for p in self.providers if p['api_key']])})")
                
                if provider["name"] == "gemini":
                    print(f"[DEBUG] Gemini API'sine istek gönderiliyor (model: gemini-3.5-flash)...")
                    if self.client_gemini is None:
                        raise Exception("Gemini istemcisi başlatılamadı")
                    response = self.client_gemini.models.generate_content(
                        model="models/gemini-3.5-flash",
                        contents=prompt
                    )
                    response_text = response.text or ""
                    self.failure_counts[p_name] = 0  # Başarı durumunda sıfırla
                    if p_name in self.circuit_breakers: del self.circuit_breakers[p_name]
                    print(f"[DEBUG] Gemini başarıyla yanıt verdi")
                    return response_text
                    
                elif provider["name"] == "groq":
                    print(f"[DEBUG] Groq API'sine istek gönderiliyor (model: llama-3.3-70b-versatile)...")
                    if self.client_groq is None:
                        raise Exception("Groq istemcisi başlatılamadı")
                    chat_completion = self.client_groq.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                        timeout=30.0
                    )
                    response_content = chat_completion.choices[0].message.content or ""
                    self.failure_counts[p_name] = 0
                    if p_name in self.circuit_breakers: del self.circuit_breakers[p_name]
                    print(f"[DEBUG] Groq başarıyla yanıt verdi")
                    return response_content
                    
                elif provider["name"] == "openrouter":
                    print(f"[DEBUG] OpenRouter API'sine istek gönderiliyor (model: google/gemini-2.0-flash-lite-preview:free)...")
                    if self.client_openrouter is None:
                        raise Exception("OpenRouter istemcisi başlatılamadı")
                    completion = self.client_openrouter.chat.completions.create(
                        model="google/gemini-2.0-flash-lite-preview:free",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    response_content = completion.choices[0].message.content or ""
                    self.failure_counts[p_name] = 0
                    if p_name in self.circuit_breakers: del self.circuit_breakers[p_name]
                    print(f"[DEBUG] OpenRouter başarıyla yanıt verdi")
                    return response_content
            
            except Exception as e:
                last_error = e
                self.failure_counts[p_name] = self.failure_counts.get(p_name, 0) + 1
                
                print(f"[DEBUG] {p_name} hata fırlattı: {type(e).__name__} (Hata Sayısı: {self.failure_counts[p_name]})")
                
                if self.failure_counts[p_name] >= self.MAX_FAILURES:
                    self.circuit_breakers[p_name] = time.time() + self.RECOVERY_TIME
                    print(f"[DEBUG] {p_name} için Circuit Breaker AÇILDI. {self.RECOVERY_TIME}s devre dışı.")

                action = self._handle_error(e, p_name)
                continue
        
        print("[DEBUG] Tüm sağlayıcılar başarısız oldu.")
        print(f"[DEBUG] Denenen sağlayıcılar: {', '.join(attempted_providers)}")
        
        if last_error:
            error_msg = f"Tüm sağlayıcılar başarısız oldu. Son hata: {type(last_error).__name__} - {str(last_error)}"
        else:
            error_msg = "Tüm sağlayıcılar başarısız oldu. (Kullanılabilir sağlayıcı yok)"
        
        print(f"[DEBUG] {error_msg}")
        raise Exception(error_msg)
