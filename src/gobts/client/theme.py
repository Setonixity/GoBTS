from __future__ import annotations
from dataclasses import dataclass, field

RGB = tuple[int, int, int]

@dataclass
class BoardTheme:
    background_rgb: RGB = (222, 184, 106)
    line_rgb: RGB = (0, 0, 0)
    star_rgb: RGB = (0, 0, 0)
    
    black_rgb: RGB = (0, 0, 0)
    white_rgb: RGB = (255, 255, 255)
    stone_edge_rgb: RGB = (0, 0, 0)

    ghost_alpha: int = 100

    edge_cells: float = 1.3 # space b/w outer lines and window edge
    px_per_line: int = 800 # lines thickness +1px for about every this many px
    min_star_radius: int = 2
    star_radius: float = 0.1 # 10th of a cell

    stone_radius: float = 0.47 # of a cell
    stone_edge: float = 0.05 # of the stone radius. min = 1px

@dataclass
class Theme:
    board: BoardTheme = field(default_factory=BoardTheme)