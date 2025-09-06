from .base_solver import BaseSolver
from z3 import *

class NaiveSolver(BaseSolver):
    """Solve STS problem with naive approach based on time home-away slots that need to be filled by teams.
    
    There is one slot per week per period.
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
        """Assign a weight to the given team.
        
        Used to break up the week symmetry.
        """
        return t + 1

    def create_constraints(self):
        # **** CORE CONSTRAINTS ****

        # Every team plays against every other team over the course of the turnament
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
                    self.solver.add(matches_12 == 1)
    
        # Every team plays at most once a week
        for w in self.WEEKS:
            for t in self.TEAMS:
                matches_tw = Sum([
                    If(Or(
                        self.teams[p][w][0] == t,
                        self.teams[p][w][1] == t
                    ), 1, 0)
                    for p in self.PERIODS
                ])
                self.solver.add(matches_tw <= 1)
    
        # Every team plays at most 2 matches in any given period
        for t in self.TEAMS:
            for p in self.PERIODS:
                matches_tp = Sum([
                    If(Or(
                        self.teams[p][w][0] == t,
                        self.teams[p][w][1] == t
                    ), 1, 0)
                    for w in self.WEEKS
                ])
                self.solver.add(matches_tp <= 2)

        # **** IMPLIED CONSTRAINTS ****
        if self.implied_constraints:
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
                self.solver.add(matches_tt == 0)

        # **** SYMMETRY-BREAKING CONSTRAINTS ****
        if self.symmetry_constraints:
            # Order weeks by the sum of the weights of the teams playing home to break up the week symmetry
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
                self.solver.add(week_weights[w] <= week_weights[w + 1])

    def format_solution(self):
        # Initialize solution
        self.sol = [[None for w in self.WEEKS] for p in self.PERIODS]

        # Populate solution
        for p in self.PERIODS:
            for w in self.WEEKS:
                team_a = self.model.eval(self.teams[p][w][0]).as_long() + 1
                team_b = self.model.eval(self.teams[p][w][1]).as_long() + 1
                self.sol[p][w] = [team_a, team_b]
                
