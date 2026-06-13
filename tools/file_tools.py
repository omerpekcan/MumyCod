import os

def write_to_file(filepath: str, content: str) -> str:
    """
    Belirtilen dosya yoluna içeriği yazar. Dosya yoksa oluşturur, varsa üzerine yazar.
    """
    try:
        # Klasör yapısı yoksa oluştur
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Başarıyla yazıldı: {filepath}"
    except Exception as e:
        return f"Hata oluştu: {str(e)}"
