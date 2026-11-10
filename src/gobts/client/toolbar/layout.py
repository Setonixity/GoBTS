from __future__ import annotations
from dataclasses import dataclass

import pygame

from gobts.client.theme import ToolbarTheme
from gobts.client.toolbar.tool import Tool

@dataclass
class ToolbarLayout:
    rect: pygame.Rect
    button_rects: dict[Tool, pygame.Rect]

    @classmethod
    def fit(cls, rect: pygame.Rect, theme: ToolbarTheme) -> ToolbarLayout:
        size, pad = theme.button_size, theme.pad
        y = rect.centery - size // 2
        return cls(
            rect = rect,
            button_rects = {tool: pygame.Rect(rect.x + pad + i*(size + pad), y, size, size) for i, tool in enumerate(Tool)}
        )

    def to_tool(self, px: float, py: float) -> Tool|None:
        if not self.rect.collidepoint(px, py):
            return None
        for tool, rect in self.button_rects.items():
            if rect.collidepoint(px, py):
                return tool
        return None