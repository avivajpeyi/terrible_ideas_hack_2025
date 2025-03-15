import pygame
from pygame.locals import *
from game import Game
from config import *
from util import Direction
from pose_input_controller import PoseInputController


MOVE_LEFT = "move_left"
MOVE_RIGHT = "move_right"
MOVE_UP = "move_up"
MOVE_DOWN = "move_down"

if __name__ == '__main__':
    pygame.init()
    pose_input_reader = PoseInputController(single_trigger=False)
    pose_input_reader.run()
    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    clock = pygame.time.Clock()  # Create a Clock object
    FPS = 30  # Reduce FPS to slow down the gameqqq

    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_t:
                    game.switch_my_tank()
                elif event.key == K_ESCAPE:
                    running = False
                elif event.key == K_SPACE:
                    game.fire()
                elif event.key == K_r:
                    game = Game()
                elif event.key == K_p:
                    game.testus()

        keys = pygame.key.get_pressed()
        events = pose_input_reader.get_events()

        if keys[pygame.K_UP] or keys[pygame.K_w] or MOVE_UP in events:
            game.my_tank_move_to_direction = Direction.UP
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            game.my_tank_move_to_direction = Direction.DOWN
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            game.my_tank_move_to_direction = Direction.LEFT
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            game.my_tank_move_to_direction = Direction.RIGHT
        else:
            game.my_tank_move_to_direction = None
        
        screen.fill((128, 128, 128))

        game.update()
        game.render(screen)

        if DEBUG:
            pygame.draw.circle(screen, (0, 255, 255), game.my_tank.gun_point, 4, 1)

        pygame.display.flip()
        clock.tick(FPS)  # Limit the frame rate

    pygame.quit()
