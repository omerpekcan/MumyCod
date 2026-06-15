import os

def read_file(filepath: str) -> str:
    abs_path = os.path.abspath(filepath)
    print(f"[DEBUG] Dosya okunuyor: {abs_path}")
    try:
        if not os.path.exists(abs_path):
            print(f"[ERROR] Dosya bulunamadı: {abs_path}")
            return f"Hata: '{abs_path}' dosyası bulunamadı."
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"[DEBUG] Dosya başarıyla okundu: {abs_path} (Boyut: {len(content)})")
            return content
    except Exception as e:
        print(f"[ERROR] Dosya okunurken istisna oluştu: {str(e)}")
        return f"Dosya okunurken hata oluştu: {str(e)}"

def write_file(filepath: str, content: str) -> str:
    abs_path = os.path.abspath(filepath)
    print(f"[DEBUG] Dosya yazma isteği: {abs_path}")
    try:
        dir_name = os.path.dirname(abs_path)
        if dir_name and not os.path.exists(dir_name):
            print(f"[DEBUG] Dizin oluşturuluyor: {dir_name}")
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
            
        print(f"[DEBUG] Yazılacak içerik boyutu: {len(cleaned_content)} karakter")
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
            
        if os.path.exists(abs_path):
            print(f"[DEBUG] Yazma işlemi doğrulandı: {abs_path}")
            return f"Başarıyla yazıldı: {abs_path}"
        else:
            print(f"[ERROR] Dosya yazıldı dendi ama bulunamadı: {abs_path}")
            return f"Hata: Dosya yazma işlemi başarısız oldu (dosya oluşturulamadı): {abs_path}"
    except Exception as e:
        print(f"[ERROR] Dosya yazılırken istisna oluştu: {str(e)}")
        return f"Dosya yazılırken hata oluştu: {str(e)}"
