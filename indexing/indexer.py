import os
import json
from llm.embedding import get_embedding
from indexing.vector_store import VectorStore

def chunk_text(text, chunk_size=500):
    """
    Metni belirtilen boyutta parçalara böler.
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def index_project(root_path="."):
    """
    Projeyi tarar, dosyaları okur, embedding üretir ve vektör deposuna kaydeder.
    """
    # Vektör deposunu başlat (brain.json dosyasına kaydedecek şekilde)
    vector_store = VectorStore(store_path="memory/brain.json")
    
    # Göz ardı edilecek dizinler ve dosyalar
    ignore_list = {".venv", ".git", ".aider", "__pycache__", "todos.json", "memory", "indexing"}
    
    print(f"Proje taranıyor: {root_path}...")
    
    for root, dirs, files in os.walk(root_path):
        # Dizinleri filtrele
        dirs[:] = [d for d in dirs if d not in ignore_list and not d.startswith(".")]
        
        for file in files:
            if file.endswith((".py", ".txt")) and file not in ignore_list:
                file_path = os.path.join(root, file)
                print(f"İndeksleniyor: {file_path}")
                
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    chunks = chunk_text(content)
                    
                    for chunk in chunks:
                        if chunk.strip():
                            embedding = get_embedding(chunk)
                            vector_store.add_document(file_path, chunk, embedding)
                            
                except Exception as e:
                    print(f"Hata: {file_path} okunamadı: {e}")
    
    # Belleği kaydet
    vector_store.save_store()
    print("İndeksleme tamamlandı! 'memory/brain.json' oluşturuldu.")

if __name__ == "__main__":
    # memory dizininin var olduğundan emin ol
    if not os.path.exists("memory"):
        os.makedirs("memory")
        
    index_project()
