from pygame.locals import QUIT, KEYDOWN, K_SPACE
import pygame
import random
import json


class Snake:
    def __init__(self, genome = None, start_x = 10, start_y = 10):
        self.body = [(start_x, start_y)]
        self.cerveau = NeuralNetwork(genome)
        self.fitness = 0
        self.direction = [1, 0, 0, 0]

    def get_head(self):
        return self.body[0]

    def get_body(self):
        return self.body
    
    def get_direction(self):
        return self.direction

    def move(self, next_pos, is_food):
        
        direction = [0] * 4
        directions = [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0)
        ]

        dx, dy = next_pos[0] - self.get_head()[0], next_pos[1] - self.get_head()[1]

        for i, (x, y) in enumerate(directions):
            if (x, y) == (dx, dy):
                direction[i] = 1

        self.direction = direction

        if is_food:
            self.body.insert(0, next_pos)
        else:
            self.body.insert(0, next_pos)
            self.body.pop()
            
    def check_collision(self, pos, board_width, board_height):
        x, y = pos
        if x < 0 or x >= board_width or y < 0 or y >= board_height:
            return True

        if pos in self.body[:-1]:
            return True
        
        return False
        
class Food():
    def __init__(self, board_width, board_height):
        self.board_width = board_width
        self.board_height = board_height
        self.position = None
    
    def random_food(self, snake_body):
        while True:
            x = random.randint(0, self.board_width - 1)
            y = random.randint(0, self.board_height - 1)
            pos_food = (x, y)

            if pos_food not in snake_body:
                self.position = pos_food

                return self.position
                
    def get_position(self):
        return self.position
    
    def set_position(self, position):
        self.position = position
    
    def is_eaten(self, head_position):
        if head_position == self.position:
            return True 
        else:
            return False


class NeuralNetwork:
    def __init__(self, genome = None):
        self.structure = [24, 8, 4]
        self.poids = None

        if genome is None:
            self.genome = self.cree_genome_aleatoire()
        else:
            self.genome = genome

    def cree_genome_aleatoire(self):
        nb_poids = (24 * 8 + 8) + (8 * 4 + 4)
        return [random.uniform(-1, 1) for _ in range(nb_poids)]

    def construire_poids(self):
        w_input_hidden = []
        index_genome = 0

        for _ in range(8):
            ligne = [0] * 24
            for j in range(24):
                ligne[j] = self.genome[index_genome]
                index_genome += 1
            w_input_hidden.append(ligne)

        b_hidden = self.genome[192:200]

        w_hidden_output = []
        index_genome = 200

        for i in range(8):
            ligne = [0] * 4 
            for j in range(4):
                ligne[j] = self.genome[index_genome]
                index_genome += 1
            w_hidden_output.append(ligne)

        b_output = self.genome[232:236]

        return {
            'w_input_hidden': w_input_hidden,
            'b_hidden': b_hidden,
            'w_hidden_output': w_hidden_output,
            'b_output': b_output
        }
          
    def forward(self, entrees):

        def ReLU(x):
            if x < 0:
                x = 0
                return 0
            else:
                return x
        if self.poids is None:
            self.poids = self.construire_poids()
        
        poids = self.poids
        w_ih = poids['w_input_hidden']  
        b_h = poids['b_hidden']  
        w_ho = poids['w_hidden_output']  
        b_o = poids['b_output']

        hidden = [0 for _ in range(8)]

        for i in range(8):
            somme = b_h[i]
            for j in range(24):
                somme += entrees[j] * w_ih[i][j]
            hidden[i] = ReLU(somme)
        
        output = [0 for _ in range(4)]

        for i in range(4):
            somme = b_o[i]
            for j in range(8):
                somme += hidden[j] * w_ho[j][i]
            output[i] = somme

        return output

    def choisir_action(self, sorties):
        return sorties.index(max(sorties))

class AlgoGenetique:
    def __init__(self):
        self.game = Game()

    def cree_population(self, taille):
        population = []

        for i in range(0, taille):
            nn = NeuralNetwork()
            population.append(nn)
        
        return population

    def evaluer_population(self, population):
        results = []

        for neural_net in population:
            result = self.game.jouer_partie(neural_net)
            fitness = result['fitness']

            results.append(
                {"neural_net" : neural_net,
                 "fitness" : fitness,
                 "nourriture" : result["nourriture"],
                 "tours" : result["tours"]
                 }
            )

        return results

    def selection(self, population, taux):
        population = sorted(population, key=lambda e: e["fitness"], reverse=True)
        nombre_a_garder = round(len(population) * taux)
        survivants = population[0:nombre_a_garder]
        return survivants

    def crossover(self, parent1, parent2):
        genome1 = parent1["neural_net"].genome
        genome2 = parent2["neural_net"].genome

        taille = min(len(genome1), len(genome2))
        nouveau_genome = []

        for i in range(taille):
            if random.random() < 0.5:
                nouveau_genome.append(genome1[i])
            else:
                nouveau_genome.append(genome2[i])

        return {"neural_net": NeuralNetwork(nouveau_genome)}

    def mutation(self, genome, taux, amplitude):
        taille = len(genome)
        
        for i in range(taille):
            if random.random() < taux:
                bruit = random.uniform(-amplitude, amplitude)
                genome[i] = genome[i] + bruit

                if genome[i] < -2:
                    genome[i] = -2
                if genome[i] > 2:
                    genome[i] = 2
        
        return genome

    def evoluer(self, nb_generations, taille_population, taux_selection, taux_mutation):
        population = self.cree_population(taille_population)

        meilleur = None
        meilleur_fitness = 0

        for generation in range(nb_generations):

            resultat = self.evaluer_population(population)

            resultat_trie = sorted(resultat, key=lambda e: e["fitness"], reverse=True)
            meilleur_gen = resultat_trie[0]

            fitness_moyen = sum(r["fitness"] for r in resultat_trie) / len(resultat_trie)

            print(f" Génération {generation} ")
            print(f" Meilleur fitness : {meilleur_gen['fitness']}")
            print(f" Moyenne : {fitness_moyen}")
            print(f" Nourriture : {meilleur_gen["nourriture"]}")

            if meilleur_gen["fitness"] > meilleur_fitness:
                meilleur_fitness = meilleur_gen["fitness"]
                meilleur = meilleur_gen
            
            survivants = self.selection(resultat, taux_selection)

            nouvelle_population = []

            for survivant in survivants:
                nouvelle_population.append(survivant['neural_net'])

            nb_enfants = taille_population - len(survivants)

            for i in range(nb_enfants):
                parent1 = random.choice(survivants)
                parent2 = random.choice(survivants)

                enfant = self.crossover(parent1, parent2)

                if random.random() < taux_mutation:
                    self.mutation(enfant['neural_net'].genome, 0.10, 0.3)
                
                nouvelle_population.append(enfant["neural_net"])

            population = nouvelle_population

        return {
            "genome" : meilleur["neural_net"].genome,
            "fitness" : meilleur_fitness,
            "nourriture" : meilleur["nourriture"]
        }

    def sauvegarder_champion(self, genome):
        data = {
            "genome" : genome,
            "taille" : len(genome)
        }

        with open("champion.json", "w") as f:
            json.dump(data, f, indent=4)

    def afficher_champion(self, genome):
        try:
            pygame.init()
            taille_case = 20
            largeur = self.game.board_width * taille_case
            hauteur = self.game.board_height * taille_case
            fenetre = pygame.display.set_mode((largeur, hauteur))
            clock = pygame.time.Clock()

            champion = NeuralNetwork(genome)
            snake = Snake(genome, 10, 7)
            self.game.snake = snake
            self.game.food.random_food(snake.get_body())

            score = 0
            running = True

            while running:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False
                    if event.type == KEYDOWN and event.key == K_SPACE:
                        running = False
                
                vision = self.game.calculer_vision(snake)

                sorties = champion.forward(vision)
                direction = champion.choisir_action(sorties)

                head_x, head_y = snake.get_head()

                if direction == 0 :
                    next_pos = (head_x, head_y - 1)
                if direction == 1 :
                    next_pos = (head_x, head_y + 1)
                if direction == 2 :
                    next_pos = (head_x - 1, head_y)
                if direction == 3 :
                    next_pos = (head_x + 1, head_y)

                if snake.check_collision(next_pos, self.game.board_width, self.game.board_height):
                    break

                is_food = self.game.food.is_eaten(next_pos)
                snake.move(next_pos, is_food)

                if is_food:
                    self.game.food.random_food(snake.get_body())
                    score += 1

                self.game.draw(fenetre)
                self.game.update()
                font = pygame.font.Font(None, 36)
                texte = font.render(f"Score : {score}", True, (255, 255, 255))
                fenetre.blit(texte, (10, 10))

                pygame.display.flip()
                clock.tick(15)
        except Exception as e:
            print(f"\n ERREUR lors de la visualisation : {e}")
            print(f"   Type d'erreur : {type(e).__name__}")
            pygame.quit()
            
        finally:
            pygame.quit()


class Game():
    def __init__(self):
        self.board_width = 20
        self.board_height = 15
        self.snake = None
        self.food = Food(self.board_width, self.board_height)
    
    def calculer_vision(self, snake):

        vision = [0] * 24
        head_x, head_y = snake.get_head()
        food_pos = self.food.get_position()
        if food_pos is None:
            self.food.random_food(self.snake.get_body())
            food_pos = self.food.get_position()

        food_x, food_y = food_pos

        directions = [
            (0, -1),   
            (0, 1),    
            (-1, 0),   
            (1, 0),    
            (-1, -1), 
            (1, -1),   
            (-1, 1),   
            (1, 1)     
        ]

        for i, (dx, dy) in enumerate(directions):

            distance = 0
            x, y = head_x, head_y

            while 0 <= x + dx < self.board_width and 0 <= y + dy < self.board_height:
                x += dx
                y += dy
                distance += 1

            vision[i] = distance / max(self.board_width, self.board_height)

        danger_head = [
            (0, -1),
            (0, +1),
            (-1, 0),
            (+1, 0)
        ]

        for i, (dx, dy) in enumerate(danger_head):
            x, y = head_x, head_y
            x, y = (x + dx, y + dy)
            danger = 0

            if x < 0 or x >= self.board_width or y < 0 or y >= self.board_height:
                danger = 1

            if (x, y) in snake.get_body():
                danger = 1
        
            vision[8 + i] = danger

        vision[12] = 1 if food_x < head_x else 0
        vision[13] = 1 if food_x > head_x else 0
        vision[14] = 1 if food_y < head_y else 0
        vision[15] = 1 if food_y > head_y else 0

        vision[16:20] = snake.get_direction()

        delta_x = food_x - head_x
        vision[20] = delta_x / self.board_width

        delta_y = food_y - head_y
        vision[21] = delta_y / self.board_height

        taille_max = self.board_height * self.board_width
        vision[22] = len(snake.body) / taille_max

        vision[23] = 0.5

        return vision


    def jouer_partie(self, neural_net):
        self.snake = Snake(start_x=10, start_y=7)
        self.snake.cerveau = neural_net
        self.food = Food(self.board_width, self.board_height)
        self.food.random_food(self.snake.get_body())

        tours = 0
        max_tours = 2000
        nourriture_mange = 0

        while tours < max_tours:
            vision = self.calculer_vision(self.snake)

            sortie = neural_net.forward(vision)
            direction_index = neural_net.choisir_action(sortie)

            head_x, head_y = self.snake.get_head()

            if direction_index == 0:
                next_pos = (head_x, head_y - 1)
            elif direction_index == 1:
                next_pos = (head_x, head_y + 1)
            elif direction_index == 2:
                next_pos = (head_x - 1, head_y)
            elif direction_index == 3:
                next_pos = (head_x + 1, head_y)

            if self.snake.check_collision(next_pos, self.board_width, self.board_height):
                break

            is_food = self.food.is_eaten(next_pos)
            self.snake.move(next_pos, is_food)

            if is_food:
                self.food.random_food(self.snake.get_body())
                nourriture_mange += 1

            tours += 1

            fitness = (nourriture_mange * 20000) + tours

        return {
            "fitness" : fitness,
            "nourriture" : nourriture_mange,
            "tours" : tours
        }
        
    def update(self):
        self.tableau = [[0 for _ in range(self.board_width)] for _ in range(self.board_height)]
        
        for x, y in self.snake.get_body():
            self.tableau[y][x] = 1
        
        food_pos = self.food.get_position()
        if food_pos is not None:
            food_x, food_y = food_pos
            self.tableau[food_y][food_x] = 2

    def draw(self, fenetre):
        taille_case = 20
        fenetre.fill((0,0,0))

        for (x, y) in self.snake.get_body():
            pygame.draw.rect(fenetre, (0, 255, 0), (x * taille_case, y * taille_case, taille_case, taille_case))

        food_x, food_y = self.food.get_position()
        pygame.draw.rect(fenetre, (255, 0, 0), (food_x * taille_case, food_y * taille_case, taille_case, taille_case))

if __name__ == "__main__":
    algo = AlgoGenetique()
    
    print("DÉBUT DE L'ENTRAÎNEMENT...")
    print("=" * 50)
    
    champion = algo.evoluer(
        nb_generations=200,
        taille_population=500,
        taux_selection=0.08,
        taux_mutation=0.80
    )
    
    print("\n" + "=" * 50)
    print(" CHAMPION TROUVÉ !")
    print(f"   Fitness : {champion['fitness']}")
    print(f"   Nourritures mangées : {champion['nourriture']}")
    print("=" * 50)
    
    algo.sauvegarder_champion(champion['genome'])
    print("\nChampion sauvegardé dans 'champion.json'")
    
    print("\n Visualisation du champion...")
    print("   (Appuyez sur ESPACE ou fermez la fenêtre pour arrêter)")
    algo.afficher_champion(champion['genome'])
    
    print("\n Test terminé !")