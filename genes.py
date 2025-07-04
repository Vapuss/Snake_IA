# genes.py

import random
import math
import config

from config import SW, SH

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
        # Cu probabilitate `rate`, modificam fiecare gena putin
        for k in self.genes:
            if random.random() < rate:
                self.genes[k] += random.uniform(-0.2, 0.2)
                self.genes[k] = max(0, min(1, self.genes[k]))

    def mutated_copy(self):
        # Copiem genele si le mutam, apoi le rebalansam
        genes_copy = dict(self.genes)
        new_chrom = Chromosome(genes_copy)
        new_chrom.mutate()
        return rebalance_gene_weights(new_chrom)



    def crossover(self, other):
        # Recombina genele cu alt cromozom, alegand aleator de la fiecare parinte
        new_genes = {}
        for k in self.genes:
            new_genes[k] = random.choice([self.genes[k], other.genes[k]])
        return rebalance_gene_weights(Chromosome(new_genes))

    def evaluate(self, state, direction):
        # Evalueaza scorul unei directii pe baza genelor si a mediului
        score = 0
        for gene, weight in self.genes.items():
            func = gene_functions.get(gene)
            if func:
                score += weight * func(state, direction)
        return score

# === Funcții de scor pentru fiecare genă ===
def avoid_walls(state, direction):
    # Penalizeaza miscarea catre pereti
    head = state["head"]
    dx, dy = DIRECTIONS[direction]
    new_x = head[0] + dx
    new_y = head[1] + dy
    if not (0 <= new_x < SW // config.BLOCK_SIZE and 0 <= new_y < SH // config.BLOCK_SIZE):
        return -10  # perete
    return 0

def avoid_body(state, direction):
    # Penalizeaza daca se intoarce in propriul corp
    head = state["head"]
    body = state["body"]
    dx, dy = DIRECTIONS[direction]
    new_pos = (head[0] + dx, head[1] + dy)
    return -5 if new_pos in body else 0

def chase_food(state, direction):
    # Recompenseaza apropierea de mancare
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
    # Penalizeaza miscarea catre marginile hartii
    head = state["head"]
    center = (SW // config.BLOCK_SIZE // 2, SH // config.BLOCK_SIZE // 2)
    dx, dy = DIRECTIONS[direction]
    new_pos = (head[0] + dx, head[1] + dy)
    dist = abs(center[0] - new_pos[0]) + abs(center[1] - new_pos[1])
    return -dist / 2

def avoid_snakes(state, direction):
    # Evita serpii mai mari
    head = state["head"]
    others = state.get("others", [])
    length = state.get("length", 3)

    dx, dy = DIRECTIONS[direction]
    new_pos = (head[0] + dx, head[1] + dy)

    # Dacă lungimea altui șarpe e mai mare decât a ta, evită-l
    danger = 0
    for snake in others:
        enemy_length = len(snake) + 1  # Lungimea altui șarpe (cap + corp)
        if enemy_length >= length:  # Evită șerpii mai mari
            if new_pos in snake:
                danger += 1

    return -5 * danger  # Penalizează dacă se apropie de un șarpe mai mare



def hunt_snakes(state, direction):
    # Recompenseaza miscarea catre serpi mai mici
    head = state["head"]
    heads = state.get("other_heads", [])
    length = state.get("length", 3)

    dx, dy = DIRECTIONS[direction]
    new_pos = (head[0] + dx, head[1] + dy)

    # Dacă șarpele este prea mic, nu vânează
    if length < 4:
        return 0  # Prea mic pentru vânătoare

    # Căutăm șerpi mai mici decât noi
    potential_prey = []
    for idx, (hx, hy) in enumerate(heads):
        enemy_length = len(state["others"][idx]) + 1  # Lungimea altui șarpe
        if enemy_length < length:  # Dacă alt șarpe e mai mic decât noi
            dist = abs(hx - new_pos[0]) + abs(hy - new_pos[1])
            potential_prey.append((dist, (hx, hy)))

    if potential_prey:
        # Alege cel mai apropiat șarpe pe care să-l vânezi
        closest_prey = min(potential_prey, key=lambda x: x[0])
        prey_pos = closest_prey[1]
        return max(0, 15 - closest_prey[0])  # Mai aproape = mai multe puncte

    return 0  # Dacă nu am găsit prada, nu se întâmplă nimic


def prefer_corners(state, direction):
    # Tine sarpele mai aproape de colturi
    corners = [(0,0), (SW // config.BLOCK_SIZE - 1, 0), (0, SH // config.BLOCK_SIZE - 1), (SW // config.BLOCK_SIZE - 1, SH // config.BLOCK_SIZE - 1)]
    head = state["head"]
    dx, dy = DIRECTIONS[direction]
    new_pos = (head[0] + dx, head[1] + dy)
    dist = min(abs(cx - new_pos[0]) + abs(cy - new_pos[1]) for cx, cy in corners)
    return -dist / 2

def fear_poison(state, direction):
    # Evita mancarea otravita
    poisons = state.get("poison", [])
    head = state["head"]
    dx, dy = DIRECTIONS[direction]
    new_pos = (head[0] + dx, head[1] + dy)
    danger = any(abs(px - new_pos[0]) + abs(py - new_pos[1]) <= 2 for px, py in poisons)
    return -40 if danger else 0

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
        if (0 <= nx < SW // config.BLOCK_SIZE) and (0 <= ny < SH // config.BLOCK_SIZE):
            if (nx, ny) not in body:
                open_space += 1
    return open_space - 2  # pozitiv dacă spațiu mare


def patience(state, direction):
    return -1  # penalizează orice mișcare (să nu se arunce aiurea)

def hunter_mode(state, direction):
    # Mod de comportament dependent de lungime: mic = fugi si mananca, mare = vaneaza
    length = state.get("length", 3)
    if length < 4:
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

    # Normalizam toate valorile astfel incat suma lor sa fie 1
    total = sum(genes.values())
    if total > 0:
        for k in genes:
            genes[k] /= total

    chromosome.genes = genes
    return chromosome