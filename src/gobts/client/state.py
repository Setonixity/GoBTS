from __future__ import annotations
from pathlib import Path
from typing import Optional
from pydantic.dataclasses import dataclass
from pydantic import TypeAdapter, ValidationError

from gobts.client.paths import STATE_FILE

@dataclass
class State:
    theme: Optional[str] = "goban" 
    game: Optional[Path] = None 

    @classmethod
    def load(cls, path: Path = STATE_FILE) -> State:
        try:
            return TypeAdapter(cls).validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValidationError): 
            return cls()

    def save(self, path: Path = STATE_FILE) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(TypeAdapter(State).dump_json(self, indent=4))