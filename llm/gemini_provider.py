import os
import google.generativeai as genai

class GeminiProvider:
    def __init__(self):
        print("[DEBUG] GeminiProvider başlatılıyor...")
        # API anahtarını ortam değişkenlerinden güvenle alıyoruz
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("[DEBUG] HATA: GEMINI_API_KEY bulunamadı!")
            raise ValueError("Hata: GEMINI_API_KEY ortam değişkeni bulunamadı! Lütfen .env dosyanızı veya terminal değişkenlerinizi kontrol edin.")
        
        genai.configure(api_key=api_key)
        # Kararlı ve otonom işlere en uygun model olan gemini-2.5-flash sürümünü ayağa kaldırıyoruz
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        print("[DEBUG] GeminiProvider başarıyla başlatıldı.")

    def chat(self, history_or_prompt):
        print(f"[DEBUG] GeminiProvider.chat() çağrıldı.")
        try:
            # Eğer gelen veri düz bir string ise direkt üret ve dön
            if isinstance(history_or_prompt, str):
                print("[DEBUG] Gemini'ye düz metin gönderiliyor...")
                response = self.model.generate_content(history_or_prompt)
                print("[DEBUG] Gemini'den yanıt alındı.")
                return response

            # Eğer gelen veri bir listeyse (Ajan geçmişiyse) formatı tam uyumlu hale getiriyoruz
            print("[DEBUG] Gemini'ye geçmiş listesi gönderiliyor...")
            formatted_contents = []
            for message in history_or_prompt:
                # MumyCod sisteminde 'role' anahtarını aynen koru
                role = message.get("role", "user")
                
                # 'parts' listesindeki metinleri toparla
                parts_list = message.get("parts", [])
                text_content = ""
                if isinstance(parts_list, list) and len(parts_list) > 0:
                    text_content = str(parts_list[0])
                else:
                    text_content = str(parts_list)
                
                # Gemini kütüphanesinin tam olarak beklediği yapı: {'role': ..., 'parts': [...]}
                formatted_contents.append({
                    "role": role,
                    "parts": [text_content]
                })

            # Temizlenmiş ve 'content' hatası vermesi imkansız olan formatı API'ye uçuruyoruz
            response = self.model.generate_content(formatted_contents)
            print("[DEBUG] Gemini'den geçmiş yanıtı alındı.")
            return response

        except Exception as e:
            # Hata oluşursa terminalde neyin eksik olduğunu görebilmemiz için buraya düşecek
            print(f"[DEBUG] !!! GeminiProvider HATA !!!: {str(e)}")
            class FallbackResponse:
                def __init__(self, text_val):
                    self.text = text_val
            return FallbackResponse(f"Gemini Sağlayıcı Hatası: {str(e)}")
