import time
from z3 import *

class BaseSolver:
    """Base class to solve (up to satisfiability) the STS with z3 SMT.
    
    How to use:
        - Implement create_solver, create_variables, and create_constraints methods
        - Append batches of constraints to self.constraint_batches
        - Each batch should come as a list of constraints which are later added to the inner solver by the solve method
    """
    def __init__(self, instance, timeout=300, implied_constraint_mask=[False], symmetry_breaking=False, optimization=False, **kwargs):
        # Start timer
        self.start_time = time.time()

        # Store parameters
        self.n = instance
        self.timeout = timeout
        self.implied_constraint_mask = implied_constraint_mask

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
        """Initialize the decision variables and their domains."""
        pass

    def create_constraints(self):
        """Create batches of constraints to add to the solver."""
        pass

    def check_optimality(self):
        """Check for optimality of the computed solution and store objective function value and optimality status.
        
        Use the maximum absolute imbalance as the objective function.
        """
        # Compute absolute imbalances
        imbalances = []
        for t in self.TEAMS:
            home_games = sum([1 for p in self.PERIODS for w in self.WEEKS if self.sol[p][w][0] == t + 1])
            away_games = sum([1 for p in self.PERIODS for w in self.WEEKS if self.sol[p][w][1] == t + 1])
            imbalances.append(abs(home_games - away_games))
        
        # Compute objective function and optimality status
        self.obj = max(imbalances)
        self.optimal = (self.obj == 1)

    def solve(self):
        """Solve the satisfiability problem."""
        # Do intermediate check after adding every constraint batch
        # Stop adding constraints if unsat
        for constraint_batch in self.constraint_batches:
            self.solver.add(constraint_batch)
            status = self.solver.check()
            if status == unsat:
                break

        # End timer and compute execution time
        end_time = time.time()
        self.exec_time = end_time - self.start_time

        # If the problem is sat, extract a well-formatted solution and print out the objective value and 
        # whether the solution is optimal
        if status == sat:
            self.model = self.solver.model()
            self.format_solution()
            self.check_optimality()
        else:
            self.sol = None
            self.obj = None
            self.optimal = None

        # Create output dictionary
        self.results = {
            "time": self.exec_time,
            "optimal": self.optimal,
            "obj": self.obj,
            "sol": self.sol,
        }
        return self.results