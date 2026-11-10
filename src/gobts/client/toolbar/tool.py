from __future__ import annotations
from enum import Enum

from gobts.core.board import Color, Label, Marker

class Tool(Enum):
    SETUP = (Color.BLACK, Color.WHITE) 
    TRIANGLE_CROSS = (Marker.TRIANGLE, Marker.CROSS)
    CIRCLE_SQUARE = (Marker.CIRCLE, Marker.SQUARE)
    LETTER_NUMBER = (Label.LETTER, Label.NUMBER)

    def __init__(self, left: Color|Marker|Label, right: Color|Marker|Label|None):
        self.left = left
        self.right = right