import pygame as pg
import random
from typing import Optional, List, Tuple

# Constants
FIELD_SIZE = (10, 20)
WINDOW_SIZE = (400, 800)  # Doubled for better visibility
BLOCK_SIZE = (WINDOW_SIZE[0] // FIELD_SIZE[0], WINDOW_SIZE[1] // FIELD_SIZE[1])
FALL_TIME = 0.5
FAST_FALL_TIME = 0.05
MOVE_REPEAT_DELAY = 0.15
MOVE_REPEAT_RATE = 0.05

# Shape definitions with proper centers
SHAPES = [
    {"map": [(0, -1), (0, 0), (0, 1), (0, 2)], "color": (0, 255, 255), "name": "I"},
    {"map": [(0, -1), (0, 0), (0, 1), (1, 1)], "color": (0, 0, 255), "name": "L"},
    {"map": [(0, -1), (0, 0), (0, 1), (-1, 1)], "color": (255, 112, 0), "name": "J"},
    {"map": [(0, 0), (-1, 1), (0, 1), (1, 1)], "color": (255, 0, 255), "name": "T"},
    {"map": [(0, 0), (0, 1), (1, 0), (1, 1)], "color": (255, 255, 0), "name": "O"},
    {"map": [(1, -1), (0, -1), (0, 0), (-1, 0)], "color": (0, 255, 0), "name": "S"},
    {"map": [(-1, -1), (0, -1), (0, 0), (1, 0)], "color": (255, 0, 0), "name": "Z"},
]


class Block:
    """Represents a single block in the game."""
    
    def __init__(self, pos: pg.Vector2, color: Tuple[int, int, int]):
        self.pos = pos
        self.color = color

    def draw(self, surface: pg.Surface, grid_pos: List[List[pg.Vector2]]):
        """Draw the block with a border effect."""
        x, y = int(self.pos.x), int(self.pos.y)
        rect = pg.Rect(grid_pos[x][y], BLOCK_SIZE)
        
        # Draw main block
        pg.draw.rect(surface, self.color, rect)
        
        # Draw border for 3D effect
        border_color = tuple(min(c + 40, 255) for c in self.color)
        pg.draw.rect(surface, border_color, rect, 2)


class Shape:
    """Represents a tetromino shape."""
    
    def __init__(self, shape_def: dict, field: 'Field'):
        self.field = field
        self.shape_map = shape_def["map"]
        self.color = shape_def["color"]
        self.blocks: List[Block] = []
        self.core_block: Optional[Block] = None
        
        # Calculate spawn position
        top = min(pos[1] for pos in self.shape_map)
        spawn_x = FIELD_SIZE[0] // 2
        spawn_pos = pg.Vector2(spawn_x, -top)
        
        # Check if can spawn
        if not self._can_place_at(spawn_pos):
            self.success = False
            return
        
        self.success = True
        
        # Create blocks
        for pos in self.shape_map:
            block = Block(spawn_pos + pg.Vector2(pos[0], pos[1]), self.color)
            if pos[0] == 0 and pos[1] == 0:
                self.core_block = block
            self.blocks.append(block)

    def _can_place_at(self, pos: pg.Vector2, offsets: Optional[List[pg.Vector2]] = None) -> bool:
        """Check if shape can be placed at position with optional offsets."""
        if offsets is None:
            offsets = [pg.Vector2(p[0], p[1]) for p in self.shape_map]
        
        for offset in offsets:
            check_pos = pos + offset
            x, y = int(check_pos.x), int(check_pos.y)
            
            # Check bounds
            if not (0 <= x < FIELD_SIZE[0] and 0 <= y < FIELD_SIZE[1]):
                return False
            
            # Check if position is empty
            if not self.field.is_empty(check_pos):
                return False
        
        return True

    def move(self, x_offset: int, y_offset: int) -> bool:
        """Move the shape by offset. Returns True if successful."""
        # Check if all blocks can move
        can_move = all(
            block.pos.x + x_offset >= 0 and
            block.pos.x + x_offset < FIELD_SIZE[0] and
            block.pos.y + y_offset < FIELD_SIZE[1] and
            self.field.is_empty(block.pos + pg.Vector2(x_offset, y_offset))
            for block in self.blocks
        )
        
        if can_move:
            for block in self.blocks:
                block.pos += pg.Vector2(x_offset, y_offset)
        
        return can_move

    def rotate(self) -> bool:
        """Rotate the shape clockwise with wall kick attempts."""
        if not self.core_block:
            return False
        
        # Calculate rotated positions
        new_offsets = []
        for block in self.blocks:
            rel_pos = block.pos - self.core_block.pos
            rotated = pg.Vector2(rel_pos.y, -rel_pos.x)
            new_offsets.append(rotated)
        
        # Try standard rotation
        if self._can_place_at(self.core_block.pos, new_offsets):
            for block, offset in zip(self.blocks, new_offsets):
                block.pos = self.core_block.pos + offset
            return True
        
        # Try wall kicks (simple implementation)
        kick_tests = [(1, 0), (-1, 0), (0, -1), (2, 0), (-2, 0)]
        for kick_x, kick_y in kick_tests:
            test_pos = self.core_block.pos + pg.Vector2(kick_x, kick_y)
            if self._can_place_at(test_pos, new_offsets):
                self.core_block.pos = test_pos
                for block, offset in zip(self.blocks, new_offsets):
                    block.pos = self.core_block.pos + offset
                return True
        
        return False

    def draw(self, surface: pg.Surface, grid_pos: List[List[pg.Vector2]]):
        """Draw all blocks in the shape."""
        for block in self.blocks:
            if block.pos.y >= 0:  # Only draw visible blocks
                block.draw(surface, grid_pos)

    def place(self):
        """Place the shape on the field."""
        for block in self.blocks:
            if block.pos.y >= 0:
                self.field.place(block)


class Field:
    """Represents the game field/board."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid_pos = [
            [pg.Vector2(x * BLOCK_SIZE[0], y * BLOCK_SIZE[1]) 
             for y in range(height)] 
            for x in range(width)
        ]
        self.grid: List[List[Optional[Block]]] = [
            [None for _ in range(height)] 
            for _ in range(width)
        ]
        self.lines_cleared = 0
        self.score = 0

    def is_empty(self, pos: pg.Vector2) -> bool:
        """Check if position is empty."""
        x, y = int(pos.x), int(pos.y)
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.grid[x][y] is None

    def place(self, block: Block):
        """Place a block on the field."""
        x, y = int(block.pos.x), int(block.pos.y)
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[x][y] = block

    def check_and_clear_lines(self) -> int:
        """Check for complete lines and clear them. Returns number cleared."""
        lines_to_clear = []
        
        # Find all complete lines
        for y in range(self.height):
            if all(self.grid[x][y] is not None for x in range(self.width)):
                lines_to_clear.append(y)
        
        # Clear lines and update score
        if lines_to_clear:
            for y in lines_to_clear:
                for x in range(self.width):
                    self.grid[x][y] = None
            
            # Lower blocks above cleared lines
            for clear_y in sorted(lines_to_clear, reverse=True):
                self._lower_blocks(clear_y)
            
            # Update stats
            num_cleared = len(lines_to_clear)
            self.lines_cleared += num_cleared
            # Tetris scoring: 1=100, 2=300, 3=500, 4=800
            score_values = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += score_values.get(num_cleared, num_cleared * 100)
            
            return num_cleared
        
        return 0

    def _lower_blocks(self, cleared_line: int):
        """Lower all blocks above the cleared line."""
        for y in range(cleared_line, 0, -1):
            for x in range(self.width):
                self.grid[x][y] = self.grid[x][y - 1]
                if self.grid[x][y]:
                    self.grid[x][y].pos = pg.Vector2(x, y)
        
        # Clear top line
        for x in range(self.width):
            self.grid[x][0] = None

    def draw(self, surface: pg.Surface):
        """Draw the field and all placed blocks."""
        # Draw grid lines
        for x in range(self.width + 1):
            pg.draw.line(
                surface, 
                (50, 50, 50),
                (x * BLOCK_SIZE[0], 0),
                (x * BLOCK_SIZE[0], WINDOW_SIZE[1])
            )
        
        for y in range(self.height + 1):
            pg.draw.line(
                surface,
                (50, 50, 50),
                (0, y * BLOCK_SIZE[1]),
                (WINDOW_SIZE[0], y * BLOCK_SIZE[1])
            )
        
        # Draw blocks
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[x][y]:
                    self.grid[x][y].draw(surface, self.grid_pos)


class Game:
    """Main game controller."""
    
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(WINDOW_SIZE)
        pg.display.set_caption("Tetris")
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, 36)
        self.big_font = pg.font.Font(None, 72)
        
        self.reset_game()

    def reset_game(self):
        """Reset the game state."""
        self.field = Field(FIELD_SIZE[0], FIELD_SIZE[1])
        self.current_shape = self._spawn_shape()
        self.is_game_over = False
        self.fall_timer = FALL_TIME
        self.move_timer = 0
        self.held_key = None
        self.fast_fall = False

    def _spawn_shape(self) -> Optional[Shape]:
        """Spawn a new random shape."""
        shape = Shape(random.choice(SHAPES), self.field)
        if not shape.success:
            self.is_game_over = True
            return None
        return shape

    def handle_input(self, dt: float):
        """Handle keyboard input with key repeat."""
        keys = pg.key.get_pressed()
        
        # Handle rotation (no repeat - only on key press, not hold)
        # This is handled in the event loop now, not here
        pass
        
        # Handle fast fall
        self.fast_fall = keys[pg.K_DOWN] or keys[pg.K_s]
        
        # Handle horizontal movement with repeat
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            if self.held_key != 'left':
                self.current_shape.move(-1, 0)
                self.held_key = 'left'
                self.move_timer = MOVE_REPEAT_DELAY
            else:
                self.move_timer -= dt
                if self.move_timer <= 0:
                    self.current_shape.move(-1, 0)
                    self.move_timer = MOVE_REPEAT_RATE
        
        elif keys[pg.K_RIGHT] or keys[pg.K_d]:
            if self.held_key != 'right':
                self.current_shape.move(1, 0)
                self.held_key = 'right'
                self.move_timer = MOVE_REPEAT_DELAY
            else:
                self.move_timer -= dt
                if self.move_timer <= 0:
                    self.current_shape.move(1, 0)
                    self.move_timer = MOVE_REPEAT_RATE
        
        # Handle hard drop
        elif keys[pg.K_SPACE]:
            if self.held_key != 'hard_drop':
                while self.current_shape.move(0, 1):
                    pass
                self._lock_shape()
                self.held_key = 'hard_drop'
        
        # Reset held key when no relevant keys are pressed
        elif not (keys[pg.K_LEFT] or keys[pg.K_a] or keys[pg.K_RIGHT] or keys[pg.K_d] or keys[pg.K_SPACE]):
            if self.held_key in ['left', 'right', 'hard_drop']:
                self.held_key = None

    def _lock_shape(self):
        """Lock the current shape and spawn a new one."""
        self.current_shape.place()
        self.field.check_and_clear_lines()
        self.current_shape = self._spawn_shape()
        self.fall_timer = FALL_TIME

    def update(self, dt: float):
        """Update game state."""
        if self.is_game_over:
            return
        
        # Apply gravity
        fall_speed = FAST_FALL_TIME if self.fast_fall else FALL_TIME
        self.fall_timer -= dt
        
        if self.fall_timer <= 0:
            if not self.current_shape.move(0, 1):
                self._lock_shape()
            self.fall_timer = fall_speed

    def draw(self):
        """Draw everything."""
        self.screen.fill((20, 20, 20))
        
        # Draw field and blocks
        self.field.draw(self.screen)
        
        if not self.is_game_over and self.current_shape:
            self.current_shape.draw(self.screen, self.field.grid_pos)
        
        # Draw UI
        score_text = self.font.render(f"Score: {self.field.score}", True, (255, 255, 255))
        lines_text = self.font.render(f"Lines: {self.field.lines_cleared}", True, (255, 255, 255))
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lines_text, (10, 50))
        
        # Draw game over
        if self.is_game_over:
            overlay = pg.Surface(WINDOW_SIZE)
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("GAME OVER", True, (255, 50, 50))
            restart_text = self.font.render("Press R to Restart", True, (255, 255, 255))
            
            self.screen.blit(
                game_over_text,
                ((WINDOW_SIZE[0] - game_over_text.get_width()) // 2,
                 (WINDOW_SIZE[1] - game_over_text.get_height()) // 2 - 50)
            )
            self.screen.blit(
                restart_text,
                ((WINDOW_SIZE[0] - restart_text.get_width()) // 2,
                 (WINDOW_SIZE[1] - restart_text.get_height()) // 2 + 50)
            )

    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            # Handle events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    # Rotation only on key press (KEYDOWN), not hold
                    if event.key in (pg.K_UP, pg.K_w, pg.K_z):
                        if not self.is_game_over:
                            self.current_shape.rotate()
                    elif event.key == pg.K_r and self.is_game_over:
                        self.reset_game()
                    elif event.key == pg.K_ESCAPE:
                        running = False
            
            # Update and draw
            if not self.is_game_over:
                self.handle_input(dt)
                self.update(dt)
            
            self.draw()
            pg.display.flip()
        
        pg.quit()


if __name__ == "__main__":
    game = Game()
    game.run()