from __future__ import annotations

from pathlib import Path
import random

import pygame

from gobts.client.theme import SoundTheme

SOUND_TYPES = ("*.ogg", "*.mp3")

class SoundPlayer:
    def __init__(self, theme: SoundTheme):
        self.theme = theme
        self.stones = self.load_sounds(theme.stone_sounds)

    def play_stone(self):
        if self.stones:
            random.choice(self.stones).play()

    def load_sounds(self, folder: Path) -> list[pygame.mixer.Sound]:
        if not pygame.mixer.get_init() or not folder.is_dir():
            return []
        paths = sorted(path for pattern in SOUND_TYPES for path in folder.glob(pattern))
        sounds = [pygame.mixer.Sound(path) for path in paths]
        for sound in sounds:
            sound.set_volume(self.theme.volume)
        return sounds