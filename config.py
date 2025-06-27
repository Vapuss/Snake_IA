from settings_manager import load_settings, get_block_size

# Screen width and height, most likely will have to be changed depending on the user's screen size, should implement an option to change it from the settings/adaptiveness for each screen size
SW, SH = 1600, 900
BLOCK_SIZE = get_block_size()
APPLE_LIFESPAN = 10
FADE_START = 5  # secunde


player_name = load_settings()

GAME_TYPE = "solo"  # valori posibile: "solo", "ai_only", "ai_with_player"

SNAKE_SPEED = 2  # frame-uri pe secundă (FPS)


# Viteza inițială și raza de vizualizare pentru AI snakes
V_INIT = 10
R_INIT = 80

# Număr inițial de șerpi AI
NUM_AI_SNAKES = 8

# Număr de elită (pentru algoritm genetic, folosit mai târziu)
N_ELITE = 2

# Pași pentru îmbătrânire
PV = 200  # la fiecare PV pași scade viteza și raza
V_PAS = 1
R_PAS = 1

#numărul de pași până la următoarea generație
T = 300

L_PROCENT = 0.5 

CONTROLLED_BY_HUMAN = True
