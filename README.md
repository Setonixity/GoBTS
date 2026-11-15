# GOBTS (Go: back to sleep)
An eepy python application for the board game Go :3

Note: For Chula's ISE 2190101 Computer Programming Project. This is the second iteration of the repo, after archiving the original prototype, and a complete rewrite of the project.

## Dependencies
All PyPI dependencies listed in pyproject.toml 
```
pip install -e .
```

This project vendors its goscoring algorithm from [lightvector](https://github.com/lightvector)'s
[goscorer](https://github.com/lightvector/goscorer), vendored unmodified as core/goscorer.py (MIT License)

## Running
```
python -m gobts
```

## Building executables
```
pip install -e .[build] 
pyinstaller gobts.spec --noconfirm
```

Output is `dist/gobts/` on Windows and Linux, `dist/GOBTS.app` on macOS.

## Custom themes
Put your themes in the user themes folder (Themes > Open Themes Folder), then Themes > Reload Themes Folder. 

| OS | Themes folder | State file |
|---|---|---|
| Windows | `%LOCALAPPDATA%\gobts\themes` | `%LOCALAPPDATA%\gobts\state.json` |
| macOS | `~/Library/Application Support/gobts/themes` | `~/Library/Application Support/gobts/state.json` |
| Linux | `~/.local/share/gobts/themes` | `~/.local/state/gobts/state.json` |

## AI and Sources Disclosure
Google search summary LLM was used for solution queries, and the actual sources behind the the general implimentation is credited in [ARCHITECTURE.md](ARCHITECTURE.md).
