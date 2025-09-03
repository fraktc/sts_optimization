"""SAT solver and optimizer that uses a slot-based model."""

from z3 import *
import time

from .constraints import CardinalityConstraints

class SlotBasedSolver(CardinalityConstraints):
    """Solve STS problem in Z3 SAT using a slot-based model. No optimization.

    The at_most_one_encoding and at_most_k_encoding parameters can be used to customize the
    cardinality constraint encoding. 
    """
    def __init__(self, instance, timeout=300, at_most_one_encoding="pairwise", at_most_k_encoding="pairwise"):
        # Start timer
        self.start_time = time.time()

        # Store parameters
        self.n = instance
        self.timeout = timeout

        # Set the chosen cardinality constraint encoding
        match at_most_one_encoding:
            case "pairwise":
                self.at_most_one = self.at_most_one_pairwise
            case "sequential":
                self.at_most_one = self.at_most_one_sequential
            case "bitwise":
                self.at_most_one = self.at_most_one_bitwise
            case "heule":
                self.at_most_one = self.at_most_one_heule
            case "z3":
                self.at_most_one = self.at_most_one_z3
        match at_most_k_encoding:
            case "pairwise":
                self.at_most_k = self.at_most_k_pairwise
            case "sequential":
                self.at_most_k = self.at_most_k_sequential
            case "z3":
                self.at_most_k = self.at_most_k_z3

        # Create model
        self.create_parameters()
        self.create_solver()
        self.create_variables()
        self.create_constraints()
        
    def create_parameters(self):
        """Compute the parameters of the STS problem and initialize the associated ranges."""
        # Parameters
        self.weeks = self.n - 1
        self.periods = self.n // 2
        self.slots = 2

        # Ranges
        self.TEAMS = range(self.n)
        self.WEEKS = range(self.weeks)
        self.PERIODS = range(self.periods)
        self.SLOTS = range(self.slots)

    def create_solver(self):
        """Initialize solver."""
        self.solver = Solver()
        self.solver.set("timeout", int(self.timeout * 1000))

    def create_variables(self):
        """Initialize the decision variables."""
        self.teams = [[[[
            Bool(f"teams_{p}_{w}_{s}_{t}")
            for t in self.TEAMS]
            for s in self.SLOTS]
            for w in self.WEEKS]
            for p in self.PERIODS
        ]

    def create_constraints(self):
        """Add main constraints to the solver."""
        # Every period+week+slot combination can be assigned to exactly a single team
        for p in self.PERIODS:
            for w in self.WEEKS:
                for s in self.SLOTS:
                    assignments_pws = [
                        self.teams[p][w][s][t]
                        for t in self.TEAMS
                    ]
                    self.solver.add(self.exactly_one(assignments_pws))

        # Every team plays against every other team exactly once over the course of the tournament
        for t1 in self.TEAMS:
            for t2 in self.TEAMS:
                if t1 < t2:
                    matches_12 = [
                        Or(
                            And(self.teams[p][w][0][t1], self.teams[p][w][1][t2]),
                            And(self.teams[p][w][0][t2], self.teams[p][w][1][t1])
                        )
                        for p in self.PERIODS
                        for w in self.WEEKS
                    ]
                    self.solver.add(self.exactly_one(matches_12))

        # Every team plays exactly once a week
        for w in self.WEEKS:
            for t in self.TEAMS:
                matches_tw = [
                    Or(
                        self.teams[p][w][0][t],
                        self.teams[p][w][1][t]
                    )
                    for p in self.PERIODS
                ]
                self.solver.add(self.exactly_one(matches_tw))

        # Every team plays at most 2 matches in any given period
        for t in self.TEAMS:
            for p in self.PERIODS:
                matches_tp = [
                    Or(
                        self.teams[p][w][0][t],
                        self.teams[p][w][1][t]
                    )
                    for w in self.WEEKS
                ]
                self.solver.add(self.at_most_k(matches_tp, 2))

    def format_solution(self):
        """Format solution for export."""
        # Initialize solution
        self.sol = [[None for w in self.WEEKS] for p in self.PERIODS]

        # Populate solution
        for p in self.PERIODS:
            for w in self.WEEKS:
                team_a = None
                team_b = None
                for t in self.TEAMS:
                    if self.model.eval(self.teams[p][w][0][t]):
                        team_a = t + 1
                    if self.model.eval(self.teams[p][w][1][t]):
                        team_b = t + 1
                self.sol[p][w] = [team_a, team_b]

    def compute_objective(self):
        """Compute objective function, i.e. max imbalance."""
        match_counts = [[0 for t in self.TEAMS] for s in self.SLOTS]
        for p in self.PERIODS:
            for w in self.WEEKS:
                for s in self.SLOTS:
                    match_counts[s][self.sol[p][w][s] - 1] += 1
        imbalances = [abs(match_counts[0][t] - match_counts[1][t]) for t in self.TEAMS]
        self.max_imbalance = max(imbalances)

    def solve(self):
        """Solve the STS satisfiability problem."""
        # Look for a solution
        status = self.solver.check()

        # End timer and compute execution time
        end_time = time.time()
        self.exec_time = end_time - self.start_time

        # If the problem is sat, extract a well-formatted solution and print out the objective value and
        # whether the solution is optimal
        if status == sat:
            self.model = self.solver.model()
            self.format_solution()
            self.compute_objective()
            self.obj = self.max_imbalance
            self.optimal = self.obj == 1
        else:
            self.sol = None
            self.obj = None
            self.optimal = None

        # Create output dictionary
        self.results = {
            "time": self.exec_time,
            "opt": self.optimal,
            "obj": self.obj,
            "sol": self.sol,
        }
        return self.results
    
class SlotBasedOptimizer(SlotBasedSolver):
    """Solve the STS problem maximizing the number of balanced teams with a Z3-powered MAXSAT approach.
    
    A team is optimized if abs(num_home_games - num_away_games) < 1.
    """
    def __init__(self, instance, timeout=300, at_most_one_encoding="pairwise", at_most_k_encoding="pairwise"):
        super().__init__(instance, timeout, at_most_one_encoding, at_most_k_encoding)

        # Prepare for optimization
        self.optimal = False
        self.num_balanced_teams = 0
   
    def create_variables(self):
        super().create_variables()

        # Create optimization variables
        self.balanced = [Bool(f"balanced_{t}") for t in self.TEAMS]

    def create_constraints(self):
        super().create_constraints()

        # Add optimization constraints
        for t in self.TEAMS:
            home_matches = [self.teams[p][w][0][t] for p in self.PERIODS for w in self.WEEKS]
            self.solver.add(And(
                    self.at_most_k(home_matches, self.n // 2),
                    self.at_least_k(home_matches, self.n // 2 - 1)
                ) == self.balanced[t])

    def compute_objective(self):
        """Compute value of objective function, i.e. number of balanced teams."""
        self.num_balanced_teams = sum([is_true(self.model.eval(self.balanced[t])) for t in self.TEAMS])

    def solve(self):
        """Solve the satisfiability problem iteratively maximizing the objective."""
        while not self.optimal:
            # Add optimization constraints
            self.solver.add(self.at_least_k(self.balanced, self.num_balanced_teams + 1))

            # Look for a solution
            status = self.solver.check()
            
            # If the problem is sat, extract a well-formatted solution and compute number of non-balanced teams
            if status == sat:
                self.model = self.solver.model()
                self.format_solution()
                self.compute_objective()
                self.obj = self.n - self.num_balanced_teams
                self.optimal = (self.obj == 0)
            # If the problem is not sat, breaks and return empty solution
            else:
                self.sol = None
                self.obj = None
                self.optimal = None
                break
        
        # End timer and compute execution time
        end_time = time.time()
        self.exec_time = end_time - self.start_time


        # Create output dictionary
        self.results = {
            "time": self.exec_time,
            "opt": self.optimal,
            "obj": self.obj,
            "sol": self.sol
        }
        return self.results