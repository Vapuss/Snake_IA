import pygame
import random
import time
from config import *
from utils import manhattan_dist

class AppleBase:
    def __init__(self, occupied):
        while True:
            self.x = random.randint(0, SW // BLOCK_SIZE - 1) * BLOCK_SIZE
            self.y = random.randint(0, SH // BLOCK_SIZE - 1) * BLOCK_SIZE
            if (self.x, self.y) not in occupied:
                break
        self.rect = pygame.Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)
        self.spawn_time = time.time()
        self.alpha = 255

    def is_expired(self):
        return time.time() - self.spawn_time >= APPLE_LIFESPAN

    def fading(self):
        t = time.time() - self.spawn_time
        if t > FADE_START:
            return int(255 * (1 - (t - FADE_START) / (APPLE_LIFESPAN - FADE_START)))
        return 255

    def draw(self, screen, snake_head):
        surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        color = self.get_color(snake_head)
        alpha = self.fading()
        surface.fill((*color, alpha))
        screen.blit(surface, (self.rect.x, self.rect.y))

    def get_color(self, snake_head):
        # convertim în coordonate de grid
        head_pos = (snake_head.x // BLOCK_SIZE, snake_head.y // BLOCK_SIZE)
        apple_pos = (self.rect.x // BLOCK_SIZE, self.rect.y // BLOCK_SIZE)
        dist = manhattan_dist(head_pos, apple_pos)
        return self.warn_color if dist <= 3 else self.base_color

    def apply_effect(self, snake):
        pass  # override în subclasses

class NormalApple(AppleBase):
    base_color = (255, 0, 0)
    warn_color = (255, 0, 0)

    def apply_effect(self, snake):
        snake.grow()

class RottenApple(AppleBase):
    base_color = (255, 0, 0)
    warn_color = (139, 69, 19)  # maro

    def apply_effect(self, snake):
        snake.shrink(snake.rotten_penalty)
        snake.rotten_penalty += 1

class PoisonousApple(AppleBase):
    base_color = (255, 0, 0)
    warn_color = (128, 0, 128)  # mov

    def apply_effect(self, snake):
        if len(snake.body) + 1 >= 4:
            snake.dead = True
