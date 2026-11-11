from __future__ import annotations
from dataclasses import dataclass
import math

import pygame

from gobts.client.theme import BoardTheme
from gobts.core.board import *

@dataclass
class BoardLayout:
    rect: pygame.Rect
    size: int
    start_x: float
    start_y: float
    line_width: int
    spacing: float
    stone_radius: int

    @classmethod
    def fit(cls, size, width, height, theme: BoardTheme, top: float = 0) -> BoardLayout:
        cells_across = (size - 1) + (2 * theme.edge_cells)
        spacing = max(1.0, (min(width, height) / cells_across))
        gridpx_across = (size - 1) * spacing
        boardpx_across = round(cells_across * spacing)
        rect = pygame.Rect(0, 0, boardpx_across, boardpx_across)
        rect.center = (round(width / 2), round(top + height / 2))
        return cls(
            rect = rect,
            size = size,
            start_x = (width - gridpx_across) / 2,
            start_y = top + (height - gridpx_across) / 2,
            line_width = max(1, round(min(width, height) / theme.px_per_line)),
            spacing = spacing,
            stone_radius = int(spacing * theme.stone_radius)
        )

    def to_pixel(self, point: Point) -> tuple[float, float]:
        return (
            round(self.start_x + (point.x*self.spacing)),
            round(self.start_y + (point.y*self.spacing))
        )

    def to_point(self, px: float, py: float) -> Point|None:
        x = math.floor((px - self.start_x) / self.spacing + 0.5)
        y = math.floor((py - self.start_y) / self.spacing + 0.5)
        if 0 <= x < self.size and 0 <= y < self.size:
            return Point(x, y)
        return None