import pygame as pg
import time

WIDTH = 350
HEIGHT = 700

class Figure:
    def __init__(self, screen):
        self.width = 30
        self.height = 30
        self.screen = screen
        self.pos = ((WIDTH // 2), (HEIGHT // 2))


    def draw(self):
        pg.draw.rect(self.screen, (255, 0,0), (
            self.pos[0], 
            0,
            self.width, self.height)
        )
    
    def move(self, dx, dy):
        print(dx, dy)   
        self.pos = (self.pos[0] + dx, self.pos[1] + dy)



def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    figure = Figure(screen)


    while True:
        screen.fill((0, 0, 0))  # Clear screen each frame
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    figure.move(-figure.width, 0)
                if event.key == pg.K_RIGHT:
                    figure.move(figure.width, 0)
            elif event.type == pg.KEYUP:
                if event.key == pg.K_LEFT:
                    print('Left key released')
                if event.key == pg.K_RIGHT:
                    print('Right key released')
        figure.draw()  # Redraw figure after moving
        pg.display.flip()


if __name__ == "__main__":
    main()
    pg.quit()



