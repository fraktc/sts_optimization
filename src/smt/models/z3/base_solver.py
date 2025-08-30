import time
from z3 import *

class BaseSolver:
    """Base class to solve (up to satisfiability) the STS with z3 SMT.

    How to use:
        - Implement create_solver, create_variables, and create_constraints methods
        - If optimization is set to False, append batches of constraints to self.constraint_batches
        - Each batch should come as a list of constraints which are later added to the inner solver by the solve method
        - If optimization is set to True, add all constraints in a single batch
    """
    def __init__(self, instance, timeout=300, implied_constraint_mask=None, symmetry_constraint_mask=None, optimization=False, **kwargs):
        # Start timer
        self.start_time = time.time()

        # Store parameters
        self.n = instance
        self.timeout = timeout
        self.implied_constraint_mask = implied_constraint_mask
        self.symmetry_constraint_mask = symmetry_constraint_mask
        self.optimization = optimization

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
        self.solver = Optimize() if self.optimization else Solver()
        self.solver.set("timeout", int(self.timeout * 1000))

    def create_variables(self):
        """Initialize the decision variables and their domains."""
        pass

    def create_constraints(self):
        """Create batches of constraints to add to the solver."""
        pass

    def create_objective(self):
        """Create minimization objective function.
        
        Use maximum absolute imbalance between numbers of home and away games.
        """
        counts = [[Int(f"home_count_{t}_{s}") for s in self.SLOTS] for t in self.TEAMS]
        imbalances = [Int(f"imbalance_{t}") for t in self.TEAMS]        
        
        for t in self.TEAMS:
            for s in self.SLOTS:
                count = Sum([
                    If(self.teams[p][w][s] == t, 1, 0)
                    for p in self.PERIODS 
                    for w in self.WEEKS
                ])
                self.solver.add(counts[t][s] == count)
            
        for t in self.TEAMS:
            diff = counts[t][0] - counts[t][1]
            self.solver.add(imbalances[t] == If(diff >= 0, diff, -diff))
                
        self.max_imbalance = Int("max_imbalance")    
        for t in self.TEAMS:
            self.solver.add(self.max_imbalance >= imbalances[t])
        self.solver.add(Or([self.max_imbalance == imbalances[t] for t in self.TEAMS]))
        self.solver.add(self.max_imbalance >= 1)

    def solve(self):
        """Solve the satisfiability problem."""
        self.create_objective()
        if self.optimization:
            self.solver.minimize(self.max_imbalance)

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
            self.obj = self.model.eval(self.max_imbalance).as_long()
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