import pygame
import random
import config

from config import SW, SH, R_INIT, PV, V_PAS, R_PAS
from genes import Chromosome, DIRECTIONS
from pathfinding import a_star


class SnakeAI:
    counter = 1
    def __init__(self, chromosome=None, start_pos=(1, 1)):
        self.chromosome = chromosome or Chromosome()
        self.xdir = 1
        self.ydir = 0
        self.head = pygame.Rect(start_pos[0]*config.BLOCK_SIZE, start_pos[1]*config.BLOCK_SIZE, config.BLOCK_SIZE, config.BLOCK_SIZE)
        self.body = [pygame.Rect(self.head.x - config.BLOCK_SIZE, self.head.y, config.BLOCK_SIZE, config.BLOCK_SIZE)]
        self.dead = False
        self.rotten_penalty = 1
        self.steps = 0
        self.vision = R_INIT
        self.speed = 1  # used for PV steps aging
        self.score = 0
        self.kills = 0
        self.steps_survived = 0
        self.visited_positions = set()
        self.move_counter = 0
        self.idle_penalized = False  # ca să nu penalizăm de mai multe ori
        self.name = f"AI {SnakeAI.counter}"
        SnakeAI.counter += 1
        self.rotten_count = 0

        self.fruit_streak = 0  # Inițializare streak de mere
        self.last_apple_type = None  # Ținem minte ce tip de măr a fost ultimul consumat

    def reset_streak(self):
        self.fruit_streak = 0  # Resetăm streak-ul când mănâncă un rotten apple

    def get_grid_pos(self, rect):
        return rect.x // config.BLOCK_SIZE, rect.y // config.BLOCK_SIZE

    def decide(self, state):
        head = state["head"]
        
        # === Dacă vede mâncare și are vizibilitate decentă, încearcă A* ===
        if state["foods"] and self.vision >= 2:
            closest_food = min(state["foods"], key=lambda f: abs(f[0] - head[0]) + abs(f[1] - head[1]))

            # Construim obstacole
            obstacles = set(state["body"])
            for enemy in state["enemies"]:
                obstacles.update(enemy["body"])

            direction = a_star(
                start=head,
                goal=closest_food,
                obstacles=obstacles,
                grid_width=SW // config.BLOCK_SIZE,
                grid_height=SH // config.BLOCK_SIZE
            )

            if direction:
                self.xdir, self.ydir = DIRECTIONS[direction]
                return  # A* a găsit cale

        # === Fallback: gene + scoruri ===
        scores = {}
        for dir_key in DIRECTIONS:
            scores[dir_key] = self.chromosome.evaluate(state, dir_key)

        best = max(scores, key=scores.get)
        best_score = scores[best]

        # === Dacă toate scorurile sunt egale (sau aproape), evită stagnarea ===
        unique_scores = set(round(s, 1) for s in scores.values())
        if len(unique_scores) <= 1:
            def free_space(dir_key):
                dx, dy = DIRECTIONS[dir_key]
                new_pos = (head[0] + dx, head[1] + dy)
                count = 0
                for ddx, ddy in DIRECTIONS.values():
                    check = (new_pos[0] + ddx, new_pos[1] + ddy)
                    if 0 <= check[0] < SW // config.BLOCK_SIZE and 0 <= check[1] < SH // config.BLOCK_SIZE:
                        if check not in set(state["body"]):
                            count += 1
                return count

            best = max(DIRECTIONS, key=free_space)
            self.xdir, self.ydir = DIRECTIONS[best]
            print("[Fallback] Scoruri egale → ales după spațiu liber:", best)
        else:
            self.xdir, self.ydir = DIRECTIONS[best]

        # === Noua logică pentru vanarea altor șerpi ===
        # Comparăm lungimile pentru a decide dacă trebuie să atacăm
        def should_hunt(snake):
            """ Verifică dacă șarpele ar trebui să vâneze un alt șarpe mai mic decât el """
            return len(self.body) > enemy["length"] # Atacă dacă este mai mare

        # Căutăm șerpii mai mici care pot fi vânați
        for enemy in state["enemies"]:
            if enemy != self and not enemy["dead"] and should_hunt(enemy):
                # Apelăm funcția calculate_attack_direction pentru a obține direcția de atac
                self.xdir, self.ydir = self.calculate_attack_direction(state, enemy)
                print(f"Atacăm {enemy['name']}!")
                return

        # Dacă nu am găsit pe nimeni de vânat, păstrăm direcția aleasă
        print("Niciun atac realizat, păstrăm direcția aleasă.")



    


    def update(self, state):
        if self.dead:
            return

        self.decide(state)


        
        for square in self.body:
            if self.head.colliderect(square):
                self.dead = True

        if self.head.x not in range(0, SW) or self.head.y not in range(0, SH):
            self.dead = True

        if not self.dead:
            self.steps_survived += 1
            self.body.append(self.head.copy())
            for i in range(len(self.body) - 1):
                self.body[i].x, self.body[i].y = self.body[i + 1].x, self.body[i + 1].y
            self.head.x += self.xdir * config.BLOCK_SIZE
            self.head.y += self.ydir * config.BLOCK_SIZE
            if self.body:
                self.body.pop()

            # 🔍 Tracking mișcări
            grid_pos = self.get_grid_pos(self.head)
            self.visited_positions.add(grid_pos)
            self.move_counter += 1

            # Penalizare graduală pentru lipsă de explorare
            if self.move_counter == 20 and not self.idle_penalized:
                unique = len(self.visited_positions)
                if unique < 5:
                    self.score -= 20
                    print(f"[IdlePenalty] -20 | doar {unique} blocuri unice")
                elif unique < 10:
                    self.score -= 10
                    print(f"[IdlePenalty] -10 | doar {unique} blocuri unice")
                elif unique < 20:
                    self.score -= 5
                    print(f"[IdlePenalty] -5  | doar {unique} blocuri unice")
                else:
                    print(f"[IdlePenalty]  OK: {unique} blocuri vizitate")
                self.idle_penalized = True


            self.steps += 1

            # Îmbătrânire
            if self.steps % PV == 0:
                self.speed = max(1, self.speed - V_PAS)
                self.vision = max(1, self.vision - R_PAS)

           
    def grow(self):
        if self.body:
            last = self.body[-1]
        else:
            last = self.head
        self.body.append(pygame.Rect(last.x, last.y, config.BLOCK_SIZE, config.BLOCK_SIZE))
        self.score += 1

    def shrink(self, amount):
        for _ in range(amount):
            if self.body:
                self.body.pop(0)
        if len(self.body) < 1:
            self.dead = True

    def build_state(self, all_foods, other_snakes):
        head_pos = self.get_grid_pos(self.head)
        body_pos = [self.get_grid_pos(b) for b in self.body]

        visible_foods = []
        visible_poison = []

        for f in all_foods:
            fx, fy = f.rect.x // config.BLOCK_SIZE, f.rect.y // config.BLOCK_SIZE
            dist = abs(fx - head_pos[0]) + abs(fy - head_pos[1])
            if dist <= self.vision:
                if getattr(f, "is_poison", False):
                    visible_poison.append((fx, fy))
                else:
                    visible_foods.append((fx, fy))

        enemies = []
        enemy_heads = []

        for other in other_snakes:
            if other == self or other.dead:
                continue
            enemy = {
            "head": self.get_grid_pos(other.head),
            "body": [self.get_grid_pos(b) for b in other.body],
            "dead": other.dead,  # Adăugăm atributul `dead`
            "name": other.name,
            "length": len(other.body) + 1,
            }
            enemies.append(enemy)
            enemy_heads.append(enemy["head"])

        enemy_bodies = [enemy["body"] for enemy in enemies]
        return {
            "head": head_pos,
            "body": body_pos,
            "foods": visible_foods,
            "poison": visible_poison,
            "enemies": enemies,
            "other_heads": enemy_heads,
            "others": enemy_bodies,
            "vision": self.vision,
            "length": len(self.body) + 1,
            "score": self.score,  
            "fruit_streak": self.fruit_streak,
        }


    def has_timed_out(self):
        MAX_STEPS_BASE = 200  # pași inițiali per șarpe
        EXTRA_STEPS_PER_SCORE = 150  # câți pași în plus per scor
        
        max_allowed_steps = MAX_STEPS_BASE + self.score * EXTRA_STEPS_PER_SCORE
        return self.steps > max_allowed_steps
    

    def randomize_position_away_from(self, others, min_distance=5):
        max_attempts = 100
        grid_w = SW // config.BLOCK_SIZE
        grid_h = SH // config.BLOCK_SIZE

        for _ in range(max_attempts):
            x = random.randint(1, grid_w - 2)
            y = random.randint(1, grid_h - 2)
            pos_ok = True
            for other in others:
                dist = abs(other.head.x // config.BLOCK_SIZE - x) + abs(other.head.y // config.BLOCK_SIZE - y)
                if dist < min_distance:
                    pos_ok = False
                    break
            if pos_ok:
                self.head.x = x * config.BLOCK_SIZE
                self.head.y = y * config.BLOCK_SIZE
                self.body = []
                return

        # fallback dacă nu găsește loc
        self.head.x = random.randint(1, grid_w - 2) * config.BLOCK_SIZE
        self.head.y = random.randint(1, grid_h - 2) * config.BLOCK_SIZE
        self.body = []


    
    def calculate_attack_direction(self, state, enemy):
        """ Calculam directia de atac catre orice parte a corpului inamicului """
        head = state["head"]

        # Facem o lista cu toate celulele din corpul inamicului, inclusiv capul
        targets = enemy["body"] + [enemy["head"]]

        # Consideram corpul propriu ca obstacol pentru algoritmul A*
        obstacles = set(state["body"])

        # Parcurgem toate pozitiile din corpul inamicului ca potentiale tinte
        for target in targets:
            # Incercam sa gasim un drum valid cu A* catre acea celula
            direction = a_star(
                start=head,
                goal=target,
                obstacles=obstacles,
                grid_width=SW // config.BLOCK_SIZE,
                grid_height=SH // config.BLOCK_SIZE
            )
            if direction:
                # Daca gasim un drum, returnam prima directie din acel drum
                return DIRECTIONS[direction]

        # Daca nu s-a gasit niciun drum catre corpul inamicului, continuam in directia curenta
        return self.xdir, self.ydir




