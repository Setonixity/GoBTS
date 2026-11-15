from __future__ import annotations
from pathlib import Path

from gobts.client.actionbar.action import Action
from gobts.client.actionbar.layout import ActionBarLayout
from gobts.client.actionbar.renderer import ActionBarRenderer
from gobts.client.board.layout import BoardLayout
from gobts.client.board.renderer import BoardRenderer
from gobts.client.comment.layout import CommentLayout
from gobts.client.comment.renderer import CommentRenderer
from gobts.client.panel.layout import PanelLayout
from gobts.client.panel.renderer import PanelRenderer
from gobts.client.paths import USER_THEMES_DIR
from gobts.client.sound import SoundPlayer
from gobts.client.state import State
from gobts.client.theme import Theme
from gobts.client.toolbar.layout import ToolbarLayout
from gobts.client.toolbar.renderer import ToolbarRenderer
from gobts.client.toolbar.tool import Tool
from gobts.client.tree.layout import TreeLayout
from gobts.client.tree.renderer import TreeRenderer
from gobts.client.ui.menu import Menu, MenuItem
from gobts.client.ui.menubar import MenuBar
from gobts.client.ui.renderer import UIRenderer
from gobts.core.board import Board, Color, Label, Marker, Point
from gobts.sgf.node import SGFNode

import gobts.client.ui.dialogs as dialogs
import gobts.core.rules as rules
import gobts.core.scoring as scoring
import gobts.sgf.converter as converter
import gobts.sgf.parser as parser
import gobts.sgf.writer as writer

import pygame
from pygame._sdl2.video import Window

WINDOW_TITLE = "GOBTS - Go: Back To Sleep"
PANEL_WIDTH = 240
WINDOW_SIZE = (800 + PANEL_WIDTH, 822)
FPS = 60

REDRAW_EVENTS = {pygame.VIDEORESIZE, pygame.WINDOWSIZECHANGED, pygame.WINDOWEXPOSED, pygame.MOUSEMOTION}

class ClientApp:
    def __init__(self, size: int = 19):
        pygame.init()
        self.window = Window(WINDOW_TITLE, WINDOW_SIZE, resizable=True)
        pygame.key.set_repeat(300, 50)
        self.maximized = False
        self.layout_size = None

        self.size = size
        self.board = Board(size)
        self.state = State.load()
        self.theme_names = Theme.available_themes()
        self.theme_name: str|None = None
        self.theme = Theme()
        self.show_panel = True
        self.show_tree = True
        self.show_comment = True
        self.show_toolbar = True
        self.tool: Tool|None = None
        self.new_game()
        self.set_theme(self.state.theme if self.state.theme in self.theme_names else None)
        self.restore_game()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        needs_redraw = True
        while running:
            if needs_redraw:
                events = pygame.event.get()
            else:
                events = [pygame.event.wait(), *pygame.event.get()]

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif self.handle_event(event):
                    needs_redraw = True

            if needs_redraw:
                self.draw()
                needs_redraw = self.board_renderer.animating
                clock.tick(FPS)

        self.save_state()
        pygame.quit()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.menubar.handle_event(event):
            return True
        elif event.type == pygame.WINDOWMAXIMIZED:
            self.maximized = True
        elif event.type == pygame.WINDOWRESTORED:
            self.maximized = False
        elif event.type in REDRAW_EVENTS:
            return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            node = self.tree_renderer.layout.to_node(*event.pos)
            tool = self.toolbar_renderer.layout.to_tool(*event.pos)
            action = self.actionbar_renderer.layout.to_action(*event.pos)
            if node != None:
                self.go_to(node)
            elif tool != None:
                self.tool = None if tool == self.tool else tool
            elif action != None:
                self.on_action(action)
            elif self.score != None:
                self.on_mark_dead(self.board_renderer.layout.to_point(*event.pos))
            elif self.tool == None and self.score == None:
                self.on_play(self.board_renderer.layout.to_point(*event.pos))
            else:
                self.on_edit(self.board_renderer.layout.to_point(*event.pos), self.tool.left)
            return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.tool != None:
                self.on_edit(self.board_renderer.layout.to_point(*event.pos), self.tool.right)
                return True
        elif event.type == pygame.MOUSEWHEEL:
            mouse = pygame.mouse.get_pos()
            if self.tree_renderer.layout.rect.collidepoint(pygame.mouse.get_pos()):
                self.on_scroll(event.y)
                return True
            elif self.comment_renderer.layout.rect.collidepoint(mouse):
                return self.comment_renderer.layout.scroll_by(-event.y*self.theme.comment.scroll_lines)
        elif event.type == pygame.KEYDOWN:
            self.on_key(event.key)
            return True

    def draw(self):
        screen = self.window.get_surface()
        if screen.get_size() != self.layout_size:
            self.refit_layouts(screen.get_size())       

        markers = converter.markers_at(self.node, self.size)
        labels = converter.labels_at(self.node, self.size)
        territory = self.score.territory if self.score != None else None
        dead = self.score.dead if self.score != None else None
        self.board_renderer.draw(screen, markers, labels, self.ghost_preview(), territory, dead)

        if self.show_panel:
            self.panel_renderer.draw(screen)
            if self.show_tree:
                self.tree_renderer.draw(screen, self.node)
            if self.show_comment:
                self.comment_renderer.draw(screen)
            if self.show_toolbar:
                self.toolbar_renderer.draw(screen, self.tool)
            self.actionbar_renderer.draw(screen, self.score.result if self.score != None else None)
        self.ui_renderer.draw(screen)
        self.window.flip()

    def ghost_preview(self) -> tuple[Point, Color]|None:
        if self.tool != None or not pygame.mouse.get_focused():
            return None
        point = self.board_renderer.layout.to_point(*pygame.mouse.get_pos())
        if point == None or not rules.is_legal(self.board, point, self.color_to_play):
            return None
        return (point, self.color_to_play)

    def refit_layouts(self, window_size: tuple[int, int]):
        self.layout_size = window_size
        self.board_renderer.layout, self.panel_renderer.layout, self.tree_renderer.layout, self.comment_renderer.layout, self.toolbar_renderer.layout, self.actionbar_renderer.layout = self.fit_layouts(self.layout_size)

    def on_play(self, point: Point|None):
        if point == None or not rules.is_legal(self.board, point, self.color_to_play):
            return
        id, value = self.color_to_play.value, converter.format_point(point)
        child = next((child for child in self.node.children if child.get(id) == [value]), None)
        if child == None:
            child = SGFNode({id: [value]}, parent=self.node)
            self.node.children.append(child)
        self.go_to(child)
        self.sounds.play_stone()

    def on_key(self, key: int):
        if key == pygame.K_UP and self.node.parent != None:
            self.go_to(self.node.parent)
        elif key == pygame.K_DOWN and self.node.children:
            self.go_to(self.node.children[0])
        elif key in (pygame.K_LEFT, pygame.K_RIGHT):
            step = -1 if key == pygame.K_LEFT else 1
            node = self.tree_renderer.layout.row_neighbor(self.node, step)
            if node != None:
                self.go_to(node)

    def on_scroll(self, steps: int):
        node = self.node
        for _ in range(abs(steps)):
            next_node = node.parent if steps > 0 else (node.children[0] if node.children else None)
            if next_node == None:
                break
            node = next_node
        if node is not self.node:
            self.go_to(node)

    def on_edit(self, point: Point|None, edit: Color|Marker):
        if point == None:
            return
        if isinstance(edit, Label):
            converter.toggle_label(self.node, point, edit, self.size)
            return
        if isinstance(edit, Marker):
            converter.toggle_marker(self.node, point, edit, self.size)
            return
        node = self.node
        if "B" in node or "W" in node: 
            node = SGFNode(parent=self.node)
            self.node.children.append(node)
        converter.toggle_setup_stone(node, point, edit, self.size)
        self.go_to(node)

    def on_pass(self):
        id = self.color_to_play.value
        child = next((child for child in self.node.children if converter.is_pass(child, self.color_to_play, self.size)), None)
        if child == None:
            child = SGFNode({id: [""]}, parent=self.node)
            self.node.children.append(child)
        self.go_to(child)

    def on_action(self, action: Action):
        if action == Action.PASS:
            self.on_pass()
        elif action == Action.SCORE:
            self.toggle_score()

    def toggle_score(self):
        if self.score != None:
            self.score = None
        else:
            self.score = scoring.territory_score(self.board, converter.komi(self.root))

    def on_mark_dead(self, point: Point|None):
        if point == None or self.board.is_empty(point):
            return
        dead = scoring.toggle_dead(self.board, self.score.dead, point)
        self.score = scoring.territory_score(self.board, converter.komi(self.root), dead)

    def go_to(self, node: SGFNode):
        board = converter.board_at(node)
        self.board = board
        self.size = board.size
        self.color_to_play = converter.next_color(node)
        self.board_renderer.board = board
        self.node = node
        self.score = None
        self.layout_size = None
    
    def open_game(self):
        path = dialogs.ask_open_path("Open Game")
        if path == None:
            return
        try:
            self.load_game(path)
        except Exception as error:
            dialogs.show_error("Could not open file", f"{path}\n{error}")

    def load_game(self, path: str|Path):
        root = parser.load(path)[0]
        node = list(root.main_line())[-1]
        self.go_to(node)
        self.root = root
        self.path = path

    def restore_game(self):
        path = self.state.game
        if path == None or not path.is_file():
            return
        try:
            self.load_game(path)
        except Exception: 
            pass

    def save_state(self):
        self.state.theme = self.theme_name
        self.state.game = Path(self.path) if self.path != None else None
        try:
            self.state.save()
        except OSError: 
            pass

    def save_game(self, ask_path: bool = False):
        path = self.path
        if ask_path or path == None:
            path = dialogs.ask_save_path("Save Game")
            if path == None:
                return
        try:
            writer.save(self.root, path)
            self.path = path
        except OSError as error:
            dialogs.show_error("Could not save file", f"{path}\n{error}")

    def new_game(self):
        self.board.clear()
        self.color_to_play = Color.BLACK
        self.root = SGFNode({"GM": ["1"], "FF": ["4"], "SZ": [str(self.size)]})
        self.node = self.root
        self.path = None
        self.score: scoring.Score|None = None
        self.layout_size = None

    def toggle_panel(self):
        self.show_panel = not self.show_panel
        screen = self.window.get_surface()
        if not (self.maximized or screen.get_flags() & pygame.FULLSCREEN):
            width, height = screen.get_size()
            full_board = height - self.menubar.layout.height
            panel_w = self.theme.panel.width
            if self.show_panel:
                new_width = max(width, min(width, full_board) + panel_w)
            else:
                new_width = min(width, max(width - panel_w, full_board))
            if new_width != width:
                self.window.size = (max(new_width, 1), height)
        self.layout_size = None

    def toggle_tree(self):
        self.show_tree = not self.show_tree
        self.layout_size = None

    def toggle_comment(self):
        self.show_comment = not self.show_comment
        self.layout_size = None

    def toggle_toolbar(self):
        self.show_toolbar = not self.show_toolbar
        if not self.show_toolbar:
            self.tool = None
        self.layout_size = None

    def fit_layouts(self, window_size: tuple[int, int]) -> tuple[BoardLayout, PanelLayout, TreeLayout, ToolbarLayout, ActionBarLayout]:
        width, height = window_size
        bar_height = self.menubar.layout.height
        panel_width = self.theme.panel.width if self.show_panel else 0
        board_layout = BoardLayout.fit(self.size, width - panel_width, height - bar_height, self.theme.board, top=bar_height)
        panel_layout = PanelLayout.fit(pygame.Rect(width - panel_width, bar_height, panel_width, height - bar_height), self.show_tree, self.show_comment, self.show_toolbar, self.theme.comment.height, self.theme.toolbar.height, self.theme.actionbar.height)
        tree_layout = TreeLayout.fit(self.root, self.node, panel_layout.tree_rect, self.theme.tree) 
        comment_layout = CommentLayout.fit(panel_layout.comment_rect, converter.node_name(self.node), converter.comment(self.node), self.comment_font, self.theme.comment)
        toolbar_layout = ToolbarLayout.fit(panel_layout.toolbar_rect, self.theme.toolbar)
        actionbar_layout = ActionBarLayout.fit(panel_layout.actionbar_rect, self.theme.actionbar)
        return board_layout, panel_layout, tree_layout, comment_layout, toolbar_layout, actionbar_layout

    def load_theme(self, name: str|None) -> Theme:
        return Theme() if name == None else Theme.from_dir(name)

    def open_themes_folder(self):
        try:
            dialogs.open_folder(USER_THEMES_DIR)
        except OSError as error:
            dialogs.show_error("Could not open themes folder", f"{USER_THEMES_DIR}\n{error}")

    def reload_themes(self):
        self.theme_names = Theme.available_themes()
        if self.theme_name in self.theme_names:
            self.set_theme(self.theme_name)
        else:
            self.build_menubar()

    def set_theme(self, name: str|None):
        previous = (self.theme, self.theme_name)
        try:
            self.theme, self.theme_name = self.load_theme(name), name
            self.build_ui() 
        except Exception as error:
            self.theme, self.theme_name = previous
            self.build_ui()
            dialogs.show_error("Could not load theme", f"{name or 'default'}\n{error}")

    def build_menubar(self):
        theme = self.theme
        font = pygame.font.Font(theme.menu.font, theme.menu.font_size)
        self.menubar = MenuBar([
            Menu("File", [
                MenuItem("New Game", self.new_game),
                MenuItem("Open Game", self.open_game),
                MenuItem("Save Game", self.save_game),
                MenuItem("Save Game As", lambda: self.save_game(ask_path=True))
            ]),
            Menu("Edit", [
                MenuItem("Clear Annotations", self.clear_annotations)
            ]),
            Menu("View", [
                MenuItem("Toggle Side Panel", self.toggle_panel, checked=lambda: self.show_panel),
                MenuItem("Toggle Game Tree", self.toggle_tree, checked=lambda: self.show_tree),
                MenuItem("Toggle Comments", self.toggle_comment, checked=lambda: self.show_comment),
                MenuItem("Toggle Toolbar", self.toggle_toolbar, checked=lambda: self.show_toolbar)
            ]),
            Menu("Themes", [
                MenuItem("Open Themes Folder", self.open_themes_folder),
                MenuItem("Reload Themes Folder", self.reload_themes),
                MenuItem("classic", lambda: self.set_theme(None), checked=lambda: self.theme_name == None),
                *(MenuItem(name, lambda name=name: self.set_theme(name), checked=lambda name=name: name == self.theme_name) for name in self.theme_names)
            ])
        ], font, theme.menu)
        self.ui_renderer = UIRenderer(self.menubar, font, theme.menu)

    def build_ui(self):
        theme = self.theme
        self.build_menubar()
        self.comment_font = pygame.font.Font(theme.comment.font, theme.comment.font_size)
        board_layout, panel_layout, tree_layout, comment_layout, toolbar_layout, actionbar_layout = self.fit_layouts(self.window.get_surface().get_size())
        self.board_renderer = BoardRenderer(self.board, board_layout, theme.board)
        self.panel_renderer = PanelRenderer(panel_layout, theme.panel)
        self.tree_renderer = TreeRenderer(tree_layout, theme.tree)
        self.comment_renderer = CommentRenderer(comment_layout, self.comment_font, theme.comment)
        self.toolbar_renderer = ToolbarRenderer(toolbar_layout, theme.toolbar)
        self.actionbar_renderer = ActionBarRenderer(actionbar_layout, theme.actionbar)
        self.sounds = SoundPlayer(theme.sound)
        self.layout_size = None

    def clear_annotations(self):
        converter.clear_annotations(self.node)