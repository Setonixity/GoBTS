from __future__ import annotations
from dataclasses import dataclass
import math

from gobts.core.board import *

EDGE_CELL = 1.3

@dataclass
class BoardLayout:
    size: int
    start_x: float
    start_y: float
    line_width: int
    spacing: float

    @classmethod
    def fit(cls, size, width, height) -> BoardLayout:
        cells_across = (size - 1) + (2 * EDGE_CELL)
        spacing = max(1.0, (min(width, height) / cells_across))
        gridpx_across = (size - 1) * spacing
        return cls(
            size = size,
            start_x = (width - gridpx_across) / 2,
            start_y = (height - gridpx_across) / 2,
            line_width = 1,
            spacing = spacing
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

    def stone_radius(self) -> float:
        return int(self.spacing * (0.5 - 0.03))