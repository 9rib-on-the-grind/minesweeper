class Constraint:
    def __init__(self, variables, value):
        self.variables = variables
        self.value = value

    def __len__(self):
        return len(self.variables)

    def __eq__(self, other):
        return self.variables == other.variables and self.value == other.value

    def __gt__(self, other):
        return self.variables > other.variables

    def __sub__(self, other):
        return Constraint(self.variables - other.variables, self.value - other.value)

    def __hash__(self):
        return hash((tuple(self.variables), self.value))

    def is_trivial(self):
        if self.value == 0:
            return 0
        elif len(self.variables) == self.value:
            return 1
        else:
            return None