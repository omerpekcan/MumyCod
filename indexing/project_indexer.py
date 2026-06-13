from typing import Dict
import json
from pathlib import Path
from workspace.scanner import scan_workspace

class ProjectIndexer:
    def build_index(self, root_path: str) -> Dict:
        """
        Projeyi tarar ve bir dizin oluşturur.

        Args:
        root_path (str): Projenin kök dizini.

        Returns:
        Dict: Oluşturulan dizin.
        """
        files = scan_workspace(root_path)
        index = {}
        for file in files:
            if file["ext"] == ".py":
                index[file["path"]] = {"path": file["path"]}
        return index

    def save_index(self, path: str, index: Dict) -> None:
        """
        Dizini belirtilen yola kaydeder.

        Args:
        path (str): Dizinin kaydedileceği yol.
        index (Dict): Kaydedilecek dizin.
        """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=4)

    def load_index(self, path: str) -> Dict:
        """
        Belirtilen yoldan dizini yükler.

        Args:
        path (str): Dizinin yüklenileceği yol.

        Returns:
        Dict: Yüklenen dizin. Dosya yoksa boş bir sözlük döner.
        """
        file_path = Path(path)
        if file_path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
