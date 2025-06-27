import pygame
import config

from config import  SW, SH


class Snake:
    def __init__(self):
        self.x, self.y = config.BLOCK_SIZE, config.BLOCK_SIZE
        self.xdir = 1
        self.ydir = 0
        self.head = pygame.Rect(self.x, self.y, config.BLOCK_SIZE, config.BLOCK_SIZE)
        self.body = [pygame.Rect(self.x - config.BLOCK_SIZE, self.y, config.BLOCK_SIZE, config.BLOCK_SIZE)]
        self.dead = False
        self.rotten_penalty = 1  # câte segmente pierde la următorul rotten
        self.score = 0
        self.kills = 0
        self.rotten_count = 0

        self.fruit_streak = 0  # Inițializare streak de mere
        self.last_apple_type = None  # Ținem minte ce tip de măr a fost ultimul consumat
        
    def reset_streak(self):
        self.fruit_streak = 0  # Resetăm streak-ul când mănâncă un rotten apple

    def reset(self):
        self.__init__()

    def update(self):
        for square in self.body:
            if self.head.colliderect(square):
                self.dead = True
        if self.head.x not in range(0, SW) or self.head.y not in range(0, SH):
            self.dead = True

        if not self.dead:
            self.body.append(self.head.copy())
            for i in range(len(self.body)-1):
                self.body[i].x, self.body[i].y = self.body[i+1].x, self.body[i+1].y
            self.head.x += self.xdir * config.BLOCK_SIZE
            self.head.y += self.ydir * config.BLOCK_SIZE
            if self.body:
                self.body.pop()


    def grow(self):
        if self.body:
            last = self.body[-1]
        else:
            last = self.head
        self.body.append(pygame.Rect(last.x, last.y, config.BLOCK_SIZE, config.BLOCK_SIZE))

    def shrink(self, amount):
        for _ in range(amount):
            if self.body:
                self.body.pop(0)
        # dacă rămâne fără corp, moare
        if len(self.body) < 1:
            self.dead = True

