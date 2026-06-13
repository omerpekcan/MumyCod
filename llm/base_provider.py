from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseProvider(ABC):
    """
    MumyCod içindeki tüm LLM sağlayıcılarının (Groq, Gemini, Ollama vb.)
    türemek zorunda olduğu soyut temel sınıf.
    """
    
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Gelen mesaj geçmişini (prompt) alıp yapay zekadan ham metin yanıtı döner.
        """
        pass

    @abstractmethod
    def chat(self, messages: list) -> str:
        """
        Gelen mesaj geçmişini (prompt) alıp yapay zekadan ham metin yanıtı döner.
        """
        pass

    @abstractmethod
    def summarize(self, text: str) -> str:
        """
        Gelen metni özetler.
        """
        pass

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """
        Gelen metni vektörleştirir.
        """
        pass
