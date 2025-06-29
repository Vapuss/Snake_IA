import random
from snake_ai import SnakeAI  # Clasa care controleaza AI-ul pentru sarpe
from genes import Chromosome, rebalance_gene_weights  # Clasa de cromozomi si functia de echilibrare
import config  # Parametri globali (ex: numar de sarpi, dimensiuni, etc.)
import os
import json  # Pentru a salva/incarca elitele din fisier

# Incarca elitele (cromozomii de top) salvate din fisier
def load_elites_from_file():
    if os.path.exists("elites.json"):
        with open("elites.json", "r") as f:
            data = json.load(f)
            return [Chromosome(genes) for genes in data]
    return []

# Incarca cel mai bun scor salvat vreodata
def load_best_score():
    try:
        with open("best_score.txt", "r") as f:
            return float(f.read())
    except:
        return 0.0

# Salveaza noul scor maxim
def save_best_score(score):
    with open("best_score.txt", "w") as f:
        f.write(str(score))

# Clasa care gestioneaza populatia de sarpi
class PopulationManager:
    def __init__(self):
        self.snakes = []  # lista de sarpi curenti
        self.generation = 1  # numarul generatiei curente

    # Creeaza sarpi noi (initiali) la inceputul jocului
    def initialize_population(self, count):
        self.snakes = []
        elites = load_elites_from_file()  # Incarca cromozomi de top

        for i in range(count):
            if elites:
                chrom = random.choice(elites).mutated_copy()  # Copie mutata a unui cromozom elite
            else:
                chrom = Chromosome()  # Creeaza un cromozom complet random
            x = random.randint(2, config.SW // config.BLOCK_SIZE - 3)
            y = random.randint(2, config.SH // config.BLOCK_SIZE - 3)
            snake = SnakeAI(chromosome=chrom, start_pos=(x, y))  # Creeaza sarpele
            self.snakes.append(snake)

    # Returneaza doar sarpii care inca sunt in viata
    def get_alive_snakes(self):
        return [s for s in self.snakes if not s.dead]

    # Functie ajutatoare (nu e folosita in codul curent)
    def mutated_copy(self, rate=0.1):
        new = Chromosome(self.genes.copy())
        new.mutate(rate)
        return new

    # Evolueaza populatia actuala (algoritm genetic)
    def evolve_population(self):
        SnakeAI.counter = 1  # Resetam indexul AI

        # Calculam scorul fiecarui sarpe
        scored = [
            (
                snake,
                snake.score + snake.kills * 5 + snake.steps_survived * 0.1
            )
            for snake in self.snakes
        ]
        scored.sort(key=lambda x: x[1], reverse=True)  # Sortam sarpii descrescator dupa scor

        # Selectam cei mai buni N_ELITE sarpi
        elites = [snake.chromosome for snake, _ in scored[:config.N_ELITE]]

        new_snakes = []
        while len(new_snakes) < config.NUM_AI_SNAKES:
            # Alegem doi parinti elite si facem crossover + mutatie
            parent1 = random.choice(elites)
            parent2 = random.choice(elites)
            child_chrom = parent1.crossover(parent2)
            child_chrom.mutate()
            child_chrom = rebalance_gene_weights(child_chrom)

            # Cream sarpe nou din cromozom
            x = random.randint(2, config.SW // config.BLOCK_SIZE - 3)
            y = random.randint(2, config.SH // config.BLOCK_SIZE - 3)
            new_snakes.append(SnakeAI(chromosome=child_chrom, start_pos=(x, y)))

        self.snakes = new_snakes  # Inlocuim populatia veche cu cea noua
        self.generation += 1  # Generatia creste

        # Verificam daca trebuie sa salvam elitele in fisier
        best_score_this_gen = scored[0][1]
        best_score_ever = load_best_score()
        best_snake, _ = scored[0]

        if best_score_this_gen > best_score_ever:
            print(f"[ELITE] New best score: {best_score_this_gen:.2f} (previous: {best_score_ever:.2f})")
            save_best_score(best_score_this_gen)

            # Salvam genele celor mai buni N_ELITE sarpi
            elites = [rebalance_gene_weights(snake.chromosome) for snake, _ in scored[:config.N_ELITE]]
            elite_genes = [chrom.genes for chrom in elites]
            with open("elites.json", "w") as f:
                json.dump(elite_genes, f, indent=2)

        else:
            print(f"[ELITE] Skipping save (score {best_score_this_gen:.2f} <= {best_score_ever:.2f})")

            # Exceptie: daca sarpele a murit de otrava, dar a avut un scor mare, tot salvam
            if getattr(best_snake, "last_death_reason", "") == "poison" and best_snake.score > 200:
                print(f"[PATCH] Best snake died poisoned with score {best_snake.score}. Boosting 'fear_poison' and saving anyway.")

                # Marim gena 'fear_poison'
                best_snake.chromosome.genes["fear_poison"] = min(
                    best_snake.chromosome.genes.get("fear_poison", 0) + 0.05,
                    1.0
                )

                # Salveaza elitele cu cromozomul ajustat
                best_snake.chromosome = rebalance_gene_weights(best_snake.chromosome)
                elites = [rebalance_gene_weights(snake.chromosome) for snake, _ in scored[:config.N_ELITE]]
                elites[0] = best_snake.chromosome  # Inlocuim primul cromozom cu cel modificat
                elite_genes = [chrom.genes for chrom in elites]

                with open("elites.json", "w") as f:
                    json.dump(elite_genes, f, indent=2)

                print("[ELITE PATCHED] elites.json updated with adjusted poison-fear elite.")
