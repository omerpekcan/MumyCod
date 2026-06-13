import os
from groq import Groq
from llm.base_provider import BaseProvider
from typing import List, Dict
import os
from dotenv import load_dotenv


class DeepSeekProvider(BaseProvider):
    """Groq API üzerinden Llama ve DeepSeek modellerini uçuran sınıf."""

    def __init__(
        self,
        api_key: str = None,
        model_name: str = "llama-3.3-70b-specdec"
    ):
        load_dotenv()
        actual_key = api_key or os.getenv("GROQ_API_KEY")

        if not actual_key:
            raise ValueError(
                "Kanka .env dosyası içinde GROQ_API_KEY bulamadım! Kontrol et."
            )

        super().__init__(
            api_key=actual_key,
            model_name=model_name
        )

        self.client = Groq(
            api_key=self.api_key
        )

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:

        try:
            temperature = kwargs.get("temperature", 0.2)

            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=kwargs.get("max_tokens", 4096)
            )

            return completion.choices[0].message.content

        except Exception as e:

            return (
                f"🚨 [MumyCod LLM Hatası]: "
                f"Groq API ile konuşurken bir şeyler patladı: {str(e)}"
            )

    def generate(self, prompt: str) -> str:

        return self.generate_response(
            [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

    def chat(self, messages: list) -> str:

        return self.generate_response(messages)

    def summarize(self, text: str) -> str:

        return self.generate(
            f"Şu metni özetle:\n\n{text}"
        )

    # Embed fonksiyonu henüz implement edilmedi
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError(
            "Embedding henüz implement edilmedi."
        )

        raise NotImplementedError(
            "Embedding henüz implement edilmedi."
        )
