import pygame
import sys
import random

pygame.init()

SW, SH = 600, 600

BLOCK_SIZE = 50
FONT = pygame.font.Font("arial.ttf", BLOCK_SIZE*2)

screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Snake!")
clock = pygame.time.Clock()

class Snake:
    def __init__(self):
        self.x, self.y = BLOCK_SIZE, BLOCK_SIZE
        self.xdir = 1
        self.ydir = 0
        self.head = pygame.Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)
        self.body = [pygame.Rect(self.x - BLOCK_SIZE, self.y, BLOCK_SIZE, BLOCK_SIZE)]

        self.dead = False

    def update(self):

        global apple
        for square in self.body:
            if self.head.x == square.x and self.head.y == square.y:
                self.dead = True
            if self.head.x not in range(0, SW) or self.head.y not in range(0, SH):
                self.dead = True

        if self.dead:
            self.x, self.y = BLOCK_SIZE, BLOCK_SIZE
            self.head = pygame.Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)
            self.body = [pygame.Rect(self.x - BLOCK_SIZE, self.y, BLOCK_SIZE, BLOCK_SIZE)]
            self.xdir = 1
            self.ydir = 0

            self.dead = False
            occupied = [(square.x, square.y) for square in self.body]
            occupied.append((self.head.x, self.head.y))
            apple = Apple(occupied)


        self.body.append(self.head)
        for i in range(len(self.body)-1):
            self.body[i].x, self.body[i].y = self.body[i+1].x, self.body[i+1].y
        self.head.x += self.xdir * BLOCK_SIZE
        self.head.y += self.ydir * BLOCK_SIZE
        self.body.remove(self.head)

class Apple:
    def __init__(self, occupied_positions):
        while True:
            self.x = random.randint(0, SW // BLOCK_SIZE - 1) * BLOCK_SIZE
            self.y = random.randint(0, SH // BLOCK_SIZE - 1) * BLOCK_SIZE
            if (self.x, self.y) not in occupied_positions:
                break
        
        self.rect = pygame.Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)

    def update(self):
        pygame.draw.rect(screen, "red", self.rect)

def drawGrid():
    for x in range(0, SW, BLOCK_SIZE):
        for y in range(0, SH, BLOCK_SIZE):
            rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, "#3c3c3b", rect, 1)

score = FONT.render("1", True, "white")
score_rect = score.get_rect(center=(SW/2, SH/20)) 


drawGrid()


snake = Snake()

occupied = [(square.x, square.y) for square in snake.body]
occupied.append((snake.head.x, snake.head.y))
apple = Apple(occupied)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                snake.ydir = 1
                snake.xdir = 0
            elif event.key == pygame.K_UP:
                snake.ydir = -1
                snake.xdir = 0
            elif event.key == pygame.K_RIGHT:
                snake.ydir = 0
                snake.xdir = 1
            elif event.key == pygame.K_LEFT:
                snake.ydir = 0
                snake.xdir = -1

    snake.update()

    screen.fill("black")
    drawGrid()

    apple.update()

    score = FONT.render(f"{len(snake.body) + 1}", True, "white")

    


    screen.blit(score, score_rect)

    # === CUSTOM COLORS ===
    green = (60, 179, 113)
    darkgreen = (0, 100, 0)


    # desenăm capul
    pygame.draw.rect(screen, darkgreen, snake.head)

    # desenăm corpul fără coadă
    if len(snake.body) > 1:
        for square in snake.body[1:]:
            pygame.draw.rect(screen, green, square)

    # desenăm coada cu transparență
    if snake.body:
        tail = snake.body[0]
        tail_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        tail_surface.fill((0, 100, 0, 100))  # dark green cu transparență
        screen.blit(tail_surface, (tail.x, tail.y))


    if snake.head.x == apple.x and snake.head.y == apple.y:
        last = snake.body[-1]
        snake.body.append(pygame.Rect(last.x, last.y, BLOCK_SIZE, BLOCK_SIZE))

        occupied = [(square.x, square.y) for square in snake.body]
        occupied.append((snake.head.x, snake.head.y))
        apple = Apple(occupied)

    pygame.display.update()
    clock.tick(6)
