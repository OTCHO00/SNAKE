import pygame
import random


class Snake:
    def __init__(self, start_x=7, start_y=9):  
        self.body = [(start_x, start_y)]
        self.direction = "up"
        self.next_direction = "up"
    
    def get_head(self):
        return self.body[0]
    
    def get_body(self):
        return self.body

    def changer_direction(self, new_direction):
        directions_opposees = {
            "up": "down",
            "down": "up", 
            "left": "right",
            "right": "left"
        }

        if new_direction != directions_opposees[self.direction]:
            self.next_direction = new_direction
    
    def move(self, tableau, board_width, board_height):
        snake_direction = {"up": (self.body[0][0], self.body[0][1] - 1) , 
                           "down" : (self.body[0][0], self.body[0][1] + 1),
                           "left" : (self.body[0][0] - 1, self.body[0][1]),
                           "right" : (self.body[0][0] + 1, self.body[0][1])}
        
        nouvelle_position = snake_direction[self.next_direction] 
        
        if self.check_collision(nouvelle_position, board_width, board_height):
            return False
        elif tableau[nouvelle_position[1]][nouvelle_position[0]] != 2:  
            self.direction = self.next_direction
            self.body.insert(0, nouvelle_position)
            self.body.pop()  # Pas de croissance
        else:
            self.direction = self.next_direction
            self.body.insert(0, nouvelle_position)  
        return True

    def check_collision(self, new_head, board_width, board_height):
        if new_head[0] < 0 or new_head[0] >= board_width or new_head[1] < 0 or new_head[1] >= board_height:
            return True
        elif new_head in self.body[1:]:
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
            self.position = (x, y)

            if self.position not in snake_body:
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
        self.tableau = [[0 for _ in range(self.NB_CASES_X)] for _ in range(self.NB_CASES_Y)]
        self.snake = Snake(7, 9)   
        self.food = Food(self.NB_CASES_X, self.NB_CASES_Y)
        self.food.random_food(self.snake.get_body())

    def update_tableau(self):
        for y in range(self.NB_CASES_Y):
            for x in range(self.NB_CASES_X):
                if self.tableau[y][x] != 2: 
                    self.tableau[y][x] = 0

        for (x, y) in self.snake.get_body():
            self.tableau[y][x] = 1

        food_pos = self.food.get_position()
        if food_pos:
            self.tableau[food_pos[1]][food_pos[0]] = 2

    def handle_input(self, new_direction):
        self.snake.changer_direction(new_direction)

    def draw(self, fenetre):
        for y in range(self.NB_CASES_Y):
            for x in range(self.NB_CASES_X):
                if self.tableau[y][x] == 1:  
                    pygame.draw.rect(fenetre, (0, 255, 0), (x*self.TAILLE_CASE, y*self.TAILLE_CASE, self.TAILLE_CASE, self.TAILLE_CASE))
                elif self.tableau[y][x] == 2:  
                    pygame.draw.rect(fenetre, (255, 0, 0), (x*self.TAILLE_CASE, y*self.TAILLE_CASE, self.TAILLE_CASE, self.TAILLE_CASE))
        
    def game_loop(self, fenetre, clock):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.handle_input("up")
                    elif event.key == pygame.K_DOWN:
                        self.handle_input("down")
                    elif event.key == pygame.K_LEFT:
                        self.handle_input("left")
                    elif event.key == pygame.K_RIGHT:
                        self.handle_input("right")

            if not self.snake.move(self.tableau, self.NB_CASES_X, self.NB_CASES_Y):
                self.running = False  # Game Over
                continue

            if self.food.is_eaten(self.snake.get_head()):
                self.food.random_food(self.snake.get_body())

            self.update_tableau()
            fenetre.fill((0, 0, 0))
            self.draw(fenetre)
            pygame.display.flip()
            clock.tick(5)
    
    def main(self):
        pygame.init()
        fenetre = pygame.display.set_mode((self.NB_CASES_X * self.TAILLE_CASE, self.NB_CASES_Y * self.TAILLE_CASE))
        pygame.display.set_caption("Snake - Version OOP")
        clock = pygame.time.Clock()
        
        self.game_loop(fenetre, clock)
        
        print("Game Over!")
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.main()