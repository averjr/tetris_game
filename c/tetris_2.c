#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifdef _WIN32
#include <conio.h>
#include <windows.h>
#define CLEAR "cls"
#else
#include <termios.h>
#include <unistd.h>
#include <sys/select.h>
#define CLEAR "clear"
#endif

#define WIDTH 10
#define HEIGHT 20
#define SHAPES 7

int board[HEIGHT][WIDTH];
int score = 0;
int gameOver = 0;

typedef struct {
    int x, y;
    int shape[4][4];
    int size;
} Tetromino;

int shapes[SHAPES][4][4] = {
    {{1,1,1,1}, {0,0,0,0}, {0,0,0,0}, {0,0,0,0}}, // I
    {{1,1,0,0}, {1,1,0,0}, {0,0,0,0}, {0,0,0,0}}, // O
    {{0,1,0,0}, {1,1,1,0}, {0,0,0,0}, {0,0,0,0}}, // T
    {{1,1,0,0}, {0,1,1,0}, {0,0,0,0}, {0,0,0,0}}, // S
    {{0,1,1,0}, {1,1,0,0}, {0,0,0,0}, {0,0,0,0}}, // Z
    {{1,0,0,0}, {1,1,1,0}, {0,0,0,0}, {0,0,0,0}}, // L
    {{0,0,1,0}, {1,1,1,0}, {0,0,0,0}, {0,0,0,0}}  // J
};

Tetromino current;

// Function prototypes
void initBoard();
void newTetromino();
int canMove(int dx, int dy);
void rotate();
void mergeTetromino();
void clearLines();
void draw();
void sleep_ms(int ms);

#ifndef _WIN32
struct termios orig_termios;

void disableRawMode() {
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios);
}

void enableRawMode() {
    tcgetattr(STDIN_FILENO, &orig_termios);
    atexit(disableRawMode);
    struct termios raw = orig_termios;
    raw.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw);
}

int kbhit() {
    struct timeval tv = {0, 0};
    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(STDIN_FILENO, &fds);
    return select(STDIN_FILENO + 1, &fds, NULL, NULL, &tv);
}

int getch() {
    int c = getchar();
    return c;
}
#endif

void initBoard() {
    for (int i = 0; i < HEIGHT; i++)
        for (int j = 0; j < WIDTH; j++)
            board[i][j] = 0;
}

void newTetromino() {
    int type = rand() % SHAPES;
    current.x = WIDTH / 2 - 2;
    current.y = 0;
    current.size = 4;
    memcpy(current.shape, shapes[type], sizeof(shapes[type]));
    
    if (!canMove(0, 0)) {
        gameOver = 1;
    }
}

int canMove(int dx, int dy) {
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            if (current.shape[i][j]) {
                int newX = current.x + j + dx;
                int newY = current.y + i + dy;
                if (newX < 0 || newX >= WIDTH || newY >= HEIGHT)
                    return 0;
                if (newY >= 0 && board[newY][newX])
                    return 0;
            }
        }
    }
    return 1;
}

void rotate() {
    int temp[4][4];
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++)
            temp[i][j] = current.shape[3-j][i];
    
    int oldShape[4][4];
    memcpy(oldShape, current.shape, sizeof(current.shape));
    memcpy(current.shape, temp, sizeof(temp));
    
    if (!canMove(0, 0))
        memcpy(current.shape, oldShape, sizeof(oldShape));
}

void mergeTetromino() {
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++)
            if (current.shape[i][j])
                board[current.y + i][current.x + j] = 1;
}

void clearLines() {
    for (int i = HEIGHT - 1; i >= 0; i--) {
        int full = 1;
        for (int j = 0; j < WIDTH; j++) {
            if (!board[i][j]) {
                full = 0;
                break;
            }
        }
        if (full) {
            for (int k = i; k > 0; k--)
                for (int j = 0; j < WIDTH; j++)
                    board[k][j] = board[k-1][j];
            for (int j = 0; j < WIDTH; j++)
                board[0][j] = 0;
            score += 100;
            i++;
        }
    }
}

void draw() {
    system(CLEAR);
    printf("\n  TETRIS - Score: %d\n\n", score);
    printf("  ");
    for (int i = 0; i < WIDTH + 2; i++) printf("-");
    printf("\n");
    
    for (int i = 0; i < HEIGHT; i++) {
        printf("  |");
        for (int j = 0; j < WIDTH; j++) {
            int filled = board[i][j];
            for (int ti = 0; ti < 4; ti++) {
                for (int tj = 0; tj < 4; tj++) {
                    if (current.shape[ti][tj] && 
                        current.y + ti == i && 
                        current.x + tj == j)
                        filled = 1;
                }
            }
            printf(filled ? "[]" : "  ");
        }
        printf("|\n");
    }
    
    printf("  ");
    for (int i = 0; i < WIDTH + 2; i++) printf("-");
    printf("\n\n  Controls: A/D = Left/Right, W = Rotate, S = Drop, Q = Quit\n");
}

void sleep_ms(int ms) {
#ifdef _WIN32
    Sleep(ms);
#else
    usleep(ms * 1000);
#endif
}

int main() {
    srand(time(NULL));
    initBoard();
    newTetromino();
    
#ifndef _WIN32
    enableRawMode();
#endif

    int counter = 0;
    
    while (!gameOver) {
        draw();
        
        if (kbhit()) {
            char c = getch();
#ifndef _WIN32
            if (c == 27) {
                getch(); getch();
            }
#endif
            if (c == 'a' || c == 'A') {
                if (canMove(-1, 0)) current.x--;
            } else if (c == 'd' || c == 'D') {
                if (canMove(1, 0)) current.x++;
            } else if (c == 'w' || c == 'W') {
                rotate();
            } else if (c == 's' || c == 'S') {
                while (canMove(0, 1)) current.y++;
            } else if (c == 'q' || c == 'Q') {
                gameOver = 1;
            }
        }
        
        if (counter++ >= 10) {
            if (canMove(0, 1)) {
                current.y++;
            } else {
                mergeTetromino();
                clearLines();
                newTetromino();
            }
            counter = 0;
        }
        
        sleep_ms(50);
    }
    
    draw();
    printf("\n  Game Over! Final Score: %d\n\n", score);
    
#ifndef _WIN32
    disableRawMode();
#endif
    
    return 0;
}
