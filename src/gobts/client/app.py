from __future__ import annotations

from gobts.client.board import *
from gobts.core import *

import pygame

WINDOW_TITLE = "GO TO FUCKING SLEEP"
WINDOW_SIZE = (800, 800)
FPS = 60

REDRAW_EVENTS = {pygame.VIDEORESIZE, pygame.WINDOWSIZECHANGED, pygame.WINDOWEXPOSED}

class ClientApp:
    def __init__(self, size: int = 19):
        self.size = size
        self.board = Board(size)
        self.board.set(Point(3, 3), Color.BLACK)
        self.board.set(Point(3, 4), Color.WHITE)
        self.color_to_play = Color.BLACK

    def run(self):
        pygame.init()
        pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption(WINDOW_TITLE)

        layout_size = None
        self.renderer = BoardRenderer(self.board, BoardLayout.fit(self.size, *WINDOW_SIZE))

        running = True
        needs_redraw = True
        while running:
            if not needs_redraw:
                events = [pygame.event.wait(), *pygame.event.get()]
            else:
                events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type in REDRAW_EVENTS:
                    needs_redraw = True
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.on_click(self.renderer.layout.to_point(*event.pos))
                    needs_redraw = True


            if needs_redraw:
                screen = pygame.display.get_surface()
                if screen.get_size() != layout_size:
                    layout_size = screen.get_size()
                    self.renderer.layout = BoardLayout.fit(self.size, * layout_size)
                self.renderer.draw(screen)
                pygame.display.flip()
                needs_redraw = False
            
        pygame.quit()

    def on_click(self, point: Point|None):
        if point == None:
            return
        play(self.board, point, self.color_to_play)
        self.color_to_play = self.color_to_play.switch()
    

ClientApp().run()
