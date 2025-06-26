# genes.py

import random
import math
from config import SW, SH, BLOCK_SIZE

# Direcțiile posibile: sus, jos, stânga, dreapta
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

# === Clasa pentru cromozomi ===
class Chromosome:
    def __init__(self, genes=None):
        # Inițializare cu gene random (11 gene)
        if genes is None:
            self.genes = {
                "avoid_walls": random.uniform(0, 1),
                "avoid_body": random.uniform(0, 1),
                "chase_food": random.uniform(0.6, 1),
                "stay_centered": random.uniform(0, 1),
                "avoid_snakes": random.uniform(0, 1),
                "hunt_snakes": random.uniform(0.6, 1),
                "prefer_corners": random.uniform(0, 1),
                "fear_poison": random.uniform(0, 1),
                "risk_loving": random.uniform(0, 1),
                "patience": random.uniform(0.05, 0.2),
                "hunter_mode": random.uniform(0.6, 1),
            }
        else:
            self.genes = genes

    def mutate(self, rate=0.1):
        for k in self.genes:
            if random.random() < rate:
                self.genes[k] += random.uniform(-0.2, 0.2)
                self.genes[k] = max(0, min(1, self.genes[k]))

    def mutated_copy(self):
        genes_copy = dict(self.genes)
        new_chrom = Chromosome(genes_copy)
        new_chrom.mutate()
        return rebalance_gene_weights(new_chrom)



    def crossover(self, other):
        new_genes = {}
        for k in self.genes:
            new_genes[k] = random.choice([self.genes[k], other.genes[k]])
        return rebalance_gene_weights(Chromosome(new_genes))

    def evaluate(self, state, direction):
        score = 0
        for gene, weight in self.genes.items():
            func = gene_functions.get(gene)
            if func:
                score += weight * func(state, direction)
        return score

# === Funcții de scor pentru fiecare genă ===
def avoid_walls(state, direction):
    head = state["head"]
    dx, dy = DIRECTIONS[direction]
    new_x = head[0] + dx
    new_y = head[1] + dy
    if not (0 <= new_x < SW // BLOCK_SIZE and 0 <= new_y < SH // BLOCK_SIZE):
        return -10  # perete
    return 0

def avoid_body(state, direction):
    head = state["head"]
    body = state["body"]
    dx, dy = DIRECTIONS[direction]
    new_pos = (head[0] + dx, head[1] + dy)
    return -5 if new_pos in body else 0

def chase_food(state, direction):
    head = state["head"]
    food = state.get("foods", [])
    dx, dy = DIRECTIONS[direction]
    new_pos = (head[0] + dx, head[1] + dy)
    if not food:
        return 0

    dists = [abs(fx - new_pos[0]) + abs(fy - new_pos[1]) for fx, fy in food]
    min_dist = min(dists)

    # BONUS dacă mâncarea e aproape
    if min_dist <= 1:
        return 60
    elif min_dist <= 2:
        return 30
    elif min_dist <= 4:
        return 15
    else:
        return max(0, 20 - min_dist * 3)


def stay_centered(state, direction):
    head = state["head"]
    center = (SW // BLOCK_SIZE // 2, SH // BLOCK_SIZE // 2)
    dx, dy = DIRECTIONS[direction]
    new_pos = (head[0] + dx, head[1] + dy)
    dist = abs(center[0] - new_pos[0]) + abs(center[1] - new_pos[1])
    return -dist / 2

def avoid_snakes(state, direction):
    head = state["head"]
    others = state.get("others", [])
    length = state.get("length", 3)

    dx, dy = DIRECTIONS[direction]
    new_pos = (head[0] + dx, head[1] + dy)

    # evită doar dacă e slab
    if length >= 10:
        return 0

    danger = sum(1 for snake in others if new_pos in snake)
    return -5 * danger


def hunt_snakes(state, direction):
    head = state["head"]
    heads = state.get("other_heads", [])
    length = state.get("length", 3)

    dx, dy = DIRECTIONS[direction]
    new_pos = (head[0] + dx, head[1] + dy)

    if length < 7:
        return 0  # prea mic pentru vânătoare

    dists = [abs(hx - new_pos[0]) + abs(hy - new_pos[1]) for hx, hy in heads]
    return max(0, 15 - min(dists)) if dists else 0


def prefer_corners(state, direction):
    corners = [(0,0), (SW // BLOCK_SIZE - 1, 0), (0, SH // BLOCK_SIZE - 1), (SW // BLOCK_SIZE - 1, SH // BLOCK_SIZE - 1)]
    head = state["head"]
    dx, dy = DIRECTIONS[direction]
    new_pos = (head[0] + dx, head[1] + dy)
    dist = min(abs(cx - new_pos[0]) + abs(cy - new_pos[1]) for cx, cy in corners)
    return -dist / 2

def fear_poison(state, direction):
    poisons = state.get("poison", [])
    head = state["head"]
    dx, dy = DIRECTIONS[direction]
    new_pos = (head[0] + dx, head[1] + dy)
    danger = any(abs(px - new_pos[0]) + abs(py - new_pos[1]) <= 2 for px, py in poisons)
    return -10 if danger else 0

def risk_loving(state, direction):
    # Încurajează mișcări noi și explorare
    head = state["head"]
    body = set(state["body"])

    dx, dy = DIRECTIONS[direction]
    new_pos = (head[0] + dx, head[1] + dy)

    if new_pos in body:
        return -5  # nu încurajăm riscul stupid

    # Cu cât e mai liber, cu atât mai ok
    open_space = 0
    for ddx, ddy in [(-1,0), (1,0), (0,-1), (0,1)]:
        nx, ny = new_pos[0] + ddx, new_pos[1] + ddy
        if (0 <= nx < SW // BLOCK_SIZE) and (0 <= ny < SH // BLOCK_SIZE):
            if (nx, ny) not in body:
                open_space += 1
    return open_space - 2  # pozitiv dacă spațiu mare


def patience(state, direction):
    return -1  # penalizează orice mișcare (să nu se arunce aiurea)

def hunter_mode(state, direction):
    length = state.get("length", 3)
    if length < 10:
        # mic -> caută mâncare, evită
        return 0.7 * chase_food(state, direction) + avoid_snakes(state, direction)
    else:
        # mare -> vânează activ și stă central
        return 1.2 * hunt_snakes(state, direction) - 0.3 * stay_centered(state, direction)


# === Mapare ===
gene_functions = {
    "avoid_walls": avoid_walls,
    "avoid_body": avoid_body,
    "chase_food": chase_food,
    "stay_centered": stay_centered,
    "avoid_snakes": avoid_snakes,
    "hunt_snakes": hunt_snakes,
    "prefer_corners": prefer_corners,
    "fear_poison": fear_poison,
    "risk_loving": risk_loving,
    "patience": patience,
    "hunter_mode": hunter_mode,
}

def rebalance_gene_weights(chromosome):
    """
    Ajustează genele prea dezechilibrate:
    - crește `chase_food` dacă e prea mic
    - limitează `stay_centered` sau `prefer_corners` dacă sunt prea mari
    - normalizează totalul pentru a păstra un comportament sănătos
    """
    genes = chromosome.genes

    if genes["chase_food"] < 0.3:
        genes["chase_food"] = random.uniform(0.6, 0.9)

    if genes["avoid_walls"] < 0.2:
        genes["avoid_walls"] = random.uniform(0.5, 1.0)

    if genes["avoid_body"] < 0.2:
        genes["avoid_body"] = random.uniform(0.4, 0.8)

    if genes["fear_poison"] < 0.1:
        genes["fear_poison"] = random.uniform(0.3, 0.8)

    if genes["hunter_mode"] < 0.05:
        genes["hunter_mode"] = random.uniform(0.3, 0.6)

    if genes["hunt_snakes"] < 0.01:
        genes["hunt_snakes"] = random.uniform(0.1, 0.4)

    if genes["avoid_snakes"] < 0.01:
        genes["avoid_snakes"] = random.uniform(0.1, 0.3)

    if genes["patience"] < 0.001:
        genes["patience"] = 0.2

    # Normalizează totalul
    total = sum(genes.values())
    if total > 0:
        for k in genes:
            genes[k] /= total

    chromosome.genes = genes
    return chromosome