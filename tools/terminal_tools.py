import subprocess

def execute_command(command: str) -> str:
    """
    Verilen terminal komutunu çalıştırır ve çıktısını (stdout/stderr) döndürür.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        output = result.stdout if result.stdout else ""
        error = result.stderr if result.stderr else ""
        
        if result.returncode != 0:
            return f"Komut hata ile sonuçlandı (Kod: {result.returncode}):\n{error}"
        
        return output if output else "Komut başarıyla çalıştı (çıktı yok)."
    except Exception as e:
        return f"Komut çalıştırılırken beklenmedik bir hata oluştu: {str(e)}"
