from __future__ import annotations
from pathlib import Path
import sys

from platformdirs import PlatformDirs

APP_NAME = "gobts"

# built-in 
if getattr(sys, "frozen", False): 
    BUNDLE_DIR = Path(sys._MEIPASS) 
else:
    BUNDLE_DIR = Path(__file__).parents[3] # src/gobts/client
DATA_DIR = BUNDLE_DIR / "data" / "gobts"
FONTS_DIR = DATA_DIR / "fonts"
THEMES_DIR = DATA_DIR / "themes"
IMAGES_DIR = DATA_DIR / "images"
SOUNDS_DIR = DATA_DIR / "sounds"

# per-user
USER_DIRS = PlatformDirs(APP_NAME, appauthor=False)
USER_DATA_DIR = USER_DIRS.user_data_path
USER_THEMES_DIR = USER_DATA_DIR / "themes"
STATE_FILE = USER_DIRS.user_state_path / "state.json"