from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path


class TargetGenerator(ABC):
    def __init__(self, output_path: str):
        self.output_path = output_path

    @abstractmethod
    def generate(self, targets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def save(self, transformed_targets: List[Dict[str, Any]]) -> None:
        pass

    def _ensure_output_dir(self) -> None:
        output_dir = Path(self.output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

    def process(self, targets: List[Dict[str, Any]]) -> int:
        transformed = self.generate(targets)
        self.save(transformed)
        return len(transformed)
