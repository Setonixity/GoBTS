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

## Fixed
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
- (client) file dialog box

## Fixed
- (client) wrong move order
- (client) new game not resetting play color

## Changed
- (core) moved play() to core/rules.py