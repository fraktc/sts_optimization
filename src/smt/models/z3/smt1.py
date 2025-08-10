from z3 import *
import time

class STSSolver:
    def __init__(self, instance, timeout=300, incremental=False, implied_constraint_mask=[False], symmetry_breaking=False, optimization=False, **kwargs):
        self.incremental = incremental
        
        self.n = instance
        self.weeks = self.n - 1
        self.periods = self.n // 2
        self.slots = 2

        self.TEAMS = range(self.n)
        self.WEEKS = range(self.weeks)
        self.PERIODS = range(self.periods)
        self.SLOTS = range(self.slots)

        self.implied_constraint_mask = implied_constraint_mask
    
    def create_solver(self):
        self.solver = Solver()

    def create_variables(self):
        # Create representations
        
        self.teams = [[[
            Int(f"team_{w}_{p}_{s}") 
        for s in self.SLOTS] 
        for p in self.PERIODS] 
        for w in self.WEEKS]
        
        self.match_count = Array('match_count', IntSort(), ArraySort(IntSort(), IntSort()))
        self.period_count = Array('period_count', IntSort(), ArraySort(IntSort(), IntSort()))
        self.week_count = Array('week_count', IntSort(), ArraySort(IntSort(), IntSort()))

        # Define domains
        for w in self.WEEKS:
            for p in self.PERIODS:
                for s in self.SLOTS:
                    self.solver.add(And(self.teams[w][p][s] >= 0, self.teams[w][p][s] <= self.n - 1))

        # Consistency between self.teams and self.match_count
        for t1 in self.TEAMS:
            for t2 in self.TEAMS:
                matches_12 = Sum([
                    If(And(
                        self.teams[w][p][0] == t1,
                        self.teams[w][p][1] == t2
                    ), 1, 0)
                    for w in self.WEEKS
                    for p in self.PERIODS
                ])
                self.solver.add(Select(Select(self.match_count, t1), t2) == matches_12)
        
        # Consistency between self.teams and self.period_count
        for t in self.TEAMS:
            for p in self.PERIODS:
                matches_tp = Sum([
                    If(Or(
                        self.teams[w][p][0] == t,
                        self.teams[w][p][1] == t
                    ), 1, 0)
                    for w in self.WEEKS
                ])
                self.solver.add(Select(Select(self.period_count, t), p) == matches_tp)

        # Consistency between self.teams and self.week_count
        for t in self.TEAMS:
            for w in self.WEEKS:
                matches_tw = Sum([
                    If(Or(
                        self.teams[w][p][0] == t,
                        self.teams[w][p][1] == t
                    ), 1, 0)
                    for p in self.PERIODS
                ])
                self.solver.add(Select(Select(self.week_count, t), p) == matches_tw)

    def add_ACC1(self):
        # ACC1: Every team plays against every other team over the course of the turnament
        for t1 in self.TEAMS:
            for t2 in self.TEAMS:
                if t1 != t2:
                    self.solver.add(
                            (Select(Select(self.match_count, t1), t2) == 1) !=
                            (Select(Select(self.match_count, t2), t1) == 1)
                        )
    
    def add_ACC2(self):
        # ACC2: Every team plays at most once a week
        for w in self.WEEKS:
            for t in self.TEAMS:
                    self.solver.add(Select(Select(self.week_count, t), w) <= 1)
    
    def add_ACC3(self):
        # ACC3: Every team plays at most 2 matches in any given period
        for t in self.TEAMS:
            for p in self.PERIODS:
                self.solver.add(Select(Select(self.period_count, t), p) <= 2)

    def add_implied(self):
        if self.implied_constraint_mask[0]:
            # No team plays against itself
            for t in self.TEAMS:
                solver.add(Select(Select(self.match_count, t),t) == 0)
    
    def solve(self):
        start_time = time.time()
        
        self.create_solver()
        self.create_variables()
        self.add_ACC1()
        self.add_ACC2()
        self.add_implied()
        if self.incremental: 
            self.solver.check()
        self.add_ACC3()
        self.solver.check()
        
        end_time = time.time()
        exec_time = end_time - start_time

        model = self.solver.model()

        results = {
            "time": exec_time,
            "opt": False,
            "obj": None,
            "sol": [[[model.eval(self.teams[w][p][s]) for s in self.SLOTS] for p in self.PERIODS] for w in self.WEEKS],
        }
        return results

