import subprocess
import locale
import platform # platform modülünü ekledik
from subprocess import Popen, PIPE, TimeoutExpired

def decode_output(output_bytes: bytes) -> str:
    """
    Bayt dizisini güvenli bir şekilde string'e dönüştürür.
    """
    # Önce UTF-8 dene
    try:
        return output_bytes.decode('utf-8', errors='replace')
    except UnicodeDecodeError:
        pass
    
    # Sistem varsayılan kodlamasını dene
    try:
        return output_bytes.decode(locale.getpreferredencoding(), errors='replace')
    except UnicodeDecodeError:
        pass
        
    # Son çare olarak CP1254 (Türkçe Windows) dene
    try:
        return output_bytes.decode('cp1254', errors='replace')
    except UnicodeDecodeError:
        return output_bytes.decode('latin-1', errors='replace')

def execute_command(command: str, timeout: int = 10) -> str:
    """
    Verilen terminal komutunu çalıştırır ve çıktısını (stdout/stderr) döndürür.
    Sonsuz döngüye giren veya GUI açan komutlar için zaman aşımı yönetimi yapar.
    """
    try:
        creationflags = 0
        if platform.system() == "Windows":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        with Popen(
            command,
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
            creationflags=creationflags # Windows için yeni process grubu oluştur
        ) as process:
            try:
                stdout_bytes, stderr_bytes = process.communicate(timeout=timeout)
                stdout = decode_output(stdout_bytes) if stdout_bytes else ""
                stderr = decode_output(stderr_bytes) if stderr_bytes else ""
                
                if process.returncode != 0:
                    return f"Komut hata ile sonuçlandı (Kod: {process.returncode}):\n{stderr}"
                
                return stdout if stdout else "Komut başarıyla çalıştı (çıktı yok)."
            except TimeoutExpired:
                if platform.system() == "Windows":
                    # Windows'ta tüm process ağacını sonlandır
                    subprocess.run(f"taskkill /F /T /PID {process.pid}", shell=True, capture_output=True)
                else:
                    process.kill() # Diğer OS'lerde sadece ana process'i öldür
                
                stdout_bytes, stderr_bytes = process.communicate() # Kalan çıktıyı oku
                stdout = decode_output(stdout_bytes) if stdout_bytes else ""
                stderr = decode_output(stderr_bytes) if stderr_bytes else ""
                
                # GUI uygulaması gibi uzun süren komutlar için nötr mesaj
                return (f"Komut zaman aşımına uğradı ({timeout} saniye). "
                        f"Bu, bir GUI uygulamasının arka planda çalışması gibi durumlarda normal olabilir.\n"
                        f"Kısmi çıktı:\n{stdout}\n{stderr}")
    except Exception as e:
        return f"Komut çalıştırılırken beklenmedik bir hata oluştu: {str(e)}"
