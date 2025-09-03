from z3 import *

class CardinalityConstraints:
    """Helper class that implements various cardinality constraints for a Z3-based SAT."""

    def at_most_one_pairwise(self, vars):
        n = len(vars)
        constraints = []

        for i in range(n):
            for j in range(i + 1, n):
                constraints.append(Not(And(vars[i], vars[j])))
        
        return And(*constraints)

    def at_most_one_sequential(self, vars):
        n = len(vars)
        constraints = []
        
        s = [FreshBool(f's_{i}') for i in range(n-1)]
        self.solver.add(Implies(vars[0], s[0]))
        for i in range(1, n-1):
            constraints.append(Implies(Or(vars[i], s[i-1]), s[i]))
            constraints.append(Implies(s[i-1], Not(vars[i])))
        constraints.append(Implies(s[n-2], Not(vars[n-1])))

        return And(*constraints)

    def at_most_one_bitwise(self, vars):
        n = len(vars)
        constraints = []

        m = math.ceil(math.log2(n))
        r = [FreshBool(f'r_{j}') for j in range(m)]
        for i in range(n):
            binary_repr = [(i >> j) & 1 for j in range(m)]
            binary_constraints = []
            for j in range(m):
                if binary_repr[j] == 1:
                    binary_constraints.append(r[j])
                else:
                    binary_constraints.append(Not(r[j]))
            constraints.append(Implies(vars[i], And(binary_constraints)))
        
        return And(*constraints)

    def at_most_one_heule(self, vars):
        n = len(vars)
        if n <= 4:
            return self.at_most_one_pairwise(vars)

        constraints = [] 
        y = FreshBool(f'y_heule')
        constraints.append(self.at_most_one_pairwise(vars[:3] + [y]))
        remaining_vars = [Not(y)] + vars[3:]
        constraints.append(self.at_most_one_heule(remaining_vars))

        return And(*constraints)

    
    def at_most_k_pairwise(self, vars, k):
        n = len(vars)
        constraints = []
        
        for combo in itertools.combinations(range(n), k + 1):
            clause = [Not(vars[i]) for i in combo]
            constraints.append(Or(clause))
        
        return And(*constraints)

    def at_most_k_sequential(self, vars, k):
        n = len(vars)
        constraints = []

        s = [[FreshBool(f's_{i}_{j}') for j in range(k)] for i in range(n)]
        constraints.append(Implies(vars[0], s[0][0]))
        for j in range(1, k):
            constraints.append(Not(s[0][j]))
        for i in range(1, n - 1):
            constraints.append(Implies(Or(vars[i], s[i-1][0]), s[i][0]))
            for j in range(1, k):
                constraints.append(And(
                    Implies(Or(And(vars[i], s[i-1][j-1]), s[i-1][j]), s[i][j]), 
                    Implies(s[i-1][k-1], Not(vars[i])))
                )
        constraints.append(Implies(s[n-2][k-1], Not(vars[n-1])))

        return And(*constraints)
    
    def at_most_one_z3(self, vars):
        return AtMost(*vars, 1)
    
    def at_most_k_z3(self, vars, k):
        return AtMost(*vars, k)

    def at_most_one(self, vars):
        pass

    def at_most_k(self, vars, k):
        pass

    def at_least_one(self, vars):
        return Or(vars)

    def at_least_k(self, vars, k):
        n = len(vars)
        negated_vars = [Not(var) for var in vars]
        return self.at_most_k(negated_vars, n - k)

    def exactly_one(self, vars):
        return And(self.at_most_one(vars), self.at_least_one(vars))

    def exactly_k(self, vars, k):
        return And(self.at_most_k(vars, k), self.at_least_k(vars, k))