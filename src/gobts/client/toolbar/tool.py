from __future__ import annotations
from enum import Enum

from gobts.core.board import Color, Marker

class Tool(Enum):
    SETUP = (Color.BLACK, Color.WHITE) 
    TRIANGLE_CROSS = (Marker.TRIANGLE, Marker.CROSS)
    CIRCLE_SQUARE = (Marker.CIRCLE, Marker.SQUARE)

    def __init__(self, left: Color|Marker, right: Color|Marker): 
        self.left = left
        self.right = right