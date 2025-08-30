from .base_solver import BaseSolver
from z3 import *

class SuperSimplifiedNaiveSolver(BaseSolver):
    """
    """

    def create_variables(self):
        # Create representations
        self.teams = [[[
            Int(f"team_{p}_{w}_{s}") 
        for s in self.SLOTS]  
        for w in self.WEEKS]
        for p in self.PERIODS]
        
        # Define domains
        for p in self.PERIODS:
            for w in self.WEEKS:
                for s in self.SLOTS:
                    self.solver.add(And(self.teams[p][w][s] >= 0, self.teams[p][w][s] < self.n))

    def team_weight(self, t):
            return t + 1

    def create_constraints(self):
        self.constraint_batches = [[]]

        # **** CORE CONSTRAINTS ****

        # ACC1: Every team plays against every other team over the course of the turnament
        for t1 in self.TEAMS:
            for t2 in self.TEAMS:
                if t1 < t2:
                    matches_12 = Sum([
                        If(Or(
                            And(self.teams[p][w][0] == t1, self.teams[p][w][1] == t2),
                            And(self.teams[p][w][0] == t2, self.teams[p][w][1] == t1)
                        ), 1, 0)
                        for p in self.PERIODS
                        for w in self.WEEKS
                    ])
                    self.constraint_batches[0].append(matches_12 == 1)
    
        # ACC2: Every team plays at most once a week
        for w in self.WEEKS:
            for t in self.TEAMS:
                matches_tw = Sum([
                    If(Or(
                        self.teams[p][w][0] == t,
                        self.teams[p][w][1] == t
                    ), 1, 0)
                    for p in self.PERIODS
                ])
                self.constraint_batches[0].append(matches_tw <= 1)
    
        # ACC3: Every team plays at most 2 matches in any given period
        for t in self.TEAMS:
            for p in self.PERIODS:
                matches_tp = Sum([
                    If(Or(
                        self.teams[p][w][0] == t,
                        self.teams[p][w][1] == t
                    ), 1, 0)
                    for w in self.WEEKS
                ])
                self.constraint_batches[0].append(matches_tp <= 2)

        # **** IMPLIED CONSTRAINTS ****
        if self.implied_constraint_mask is not None:
            if self.implied_constraint_mask[0]:
                # No team plays against itself
                for t in self.TEAMS:
                    matches_tt = Sum([
                        If(And(
                            self.teams[p][w][0] == t,
                            self.teams[p][w][1] == t
                        ), 1, 0)
                        for p in self.PERIODS
                        for w in self.WEEKS
                    ])
                    self.constraint_batches[0].append(matches_tt == 0)

        # **** SYMMETRY-BREAKING CONSTRAINTS ****
        if self.symmetry_constraint_mask is not None:
            if self.symmetry_constraint_mask[0]:
                # 
                week_weights = []
                for w in self.WEEKS:
                    week_weights.append(
                        Sum([
                            If(self.teams[p][w][s] == t, self.team_weight(t), 0)
                            for s in self.SLOTS
                            for t in self.TEAMS
                            for p in self.PERIODS
                        ])
                    )
                for w in range(self.weeks - 1):
                    self.constraint_batches[0].append(week_weights[w] <= week_weights[w + 1])

    def format_solution(self):
        # Initialize solution
        self.sol = [[None for w in self.WEEKS] for p in self.PERIODS]

        # Populate solution
        for p in self.PERIODS:
            for w in self.WEEKS:
                team_a = self.model.eval(self.teams[p][w][0]).as_long() + 1
                team_b = self.model.eval(self.teams[p][w][1]).as_long() + 1
                self.sol[p][w] = [team_a, team_b]