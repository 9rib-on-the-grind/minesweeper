import pygame
import os

from coords import Coords
from main import screen

class Cell(pygame.sprite.Sprite):
    sprites = dict()
    size = int()

    @classmethod
    def setup(self, sprite_size: int):
        self.size = sprite_size
        sprites = ['covered', 'flag', 'mine', 'explosion'] + ['uncovered' + str(i) for i in range(9)]
        for sprite in sprites:
            self.sprites[sprite] = pygame.image.load(os.path.join('sprites', sprite + '.png'))
            self.sprites[sprite] = pygame.transform.scale(self.sprites[sprite], (self.size, self.size))

    def __init__(self, pos: Coords):
        super().__init__()
        self.covered = True
        self.mine = False
        self.flag = False
        self.adjacent_mines = 0
        self.pos = pos
        self.sprite = self.sprites['covered']
        self.rect = self.sprite.get_rect()
        self.rect.topleft = (self.size*pos.x, self.size*pos.y)
        self.update('covered')

    def update(self, name):
        self.sprite = self.sprites[name]
        screen.blit(self.sprite, self.rect)

    def uncover(self):
        self.covered = False
        self.update('uncovered' + str(self.adjacent_mines))

    def set_mine(self):
        self.mine = True

    def set_adjacent_mines(self, mines: int):
        self.adjacent_mines = mines

    def set_flag(self):
        self.flag = True
        self.update('flag')

    def set_explosion(self):
        self.update('explosion')

    def is_covered(self):
        return self.covered and not self.is_flagged()

    def is_mine(self):
        return self.mine

    def is_flagged(self):
        return self.flag

    def get_adjacent_mines(self):
        return self.adjacent_mines

    def reveal(self):
        if self.is_mine() and not self.is_flagged():
            self.update('mine')