import ast
import json
from pathlib import Path
from workspace.scanner import scan_workspace

class SymbolIndexer:
    def build_symbol_index(self, root_path: str) -> dict:
        """
        Projeyi tarar ve bir sembol dizini oluşturur.

        Args:
        root_path (str): Projenin kök dizini.

        Returns:
        dict: Oluşturulan sembol dizini.
        """
        files = scan_workspace(root_path)
        symbol_index = {}
        for file in files:
            if file["ext"] == ".py":
                file_path = Path(file["path"])
                try:
                    with open(
                  file_path,
                  "r",
                  encoding="utf-8",
                  errors="ignore"
                  ) as f:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                symbol_index[node.name] = str(file_path)
                            elif isinstance(node, ast.FunctionDef):
                                symbol_index[node.name] = str(file_path)
                            elif isinstance(node, ast.AsyncFunctionDef):
                                symbol_index[node.name] = str(file_path)
                except Exception as e:
                    print(f"Hata oluştu: {e}")
        return symbol_index

    def save_symbol_index(self, path: str, index: dict) -> None:
        """
        Sembol dizinini belirtilen yola kaydeder.

        Args:
        path (str): Sembol dizininin kaydedileceği yol.
        index (dict): Kaydedilecek sembol dizini.
        """
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=4)
        except Exception as e:
            print(f"Hata oluştu: {e}")

    def load_symbol_index(self, path: str) -> dict:
        """
        Belirtilen yoldan sembol dizinini yükler.

        Args:
        path (str): Sembol dizininin yüklenileceği yol.

        Returns:
        dict: Yüklenen sembol dizini. Dosya yoksa boş bir sözlük döner.
        """
        try:
            file_path = Path(path)
            if file_path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"Hata oluştu: {e}")
            return {}
