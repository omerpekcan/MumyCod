import os
from google import genai

def get_embedding(text: str) -> list[float]:
    """
    Gemini text-embedding-004 modelini kullanarak metin için embedding üretir.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    response = client.models.embed_content(
        model="text-embedding-004",
        contents=text
    )
    
    # Embedding değerlerini döndür
    return response.embeddings[0].values
