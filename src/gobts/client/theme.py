from __future__ import annotations
from dataclasses import field
from pydantic.dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel, PositiveInt, TypeAdapter, field_validator
# from pydantic import BaseModel, PositiveInt

RGB = tuple[int, int, int]
DATA_DIR = Path(__file__).parents[3] / "data" / "gobts" # from src/gobts/client
FONTS_DIR =  DATA_DIR / "fonts"
THEMES_DIR =  DATA_DIR / "themes"
IMAGES_DIR = DATA_DIR / "images"


@dataclass
class BoardTheme():
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

    marker_rgb: RGB = (0, 0, 0)
    marker_on_black_rgb: RGB = (255, 255, 255)
    # of stone radius
    marker_size: float = 0.5 
    marker_width: float = 0.12 # min = 1px
    marker_clear: float = 0.75 
 
    label_font: str|Path = FONTS_DIR / "Ubuntu-Regular.ttf"
    label_size: float = 1.2

    @field_validator("label_font", mode="after")
    @classmethod
    def resolve_font_path(cls, value: str | Path) -> Path:
        path = Path(value)
        if not path.is_absolute():
            return FONTS_DIR / path
        return path

@dataclass
class PanelTheme:
    background_rgb: RGB = (33, 33, 33)
    width: int = 240

@dataclass
class TreeTheme():
    line_rgb: RGB = (100 , 255, 255)
    faded_line_rgb: RGB = (100, 100, 100)
    background_rgb: RGB = (33, 33, 33)

    node_edge_rgb: RGB = (150, 150, 150)
    black_rgb: RGB = (0, 0, 0)
    white_rgb: RGB = (255, 255, 255)
    empty_rgb: RGB = (90, 90, 90)
    faded_alpha: int = 100 # nodes off the current line

    highlight_rgb: RGB = (70, 70, 70)

    spacing: int = 28 
    pad: int = 20 # between outer nodes and panel edge
    scroll_margin: int = 4 # rows kept before it changes page
    line_width: int = 1
    node_radius: int = 10
    node_edge_width: int = 1
    highlight_radius: int = 13
    highlight_corner: int = 5

@dataclass
class ToolbarTheme:
    background_rgb: RGB = (45, 45, 45)
    hover_rgb: RGB = (60, 60, 60)
    selected_rgb: RGB = (75, 75, 75)
    icon_rgb: RGB = (255, 255, 255)
    # node_rgb: RGB = (90, 90, 90) # blank node icon
    # node_edge_rgb: RGB = (150, 150, 150)

    setup_icon: str|Path = IMAGES_DIR / "setup.svg"
    triangle_cross_icon: str|Path = IMAGES_DIR / "triangle-cross.svg"
    circle_square_icon: str|Path = IMAGES_DIR / "circle_square.svg"
    letter_number_icon: str|Path = IMAGES_DIR / "letter-number.svg"

    height: int = 40
    button_size: int = 36
    pad: int = 4 
    icon_size: int = 32
    node_radius: int = 11
    node_edge_width: int = 1

@dataclass
class MenuTheme:
    bar_rgb: RGB = (33, 33, 33)
    dropdown_rgb: RGB = (60, 60, 60)
    hover_rgb: RGB = (100, 100, 100) # also title of opened menu
    text_rgb: RGB = (255, 255, 255)

    font: str|Path = FONTS_DIR / "Ubuntu-Regular.ttf"
    font_size: int = 13
    text_nudge: int = -1 # moves labels up/down to look centered
    check_nudge: int = 0
    check_icon: str|Path = IMAGES_DIR / "tick.svg"
    check_size: int = 12
    check_width: int = 18 # room for check mark

    bar_height: int = 24
    item_height: int = 26
    pad_x: int = 10
    min_dropdown_width: int = 180

    dropdown_pad_y: int = 6
    dropdown_corner: int = 8

@dataclass
class Theme:
    board: BoardTheme = field(default_factory=BoardTheme)
    panel: PanelTheme = field(default_factory=PanelTheme)
    tree: TreeTheme = field(default_factory=TreeTheme)
    toolbar: ToolbarTheme = field(default_factory=ToolbarTheme)
    menu: MenuTheme = field(default_factory=MenuTheme)

def load_board_theme_json(x):
    json_data = Path(x).read_text(encoding="utf-8")
    board_theme = TypeAdapter(BoardTheme).validate_json(json_data)
    return board_theme

def load_panel_theme_json(x):
    json_data = Path(x).read_text(encoding="utf-8")
    panel_theme = TypeAdapter(PanelTheme).validate_json(json_data)
    return panel_theme

def load_tree_theme_json(x):
    json_data = Path(x).read_text(encoding="utf-8")
    tree_theme = TypeAdapter(TreeTheme).validate_json(json_data)
    return tree_theme

def load_toolbar_theme_json(x):
    json_data = Path(x).read_text(encoding="utf-8")
    toolbar_theme = TypeAdapter(ToolbarTheme).validate_json(json_data)
    return toolbar_theme

def load_menu_theme_json(x):
    json_data = Path(x).read_text(encoding="utf-8")
    menu_theme = TypeAdapter(MenuTheme).validate_json(json_data)
    return menu_theme

board_theme = load_board_theme_json(THEMES_DIR / "board_theme.json")
print(board_theme.line_rgb)
print(board_theme.label_font)