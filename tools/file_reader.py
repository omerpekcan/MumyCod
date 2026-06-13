from pathlib import Path


class FileReader:

    def read(self, file_path: str) -> str:

        try:
            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:
                return f.read()

        except Exception as e:
            return f"Dosya okunamadı: {e}"