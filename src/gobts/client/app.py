from __future__ import annotations

from gobts.client.board import *
from gobts.core import *

import pygame

WINDOW_TITLE = "GO TO FUCKING SLEEP"
WINDOW_SIZE = (800, 800)
FPS = 60

class ClientApp:
    def __init__(self, size: int = 19):
        self.size = size
        self.board = Board(size)
        self.color_to_play = Color.BLACK

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption(WINDOW_TITLE)
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            width, height = screen.get_size()
            self.layout = BoardLayout.fit(self.size, width, height)
            self.renderer = BoardRenderer(self.board, self.layout)
            self.renderer.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()
    

ClientApp().run()
