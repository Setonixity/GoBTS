from __future__ import annotations

from pathlib import Path
import random

import numpy
import pygame

from gobts.client.theme import SoundTheme

SOUND_TYPES = ("*.ogg", "*.mp3", "*.oga")

class SoundPlayer:
    def __init__(self, theme: SoundTheme):
        self.theme = theme
        self.stones = self.load_sounds(theme.stone_sounds)
        self.last_stone: int|None = None

    def play_stone(self):
        if not self.stones:
            return
        choices = [i for i in range(len(self.stones)) if i != self.last_stone] or [self.last_stone]
        self.last_stone = random.choice(choices)
        self.play(self.stones[self.last_stone])

    def play(self, samples: numpy.ndarray):
        min = self.theme.pitch_variance_min
        max = self.theme.pitch_variance_max
        sound = self.pitch_shift(samples, random.uniform(min, max))
        sound.set_volume(self.theme.volume)
        sound.play()

    def load_sounds(self, folder: Path) -> list[pygame.mixer.Sound]:
        if not pygame.mixer.get_init() or not folder.is_dir():
            return []
        paths = sorted(path for pattern in SOUND_TYPES for path in folder.glob(pattern))
        return [pygame.sndarray.array(pygame.mixer.Sound(path)) for path in paths]

    def pitch_shift(self, samples: numpy.ndarray, semitones: float) -> pygame.mixer.Sound:
        ratio = 2**(semitones / 12)
        frames = numpy.arange(len(samples))
        positions = numpy.arange(0, len(samples) - 1, ratio)
        channels = samples.reshape(len(samples), -1).T
        shifted = numpy.stack([numpy.interp(positions, frames, channel) for channel in channels], axis=-1)
        return pygame.sndarray.make_sound(shifted.reshape(len(positions), *samples.shape[1:]).astype(samples.dtype))