from __future__ import annotations
from dataclasses import dataclass

import pygame

from gobts.client.ui.menu import Menu

BAR_HEIGHT = 22
PAD_X = 8

@dataclass
class MenuBarLayout:
    height: int
    title_rects: list[pygame.Rect]

    @classmethod
    def fit(cls, menus: list[Menu], font: pygame.font.Font) -> MenuBarLayout:
        rects = []
        x = 0
        for menu in menus:
            width = font.size(menu.label)[0] + 2*PAD_X 
            rects.append(pygame.Rect(x, 0, width, BAR_HEIGHT))
            x += width
        return cls(BAR_HEIGHT, rects)

    def title_at(self, pos: tuple[float, float]) -> int|None:
        for i, rect in enumerate(self.title_rects):
            if rect.collidepoint(pos):
                return i
        return None