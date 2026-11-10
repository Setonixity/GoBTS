from __future__ import annotations
from dataclasses import dataclass

import pygame

@dataclass
class PanelLayout:
    rect: pygame.Rect
    tree_rect: pygame.Rect
    toolbar_rect: pygame.Rect

    @classmethod
    def fit(cls, rect: pygame.Rect, show_tree: bool, toolbar_height: int) -> PanelLayout:
        toolbar_height = min(toolbar_height, rect.height)
        tree_height = rect.height - toolbar_height if show_tree else 0
        return cls(
            rect = rect,
            tree_rect = pygame.Rect(rect.x, rect.y, rect.width, tree_height),
            toolbar_rect = pygame.Rect(rect.x, rect.bottom - toolbar_height, rect.width, toolbar_height)
        )