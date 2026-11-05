from __future__ import annotations

import pygame

from gobts.client.tree.layout import TreeLayout
from gobts.core.board import Color
from gobts.sgf.node import SGFNode

STONE_RADIUS = 10
SUPERSAMPLE = 8

class TreeRenderer:

    def __init__(self, layout: TreeLayout):
        self.layout = layout
        self.sprites = {
            Color.BLACK: self.make_sprite((0, 0, 0)),
            Color.WHITE: self.make_sprite((255, 255, 255)),
            None: self.make_sprite((30, 30, 30)),
        }

    def draw(self, surface: pygame.Surface):
        layout = self.layout
        pygame.draw.rect(surface, (128, 128, 128), layout.rect)
        clip = surface.get_clip()
        surface.set_clip(layout.rect)
        for node in layout.positions:
            color = Color.BLACK if "B" in node else Color.WHITE if "W" in node else None
            x, y = layout.to_pixel(node)
            surface.blit(self.sprites[color], (x - STONE_RADIUS, y - STONE_RADIUS))
        surface.set_clip(clip)

    def make_sprite(self, rgb: tuple[int, int, int]) -> pygame.Surface:
        size = STONE_RADIUS*2 + 1
        ss_size = size*SUPERSAMPLE
        big = pygame.Surface((ss_size, ss_size), pygame.SRCALPHA)
        pygame.draw.circle(big, rgb, (ss_size/2, ss_size/2), STONE_RADIUS*SUPERSAMPLE)
        return pygame.transform.smoothscale(big, (size, size))