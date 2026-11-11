from __future__ import annotations
from dataclasses import field, fields
from typing import Annotated, Optional
from pydantic.dataclasses import dataclass
from pathlib import Path
from pydantic import AfterValidator, TypeAdapter, field_validator

RGB = tuple[int, int, int]
DATA_DIR = Path(__file__).parents[3] / "data" / "gobts" # from src/gobts/client
FONTS_DIR =  DATA_DIR / "fonts"
THEMES_DIR =  DATA_DIR / "themes"
IMAGES_DIR = DATA_DIR / "images"

def _resolve_in(base_dir: Path):
    def validator(value: str | Path) -> Path:
        path = Path(value)
        return path if path.is_absolute() else base_dir / path
    return validator

FontPath = Annotated[str | Path, AfterValidator(_resolve_in(FONTS_DIR))]
ImagePath = Annotated[str | Path, AfterValidator(_resolve_in(IMAGES_DIR))]

@dataclass
class BoardTheme():
    background_rgb: Optional[RGB] = (222, 184, 106)
    line_rgb: Optional[RGB] = (0, 0, 0)
    star_rgb: Optional[RGB] = (0, 0, 0)

    black_rgb: Optional[RGB] = (0, 0, 0)
    white_rgb: Optional[RGB] = (255, 255, 255)
    stone_edge_rgb: Optional[RGB] = (0, 0, 0)

    ghost_alpha: Optional[int] = 100

    edge_cells: Optional[float] = 1.3 # space b/w outer lines and window edge
    px_per_line: Optional[int] = 800 # lines thickness +1px for about every this many px
    min_star_radius: Optional[int] = 2
    star_radius: Optional[float] = 0.1 # 10th of a cell

    stone_radius: Optional[float] = 0.47 # of a cell
    stone_edge: Optional[float] = 0.05 # of the stone radius. min = 1px

    marker_rgb: Optional[RGB] = (0, 0, 0)
    marker_on_black_rgb: Optional[RGB] = (255, 255, 255)
    # of stone radius
    marker_size: Optional[float] = 0.5 
    marker_width: Optional[float] = 0.12 # min = 1px
    marker_clear: Optional[float] = 0.75 
 
    label_font: FontPath = FONTS_DIR / "Ubuntu-Regular.ttf"
    label_size: Optional[float] = 1.2

@dataclass
class PanelTheme:
    background_rgb: Optional[RGB] = (33, 33, 33)
    width: Optional[int] = 240

@dataclass
class TreeTheme():
    line_rgb: Optional[RGB] = (100 , 255, 255)
    faded_line_rgb: Optional[RGB] = (100, 100, 100)
    background_rgb: Optional[RGB] = (33, 33, 33)

    node_edge_rgb: Optional[RGB] = (150, 150, 150)
    black_rgb: Optional[RGB] = (0, 0, 0)
    white_rgb: Optional[RGB] = (255, 255, 255)
    empty_rgb: Optional[RGB] = (90, 90, 90)
    faded_alpha: Optional[int] = 100 # nodes off the current line

    highlight_rgb: Optional[RGB] = (70, 70, 70)

    spacing: Optional[int] = 28 
    pad: Optional[int] = 20 # between outer nodes and panel edge
    scroll_margin: Optional[int] = 4 # rows kept before it changes page
    line_width: Optional[int] = 1
    node_radius: Optional[int] = 10
    node_edge_width: Optional[int] = 1
    highlight_radius: Optional[int] = 13
    highlight_corner: Optional[int] = 5

@dataclass
class ToolbarTheme:
    background_rgb: Optional[RGB] = (45, 45, 45)
    hover_rgb: Optional[RGB] = (60, 60, 60)
    selected_rgb: Optional[RGB] = (75, 75, 75)
    icon_rgb: Optional[RGB] = (255, 255, 255)
    # node_rgb: RGB = (90, 90, 90) # blank node icon
    # node_edge_rgb: RGB = (150, 150, 150)

    setup_icon: ImagePath = IMAGES_DIR / "setup.svg"
    triangle_cross_icon: ImagePath = IMAGES_DIR / "triangle-cross.svg"
    circle_square_icon: ImagePath = IMAGES_DIR / "circle_square.svg"
    letter_number_icon: ImagePath = IMAGES_DIR / "letter-number.svg"

    height: Optional[int] = 40
    button_size: Optional[int] = 36
    pad: Optional[int] = 4 
    icon_size: Optional[int] = 32
    node_radius: Optional[int] = 11
    node_edge_width: Optional[int] = 1

@dataclass
class MenuTheme:
    bar_rgb: Optional[RGB] = (33, 33, 33)
    dropdown_rgb: Optional[RGB] = (60, 60, 60)
    hover_rgb: Optional[RGB] = (100, 100, 100) # also title of opened menu
    text_rgb: Optional[RGB] = (255, 255, 255)

    font: FontPath = FONTS_DIR / "Ubuntu-Regular.ttf"
    font_size: Optional[int] = 13
    text_nudge: Optional[int] = -1 # moves labels up/down to look centered
    check_nudge: Optional[int] = 0
    check_icon: ImagePath = IMAGES_DIR / "tick.svg"
    check_size: Optional[int] = 12
    check_width: Optional[int] = 18 # room for check mark

    bar_height: Optional[int] = 24
    item_height: Optional[int] = 26
    pad_x: Optional[int] = 10
    min_dropdown_width: Optional[int] = 180

    dropdown_pad_y: Optional[int] = 6
    dropdown_corner: Optional[int] = 8

@dataclass
class Theme:
    board: BoardTheme = field(default_factory=BoardTheme)
    panel: PanelTheme = field(default_factory=PanelTheme)
    tree: TreeTheme = field(default_factory=TreeTheme)
    toolbar: ToolbarTheme = field(default_factory=ToolbarTheme)
    menu: MenuTheme = field(default_factory=MenuTheme)

    @classmethod
    def from_dir(cls, folder: str | Path) -> Theme:
        folder_path = Path(THEMES_DIR / folder)
        loaded: dict[str, object] = {}

        for f in fields(cls):
            json_file = folder_path / f"{f.name}_theme.json"
            if json_file.is_file():
                json_data = json_file.read_text(encoding="utf-8")
                loaded[f.name] = TypeAdapter(f.type).validate_json(json_data)

        return cls(**loaded)

    def load_board_theme_json(path):
        json_data = Path(path).read_text(encoding="utf-8")
        board_theme = TypeAdapter(BoardTheme).validate_json(json_data)
        return board_theme

    def load_panel_theme_json(path):
        json_data = Path(path).read_text(encoding="utf-8")
        panel_theme = TypeAdapter(PanelTheme).validate_json(json_data)
        return panel_theme

    def load_tree_theme_json(path):
        json_data = Path(path).read_text(encoding="utf-8")
        tree_theme = TypeAdapter(TreeTheme).validate_json(json_data)
        return tree_theme

    def load_toolbar_theme_json(path):
        json_data = Path(path).read_text(encoding="utf-8")
        toolbar_theme = TypeAdapter(ToolbarTheme).validate_json(json_data)
        return toolbar_theme

    def load_menu_theme_json(path):
        json_data = Path(path).read_text(encoding="utf-8")
        menu_theme = TypeAdapter(MenuTheme).validate_json(json_data)
        return menu_theme

# theme = Theme.from_dir("new_theme")
# print(theme.board.background_rgb)