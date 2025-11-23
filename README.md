python -m venv .env
source ./.env/bin/activate
pip install -r requirements.txt

# Key Improvements Made:
## Architecture:

* Encapsulated game logic in a Game class
* Removed global variable dependencies
* Separated concerns better (Field, Shape, Block, Game)

## Bug Fixes:

* Fixed multiple line clearing bug
* Added wall kick system for rotation
* Improved spawn positioning (centers shapes)
* Better bounds checking

## New Features:

* Score tracking (Tetris scoring system)
* Lines cleared counter
* Hard drop (spacebar)
* Key repeat for smooth movement
* Fast fall with down key
* Restart functionality (R key)
* Better visual feedback (borders on blocks, grid lines)
* Semi-transparent game over overlay

## Code Quality:

* Proper type hints
* Consistent indentation
* Better naming conventions
* Removed unused code
* More efficient algorithms
* Added docstrings

## Gameplay:

* Doubled window size for better visibility
* Smoother controls with key repeat
* More forgiving rotation with wall kicks
* Better visual aesthetics