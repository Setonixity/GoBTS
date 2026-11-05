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
        self.sprites: dict[tuple[Color|None, bool], pygame.Surface] = {}

        for color, rgb in ((Color.BLACK, (0, 0, 0)), (Color.WHITE, (255, 255, 255)), (None, (30, 30, 30))):
            sprite = self.make_sprite(rgb)
            faded = sprite.copy()
            faded.set_alpha(100)
            self.sprites[(color, False)] = sprite
            self.sprites[(color, True)] = faded

    def draw(self, surface: pygame.Surface, current: SGFNode|None = None):
        layout = self.layout
        path: set[SGFNode] = set(current.main_line()) if current != None else set()
        node = current
        while node != None: # back to root
            path.add(node)
            node = node.parent

        pygame.draw.rect(surface, (128, 128, 128), layout.rect)
        clip = surface.get_clip()
        surface.set_clip(layout.rect)

        for node in layout.positions:
            color = Color.BLACK if "B" in node else Color.WHITE if "W" in node else None
            x, y = layout.to_pixel(node)
            surface.blit(self.sprites[(color, node not in path)], (x - STONE_RADIUS, y - STONE_RADIUS))
        surface.set_clip(clip)

    def make_sprite(self, rgb: tuple[int, int, int]) -> pygame.Surface:
        size = STONE_RADIUS*2 + 1
        ss_size = size*SUPERSAMPLE
        big = pygame.Surface((ss_size, ss_size), pygame.SRCALPHA)
        pygame.draw.circle(big, rgb, (ss_size/2, ss_size/2), STONE_RADIUS*SUPERSAMPLE)
        return pygame.transform.smoothscale(big, (size, size))