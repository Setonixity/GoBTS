# Changelog

## [0.0.1] - 2-11-2026
### Added
- setup project structure
- README, CHANGELOG, and ARCHITECTURE
- (core) shared board library
- (core) shared rules library
- (client) ascii board rendering
- (client) pygame board rendering
- (client) mouse input and stone placement
- (client) stone ghost previews

### Fixed
- (client) jitter during window resizing
- (client) inconsistent star point scaling

## [0.0.2] - 4-11-2026
### Added
- (client) working menubar
- (client) dropdown box, and callable menuitems
- (sgf) dataclass for sgf nodes
- (sgf) parser for sgf notation
- (sgf) converter for parsed to go game
- (client) new game
- (client) open game from file
- (client) open file dialog box

### Fixed
- (client) wrong move order
- (client) new game not resetting play color
- (client) when loading sgf, layout size doesn't update

### Changed
- (core) moved play() to core/rules.py

## [0.0.3] - 5-11-2026
### Added
- (client) a game tree viewer
- (client) up-down traversal keybinds
- (client) centered current node

### Changed
- (client) switched color changing marker for bg highlight
- (client) root node marker.

## [0.0.4] - 6-11-2026
### Added
- (sgf) sgf writer
- (client) save game dialog box
- (client) left-right traversal keybinds
- (client) mouse click to node in tree
- (client) scroll up-down traversal
- (client) view and toggle to menubar
- (client) game tree is togglable

### Fixed
- (Client) window resizing when enough horizontal space for tree

## [0.0.5] - 8-11-2026
### Added
- (client) theme default values
- (client) rounded dropbox 

### Changed
- (client) decoupled board magic numbers
- (client) decoupled tree magic numbers
- (client) decoupled ui magic numbers
- (client) default menu sizes
- (client) built-in default font and icons

## [0.0.6] - 10-11-2026
### Added
- (core) ko and self-capture rule
- (client) side-panel to store other widgets along with game tree
- (client) shape markers
- (client) tool/shape selecting widget in side-panel

### Fixed
- (client) using pygame depecrated methods in pygame-ce
- (client) sgf resolution