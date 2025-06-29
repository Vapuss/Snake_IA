import heapq  # folosit pentru a implementa o coada de prioritati (min-heap)
from config import SW, SH  # dimensiunile ecranului, in pixeli
import config  # importam intregul modul config (pentru BLOCK_SIZE, etc.)

# Directii posibile (miscare pe harta)
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

# Convertim o directie inversa in stringul corespunzator ("UP", "DOWN", etc.)
REVERSE_DIRECTIONS = {v: k for k, v in DIRECTIONS.items()}

def a_star(start, goal, obstacles, grid_width=None, grid_height=None):
    """
    start, goal: tupluri (x, y) in coordonate de harta
    obstacles: set de pozitii blocate (ex: pereti, corpul sarpelui, alti serpi)
    grid_width, grid_height: dimensiunea hartii; daca nu sunt date, le luam din config
    """
    grid_width = grid_width or (SW // config.BLOCK_SIZE)  # numar de celule pe orizontala
    grid_height = grid_height or (SH // config.BLOCK_SIZE)  # numar de celule pe verticala

    # Verifica daca o pozitie e in limitele hartii
    def in_bounds(pos):
        x, y = pos
        return 0 <= x < grid_width and 0 <= y < grid_height

    # Returneaza vecinii valizi ai unei celule (care nu sunt obstacole)
    def neighbors(pos):
        result = []
        for dx, dy in DIRECTIONS.values():
            nxt = (pos[0] + dx, pos[1] + dy)
            if in_bounds(nxt) and nxt not in obstacles:
                result.append(nxt)
        return result

    # Heuristica A*: distanta Manhattan intre doua puncte (ignora obstacolele)
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    frontier = []  # coada de prioritati (heap), contine celulele ce urmeaza a fi explorate
    heapq.heappush(frontier, (0, start))  # adaugam startul cu prioritate 0

    came_from = {start: None}  # tine minte cum am ajuns la fiecare celula
    cost_so_far = {start: 0}  # costul acumulat pana la fiecare celula

    # Cat timp mai avem celule de explorat
    while frontier:
        _, current = heapq.heappop(frontier)  # extragem celula cu cea mai mica prioritate

        if current == goal:  # daca am ajuns la tinta, ne oprim
            break

        for nxt in neighbors(current):  # exploram vecinii valizi
            new_cost = cost_so_far[current] + 1  # fiecare mutare are cost 1
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:  # daca gasim un drum mai scurt
                cost_so_far[nxt] = new_cost  # salvam noul cost
                priority = new_cost + heuristic(goal, nxt)  # cost real + estimare pana la tinta
                heapq.heappush(frontier, (priority, nxt))  # adaugam vecinul in coada
                came_from[nxt] = current  # marcam de unde am ajuns in el

    # Daca nu exista drum catre tinta
    if goal not in came_from:
        return None

    # Reconstruim drumul de la tinta la start
    path = []
    node = goal
    while node != start:
        path.append(node)
        node = came_from[node]
    path.reverse()  # ordinea corecta: de la start la goal

    if not path:  # nu avem niciun pas de facut
        return None

    # Calculam prima directie in care trebuie sa ne miscam
    dx = path[0][0] - start[0]
    dy = path[0][1] - start[1]
    return REVERSE_DIRECTIONS.get((dx, dy))  # intoarcem "UP", "DOWN", etc.
