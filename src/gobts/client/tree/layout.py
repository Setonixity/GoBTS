from __future__ import annotations

from dataclasses import dataclass
import math

import pygame

from gobts.sgf.node import SGFNode

SPACING = 28
PAD = 20
SCROLL_MARGIN = 4*SPACING

@dataclass
class TreeLayout:
    rect: pygame.Rect
    positions: dict[SGFNode, tuple[int, int]] # node -> (col, row)
    start_x: float
    start_y: float
    spacing: float

    @classmethod
    def fit(cls, root: SGFNode, focus: SGFNode, rect: pygame.Rect) -> TreeLayout:
        positions = grid_positions(root)
        cols = max(col for col, _ in positions.values()) + 1
        # rows = max(row for _, row in positions.values()) + 1
        focus_col, focus_row = positions[focus]
        scroll_x = scroll_offset((cols-1)*SPACING + 2*PAD, rect.width, PAD + focus_col*SPACING)
        # scroll_y = PAD + focus_row*SPACING - rect.height/2
        
        start_y = rect.y + PAD
        margin = min(SCROLL_MARGIN, rect.height/2)
        top, bottom = rect.top + margin, rect.bottom - margin
        page = max(2, int((bottom - top) / SPACING) // 2 * 2) * SPACING
        focus_y = start_y + focus_row*SPACING
        if focus_y > bottom:
            start_y -= math.ceil((focus_y - bottom) / page) * page
        elif focus_y < top:
            start_y += math.ceil((top - focus_y) / page) * page
        start_y = min(start_y, rect.y + PAD)
        return cls(
            rect = rect,
            positions = positions,
            start_x = rect.x + PAD - scroll_x,
            start_y = start_y,
            spacing = SPACING
        )

    def to_pixel(self, node: SGFNode) -> tuple[float, float]:
        col, row = self.positions[node]
        return (
            round(self.start_x + (col*self.spacing)),
            round(self.start_y + (row*self.spacing))
        )

def grid_positions(root: SGFNode) -> dict[SGFNode, tuple[int, int]]:
    positions: dict[SGFNode, tuple[int, int]] = {}
    next_free: list[int] = []
    to_place = [(root, 0, 0)]
    while to_place:
        node, col, row = to_place.pop()
        sequence = [node]
        while len(sequence[-1].children) == 1: # depth first
            sequence.append(sequence[-1].children[0])

        end_row = row + len(sequence)
        next_free.extend([0] * (end_row - len(next_free)))
        col = max([col] + next_free[row:end_row])
        if row > 0:
            next_free[row - 1] = max(next_free[row - 1], col)
        for i, step in enumerate(sequence):
            positions[step] = (col, row + i)
            next_free[row + i] = col + 1

        for child in reversed(sequence[-1].children):
            to_place.append((child, col, end_row))
    return positions

def scroll_offset(content: float, view: float, focus: float) -> float:
    return min(max(focus - view/2, 0), max(content - view, 0))