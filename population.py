import random
from snake_ai import SnakeAI
from genes import Chromosome, rebalance_gene_weights
import config
import os
import json

def load_elites_from_file():
        if os.path.exists("elites.json"):
            with open("elites.json", "r") as f:
                data = json.load(f)
                return [Chromosome(genes) for genes in data]
        return []




def load_best_score():
    try:
        with open("best_score.txt", "r") as f:
            return float(f.read())
    except:
        return 0.0

def save_best_score(score):
    with open("best_score.txt", "w") as f:
        f.write(str(score))


class PopulationManager:
    def __init__(self):
        self.snakes = []
        self.generation = 1

    

    def initialize_population(self, count):
        self.snakes = []

        

        elites = load_elites_from_file()
        
        for i in range(count):
            if elites:
                chrom = random.choice(elites).mutated_copy()
            else:
                chrom = Chromosome()
            x = random.randint(2, config.SW // config.BLOCK_SIZE - 3)
            y = random.randint(2, config.SH // config.BLOCK_SIZE - 3)
            snake = SnakeAI(chromosome=chrom, start_pos=(x, y))
            self.snakes.append(snake)



    def get_alive_snakes(self):
        return [s for s in self.snakes if not s.dead]
    

    def mutated_copy(self, rate=0.1):
        new = Chromosome(self.genes.copy())
        new.mutate(rate)
        return new

    

    def evolve_population(self):
        SnakeAI.counter = 1  # Resetăm numărătorul AI

        # Selectează cei mai buni N_ELITE
        scored = [
            (
                snake,
                snake.score + snake.kills * 5 + snake.steps_survived * 0.1
            )
            for snake in self.snakes
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        elites = [snake.chromosome for snake, _ in scored[:config.N_ELITE]]

        new_snakes = []
        while len(new_snakes) < config.NUM_AI_SNAKES:
            parent1 = random.choice(elites)
            parent2 = random.choice(elites)
            child_chrom = parent1.crossover(parent2)
            child_chrom.mutate()
            child_chrom = rebalance_gene_weights(child_chrom)
            x = random.randint(2, config.SW // config.BLOCK_SIZE - 3)
            y = random.randint(2, config.SH // config.BLOCK_SIZE - 3)
            new_snakes.append(SnakeAI(chromosome=child_chrom, start_pos=(x, y)))

        self.snakes = new_snakes
        self.generation += 1

        # ✅ Salvăm elitele doar dacă scorul e mai bun decât all-time best
        best_score_this_gen = scored[0][1]
        best_score_ever = load_best_score()

        best_snake, _ = scored[0]

        if best_score_this_gen > best_score_ever:
            print(f"[ELITE] New best score: {best_score_this_gen:.2f} (previous: {best_score_ever:.2f})")
            save_best_score(best_score_this_gen)

            elites = [rebalance_gene_weights(snake.chromosome) for snake, _ in scored[:config.N_ELITE]]
            elite_genes = [chrom.genes for chrom in elites]
            with open("elites.json", "w") as f:
                json.dump(elite_genes, f, indent=2)


        else:
            print(f"[ELITE] Skipping save (score {best_score_this_gen:.2f} <= {best_score_ever:.2f})")

            # 🧪 Excepție: dacă cel mai bun snake a murit de otravă dar a avut scor mare
            if getattr(best_snake, "last_death_reason", "") == "poison" and best_snake.score > 200:
                print(f"[PATCH] Best snake died poisoned with score {best_snake.score}. Boosting 'fear_poison' and saving anyway.")

                # creștem `fear_poison` cu +0.05
                best_snake.chromosome.genes["fear_poison"] = min(
                    best_snake.chromosome.genes.get("fear_poison", 0) + 0.05,
                    1.0
                )

                # salvăm elitele modificate
                import json
                best_snake.chromosome = rebalance_gene_weights(best_snake.chromosome)
                elites = [rebalance_gene_weights(snake.chromosome) for snake, _ in scored[:config.N_ELITE]]
                elites[0] = best_snake.chromosome  # suprascriem primul
                elite_genes = [chrom.genes for chrom in elites]


                with open("elites.json", "w") as f:
                    json.dump(elite_genes, f, indent=2)

                print("[ELITE PATCHED] elites.json updated with adjusted poison-fear elite.")


