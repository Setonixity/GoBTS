from __future__ import annotations
from dataclasses import dataclass

import pygame

@dataclass
class PanelLayout:
    rect: pygame.Rect
    tree_rect: pygame.Rect
    toolbar_rect: pygame.Rect
    actionbar_rect: pygame.Rect

    @classmethod
    def fit(cls, rect: pygame.Rect, show_tree: bool, show_toolbar: bool, toolbar_height: int, actionbar_height: int) -> PanelLayout:
        actionbar_height = min(actionbar_height, rect.height)
        toolbar_height = min(toolbar_height, rect.height - actionbar_height) if show_toolbar else 0
        tree_height = rect.height - toolbar_height -actionbar_height if show_tree else 0
        return cls(
            rect = rect,
            tree_rect = pygame.Rect(rect.x, rect.y, rect.width, tree_height),
            toolbar_rect = pygame.Rect(rect.x, rect.bottom - actionbar_height - toolbar_height, rect.width, toolbar_height),
            actionbar_rect = pygame.Rect(rect.x, rect.bottom - actionbar_height, rect.width, actionbar_height)
        )