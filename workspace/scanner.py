import pathlib
from typing import List, Dict


def scan_workspace(root_path: str) -> List[Dict]:
    """
    Recursively scans the project folders and returns a list
    of dictionaries containing file information.
    """

    root = pathlib.Path(root_path)
    files = []

    SKIP_DIRS = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__"
    }

    for file in root.rglob("*"):

        if not file.is_file():
            continue

        # Yolun herhangi bir parçasında bu klasörler varsa atla
        if any(part in SKIP_DIRS for part in file.parts):
            continue

        file_info = {
            "path": str(file.relative_to(root)),
            "size": file.stat().st_size,
            "ext": file.suffix
        }

        files.append(file_info)

    return files