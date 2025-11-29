from typing import Optional
import os


class TextLoader:
    def __init__(self, source_dir: str):
        self.source_dir = source_dir

    def load(self, path: str) -> Optional[str]:
        try:
            with open(os.path.join(self.source_dir, path), "r", encoding="utf-8") as f:
                return f.read().rstrip("\n")
        except FileNotFoundError:
            return None