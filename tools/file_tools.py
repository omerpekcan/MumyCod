import os

def write_to_file(filepath: str, content: str) -> str:
    """
    Belirtilen dosya yoluna içeriği yazar. 
    Dizin yoksa oluşturur, varsa üzerine yazar.
    """
    try:
        # Dosya yolunun dizin kısmını al
        directory = os.path.dirname(filepath)
        
        # Eğer dizin belirtilmişse ve mevcut değilse oluştur
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Başarıyla yazıldı: {filepath}"
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

def read_file(filepath: str) -> str:
    """
    Belirtilen dosya yolundaki içeriği okur.
    Dosya yoksa hata mesajı döner.
    """
    if not os.path.exists(filepath):
        return f"Hata: Dosya bulunamadı: {filepath}"
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Hata oluştu: {str(e)}"
