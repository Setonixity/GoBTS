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
class TreeTheme:
    line_rgb: RGB = (255, 255, 255)
    faded_line_rgb: RGB = (100, 100, 100)
    background_rgb: RGB = (33, 33, 33)

    node_edge_rgb: RGB = (150, 150, 150)
    black_rgb: RGB = (0, 0, 0)
    white_rgb: RGB = (255, 255, 255)
    empty_rgb: RGB = (90, 90, 90)
    faded_alpha: int = 100 # nodes off the current line

    highlight_rgb: RGB = (70, 70, 70)

    width: int = 240
    spacing: int = 28 
    pad: int = 20 # between outer nodes and panel edge
    scroll_margin: int = 4 # rows kept before it changes page
    line_width: int = 1
    node_radius: int = 10
    node_edge_width: int = 1
    highlight_radius: int = 13
    highlight_corner: int = 5
    

@dataclass
class Theme:
    board: BoardTheme = field(default_factory=BoardTheme)
    tree: TreeTheme = field(default_factory=TreeTheme)