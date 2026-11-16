from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable, TypeVar

import pygame

SGF_TYPES = [("SGF files", ("*.sgf", "*.SGF")), ("All files", "*")]
SGF_EXTENSION = ".sgf"
KEEP_APP_ALIVE_MS = 100

MACOS = sys.platform == "darwin"
OSASCRIPT = "/usr/bin/osascript"
MAC_DEFAULT_SAVE_NAME = "Untitled" + SGF_EXTENSION
MAC_OPEN_SCRIPT = """
on run argv
    return POSIX path of (choose file with prompt (item 1 of argv))
end run
"""
MAC_SAVE_SCRIPT = """
on run argv
    return POSIX path of (choose file name with prompt (item 1 of argv) default name (item 2 of argv))
end run
"""
 
T = TypeVar("T")

def ask_open_path(title: str = "Open", filetypes=SGF_TYPES) -> str|None:
    if MACOS:
        return run_osascript(MAC_OPEN_SCRIPT, title)
    from tkinter import filedialog
    path = run(lambda root: filedialog.askopenfilename(parent=root, title=title, filetypes=filetypes))
    return path if path else None
 
def ask_save_path(title: str = "Save", filetypes=SGF_TYPES) -> str|None:
    if MACOS:
        path = run_osascript(MAC_SAVE_SCRIPT, title, MAC_DEFAULT_SAVE_NAME)
        return with_default_extension(path) if path else None
    from tkinter import filedialog
    path = run(lambda root: filedialog.asksaveasfilename(parent=root, title=title, filetypes=filetypes, defaultextension=SGF_EXTENSION))
    return path if path else None
 
def show_error(title: str, message: str) -> None:
    if MACOS:
        try:
            pygame.display.message_box(title, message, message_type="error")
        finally:
            clear_clicks()
        return
    from tkinter import messagebox
    run(lambda root: messagebox.showerror(title, message, parent=root))

def run(dialog_func: Callable[[tk.Tk], T]) -> T: # always destroy the root afterwards
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    if pygame.display.get_init():
        root.after(KEEP_APP_ALIVE_MS, keep_app_alive, root)
    try:
        return dialog_func(root)
    finally:
        root.destroy()
        clear_clicks()

def keep_app_alive(root: tk.Tk):
    pygame.event.pump()
    root.after(KEEP_APP_ALIVE_MS, keep_app_alive, root)

def clear_clicks(): 
    if pygame.display.get_init():
        pygame.event.clear((pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP))

def run_osascript(script: str, *args: str) -> str|None: 
    process = subprocess.Popen(
        [OSASCRIPT, "-e", script, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        encoding="utf-8", 
    )
    try:
        while True:
            try:
                output, _ = process.communicate(timeout=KEEP_APP_ALIVE_MS / 1000)
                break
            except subprocess.TimeoutExpired:
                if pygame.display.get_init():
                    pygame.event.pump() 
    finally:
        if process.poll() is None:
            process.kill()
        clear_clicks()
    path = output.rstrip("\n")
    return path if process.returncode == 0 and path else None

def with_default_extension(path: str) -> str:
    target = Path(path)
    if target.suffix:
        return path
    extended = target.with_name(target.name + SGF_EXTENSION)
    if extended.exists(): 
        return path
    return str(extended)
 
def open_folder(path: Path) -> None: 
    path.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path], env=system_env())
 
def system_env() -> dict[str, str]:
    env = dict(os.environ)
    if getattr(sys, "frozen", False):
        original = env.pop("LD_LIBRARY_PATH_ORIG", None)
        if original != None:
            env["LD_LIBRARY_PATH"] = original
        else:
            env.pop("LD_LIBRARY_PATH", None)
    return env