import os

def read_file(filepath: str) -> str:
    try:
        if not os.path.exists(filepath):
            return f"Hata: '{filepath}' dosyası bulunamadı."
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Dosya okunurken hata oluştu: {str(e)}"

def write_file(filepath: str, content: str) -> str:
    try:
        dir_name = os.path.dirname(filepath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            
        # Markdown kod bloklarını temizle
        cleaned_content = content.strip()
        if cleaned_content.startswith("```"):
            lines = cleaned_content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned_content = "\n".join(lines)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        return f"Başarıyla yazıldı: {filepath}"
    except Exception as e:
        return f"Dosya yazılırken hata oluştu: {str(e)}"
