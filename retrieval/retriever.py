import os
import json
from llm.embedding import get_embedding

class CodeRetriever:
    def __init__(self, brain_path="memory/brain.json"):
        self.brain_path = brain_path
        self.data = self._load_brain()

    def _load_brain(self):
        if os.path.exists(self.brain_path):
            try:
                with open(self.brain_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Hafıza dosyası yüklenirken hata oluştu: {str(e)}")
                return []
        print(f"[DEBUG] Hafıza dosyası bulunamadı: {self.brain_path}")
        return []

    def retrieve_relevant_chunks(self, query: str, top_k: int = 3) -> list:
        if not self.data:
            print("[DEBUG] Hafıza boş, arama yapılamıyor.")
            return []
            
        query_vector = get_embedding(query)
        scored_chunks = []
        
        for item in self.data:
            doc_vector = item.get("embedding", [])
            if not doc_vector or len(doc_vector) != len(query_vector):
                continue
                
            # Kosinüs benzerliği (vektörler normalize edildiği için nokta çarpımı yeterli)
            score = sum(q * d for q, d in zip(query_vector, doc_vector))
            chunk_text = item.get("text") or item.get("chunk") or ""
            
            scored_chunks.append({
                "file_path": item.get("file_path", "Bilinmeyen Dosya"),
                "line_number": item.get("line_number", 0),
                "text": chunk_text,
                "score": score
            })
            
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]
