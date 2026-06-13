import subprocess

class GitTools:
    """
    Git işlemlerini otomatize eden yardımcı sınıf.
    """

    def _run_command(self, command: str) -> str:
        """
        Terminal komutunu çalıştırır ve çıktısını döndürür.
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                return f"Hata (Kod: {result.returncode}): {result.stderr}"
            return result.stdout if result.stdout else "İşlem başarıyla tamamlandı."
        except Exception as e:
            return f"Komut çalıştırılırken hata oluştu: {str(e)}"

    def git_commit(self, message: str) -> str:
        """
        Tüm değişiklikleri ekler ve belirtilen mesajla commit eder.
        """
        add_output = self._run_command("git add .")
        commit_output = self._run_command(f'git commit -m "{message}"')
        return f"Git Add Çıktısı:\n{add_output}\nGit Commit Çıktısı:\n{commit_output}"

    def git_push(self) -> str:
        """
        Değişiklikleri uzak sunucuya gönderir.
        """
        return self._run_command("git push")
