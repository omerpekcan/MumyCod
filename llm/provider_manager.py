import os
import time
from typing import Optional, Dict
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.api_core import exceptions
from groq import Groq
from openai import OpenAI

class ConfigLoader:
    """ConfigLoader: .env dosyasındaki API anahtarlarını ve ayarları yükler."""
    @staticmethod
    def load_config() -> Dict:
        load_dotenv()
        return {
            "primary": {
                "name": "gemini",
                "api_key": os.getenv("GEMINI_API_KEY"),
                "model": "models/gemini-2.5-flash-lite"
            },
            "fallbacks": [
                {
                    "name": "groq",
                    "api_key": os.getenv("GROQ_API_KEY"),
                    "model": "llama-3.3-70b-versatile"
                },
                {
                    "name": "openrouter",
                    "api_key": os.getenv("OPENROUTER_API_KEY"),
                    "model": "qwen/qwen3-next-80b-a3b-instruct:free"
                }
            ]
        }

class ProviderManager:
    def __init__(self):
        self.config = ConfigLoader.load_config()
        
        # İstemcileri başlat
        self.client_gemini = None
        self.client_groq = None
        self.client_openrouter = None
        
        self.blacklist = set()
        self.failure_counts: Dict[str, int] = {}
        self.circuit_breakers: Dict[str, float] = {}
        self.MAX_FAILURES = 5
        self.RECOVERY_TIME = 300  # 5 dakika

        # Sağlayıcı listesini config üzerinden oluştur
        self.providers = [self.config["primary"]] + self.config["fallbacks"]
        
        # API anahtarlarının varlığını kontrol et (güvenli log)
        for provider in self.providers:
            if not provider["api_key"]:
                print(f"[WARN] {provider['name'].upper()} API anahtarı bulunamadı.")

    def _get_status_code(self, e):
        """Hata nesnesinden HTTP durum kodunu çıkarır."""
        if isinstance(e, exceptions.ResourceExhausted):
            return 429
        if isinstance(e, (exceptions.ServiceUnavailable, exceptions.InternalServerError)):
            return 503
        if isinstance(e, exceptions.GoogleAPICallError):
            return getattr(e, 'code', 0)
        return getattr(e, 'status_code', getattr(e, 'code', 0))

    def _handle_error(self, e, provider_name):
        """Hata türünü analiz eder, neden ve aksiyon belirler."""
        status_code = self._get_status_code(e)
        error_type = type(e).__name__
        error_msg = str(e).lower()
        
        # 429 (Rate Limit) ve 503 (Service Unavailable) hatalarında
        if status_code in [429, 503]:
            return "NEXT"
        # 401 (Unauthorized) ve 404 (Not Found) hatalarında blacklist
        elif status_code in [401, 404]:
            self.blacklist.add(provider_name)
            return "BLACKLIST"
        # Connection hatalarında
        elif "connectionerror" in error_type.lower() or "timeout" in error_msg:
            return "NEXT"
        # Authentication hatalarında
        elif "authentication" in error_msg or "unauthenticated" in error_msg:
            self.blacklist.add(provider_name)
            return "BLACKLIST"
        # Type hatalarında (model/params yanlış)
        elif "typeerror" in error_type.lower():
            self.blacklist.add(provider_name)
            return "BLACKLIST"
        else:
            return "FAIL"

    def ask(self, prompt: str, system_prompt: str = "") -> str:
        """
        Sağlayıcılar arasında döngü kurar ve hata durumunda bir sonrakine geçer.
        Circuit Breaker mantığı ile hatalı sağlayıcıları izole eder.
        """
        last_error = None
        attempted_providers = []
        current_time = time.time()
        
        for provider in self.providers:
            p_name = provider["name"]

            # Circuit Breaker Kontrolü
            if p_name in self.circuit_breakers:
                if current_time < self.circuit_breakers[p_name]:
                    continue
                else:
                    pass  # Half-open, deneme devam eder

            if p_name in self.blacklist:
                continue
            
            if not provider["api_key"]:
                continue
            
            attempted_providers.append(p_name)
            
            try:
                # Hangi sağlayıcının kullanıldığını göster
                print(f"Kullanılan sağlayıcı: {p_name}")

                if p_name == "gemini":
                    model_name = provider.get("model", "models/gemini-2.5-flash-lite")
                    if self.client_gemini is None:
                        raise Exception("Gemini istemcisi başlatılamadı")
                    response = self.client_gemini.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            max_output_tokens=8192
                        )
                    )
                    response_text = response.text or ""
                    self.failure_counts[p_name] = 0
                    self.circuit_breakers.pop(p_name, None)
                    return response_text
                    
                elif p_name == "groq":
                    model_name = provider.get("model", "llama-3.3-70b-versatile")
                    if self.client_groq is None:
                        raise Exception("Groq istemcisi başlatılamadı")
                    chat_completion = self.client_groq.chat.completions.create(
                        messages=[{"role": "system", "content": system_prompt},
                                  {"role": "user", "content": prompt}],
                        model=model_name,
                        max_tokens=8192,
                        timeout=30.0
                    )
                    response_content = chat_completion.choices[0].message.content or ""
                    self.failure_counts[p_name] = 0
                    self.circuit_breakers.pop(p_name, None)
                    return response_content
                    
                elif p_name == "openrouter":
                    model_name = provider.get("model", "google/gemini-2.0-flash-lite-preview:free")
                    if self.client_openrouter is None:
                        raise Exception("OpenRouter istemcisi başlatılamadı")
                    completion = self.client_openrouter.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "system", "content": system_prompt},
                                  {"role": "user", "content": prompt}],
                        max_tokens=8192
                    )
                    response_content = completion.choices[0].message.content or ""
                    self.failure_counts[p_name] = 0
                    self.circuit_breakers.pop(p_name, None)
                    return response_content
            
            except Exception as e:
                last_error = e
                self.failure_counts[p_name] = self.failure_counts.get(p_name, 0) + 1

                if self.failure_counts[p_name] >= self.MAX_FAILURES:
                    self.circuit_breakers[p_name] = time.time() + self.RECOVERY_TIME

                self._handle_error(e, p_name)
                continue
        
        if last_error:
            raise Exception(f"Tüm sağlayıcılar başarısız oldu. Son hata: {type(last_error).__name__} - {str(last_error)}")
        else:
            raise Exception("Tüm sağlayıcılar başarısız oldu. (Kullanılabilir sağlayıcı yok)")
