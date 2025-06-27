import pygame
import sys
from button import Button
import config
from game import start_game  # va fi creat imediat
from settings_manager import save_settings, save_full_settings


pygame.init()

SCREEN = pygame.display.set_mode((config.SW, config.SH))

pygame.display.set_caption("Snake AI")
pygame.display.set_icon(pygame.image.load("assets/bar_ico.ico"))

BG_COLOR = (30, 30, 30)

def get_font(size):
    return pygame.font.Font("arial.ttf", size)

def main_menu():
    while True:
        BG = pygame.image.load("assets/main_menu.png")
        BG = pygame.transform.scale(BG, (config.SW, config.SH))
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        title_text = get_font(100).render("SNAKE AI", True, "#7ad47a")
        title_rect = title_text.get_rect(center=(config.SW // 2, 120))
        SCREEN.blit(title_text, title_rect)

        play_button = Button(
            image=None, pos=(200,300),
            text_input="Play", font=get_font(70),
            base_color="white", hovering_color="#e25a00"
        )
        options_button = Button(
            image=None, pos=(200, 400),
            text_input="Settings", font=get_font(70),
            base_color="white", hovering_color="#4b39f5"
        )
        quit_button = Button(
            image=None, pos=(200, 500),
            text_input="Quit Game", font=get_font(70),
            base_color="white", hovering_color="red"
        )

        for button in [play_button, options_button, quit_button]:
            button.change_color(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.check_for_input(MENU_MOUSE_POS):
                    start_game(SCREEN)
                if options_button.check_for_input(MENU_MOUSE_POS):
                    options_menu()
                if quit_button.check_for_input(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

def options_menu():
    input_box = pygame.Rect(config.SW // 2 + 50, 160, 300, 60)
    color_inactive = pygame.Color("gray15")
    color_active = pygame.Color("white")
    color = color_inactive
    active = False
    text = config.player_name
    font = get_font(40)
    label_font = get_font(36)

    from settings_manager import get_ai_snake_count, get_headstart_duration, get_challengers_enabled, get_snake_speed, get_ai_only_snake_count

    ai_snake_count = get_ai_snake_count()
    ai_battle_snake_count  = get_ai_only_snake_count()
    headstart_duration = get_headstart_duration()
    challengers_enabled = get_challengers_enabled()
    snake_speed = get_snake_speed()
    snake_speed_min = 1
    snake_speed_max = 30

    toggle_on = toggle_off = None

    game_types = ["solo", "ai_only", "ai_with_player", "ai_only_no_training"]
    game_type_names = {
        "solo": "Solo Game",
        "ai_only": "AI Training",
        "ai_with_player": "Battle Royale + You",
        "ai_only_no_training":"AI Battle Royale"
    }
    current_index = game_types.index(config.GAME_TYPE)

    
    


    while True:
        BG = pygame.image.load("assets/overlay_pause.png")
        BG = pygame.transform.scale(BG, (config.SW, config.SH))
        SCREEN.blit(BG, (0, 0))
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        minus_btn = None
        plus_btn = None
        speed_minus_btn = None
        speed_plus_btn = None
        minus_headstart = plus_headstart = None
        

        # === Titlu mare ===
        title = get_font(60).render("Settings", True, "white")
        SCREEN.blit(title, title.get_rect(center=(config.SW // 2, 60)))

        # === Etichete stânga (aliniate pe verticală) ===
        label_x = config.SW // 6
        label_y_name = 175
        label_y_mode = 335

        SCREEN.blit(label_font.render("Enter your name", True, "white"), (label_x, label_y_name))

        label_y_speed = label_y_name + 80
        SCREEN.blit(label_font.render("Snake Speed", True, "white"), (label_x, label_y_speed))




        SCREEN.blit(label_font.render("Game Mode", True, "white"), (label_x, label_y_mode))

        # === Casetă de input nume ===
        pygame.draw.rect(SCREEN, color, input_box, 2)
        name_surface = font.render(text, True, "white")
        SCREEN.blit(name_surface, (input_box.x + 10, input_box.y + 10))



        # === Snake Speed ===

        speed_y = input_box.y + 120
        speed_minus_btn = Button(None, (input_box.x + 50, speed_y), "-", get_font(50), "white", "#cc6666")
        speed_plus_btn = Button(None, (input_box.x + 270, speed_y), "+", get_font(50), "white", "#66cc66")

        speed_text = get_font(40).render(str(snake_speed), True, "#d6b400")
        SCREEN.blit(speed_text, speed_text.get_rect(center=(input_box.x + 160, speed_y + 5)))

        for b in [speed_minus_btn, speed_plus_btn]:
            b.change_color(OPTIONS_MOUSE_POS)
            b.update(SCREEN)



        # === Game Mode selector + arrows ===
        mode_y = input_box.y + 200
        left_arrow = Button(None, (input_box.x - 15, mode_y), "<", get_font(50), "white", "#7ad47a")
        right_arrow = Button(None, (input_box.x + 335, mode_y), ">", get_font(50), "white", "#7ad47a")

        mode_text = get_font(35).render(game_type_names[game_types[current_index]], True, "#d66000")
        SCREEN.blit(mode_text, mode_text.get_rect(center=(input_box.x + 160, mode_y)))

        for arrow in [left_arrow, right_arrow]:
            arrow.change_color(OPTIONS_MOUSE_POS)
            arrow.update(SCREEN)


        if game_types[current_index] == "ai_with_player":
            SCREEN.blit(label_font.render("Number of AI snakes", True, "white"), (label_x, label_y_mode + 80))

            minus_btn = Button(None, (input_box.x + 50, mode_y + 80), "-", get_font(50), "white", "#cc6666")
            plus_btn = Button(None, (input_box.x + 270, mode_y + 75), "+", get_font(50), "white", "#66cc66")

            count_text = get_font(40).render(str(ai_snake_count), True, "#d6b400")
            SCREEN.blit(count_text, count_text.get_rect(center=(input_box.x + 160, mode_y + 80)))

            for b in [minus_btn, plus_btn]:
                b.change_color(OPTIONS_MOUSE_POS)
                b.update(SCREEN)


        


            SCREEN.blit(label_font.render("Headstart duration (sec)", True, "white"), (label_x, label_y_mode + 160))

            minus_headstart = Button(None, (input_box.x + 50, mode_y + 160), "-", get_font(50), "white", "#cc6666")
            plus_headstart = Button(None, (input_box.x + 270, mode_y + 155), "+", get_font(50), "white", "#66cc66")

            head_text = get_font(40).render(str(headstart_duration), True, "#00e6e6")
            SCREEN.blit(head_text, head_text.get_rect(center=(input_box.x + 160, mode_y + 160)))

            for b in [minus_headstart, plus_headstart]:
                b.change_color(OPTIONS_MOUSE_POS)
                b.update(SCREEN)

        if game_types[current_index] == "ai_only_no_training":
            SCREEN.blit(label_font.render("Number of AI snakes", True, "white"), (label_x, label_y_mode + 80))

            minus_btn = Button(None, (input_box.x + 50, mode_y + 80), "-", get_font(50), "white", "#cc6666")
            plus_btn = Button(None, (input_box.x + 270, mode_y + 75), "+", get_font(50), "white", "#66cc66")

            
            count_text = get_font(40).render(str(ai_battle_snake_count), True, "#d6b400")
            SCREEN.blit(count_text, count_text.get_rect(center=(input_box.x + 160, mode_y + 80)))

            for b in [minus_btn, plus_btn]:
                b.change_color(OPTIONS_MOUSE_POS)
                b.update(SCREEN)


        if game_types[current_index] == "ai_only":
            SCREEN.blit(label_font.render("Enable Challengers", True, "white"), (label_x, label_y_mode + 80))

            # Butoane pentru On/Off
            toggle_on = Button(None, (input_box.x + 50, mode_y + 80), "ON", get_font(50), "white", "#66cc66")
            toggle_off = Button(None, (input_box.x + 270, mode_y + 80), "OFF", get_font(50), "white", "#cc6666")

            
            status_text = get_font(40).render("ON" if challengers_enabled else "OFF", True, "#d6b400")
            SCREEN.blit(status_text, status_text.get_rect(center=(input_box.x + 160, mode_y + 80)))

            for b in [toggle_on, toggle_off]:
                b.change_color(OPTIONS_MOUSE_POS)
                b.update(SCREEN)


        # === Buton Back colț dreapta jos ===
        back_button = Button(
            image=None,
            pos=(config.SW - 100, config.SH - 40),
            text_input="Back",
            font=get_font(40),
            base_color="white",
            hovering_color="orange"
        )
        back_button.change_color(OPTIONS_MOUSE_POS)
        back_button.update(SCREEN)


        # === Events ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False

                if left_arrow.check_for_input(OPTIONS_MOUSE_POS):
                    current_index = (current_index - 1) % len(game_types)
                    config.GAME_TYPE = game_types[current_index]

                if right_arrow.check_for_input(OPTIONS_MOUSE_POS):
                    current_index = (current_index + 1) % len(game_types)
                    config.GAME_TYPE = game_types[current_index]

                if speed_minus_btn.check_for_input(OPTIONS_MOUSE_POS):
                    if snake_speed > snake_speed_min:
                        snake_speed -= 1
                        config.SNAKE_SPEED = snake_speed

                if speed_plus_btn.check_for_input(OPTIONS_MOUSE_POS):
                    if snake_speed < snake_speed_max:
                        snake_speed += 1
                        config.SNAKE_SPEED = snake_speed



                if back_button.check_for_input(OPTIONS_MOUSE_POS):
                    name_final = text if text.strip() else "Player"
                    config.player_name = name_final
                    settings_to_save = {
                        "player_name": name_final,
                        "ai_snake_count": ai_snake_count,
                        "headstart_duration": headstart_duration,
                        "challengers_enabled": challengers_enabled,
                        "snake_speed": snake_speed,
                        "ai_only_snake_count": ai_battle_snake_count
                    }
                    save_full_settings(settings_to_save)
                    return
                
                if game_types[current_index] == "ai_only":
                    if toggle_on and toggle_on.check_for_input(OPTIONS_MOUSE_POS):
                        challengers_enabled = True
                    if toggle_off and toggle_off.check_for_input(OPTIONS_MOUSE_POS):
                        challengers_enabled = False
                
                if game_types[current_index] == "ai_with_player":
                    if minus_btn and minus_btn.check_for_input(OPTIONS_MOUSE_POS):
                        ai_snake_count = max(1, ai_snake_count - 1)
                    if plus_btn and plus_btn.check_for_input(OPTIONS_MOUSE_POS):
                        ai_snake_count = min(30, ai_snake_count + 1)

                    if minus_headstart and minus_headstart.check_for_input(OPTIONS_MOUSE_POS):
                        headstart_duration = max(0, headstart_duration - 1)
                    if plus_headstart and plus_headstart.check_for_input(OPTIONS_MOUSE_POS):
                        headstart_duration = min(30, headstart_duration + 1)

                if game_types[current_index] == "ai_only_no_training":
                    if minus_btn and minus_btn.check_for_input(OPTIONS_MOUSE_POS):
                        ai_battle_snake_count = max(1, ai_battle_snake_count - 1)
                    if plus_btn and plus_btn.check_for_input(OPTIONS_MOUSE_POS):
                        ai_battle_snake_count = min(30, ai_battle_snake_count + 1)


                    


            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    name_final = text if text.strip() else "Player"
                    config.player_name = name_final
                    save_settings(name_final)
                    return
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 12:
                        text += event.unicode

        color = color_active if active else color_inactive
        pygame.display.update()


