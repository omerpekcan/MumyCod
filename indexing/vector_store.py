import json
import os

class VectorStore:
    def __init__(self, store_path="vector_store.json"):
        self.store_path = store_path
        self.data = self._load_store()

    def _load_store(self):
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def add_document(self, file_path: str, chunk: str, embedding: list[float]):
        """
        Yeni bir dokümanı vektör deposuna ekler.
        """
        self.data.append({
            "file_path": file_path,
            "chunk": chunk,
            "embedding": embedding
        })

    def save_store(self):
        """
        Vektör deposunu JSON dosyasına kaydeder.
        """
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
