import os
import sys
import json

# Kök dizini Python yoluna ekleyelim
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm.embedding import get_embedding

def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    lines = text.splitlines()
    chunks = []
    current_chunk = []
    current_size = 0
    for line in lines:
        current_chunk.append(line)
        current_size += len(line)
        if current_size >= chunk_size:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_size = 0
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    return chunks

def scan_project():
    print("Proje taranıyor ve yerel hafıza (brain.json) oluşturuluyor...")
    ignore_dirs = {".venv", ".venv-1", ".git", ".aider", "memory", "node_modules", "__pycache__"}
    ignore_files = {"brain.json", "todos.json", "todo_items.txt"}
    brain_data = []
    
    # os.path.abspath ile yolları sabitleyelim ki ajan şaşırmasın
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".aider")]
        for file in files:
            if file in ignore_files or not (file.endswith(".py") or file.endswith(".txt") or file.endswith(".json")):
                continue
            
            # Dosya yolunu tam yol olarak al
            file_path = os.path.abspath(os.path.join(root, file))
            print(f"İndeksleniyor: {file_path}")
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                chunks = chunk_text(content)
                for idx, chunk in enumerate(chunks):
                    if not chunk.strip():
                        continue
                    vector = get_embedding(chunk)
                    brain_data.append({
                        "file_path": file_path,
                        "line_number": idx * 15,
                        "text": chunk,
                        "embedding": vector
                    })
            except Exception as e:
                print(f"Hata: {file_path} okunurken sorun oluştu: {str(e)}")
                
    os.makedirs("memory", exist_ok=True)
    with open("memory/brain.json", "w", encoding="utf-8") as f:
        json.dump(brain_data, f, indent=4, ensure_ascii=False)
    print(f"\nİndeksleme tamamlandı! Toplam {len(brain_data)} kod bloğu kaydedildi.")

if __name__ == "__main__":
    scan_project()