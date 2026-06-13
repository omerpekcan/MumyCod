import json
import os
import math
from llm.embedding import get_embedding

class CodeRetriever:
    """
    RAG sistemi için vektör tabanlı kod geri getirme (retrieval) sınıfı.
    """

    def __init__(self, brain_path="memory/brain.json"):
        self.brain_path = brain_path
        self.data = self._load_brain()

    def _load_brain(self):
        """Bellekteki vektör deposunu yükler."""
        if os.path.exists(self.brain_path):
            try:
                with open(self.brain_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """
        İki vektör arasındaki kosinüs benzerliğini hesaplar.
        Vektörler zaten normalize edildiği için nokta çarpımı (dot product) yeterlidir.
        """
        return sum(a * b for a, b in zip(vec1, vec2))

    def retrieve_relevant_chunks(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Sorgu ile en alakalı kod parçalarını getirir.
        
        Args:
            query (str): Kullanıcının arama sorgusu.
            top_k (int): Döndürülecek maksimum sonuç sayısı.
            
        Returns:
            list[dict]: En alakalı chunk'ların listesi.
        """
        if not self.data:
            return []

        # Sorguyu vektöre dönüştür
        query_embedding = get_embedding(query)
        
        scored_chunks = []
        for item in self.data:
            # Benzerlik skoru hesapla
            score = self._cosine_similarity(query_embedding, item["embedding"])
            scored_chunks.append({
                "file_path": item["file_path"],
                "chunk": item["chunk"],
                "score": score
            })
        
        # Skorlara göre azalan sırada sırala
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_chunks[:top_k]
