import pygame
import sys
import random
import time

pygame.init()

from config import SW, SH, BLOCK_SIZE, player_name
from apple import NormalApple, RottenApple, PoisonousApple
from snake import Snake
from snake_ai import SnakeAI
from population import PopulationManager
from utils import manhattan_dist
from button import Button
from settings_manager import load_settings
import config

BG_PAUSE = pygame.image.load("assets/overlay_pause.png")
BG_PAUSE = pygame.transform.scale(BG_PAUSE, (SW, SH))


FONT = pygame.font.Font("arial.ttf", BLOCK_SIZE * 2)
UI_FONT = pygame.font.Font("arial.ttf", 50)
TITLE_FONT = pygame.font.Font("arial.ttf", 100)

death_messages = []

def get_occupied_positions(snake):
    return [(square.x, square.y) for square in snake.body] + [(snake.head.x, snake.head.y)]

def spawn_apple(apples, snake, cls):
    apples.append(cls(get_occupied_positions(snake)))

def draw_grid(screen):
    for x in range(0, SW, BLOCK_SIZE):
        for y in range(0, SH, BLOCK_SIZE):
            rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, "#3c3c3b", rect, 1)



def draw_scoreboard(screen, snakes):
    font = pygame.font.SysFont("Arial", 18, bold=True)
    snakes_sorted = sorted(snakes, key=lambda s: s.score, reverse=True)

    scoreboard_surf = pygame.Surface((220, 30 + len(snakes) * 25), pygame.SRCALPHA)
    scoreboard_surf.fill((0, 0, 0, 150))  # semitransparent

    title_surface = font.render("Scoreboard", True, (255, 255, 255))
    scoreboard_surf.blit(title_surface, (10, 5))

    for i, snake in enumerate(snakes_sorted):
        name_display = (getattr(snake, "name", None) or f"Snake{getattr(snake, 'id', '?')}")

        # Folosește fallback la "True" dacă atributul `alive` nu există
        is_alive = getattr(snake, "alive", True)
        score_text = f"{i+1}: {name_display[:10]} = {snake.score}" if is_alive else f"{i+1}: {name_display[:10]} = ({snake.score})"

        line_surface = font.render(score_text, True, (255, 255, 255))
        scoreboard_surf.blit(line_surface, (10, 30 + i * 25))

    screen_width = screen.get_width()
    screen.blit(scoreboard_surf, (screen_width - scoreboard_surf.get_width() - 10, 10))




death_messages = []

def add_death_message(text):
    if text is None:
        return
    death_messages.append({
        "text": str(text),
        "created_at": pygame.time.get_ticks()
    })




def draw_death_messages(screen):
    now = pygame.time.get_ticks()
    font = pygame.font.SysFont("Arial", 20)  # font mai mic

    line_height = 24  # spațiere între linii
    bottom_margin = 10
    right_margin = 20

    # desenăm de jos în sus
    messages_to_draw = []
    for msg in death_messages[:]:
        elapsed = now - msg["created_at"]
        if elapsed > 3000:
            death_messages.remove(msg)
            continue
        alpha = max(0, 255 - int((elapsed / 3000) * 255))
        messages_to_draw.append((msg["text"], alpha))

    for i, (text, alpha) in enumerate(reversed(messages_to_draw)):
        text_surface = font.render(text, True, (255, 255, 255))
        text_surface.set_alpha(alpha)
        rect = text_surface.get_rect(bottomright=(
            config.SW - right_margin,
            config.SH - bottom_margin - i * line_height
        ))
        screen.blit(text_surface, rect)



def merge_snakes(attacker, target):
    attacker.kills = getattr(attacker, "kills", 0) + 1

    # Bonus dacă victima avea scor mai mare
    if getattr(target, "score", 0) > getattr(attacker, "score", 0):
        bonus = target.score
        attacker.score += bonus
        add_death_message(f"{attacker.name} earned {bonus} bonus points!")

    # Extinde corpul atacatorului în spate
    for _ in target.body:
        tail = attacker.body[0] if attacker.body else attacker.head
        new_block = tail.copy()
        new_block.x -= attacker.xdir * config.BLOCK_SIZE
        new_block.y -= attacker.ydir * config.BLOCK_SIZE
        attacker.body.insert(0, new_block)

    target.dead = True
    target.body.clear()




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
    apples = []
    death_messages.clear()

    global_steps = 0  # număr total de pași globali
    pop_manager = None  # populația AI


    HEADSTART_DURATION = 10  # secunde
    headstart_start_time = time.time()

    # === Setup snakes ===
    snakes = []

    if config.GAME_TYPE == "solo":
        player_name = load_settings()
        player = Snake()
        player.name = player_name
        snakes.append(player)

    elif config.GAME_TYPE == "ai_only":
        pop_manager = PopulationManager()
        pop_manager.initialize_population(config.NUM_AI_SNAKES)
        snakes = pop_manager.get_alive_snakes()

    elif config.GAME_TYPE == "ai_with_player":
        from settings_manager import get_ai_snake_count, get_headstart_duration

        player_name = load_settings()
        player = Snake()
        player.name = player_name

        pop_manager = PopulationManager()
        num_ai = get_ai_snake_count()
        pop_manager.initialize_population(num_ai)

        snakes = [player] + pop_manager.get_alive_snakes()

        headstart_duration = get_headstart_duration()
        headstart_start_time = time.time()


    elif config.GAME_TYPE == "ai_only_no_training":
        pop_manager = PopulationManager()
        pop_manager.initialize_population(config.NUM_AI_SNAKES)
        snakes = pop_manager.get_alive_snakes()

    spawn_apple(apples, snakes[0], NormalApple)  # folosim poziția primului snake

    # === Timere pentru mere ===
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
                if config.GAME_TYPE in ["solo", "ai_with_player"]:
                    
                
                    if event.key == pygame.K_DOWN and player.ydir != -1:
                        player.ydir = 1; player.xdir = 0
                    elif event.key == pygame.K_UP and player.ydir != 1:
                        player.ydir = -1; player.xdir = 0
                    elif event.key == pygame.K_RIGHT and player.xdir != -1:
                        player.ydir = 0; player.xdir = 1
                    elif event.key == pygame.K_LEFT and player.xdir != 1:
                        player.ydir = 0; player.xdir = -1

        # === Update snakes ===
    
        for snake in snakes:
            if isinstance(snake, SnakeAI):
                if not snake.dead:
                    # HEADSTART: AI snakes nu se mișcă încă
                    if config.GAME_TYPE == "ai_with_player" and (time.time() - headstart_start_time) < headstart_duration:
                        continue  # SKIP AI update
                    if snake.has_timed_out():
                        snake.dead = True
                        add_death_message(f"{snake.name} timed out after {snake.steps} steps (score: {snake.score})")
                        print(f"[TIMEOUT] {snake.name} died after {snake.steps} steps (score: {snake.score})")

                        continue  # trece la următorul snake


                    # Creează state-ul complet
                    state = snake.build_state(apples, snakes)
                    snake.update(state)
            else:
                if not snake.dead:
                    snake.update()



        global_steps += 1

        # if config.GAME_TYPE == "ai_only":
        #     if global_steps % config.T == 0:
        #         pop_manager.evolve_population()
        #         global_steps = 0
        #         snakes = pop_manager.get_alive_snakes()



        

        snakes = [s for s in snakes if not s.dead]

        from settings_manager import get_challengers_enabled

        # === Spawn challengers dacă rămâne un singur șarpe și e destul de mare ===
        if config.GAME_TYPE == "ai_only" and pop_manager:
            challengers_enabled = get_challengers_enabled()
            alive_snakes = [s for s in snakes if not s.dead]
            if len(alive_snakes) == 1:
                lone = alive_snakes[0]
                current_len = len(lone.body) + 1
                if not hasattr(lone, "last_spawn_len"):
                    lone.last_spawn_len = 0
                if challengers_enabled:
                    if current_len >= lone.last_spawn_len + 20:
                        lone.last_spawn_len = current_len

                        challengers = []
                        for i in range(2):
                            challenger = SnakeAI()
                            challenger.name = f"Challenger_{i+1}"

                            # lungime proporțională
                            percent = random.randint(50, 70)
                            clone_len = max(3, current_len * percent // 100)
                            challenger.head = lone.head.copy()
                            challenger.randomize_position_away_from([lone] + challengers)

                            for _ in range(clone_len - 1):
                                block = challenger.head.copy()
                                block.x += BLOCK_SIZE
                                challenger.body.append(block)

                            # 💡 scor inițial proporțional cu dimensiune și scorul sarpelui dominant
                            scale = (clone_len / current_len)
                            challenger.score = int(scale * lone.score * random.uniform(0.9, 1.1))  # ±10% random
                            challenger.steps_survived = int(scale * getattr(lone, "steps_survived", 0))

                            challengers.append(challenger)
                            pop_manager.snakes.append(challenger)
                            add_death_message(f"A new challenger has appeared!")

                        snakes.extend(challengers)

        # Dacă toți au murit și suntem în modul AI-only, generează generație nouă automat
        if config.GAME_TYPE == "ai_only" and pop_manager and not snakes:
            draw_death_messages(screen)
            pygame.display.update()
            pygame.time.delay(1000)  # 1 secundă ca să vedem ultimul mesaj
            pop_manager.evolve_population()
            snakes = pop_manager.get_alive_snakes()
            continue  # treci la următorul frame fără să desenezi sau accesezi head-ul inexistent

        # === Coliziune între șerpi (prădare) ===
        for attacker in snakes:
            if attacker.dead:
                continue
            for target in snakes:
                if target == attacker or target.dead:
                    continue
                for segment in target.body:
                    if attacker.head.colliderect(segment):
                        attacker_len = len(attacker.body) + 1
                        target_len = len(target.body) + 1
                        if target_len <= config.L_PROCENT * attacker_len:
                            # Apelăm funcția merge_snakes pentru a combina corpurile
                            merge_snakes(attacker, target)
                            add_death_message(f"{target.name} was eaten by {attacker.name}")

                            #  FIX: ieșim din verificări pentru ca attacker să nu moară aiurea mai jos
                            break  # ieși din for segment
                        else:
                            attacker.dead = True  # s-a izbit de un șarpe mai mare
                            add_death_message(f"{attacker.name} died hitting {target.name}")
                            break  # ieși din for segment (după moartea attackerului)
                if attacker.dead:
                    break  # dacă a murit în coliziunea curentă, nu mai verifica alte targeturi




        # === Coliziune cap-la-cap ===
        for i in range(len(snakes)):
            for j in range(i + 1, len(snakes)):
                s1, s2 = snakes[i], snakes[j]
                if s1.dead or s2.dead:
                    continue
                if s1.head.colliderect(s2.head):
                    len1 = len(s1.body) + 1
                    len2 = len(s2.body) + 1
                    if len1 > len2:
                        s2.dead = True
                        s1.body.extend(s2.body)
                        s2.body.clear()
                        s1.kills = getattr(s1, "kills", 0) + 1
                        add_death_message(f"{s2.name} died in a head clash with {s1.name}",)
                    elif len2 > len1:
                        s1.dead = True
                        s2.body.extend(s1.body)
                        s1.body.clear()
                        s2.kills = getattr(s2, "kills", 0) + 1
                        add_death_message(f"{s1.name} died in a head clash with {s2.name}")
                    else:
                        # egalitate – mor amândoi
                        s1.dead = True
                        s2.dead = True
                        add_death_message(f"{s1.name} and {s2.name} clashed equally and died")



        # === Dacă playerul moare ===
        if config.GAME_TYPE in ["solo", "ai_with_player"] and player.dead:
            choice = death_menu(screen, len(player.body) + 1)
            if choice == "again":
                return start_game(screen)
            elif choice == "menu":
                return

        # === Spawn mere ===
        alive_snake = next((s for s in snakes if not s.dead), None)
        if alive_snake:
            if now - last_rotten_spawn > ROTTEN_INTERVAL:
                spawn_apple(apples, alive_snake, RottenApple)
                last_rotten_spawn = now

            if now - last_poisonous_spawn > next_poisonous_spawn:
                spawn_apple(apples, alive_snake, PoisonousApple)
                last_poisonous_spawn = now
                next_poisonous_spawn = random.randint(POISONOUS_INTERVAL_MIN, POISONOUS_INTERVAL_MAX)

            if now - last_normal_spawn > NORMAL_SPAWN_INTERVAL:
                spawn_apple(apples, alive_snake, NormalApple)
                last_normal_spawn = now

            while len(apples) < 4:
                spawn_apple(apples, alive_snake, random.choice([NormalApple, RottenApple, PoisonousApple]))

            normal_count = sum(isinstance(a, NormalApple) for a in apples)
            while normal_count < 2:
                spawn_apple(apples, alive_snake, NormalApple)
                normal_count += 1


       # === Coliziune snake-apple ===
        to_remove = []
        for snake in snakes:
            for apple in apples:
                if apple.is_expired():
                    to_remove.append(apple)
                elif snake.head.colliderect(apple.rect):
                    apple.apply_effect(snake)
                    to_remove.append(apple)

                    # Verificăm cauza morții și adăugăm mesaj
                    if isinstance(apple, PoisonousApple) and snake.dead:
                        add_death_message(f"{snake.name} got poisoned!")
                        snake.last_death_reason = "poison"
                    elif isinstance(apple, RottenApple) and snake.rotten_count > 1 and snake.dead:
                        add_death_message(f"{snake.name} ate too many rotten apples")

                    if sum(isinstance(a, NormalApple) for a in apples if a not in to_remove) < 2:
                        spawn_apple(apples, snake, NormalApple)
                    else:
                        spawn_apple(apples, snake, random.choice([NormalApple, RottenApple, PoisonousApple]))
        for a in to_remove:
            if a in apples:
                apples.remove(a)

        # === Drawing ===
        

        screen.fill("black")
        draw_grid(screen)

        if config.GAME_TYPE == "ai_with_player":
            elapsed = time.time() - headstart_start_time
            if elapsed < headstart_duration:
                remaining = int(headstart_duration - elapsed)
                countdown_text = UI_FONT.render(f"Headstart: {remaining}", True, "#ffcc00")
                screen.blit(countdown_text, (SW // 2 - 100, 80))

            elif abs(elapsed - headstart_duration) < 1:
                go_text = UI_FONT.render("GO!", True, "#00ff00")
                screen.blit(go_text, go_text.get_rect(center=(SW // 2, 80)))

        for apple in apples:
            reference_head = snakes[0].head if snakes else pygame.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE)
            alive_snakes = [s for s in snakes if not s.dead]

            if alive_snakes:
                reference_head = alive_snakes[0].head
                for apple in apples:
                    apple.draw(screen, reference_head)


        for snake in snakes:
            if isinstance(snake, SnakeAI):  # șarpe AI
                pygame.draw.rect(screen, (255, 140, 0), snake.head)  # cap portocaliu
                for square in snake.body[1:]:
                    pygame.draw.rect(screen, (255, 215, 0), square)  # corp galben
            else:  # player uman
                pygame.draw.rect(screen, (0, 100, 0), snake.head)
                for square in snake.body[1:]:
                    pygame.draw.rect(screen, (60, 179, 113), square)
            # Desenează numele pe cap
            font = pygame.font.SysFont("Arial", 18, bold=True)
            name_surface = font.render(snake.name, True, (255, 255, 255))  # text alb
            screen.blit(name_surface, (snake.head.x + 5, snake.head.y + 5))  # poziționează lângă cap

            if snake.body:
                tail = snake.body[0]
                tail_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                tail_surface.fill((0, 100, 0, 100))  # efect de fade pe coadă
                screen.blit(tail_surface, (tail.x, tail.y))

        if config.GAME_TYPE in ["ai_only", "ai_only_no_training"] and pop_manager:
            gen_text = UI_FONT.render(f"Gen: {pop_manager.generation}", True, "white")
            screen.blit(gen_text, (20, 10))

            best_score = max((s.score + s.kills * 5 for s in snakes), default=0)
            score_text = UI_FONT.render(f"Best: {best_score}", True, "white")
            screen.blit(score_text, (20, 60))



        # === Scor player ===
        if config.GAME_TYPE in ["solo", "ai_with_player"]:
            score_text = FONT.render(f"{len(player.body)+1}", True, "white")
            score_rect = score_text.get_rect(center=(SW / 2, SH / 20))
            screen.blit(score_text, score_rect)



        

        # === Death messages (fade-out) ===
        draw_death_messages(screen)



        draw_scoreboard(screen, snakes)

        pygame.display.update()
        clock.tick(config.SNAKE_SPEED)


