import subprocess
import locale

def decode_output(output_bytes: bytes) -> str:
    """
    Bayt dizisini güvenli bir şekilde string'e dönüştürür.
    """
    # Önce UTF-8 dene
    try:
        return output_bytes.decode('utf-8', errors='replace')
    except:
        pass
    
    # Sistem varsayılan kodlamasını dene
    try:
        return output_bytes.decode(locale.getpreferredencoding(), errors='replace')
    except:
        pass
        
    # Son çare olarak CP1254 (Türkçe Windows) dene
    try:
        return output_bytes.decode('cp1254', errors='replace')
    except:
        return output_bytes.decode('latin-1', errors='replace')

def execute_command(command: str) -> str:
    """
    Verilen terminal komutunu çalıştırır ve çıktısını (stdout/stderr) döndürür.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=False, # Binary modda çalıştırıyoruz
            check=False
        )
        
        stdout = decode_output(result.stdout) if result.stdout else ""
        stderr = decode_output(result.stderr) if result.stderr else ""
        
        if result.returncode != 0:
            return f"Komut hata ile sonuçlandı (Kod: {result.returncode}):\n{stderr}"
        
        return stdout if stdout else "Komut başarıyla çalıştı (çıktı yok)."
    except Exception as e:
        return f"Komut çalıştırılırken beklenmedik bir hata oluştu: {str(e)}"
