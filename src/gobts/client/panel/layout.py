from __future__ import annotations
from dataclasses import dataclass

import pygame

@dataclass
class PanelLayout:
    rect: pygame.Rect
    tree_rect: pygame.Rect

    @classmethod
    def fit(cls, rect: pygame.Rect, show_tree: bool) -> PanelLayout:
        return cls(
            rect = rect,
            tree_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height if show_tree else 0)
        )