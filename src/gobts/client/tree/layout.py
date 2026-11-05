from __future__ import annotations

from dataclasses import dataclass

import pygame

from gobts.sgf.node import SGFNode

SPACING = 22
PAD = 22

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
        rows = max(row for _, row in positions.values()) + 1
        focus_col, focus_row = positions[focus]
        scroll_x = scroll_offset((cols-1)*SPACING + 2*PAD, rect.width, PAD + focus_col*SPACING)
        scroll_y = scroll_offset((rows-1)*SPACING + 2*PAD, rect.height, PAD + focus_row*SPACING)
        return cls(
            rect = rect,
            positions = positions,
            start_x = rect.x + PAD - scroll_x,
            start_y = rect.y + PAD - scroll_y,
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