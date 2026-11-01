from __future__ import annotations
from dataclasses import dataclass

from gobts.core import *

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

    def stone_radius(self) -> float:
        return int(self.spacing * (0.5 - 0.04))