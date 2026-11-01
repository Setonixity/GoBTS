from __future__ import annotations

import pygame

from gobts.client.board.layout import BoardLayout
from gobts.core.board import *

class BoardRenderer:

    def __init__(self, board: Board, layout: BoardLayout):
        self.board = board
        self.layout = layout
        self._sprite_cache: dict[tuple[Color, float], pygame.Surface] = {}
        self._cached_radius: float|None = None

    def draw(self, surface: pygame.Surface, ghost_preview: tuple[Point, Color]|None = None):
        layout = self.layout
        size = layout.size

        surface.fill((222, 184, 106))
        line_width = layout.line_width

        for i in range(size):
            pygame.draw.line(surface, (0, 0, 0), layout.to_pixel(Point(i, 0)), layout.to_pixel(Point(i, size-1)), line_width)
            pygame.draw.line(surface, (0, 0, 0), layout.to_pixel(Point(0, i)), layout.to_pixel(Point(size-1, i)), line_width)
    

        radius = layout.stone_radius()
        for point, color in self.board.stones:
            x, y = layout.to_pixel(point)
            surface.blit(self._stone_sprite(color, radius), (x - radius, y - radius))
        if ghost_preview != None and self.board.is_empty(ghost_preview[0]):
            x, y = layout.to_pixel(ghost_preview[0])
            sprite = self._stone_sprite(ghost_preview[1], radius).copy()
            sprite.set_alpha(100)
            surface.blit(sprite, (x - radius, y - radius))

    def draw_ascii(self):
        CORNERS = ["┌", "┐", "└", "┘"] # TL, TR, BL, BR
        EDGES = ["┬", "┴", "├", "┤"] # T, B, L, R
        CENTER       = "┼"
        STAR_POINT   = "⊕"
        HORIZONTAL   = "─"
        BLACK = "●"
        WHITE = "○"

        board = self.board
        stone_map: dict[Point, Color] = dict(board.stones)
        star_map: list[Point] = star_points(board.size)
        # print(stone_map)

        for row in range(board.size):
            row_chars = []
            for col in range(board.size):
                point = Point(col, row)
                char = ""
                if point in stone_map:
                    char = BLACK if stone_map[point] == Color.BLACK else WHITE
                elif point in star_map:
                    char = STAR_POINT

                elif point == Point(0, 0):
                    char = CORNERS[0]
                elif point == Point(board.size - 1, 0):
                    char = CORNERS[1]
                elif point == Point(0, board.size - 1):
                    char = CORNERS[2]
                elif point == Point(board.size - 1, board.size -1):
                    char = CORNERS[3]

                elif row == 0:
                    char = EDGES[0]
                elif row == board.size - 1:
                    char = EDGES[1]
                elif col == 0:
                    char = EDGES[2]
                elif col == board.size - 1:
                    char = EDGES[3]                    

                else:
                    char = CENTER
                row_chars.append(char)
            print(HORIZONTAL.join(row_chars))

    def _stone_sprite(self, color: Color, radius: float) -> pygame.Surface:
        if radius != self._cached_radius:
            self._sprite_cache.clear()
            self._cached_radius = radius

        _supersampled = 8
        edge_color = (0,0,0)
        fill_color = (0,0,0) if color == Color.BLACK else (255, 255, 255)
        sprite = self._sprite_cache.get((color, radius))
        if sprite == None:
            size = radius*2 + 1
            ss_size = size*_supersampled
            big = pygame.Surface((ss_size, ss_size), pygame.SRCALPHA)
            center = (ss_size/2, ss_size/2)
            edge = max(1, radius*0.05) * _supersampled
            pygame.draw.circle(big, edge_color, center, radius*_supersampled)
            pygame.draw.circle(big, fill_color, center, radius*_supersampled - edge)
            sprite = pygame.transform.smoothscale(big, (size, size))
            self._sprite_cache[(color, radius)] = sprite
        return sprite



def star_points(size: int = 19) -> list[Point]:
    """
    Note: My idea is:
    corners and size only for > 7
    shift corners down to 3-3 from < size 12
    sides only from odd >= size 15
    tengen only for odd sizes except 1

    Might change later, the one in 'Sabaki' has sides at like 13x13 but in my go experience, that's not common and it doesn't look that good
    """
    _star_points = []
    
    if size > 7:
        from_corner = 2 if size < 12 else 3
        far_corner = size - from_corner - 1

        #side
        if size % 2 == 1 and size >= 15:
            mid = size // 2
            for point in [Point(mid, from_corner), Point(from_corner, mid), Point(mid, far_corner), Point(far_corner, mid)]:
                _star_points.append(point)

        #corner
        for point in [Point(from_corner, from_corner), Point(from_corner, far_corner), Point(far_corner, from_corner), Point(far_corner, far_corner)]:
            _star_points.append(point)

    if size % 2 == 1 and size > 1: # tengen
        _star_points.append(Point(size // 2, size // 2))
    return _star_points

# board = Board(19)
# board.set(Point(0,0), Color.BLACK)
# board.set(Point(2,2), Color.WHITE)
# BoardRenderer().draw_ascii(board)
