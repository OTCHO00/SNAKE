from typing import List, Tuple, Dict, Set
from math import sqrt
import numpy as np
import pygame
import random
import heapq


class Node:
    def __init__(self, x, y, g=0, h=0, parent=None):
        self.x = x
        self.y = y
        self.g = g
        self.h = h
        self.parent = parent
    
    def get_f(self):
        return self.g + self.h
    
    def calculate_h(self, target_x, target_y):
        return abs(target_x - self.x) + abs(target_y - self.y)


class Snake:
    def __init__(self, start_x=7, start_y=9):  
        self.body = [(start_x, start_y)]
        self.direction = "up"
        self.next_direction = "up"

    def get_head(self):
        return self.body[0]
    
    def get_body(self):
        return self.body
    
    def move_a(self, next_position, is_food=False):
        """Déplace le serpent vers la position donnée"""
        self.body.insert(0, next_position)
        if not is_food:  
            self.body.pop()

    def check_collision(self, new_head, board_width, board_height):
        if new_head[0] < 0 or new_head[0] >= board_width or new_head[1] < 0 or new_head[1] >= board_height:
            return True
        elif new_head in self.body: 
            return True
        else:
            return False


class Food:
    def __init__(self, board_width, board_height):
        self.board_width = board_width
        self.board_height = board_height
        self.position = None

    def random_food(self, snake_body):
        while True:
            x = random.randrange(self.board_width)
            y = random.randrange(self.board_height)
            position = (x, y)

            if position not in snake_body:
                self.position = position
                return self.position
            
    def get_position(self):
        return self.position
    
    def is_eaten(self, head_position):
        return self.position == head_position


class Game:
    def __init__(self):  
        self.TAILLE_CASE = 20
        self.NB_CASES_X = 20   
        self.NB_CASES_Y = 15
        self.running = True
        self.snake = Snake(7, 9)   
        self.food = Food(self.NB_CASES_X, self.NB_CASES_Y)
        self.food.random_food(self.snake.get_body())
        self.path = []  

    def find_best_node(self, node_list):
        if not node_list:
            return None
        best_node = min(node_list, key=lambda node: node.get_f())
        return best_node

    def get_neighbors(self, x, y, snake_body):
        neighbors = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        for dx, dy in directions:
            new_x = x + dx
            new_y = y + dy
            
            if 0 <= new_x < self.NB_CASES_X and 0 <= new_y < self.NB_CASES_Y:

                if (new_x, new_y) not in snake_body[:-1]:  
                    neighbors.append((new_x, new_y))
        
        return neighbors

    def a_star(self, start_pos, goal_pos):
        if start_pos == goal_pos:
            return []
        
        start_x, start_y = start_pos
        goal_x, goal_y = goal_pos
        
        open_list = []
        closed_set = set()
        
        start_node = Node(start_x, start_y)
        start_node.h = start_node.calculate_h(goal_x, goal_y)
        open_list.append(start_node)
        
        while open_list:
            current = self.find_best_node(open_list)
            open_list.remove(current)
            closed_set.add((current.x, current.y))
            
            if (current.x, current.y) == (goal_x, goal_y):
                path = []
                while current.parent:
                    path.append((current.x, current.y))
                    current = current.parent
                path.reverse()
                return path
            
            neighbors = self.get_neighbors(current.x, current.y, self.snake.get_body())
            
            for neighbor_x, neighbor_y in neighbors:
                if (neighbor_x, neighbor_y) in closed_set:
                    continue
                
                neighbor_node = Node(neighbor_x, neighbor_y)
                neighbor_node.g = current.g + 1
                neighbor_node.h = neighbor_node.calculate_h(goal_x, goal_y)
                neighbor_node.parent = current
                
                existing_node = None
                for node in open_list:
                    if node.x == neighbor_x and node.y == neighbor_y:
                        existing_node = node
                        break
                
                if existing_node:
                    if neighbor_node.g < existing_node.g:
                        existing_node.g = neighbor_node.g
                        existing_node.parent = neighbor_node.parent
                else:
                    open_list.append(neighbor_node)
        
        return False  
    

    def calculer_score_queue(self, mouvement, queue_snake):
        x, y = mouvement
        qx, qy = queue_snake
        distance = abs(x - qx) + abs(y - qy)
        score = 100 / (distance + 1)
        return score
    
    def calculer_score_espace(self, mouvement, corps_snake):
        tab = set()
        x, y = mouvement
        attente = self.get_neighbors(x, y, corps_snake)

        while attente:
            x, y = attente.pop(0)
            tab.add((x, y))

            voisins = self.get_neighbors(x, y, corps_snake)

            for voisin in voisins:
                if voisin not in attente and voisin not in tab:
                    attente.append(voisin)

        return len(tab)

    def calculer_score_food(self, mouvement, pos_food):
        x, y = mouvement
        fx, fy = pos_food

        distance = abs(x - fx) + abs(y - fy)
        score = 100 / (distance + 1)
        return score

    def calculer_score_options(self, mouvement, corps_snake):
        x, y = mouvement

        score = len(self.get_neighbors(x, y, corps_snake))
        return score

    
    def survive(self, current_pos, snake_body, food_pos):
        x, y = current_pos

        candidats_mouvement = self.get_neighbors(x, y, snake_body)

        if candidats_mouvement == []:
            return []

        meilleur_mouvement = None 
        meilleur_score = float("-inf")

        for mouvement in candidats_mouvement:
            score1 = self.calculer_score_queue(mouvement, snake_body[-1])
            score2 = self.calculer_score_food(mouvement, food_pos)
            score3 = self.calculer_score_espace(mouvement, snake_body)
            score4 = self.calculer_score_options(mouvement, snake_body)
            final_score = (0.45 * score1) + (0.25 * score3) + (0.20 * score2) + (0.10 * score4)
        
            if final_score > meilleur_score:
                meilleur_score = final_score
                meilleur_mouvement = mouvement

        return [meilleur_mouvement]

    def update_tableau(self):
        """Met à jour la représentation du plateau pour l'affichage"""
        self.tableau = [[0 for _ in range(self.NB_CASES_X)] for _ in range(self.NB_CASES_Y)]
        
        for (x, y) in self.snake.get_body():
            self.tableau[y][x] = 1
        
        if self.food.get_position():
            food_x, food_y = self.food.get_position()
            self.tableau[food_y][food_x] = 2

    def draw(self, fenetre):
        for y in range(self.NB_CASES_Y):
            for x in range(self.NB_CASES_X):
                if self.tableau[y][x] == 1:  
                    pygame.draw.rect(fenetre, (0, 255, 0), 
                                   (x * self.TAILLE_CASE, y * self.TAILLE_CASE, 
                                    self.TAILLE_CASE, self.TAILLE_CASE))
                elif self.tableau[y][x] == 2:  
                    pygame.draw.rect(fenetre, (255, 0, 0), 
                                   (x * self.TAILLE_CASE, y * self.TAILLE_CASE, 
                                    self.TAILLE_CASE, self.TAILLE_CASE))

    def game_loop(self, fenetre, clock):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.running = False

            if not self.path:
                current_pos = self.snake.get_head()
                goal_pos = self.food.get_position()
                snake_body = self.snake.get_body()
                self.path = self.a_star(current_pos, goal_pos)
                if not self.path:
                    self.path = self.survive(current_pos, snake_body, goal_pos)
                
                if not self.path:  
                    print("Aucun chemin trouvé vers la nourriture!")
                    self.running = False
                    continue

            if self.path:
                next_pos = self.path.pop(0)
                
                is_food = self.food.is_eaten(next_pos)
                
                self.snake.move_a(next_pos, is_food)
                
                if is_food:
                    self.food.random_food(self.snake.get_body())
                    self.path = []  

            self.update_tableau()
            fenetre.fill((0, 0, 0))
            self.draw(fenetre)
            pygame.display.flip()
            clock.tick(15)

    def main(self):
        pygame.init()
        fenetre = pygame.display.set_mode((self.NB_CASES_X * self.TAILLE_CASE, self.NB_CASES_Y * self.TAILLE_CASE))
        pygame.display.set_caption("Snake - Version A*")
        clock = pygame.time.Clock()
        
        self.game_loop(fenetre, clock)
        
        print("Game Over!")
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.main()