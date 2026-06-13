from dataclasses import dataclass
from typing import List

@dataclass
class ProjectState:
    root_path: str
    file_count: int
    indexed_files: List[str]
    last_scan: str

    def to_dict(self) -> dict:
        return {
            "root_path": self.root_path,
            "file_count": self.file_count,
            "indexed_files": self.indexed_files,
            "last_scan": self.last_scan
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectState":
        return cls(
            root_path=data["root_path"],
            file_count=data["file_count"],
            indexed_files=data["indexed_files"],
            last_scan=data["last_scan"]
        )
