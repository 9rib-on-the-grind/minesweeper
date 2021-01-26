from time import time
from collections import defaultdict, Counter

from board import Board
from coords import Coords
from constraint import Constraint

class Solver:
    def __init__(self, **kwargs):
        self.board = Board(**kwargs)
        self.edge = set()
        self.mines_left = self.board.mines_left
        self.brute_force_depth = 20
        self.finished = False

    def solve(self):
        self.start_time = time()
        self.uncover(Coords(0, 0))
        while not self.is_finished():
            self.board.update()
            self.set_constraints()
            if self.find_trivial():
                self.resolve_trivial()
            elif self.deep_search() == 'unsuccessful':
                self.guess()
            self.update_edge()
        self.end_time = time()
        return self.game_result, self.end_time - self.start_time

    def uncover(self, pos: Coords):
        if pos not in self.board.covered: return
        safe = {pos}
        while safe:
            pos = safe.pop()
            self.board.covered.remove(pos)
            cell = self.board.get_cell(pos)
            cell.uncover()
            if cell.get_adjacent_mines() == 0:
                safe |= self.board.get_covered_neighbor_indices(pos)
            else:
                self.edge.add(pos)

    def set_constraints(self):
        self.constraints = set()
        for idx in self.edge:
            variables = self.board.get_covered_neighbor_indices(idx)
            value = self.board.get_unflagged_mines(idx)
            self.constraints.add(Constraint(variables, value))

    def find_trivial(self):
        self.trivial = {}
        for constraint in self.constraints:
            case = constraint.is_trivial()
            if case != None:
                for idx in constraint.variables:
                    self.trivial[idx] = case
        return len(self.trivial) != 0

    def resolve_trivial(self):
        for idx in self.trivial:
            if self.trivial[idx] == 0:
                self.uncover(idx)
            else:
                self.set_flag(idx)

    def deep_search(self):
        self.probabilities = {}
        self.reduce_constraints()
        if self.find_trivial():
            self.resolve_trivial()
            return 'successful'
        self.set_constraint_groups()
        while self.groups:
            group = min(self.groups, key=len)
            probabilities = self.search_group(group)
            if {0, 1} & set(probabilities.values()):
                self.trivial = {idx: case for (idx, case) in probabilities.items() if case in {0, 1}}
                self.resolve_trivial()
                return 'successful'
            self.probabilities |= probabilities
            self.groups.remove(group)
        return 'unsuccessful'

    def reduce_constraints(self):
        reduced = set()
        reductions = self.constraints.copy()
        for constraint in self.constraints:
            variants = {constraint - sub for sub in reductions if constraint > sub}
            if variants:
                reductions |= variants
                constraint = min(variants, key=len)
            reduced.add(constraint)
        self.constraints = reduced

    def set_constraint_groups(self):
        self.groups = []
        dependencies = defaultdict(set)
        for constraint in self.constraints:
            for idx in constraint.variables:
                dependencies[idx].add(constraint)
        while self.constraints:
            self.groups.append(set())
            added = set()
            indices = next(iter(self.constraints)).variables.copy()
            while indices:
                idx = indices.pop()
                added.add(idx)
                dependent = dependencies[idx]
                self.groups[-1] |= dependent
                indices |= {idx for constraint in dependent for idx in constraint.variables} - added
            self.constraints -= self.groups[-1]

    def search_group(self, group):
        variables = list({variable for constraint in group for variable in constraint.variables})
        if len(variables) > self.brute_force_depth: return {}
        self.valid_combinations = []
        self.brute_force(group, variables)
        total = len(self.valid_combinations)
        appearence = Counter([variable for combination in self.valid_combinations for variable in combination])
        return {variable : count/total for variable, count in appearence.items()}

    def brute_force(self, group, variables, mask = 0, length = 0):
        combination = {variables[i] for i in range(len(variables)) if mask & 1<<i}
        if length != len(variables):
            if not self.corrupted_combination(group, combination):
                self.brute_force(group, variables, mask, length + 1)
                self.brute_force(group, variables, mask | 1<<length, length + 1)
        elif self.valid_combination(group, combination):
                self.valid_combinations.append(combination)

    def corrupted_combination(self, group, combination):
        variables = defaultdict(int)
        for variable in combination:
            variables[variable] = 1
        for constraint in group:
            if sum([variables[variable] for variable in constraint.variables]) > constraint.value:
                return True
        return False

    def valid_combination(self, group, combination):
        variables = defaultdict(int)
        for variable in combination:
            variables[variable] = 1
        for constraint in group:
            if sum([variables[variable] for variable in constraint.variables]) != constraint.value:
                return False
        return True

    def guess(self):
        idx = best = None
        if self.probabilities:
            idx, best = min(self.probabilities.items(), key=lambda x: x[1])
        random = self.mines_left/len(self.board.covered)
        idx = idx if best and best <= random else self.best_random()
        if self.board.get_cell(idx).is_mine():
            self.defeat(idx)
        else:
            self.uncover(idx)

    def best_random(self):
        known = self.covered_edge()
        inner = self.board.covered - known
        if not inner:
            inner = known
        if self.board.get_corners() & inner:
            return (self.board.get_corners() & inner).pop()
        edges = self.board.get_edges() & inner
        return edges.pop() if edges else inner.pop()

    def update_edge(self):
        self.edge = {idx for idx in self.edge if len(self.board.get_covered_neighbor_indices(idx)) != 0}

    def covered_edge(self):
        return {neighbor for idx in self.edge for neighbor in self.board.get_covered_neighbor_indices(idx)}

    def set_flag(self, pos: Coords):
        self.board.get_cell(pos).set_flag()
        self.board.covered.remove(pos)
        self.mines_left -= 1

    def is_finished(self):
        if not self.board.covered:
            self.victory()
        return self.finished            

    def victory(self):
        self.game_result = 'win'
        self.end_game()  

    def defeat(self, pos: Coords):
        self.game_result = 'loss'
        self.board.reveal_mines()
        self.board.get_cell(pos).set_explosion()
        self.end_game()

    def end_game(self):
        self.finished = True
        self.board.update()