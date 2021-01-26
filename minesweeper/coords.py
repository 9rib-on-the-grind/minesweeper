class Coords:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def get_neighbors(self):
        neighbors = {Coords(self.x - 1, self.y)}
        neighbors |= {Coords(x, self.y + 1) for x in range(self.x - 1, self.x + 2)}
        neighbors |= {Coords(self.x + 1, self.y)}
        neighbors |= {Coords(x, self.y - 1) for x in range(self.x + 1, self.x - 2, -1)}
        return neighbors