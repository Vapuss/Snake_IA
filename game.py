import pygame
import sys
import random
import time

pygame.init()

from config import SW, SH, BLOCK_SIZE, player_name
from apple import NormalApple, RottenApple, PoisonousApple
from snake import Snake
from utils import manhattan_dist
from button import Button
import config

BG_PAUSE = pygame.image.load("assets/overlay_pause.png")
BG_PAUSE = pygame.transform.scale(BG_PAUSE, (SW, SH))


FONT = pygame.font.Font("arial.ttf", BLOCK_SIZE * 2)
UI_FONT = pygame.font.Font("arial.ttf", 50)
TITLE_FONT = pygame.font.Font("arial.ttf", 100)

def get_occupied_positions(snake):
    return [(square.x, square.y) for square in snake.body] + [(snake.head.x, snake.head.y)]

def spawn_apple(apples, snake, cls):
    apples.append(cls(get_occupied_positions(snake)))

def draw_grid(screen):
    for x in range(0, SW, BLOCK_SIZE):
        for y in range(0, SH, BLOCK_SIZE):
            rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, "#3c3c3b", rect, 1)

def pause_menu(screen):
    while True:
        screen.blit(BG_PAUSE, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        title = TITLE_FONT.render("PAUSED", True, "white")
        screen.blit(title, title.get_rect(center=(SW // 2, 200)))

        resume = Button(None, (SW//2, 350), "RESUME", UI_FONT, "white", "green")
        mainmenu = Button(None, (SW//2, 450), "MAIN MENU", UI_FONT, "white", "yellow")
        quitgame = Button(None, (SW//2, 550), "QUIT", UI_FONT, "white", "red")

        for b in [resume, mainmenu, quitgame]:
            b.change_color(mouse_pos)
            b.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume.check_for_input(mouse_pos):
                    return "resume"
                elif mainmenu.check_for_input(mouse_pos):
                    return "menu"
                elif quitgame.check_for_input(mouse_pos):
                    pygame.quit(); sys.exit()

        pygame.display.update()

def death_menu(screen, score):
    while True:
        screen.blit(BG_PAUSE, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        title = TITLE_FONT.render("YOU DIED", True, "red")
        screen.blit(title, title.get_rect(center=(SW // 2, 200)))

        score_txt = UI_FONT.render(f"{config.player_name}'s Score: {score}", True, "white")
        screen.blit(score_txt, score_txt.get_rect(center=(SW // 2, 280)))

        again = Button(None, (SW//2, 400), "PLAY AGAIN", UI_FONT, "white", "green")
        mainmenu = Button(None, (SW//2, 500), "MAIN MENU", UI_FONT, "white", "yellow")
        quitgame = Button(None, (SW//2, 600), "QUIT", UI_FONT, "white", "red")

        for b in [again, mainmenu, quitgame]:
            b.change_color(mouse_pos)
            b.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if again.check_for_input(mouse_pos):
                    return "again"
                elif mainmenu.check_for_input(mouse_pos):
                    return "menu"
                elif quitgame.check_for_input(mouse_pos):
                    pygame.quit(); sys.exit()

        pygame.display.update()

def start_game(screen):
    clock = pygame.time.Clock()
    snake = Snake()
    apples = []
    spawn_apple(apples, snake, NormalApple)

    last_rotten_spawn = time.time()
    last_poisonous_spawn = time.time()
    last_normal_spawn = time.time()
    ROTTEN_INTERVAL = 5
    POISONOUS_INTERVAL_MIN = 10
    POISONOUS_INTERVAL_MAX = 30
    NORMAL_SPAWN_INTERVAL = 5
    next_poisonous_spawn = random.randint(POISONOUS_INTERVAL_MIN, POISONOUS_INTERVAL_MAX)

    while True:
        now = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    choice = pause_menu(screen)
                    if choice == "menu":
                        return
                elif event.key == pygame.K_DOWN and snake.ydir != -1:
                    snake.ydir = 1; snake.xdir = 0
                elif event.key == pygame.K_UP and snake.ydir != 1:
                    snake.ydir = -1; snake.xdir = 0
                elif event.key == pygame.K_RIGHT and snake.xdir != -1:
                    snake.ydir = 0; snake.xdir = 1
                elif event.key == pygame.K_LEFT and snake.xdir != 1:
                    snake.ydir = 0; snake.xdir = -1

        snake.update()

        if snake.dead:
            choice = death_menu(screen, len(snake.body) + 1)
            if choice == "again":
                return start_game(screen)
            elif choice == "menu":
                return

        # Spawning logic
        if now - last_rotten_spawn > ROTTEN_INTERVAL:
            spawn_apple(apples, snake, RottenApple)
            last_rotten_spawn = now

        if now - last_poisonous_spawn > next_poisonous_spawn:
            spawn_apple(apples, snake, PoisonousApple)
            last_poisonous_spawn = now
            next_poisonous_spawn = random.randint(POISONOUS_INTERVAL_MIN, POISONOUS_INTERVAL_MAX)

        if now - last_normal_spawn > NORMAL_SPAWN_INTERVAL:
            spawn_apple(apples, snake, NormalApple)
            last_normal_spawn = now

        while len(apples) < 4:
            spawn_apple(apples, snake, random.choice([NormalApple, RottenApple, PoisonousApple]))
        normal_count = sum(isinstance(a, NormalApple) for a in apples)
        while normal_count < 2:
            spawn_apple(apples, snake, NormalApple)
            normal_count += 1

        # DRAWING
        screen.fill("black")
        draw_grid(screen)

        to_remove = []
        for apple in apples:
            expired = apple.is_expired()
            collided = snake.head.colliderect(apple.rect)
            if collided and not expired:
                apple.apply_effect(snake)
                to_remove.append(apple)
                normal_count = sum(isinstance(a, NormalApple) for a in apples if a not in to_remove)
                if normal_count < 2:
                    spawn_apple(apples, snake, NormalApple)
                else:
                    spawn_apple(apples, snake, random.choice([NormalApple, RottenApple, PoisonousApple]))
            elif expired:
                to_remove.append(apple)
            else:
                apple.draw(screen, snake.head)

        for a in to_remove:
            if a in apples:
                apples.remove(a)

        # Draw snake
        pygame.draw.rect(screen, (0, 100, 0), snake.head)
        for square in snake.body[1:]:
            pygame.draw.rect(screen, (60, 179, 113), square)
        if snake.body:
            tail = snake.body[0]
            tail_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
            tail_surface.fill((0, 100, 0, 100))
            screen.blit(tail_surface, (tail.x, tail.y))

        # Score
        score_text = FONT.render(f"{len(snake.body)+1}", True, "white")
        score_rect = score_text.get_rect(center=(SW / 2, SH / 20))
        screen.blit(score_text, score_rect)

        pygame.display.update()
        clock.tick(config.SNAKE_SPEED)

