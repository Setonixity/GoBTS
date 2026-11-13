from __future__ import annotations

from dataclasses import dataclass

import pygame

from gobts.client.actionbar.action import Action
from gobts.client.theme import ActionBarTheme

@dataclass
class ActionBarLayout:
    rect: pygame.Rect
    button_rects: dict[Action, pygame.Rect]

    @classmethod
    def fit(cls, rect: pygame.Rect, theme: ActionBarTheme) -> ActionBarLayout:
        width, height, pad = theme.button_width, theme.button_height, theme.pad
        buttons_width = len(Action)*width + (len(Action) - 1)*pad
        x = rect.centerx - buttons_width // 2
        y = rect.centery - height // 2
        return cls(
            rect = rect,
            button_rects = {action: pygame.Rect(x + i*(width + pad), y, width, height) for i, action in enumerate(Action)}
        )

    def to_action(self, px: float, py: float) -> Action|None:
        if not self.rect.collidepoint(px, py):
            return None
        for action, rect in self.button_rects.items():
            if rect.collidepoint(px, py):
                return action
        return None