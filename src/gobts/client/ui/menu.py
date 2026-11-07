from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

@dataclass
class MenuItem:
    label: str
    action: Callable[[], None]
    checked: Callable[[], bool]|None = None

@dataclass
class Menu:
    label: str
    items: list[MenuItem]