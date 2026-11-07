from __future__ import annotations

from dataclasses import dataclass
import math

import pygame

from gobts.sgf.node import SGFNode
from gobts.client.theme import TreeTheme

@dataclass
class TreeLayout:
    rect: pygame.Rect
    positions: dict[SGFNode, tuple[int, int]] # node -> (col, row)
    start_x: float
    start_y: float
    spacing: float

    @classmethod
    def fit(cls, root: SGFNode, focus: SGFNode, rect: pygame.Rect, theme: TreeTheme) -> TreeLayout:
        positions = grid_positions(root)
        focus_col, focus_row = positions[focus]
        spacing, pad = theme.spacing, theme.pad
        
        start_y = rect.y + pad
        margin = min(theme.scroll_margin*spacing, rect.height/2)
        top, bottom = rect.top + margin, rect.bottom - margin
        page = max(2, int((bottom - top) / spacing) // 2 * 2) * spacing

        focus_y = start_y + focus_row*spacing
        if focus_y > bottom:
            start_y -= math.ceil((focus_y - bottom) / page) * page
        elif focus_y < top:
            start_y += math.ceil((top - focus_y) / page) * page
        start_y = min(start_y, rect.y + pad)

        visible = [focus_col] + [col for col, row in positions.values() if rect.top - spacing/2 < start_y + row*spacing < rect.bottom + spacing/2]
        first_col, last_col = min(visible), max(visible)
        scroll_x = scroll_offset((last_col - first_col)*spacing + 2*pad, rect.width, pad + (focus_col - first_col)*spacing, pad)

        return cls(
            rect = rect,
            positions = positions,
            start_x = rect.x + pad - first_col*spacing - scroll_x,
            start_y = start_y,
            spacing = spacing
        )

    def to_pixel(self, node: SGFNode) -> tuple[float, float]:
        col, row = self.positions[node]
        return (
            round(self.start_x + (col*self.spacing)),
            round(self.start_y + (row*self.spacing))
        )

    def to_node(self, px: float, py: float) -> SGFNode|None:
        if not self.rect.collidepoint(px, py):
            return None
        col = math.floor((px - self.start_x) / self.spacing + 0.5)
        row = math.floor((py - self.start_y) / self.spacing + 0.5)
        for node, cell in self.positions.items():
            if cell == (col, row):
                return node
        return None

    def row_neighbor(self, node: SGFNode, step: int) -> SGFNode|None:
        if node not in self.positions:
            return None
        _, row = self.positions[node]
        nodes_in_row = (n for n, (_, r) in self.positions.items() if r == row)
        row_nodes = sorted(nodes_in_row, key=lambda n: self.positions[n][0])
        i = row_nodes.index(node) + step
        if 0 <= i < len(row_nodes):
            return row_nodes[i]
        return None

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

def scroll_offset(content: float, view: float, focus: float, pad: float) -> float:
    if content <= view: 
        return (content - view) / 2
    return max(focus + pad - view, 0)