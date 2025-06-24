import pygame
import sys
from button import Button
import config
from game import start_game  # va fi creat imediat

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
    input_box = pygame.Rect(config.SW//2 - 200, 280, 400, 70)
    color_inactive = pygame.Color("gray15")
    color_active = pygame.Color("white")
    color = color_inactive
    active = False
    text = config.player_name
    font = get_font(40)

    while True:
        BG = pygame.image.load("assets/overlay_pause.png")
        BG = pygame.transform.scale(BG, (config.SW, config.SH))
        SCREEN.blit(BG, (0, 0))

        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        label = get_font(50).render("Enter your name:", True, "white")
        SCREEN.blit(label, (config.SW // 2 - label.get_width() // 2, 200))

        pygame.draw.rect(SCREEN, color, input_box, 2)
        name_surface = font.render(text, True, "white")
        SCREEN.blit(name_surface, (input_box.x + 10, input_box.y + 15))

        back_button = Button(
            image=None, pos=(config.SW // 2, 500),
            text_input="BACK", font=get_font(60),
            base_color="white", hovering_color="green"
        )

        back_button.change_color(OPTIONS_MOUSE_POS)
        back_button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False

                if back_button.check_for_input(OPTIONS_MOUSE_POS):
                    config.player_name = text if text.strip() else "Player"
                    return

            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    config.player_name = text if text.strip() else "Player"
                    return
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 12:
                        text += event.unicode

        color = color_active if active else color_inactive
        pygame.display.update()
