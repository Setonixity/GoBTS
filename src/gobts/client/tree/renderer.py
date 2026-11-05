from __future__ import annotations
import math

import pygame

from gobts.client.tree.layout import TreeLayout
from gobts.core.board import Color
from gobts.sgf.node import SGFNode

STONE_RADIUS = 10
HIGHLIGHT_RADIUS, HIGHLIGHT_CORNER, HIGHLIGHT_RGB = 13, 5, (70, 70, 70)
LINE_WIDTH = 1
SUPERSAMPLE = 8

class TreeRenderer:

    def __init__(self, layout: TreeLayout):
        self.layout = layout
        self.sprites: dict[tuple[Color|None, bool], pygame.Surface] = {}
        self.backing = self.make_node_sprite((33,33,33), edge_rgb=(33,33,33))

        for color, rgb in ((Color.BLACK, (0, 0, 0)), (Color.WHITE, (255, 255, 255)), (None, (30, 30, 30))):
            sprite = self.make_node_sprite(rgb)
            faded = sprite.copy()
            faded.set_alpha(100)
            self.sprites[(color, False)] = sprite
            self.sprites[(color, True)] = faded

        size = HIGHLIGHT_RADIUS*2 + 1
        ss_size = size*SUPERSAMPLE
        big = pygame.Surface((ss_size, ss_size), pygame.SRCALPHA)
        big.fill((*HIGHLIGHT_RGB, 0))
        pygame.draw.rect(big, HIGHLIGHT_RGB, (0, 0, ss_size, ss_size), border_radius=HIGHLIGHT_CORNER*SUPERSAMPLE)
        self.highlight = pygame.transform.smoothscale(big, (size, size))

    def draw(self, surface: pygame.Surface, current: SGFNode|None = None):
        layout = self.layout
        path: set[SGFNode] = set(current.main_line()) if current != None else set()
        node = current
        while node != None: # back to root
            path.add(node)
            node = node.parent

        pygame.draw.rect(surface, (33,33,33), layout.rect)
        clip = surface.get_clip()
        surface.set_clip(layout.rect)

        if current != None:
            x, y = layout.to_pixel(current)
            surface.blit(self.highlight, (x - HIGHLIGHT_RADIUS, y - HIGHLIGHT_RADIUS))

        lines = [(parent, child) for parent in layout.positions for child in parent.children]
        for parent, child in lines:
            x0, y0 = layout.to_pixel(parent)
            x1, y1 = layout.to_pixel(child)
            rgb = (255, 255, 255) if child in path else (100, 100, 100)
            if x0 == x1:
                self.draw_line(surface, rgb, (x0, y0), (x1, y1))
            else:
                bend = (round(x1 - layout.spacing), y0)
                if bend[0] != x0:
                    self.draw_line(surface, rgb, (x0, y0), bend)
                self.draw_line(surface, rgb, bend, (x1, y1))

        for node in layout.positions:
            color = Color.BLACK if "B" in node else Color.WHITE if "W" in node else None
            x, y = layout.to_pixel(node)
            pos = (x - STONE_RADIUS, y - STONE_RADIUS)
            surface.blit(self.backing, pos)
            surface.blit(self.sprites[(color, node not in path)], pos)
        surface.set_clip(clip)

    def make_node_sprite(self, rgb: tuple[int, int, int], edge_rgb: tuple[int, int, int] = (150, 150, 150)) -> pygame.Surface:
        size = STONE_RADIUS*2 + 1
        ss_size = size*SUPERSAMPLE
        big = pygame.Surface((ss_size, ss_size), pygame.SRCALPHA)
        big.fill((*edge_rgb, 0))
        edge_width = 1
        pygame.draw.circle(big, edge_rgb, (ss_size/2, ss_size/2), STONE_RADIUS*SUPERSAMPLE)
        pygame.draw.circle(big, rgb, (ss_size/2, ss_size/2), STONE_RADIUS*SUPERSAMPLE - edge_width*SUPERSAMPLE)
        return pygame.transform.smoothscale(big, (size, size))

    def draw_line(self, surface: pygame.Surface, rgb: tuple[int, int, int], start: tuple[float, float], end: tuple[float, float]):
        pygame.draw.line(surface, rgb, start, end, LINE_WIDTH)