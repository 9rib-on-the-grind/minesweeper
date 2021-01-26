import pygame
import numpy as np
from random import sample

from cell import Cell
from coords import Coords
from main import resolution

class Board(pygame.sprite.Sprite):
    levels = {
        'beginner':     (Coords(10, 10), 0.1),
        'intermediate': (Coords(16, 16), 0.15625),
        'expert':       (Coords(30, 16), 0.20625)
    }

    def __init__(self, **kwargs):
        super().__init__()
        if kwargs['level'] in self.levels:
            self.size, self.mine_probability = self.levels[kwargs['level']]
        elif kwargs['level'] == 'custom':
            self.size, self.mine_probability = Coords(*kwargs['size']), kwargs['mine_probability']
        else:
            raise ValueError('invalid level =', kwargs['level'])
        self.mines_left = int(self.size.x*self.size.y*self.mine_probability)
        sprite_size = min(resolution[0]//self.size.x, resolution[1]//self.size.y)
        Cell.setup(sprite_size)
        self.setup()
        self.update()

    def setup(self):
        self.data = np.array([Cell(Coords(j, i)) for i in range(self.size.y) for j in range(self.size.x)])
        self.covered = {Coords(j, i) for i in range(self.size.y) for j in range(self.size.x)}
        mines = sample(range(1, len(self.data)), self.mines_left)
        for mine in mines:
            self.data[mine].set_mine()
        self.data = self.data.reshape((self.size.y, self.size.x))
        for row in self.data:
            for cell in row:
                neighbors = self.get_neighbors(cell.pos)
                cell.set_adjacent_mines(sum(map(lambda x: x.is_mine(), neighbors)))

    def update(self):
        pygame.display.update()

    def get_corners(self):
        return {Coords(0, 0), Coords(0, self.size.y - 1), 
                Coords(self.size.x - 1, 0), Coords(self.size.x - 1, self.size.y - 1)}

    def get_edges(self):
        return ({Coords(i, self.size.y - 1) for i in range(self.size.x)} 
              | {Coords(i, 0) for i in range(self.size.x)}
              | {Coords(0, i) for i in range(self.size.y)}
              | {Coords(self.size.x - 1, i) for i in range(self.size.y)})

    def get_cell(self, pos: Coords):
        return self.data[pos.y, pos.x]

    def get_neighbors(self, pos: Coords):
        return {self.get_cell(idx) for idx in self.get_neighbor_indices(pos)}

    def get_neighbor_indices(self, pos: Coords):
        return {idx for idx in pos.get_neighbors() if 0<=idx.y<self.size.y and 0<=idx.x<self.size.x}

    def get_covered_neighbor_indices(self, pos: Coords):
        return {cell.pos for cell in self.get_neighbors(pos) if cell.is_covered()}

    def get_unflagged_mines(self, pos: Coords):
        return self.get_cell(pos).get_adjacent_mines() - len(self.get_flagged_neighbors(pos))

    def get_flagged_neighbors(self, pos: Coords):
        return {cell for cell in self.get_neighbors(pos) if cell.is_flagged()}

    def reveal_mines(self):
        for idx in self.covered:
            self.get_cell(idx).reveal()