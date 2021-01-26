import pygame
from datetime import timedelta

from solver import *

def main():
    while True:
        screen.fill((0, 0, 0))
        solver = Solver(level='expert')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
        result, time_spent = solver.solve()
        print('{:>5},   time spent: {}'.format(result, str(timedelta(seconds = time_spent))[:-3]))

resolution = (1280, 720)
screen = pygame.display.set_mode(resolution)

if __name__ == '__main__':
    pygame.init()
    main()