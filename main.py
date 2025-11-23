import pygame as pg
import random

FIELD_SIZE = (10, 20)
WINDOW_SIZE = (200, 400)
BLOCK_SIZE = (WINDOW_SIZE[0]/FIELD_SIZE[0] ,WINDOW_SIZE[1]/FIELD_SIZE[1])
FALL_TIME = 0.25

def clamp(n, min_n, max_n):
    return min(max(n, min_n), max_n)


def can_spawn(shape_pos, shape_map):
    for pos in shape_map:
        in_x_bounds = len(field.grid_pos) > pos[0]+shape_pos.x >= 0
        if not (in_x_bounds and field.is_empty(shape_pos+pos)):
            return False
    return True


class Shape(object):
    def __init__(self, shape_map, color):
        top = shape_map[0][1]
        for block in shape_map[1:]:
            top = min(top, block[1])

        shape_pos = None
        for x in range(len(field.grid)):
            if can_spawn(pg.Vector2(x, -top), shape_map):
                shape_pos = pg.Vector2(x, -top)
                break

        if shape_pos is None:
            game_over()
            self.success = False
            return

        self.success = True
        self.blocks = []
        self.core_block = None
        for pos in shape_map:
            block = Block(shape_pos + pg.Vector2(pos[0], pos[1]), color)
            if pos[0]==0==pos[1]:
                self.core_block = block
            self.blocks.append(block)

    def move(self, x_offset, y_offset):
        shape_can_move = True
        for block in self.blocks:
            shape_can_move = shape_can_move and block.can_move(x_offset, y_offset)
        if shape_can_move:
            for block in self.blocks:
                block.move(x_offset, y_offset)

        return shape_can_move

    def draw(self):
        for block in self.blocks:
            block.draw()

    def place(self):
        for block in self.blocks:
            field.place(block)

    def rotate(self):
        can_rotate = True
        block_offsets = []
        for i, block in enumerate(self.blocks):
            block_pos = block.pos - self.core_block.pos
            block_new_pos = pg.Vector2(block_pos.y, -block_pos.x)
            block_offsets.append(block_new_pos - block_pos)

        for i, block in enumerate(self.blocks):
            if not block.can_move(block_offsets[i].x, block_offsets[i].y):
                can_rotate = False
                break

        if can_rotate:
            for i, block in enumerate(self.blocks):
                block.move(block_offsets[i].x, block_offsets[i].y)



class Block(object):
    def __init__(self, pos : pg.Vector2, color : pg.Color):
        self.pos = pos
        self.color = color

    def can_move(self, x_offset, y_offset):
        pos = self.pos + pg.Vector2(x_offset, y_offset)
        in_x_bounds = len(field.grid_pos) > pos.x >= 0
        in_y_bounds = 0 <= pos.y < len(field.grid_pos[0])
        if in_x_bounds and in_y_bounds and field.is_empty(pos):
            return True
        else:
            return False

    def move(self, x_offset, y_offset):
        if self.can_move(x_offset, y_offset):
            self.pos += pg.Vector2(x_offset, y_offset)
            return True
        else:
            return False

    def draw(self):
        rect = pg.Rect(field.grid_pos[int(self.pos.x)][int(self.pos.y)], (BLOCK_SIZE[0], BLOCK_SIZE[1]))
        pg.draw.rect(screen, self.color, rect)

class Field(object):
    def __init__(self, x, y):
        self.grid_pos = [[pg.Vector2(x * BLOCK_SIZE[0], y * BLOCK_SIZE[1]) for y in range(y)] for x in range(x)]
        self.grid :list[list[Block|None]] = [[None for y in range(y)] for x in range(x)]

    def is_empty(self, pos :pg.Vector2):
        return self.grid[int(pos.x)][int(pos.y)] is None

    def place(self, block :Block):
        self.grid[int(block.pos.x)][int(block.pos.y)] = block
        self.check_lines()

    def check_lines(self):
        for y in range(len(self.grid[0])):
            is_full = True
            for x in range(len(self.grid)):
                if self.grid[x][y] is None:
                    is_full = False
                    break
            if is_full:
                for x in range(len(self.grid)):
                    self.grid[x][y] = None
                self.lower_lines(y)

    def lower_lines(self, start_from):
        for y in range(start_from, 0, -1):
            for x in range(len(self.grid)):
                self.grid[x][y] = self.grid[x][y-1]
                if not self.grid[x][y] is None:
                    self.grid[x][y].pos = pg.Vector2(x, y)



    def draw(self):
        for column in self.grid:
            for cell in column:
                if not (cell is None):
                    cell.draw()


shapes = [
    {"shape_map": [(0,-1), (0,0), (0, 1), (0, 2)], "color": pg.Color(0, 255, 255)}, #I
    {"shape_map": [(0,-1), (0,0), (0, 1), (1, 1)], "color": pg.Color(0, 0, 255)}, #L
    {"shape_map": [(0,-1), (0,0), (0, 1), (-1, 1)], "color": pg.Color(255, 112, 0)}, #J
    {"shape_map": [(0,0), (-1,1), (0, 1), (1, 1)], "color": pg.Color(255, 0, 255)}, #T
    {"shape_map": [(0,0), (0,1), (1, 0), (1, 1)], "color": pg.Color(255, 255, 0)}, #O
    {"shape_map": [(1,-1), (0,-1), (0, 0), (-1, 0)], "color": pg.Color(0, 255, 0)}, #S
    {"shape_map": [(-1,-1), (0,-1), (0, 0), (1, 0)], "color": pg.Color(255, 0, 0)}, #Z
]
def get_random_shape():
    i = random.randint(0, len(shapes)-1)
    return Shape(shapes[i]["shape_map"], shapes[i]["color"])

def game_over():
    global is_game_over
    is_game_over = True
    print("Game Over!")

screen = pg.display.set_mode(WINDOW_SIZE)
clock = pg.time.Clock()

field = Field(10, 20)
shape = get_random_shape()

dt = 0
movement_direction = 0
drop = False

fall_timer = FALL_TIME
running = True
is_game_over = False
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
        
        # Handle rotation (no repeat)
        if keys[pg.K_UP] or keys[pg.K_w] or keys[pg.K_z]:
            if self.held_key != 'rotate':
                self.current_shape.rotate()
                self.held_key = 'rotate'
        
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
        
        else:
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
                    if event.key == pg.K_r and self.is_game_over:
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
