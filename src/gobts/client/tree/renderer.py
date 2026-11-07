from __future__ import annotations

import pygame

from gobts.client.tree.layout import TreeLayout
from gobts.core.board import Color
from gobts.sgf.node import SGFNode
from gobts.client.theme import RGB, TreeTheme

SUPERSAMPLE = 8

class TreeRenderer:

    def __init__(self, layout: TreeLayout, theme: TreeTheme):
        self.layout = layout
        self.theme = theme
        self.sprites: dict[tuple[Color|None, bool], pygame.Surface] = {}
        self.backing = self.make_node_sprite(theme.background_rgb, theme.background_rgb)

        for color, rgb in ((Color.BLACK, theme.black_rgb), (Color.WHITE, theme.white_rgb), (None, theme.empty_rgb)):
            sprite = self.make_node_sprite(rgb, theme.node_edge_rgb)
            faded = sprite.copy()
            faded.set_alpha(theme.faded_alpha)
            self.sprites[(color, False)] = sprite
            self.sprites[(color, True)] = faded

        self.highlight = self.make_highlight_sprite()

    def draw(self, surface: pygame.Surface, current: SGFNode|None = None):
        layout = self.layout
        theme = self.theme
        path: set[SGFNode] = set(current.main_line()) if current != None else set()
        node = current
        while node != None: # back to root
            path.add(node)
            node = node.parent

        pygame.draw.rect(surface, theme.background_rgb, layout.rect)
        clip = surface.get_clip()
        surface.set_clip(layout.rect)

        if current != None:
            x, y = layout.to_pixel(current)
            surface.blit(self.highlight, (x - theme.highlight_radius, y - theme.highlight_radius))

        lines = [(parent, child) for parent in layout.positions for child in parent.children]
        for parent, child in lines:
            x0, y0 = layout.to_pixel(parent)
            x1, y1 = layout.to_pixel(child)
            rgb = theme.line_rgb if child in path else theme.faded_line_rgb
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
            pos = (x - theme.node_radius, y - theme.node_radius)
            surface.blit(self.backing, pos)
            surface.blit(self.sprites[(color, node not in path)], pos)
        surface.set_clip(clip)

    def make_node_sprite(self, rgb: RGB, edge_rgb: RGB) -> pygame.Surface:
        radius, edge_width = self.theme.node_radius, self.theme.node_edge_width
        size = radius*2 + 1
        ss_size = size*SUPERSAMPLE
        big = pygame.Surface((ss_size, ss_size), pygame.SRCALPHA)
        big.fill((*edge_rgb, 0))
        pygame.draw.circle(big, edge_rgb, (ss_size/2, ss_size/2), radius*SUPERSAMPLE)
        pygame.draw.circle(big, rgb, (ss_size/2, ss_size/2), radius*SUPERSAMPLE - edge_width*SUPERSAMPLE)
        return pygame.transform.smoothscale(big, (size, size))

    def make_highlight_sprite(self) -> pygame.Surface:
        theme = self.theme
        size = theme.highlight_radius*2 + 1
        ss_size = size*SUPERSAMPLE
        big = pygame.Surface((ss_size, ss_size), pygame.SRCALPHA)
        big.fill((*theme.highlight_rgb, 0))
        pygame.draw.rect(big, theme.highlight_rgb, (0, 0, ss_size, ss_size), border_radius=theme.highlight_corner*SUPERSAMPLE)
        return pygame.transform.smoothscale(big, (size, size))

    def draw_line(self, surface: pygame.Surface, rgb: RGB, start: tuple[float, float], end: tuple[float, float]):
        pygame.draw.line(surface, rgb, start, end, self.theme.line_width)