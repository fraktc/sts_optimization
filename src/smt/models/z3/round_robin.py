


class RoundRobinSolver(BaseSolver):
    """Use the Round Robin method to generate an initial solution.

    The period constraint does not hold in the initial solution and is imposed though SMT.
    The initial solution already satisfies the optimality requirement.
    The solver assigns values to the decision variables contained in self.new_periods.
    self.new_periods is an array that maps a period, week combination to a new period.
    The match at self.teams[p][w] is supposed to actually take place during period self.new_periods[p][w] in the same week.
    The period constraint is solved by such period permutations.
    """

    def create_variables(self):
        # Create initial solution
        self.teams = [[[Int(f"teams_{p}_{w}_{s}") for s in self.SLOTS] for w in self.WEEKS] for p in self.PERIODS]
        circle = list(self.TEAMS)
        for w in self.WEEKS:
            for p in self.PERIODS:
                team_a, team_b = circle[p], circle[self.n - p - 1]
                team_a, team_b = min(team_a, team_b), max(team_a, team_b)
                if (team_a + team_b) % 2 == 1: # Use parity rule for balancing
                    team_a, team_b = team_b, team_a
                self.solver.add(self.teams[p][w][0] == team_a, self.teams[p][w][1] == team_b)
            circle = circle[:1] + circle[-1:] + circle[1:-1]

        # Create decision variables
        # self.new_periods represents a permutation of the matches of each week across the periods
        self.new_periods = [[Int(f"new_periods_{p}_{w}") for w in self.WEEKS] for p in self.PERIODS]
        for p in self.PERIODS:
            for w in self.WEEKS:
                self.solver.add(self.new_periods[p][w] >= 0, self.new_periods[p][w] < self.periods)

    def create_constraints(self):
        self.constraint_batches = [[]]

        # Each time slot (period, week) gets exactly one match
        for p in self.PERIODS:
            for w in self.WEEKS:
                count = Sum([
                    If(self.new_periods[p_old][w] == p, 1, 0)
                    for p_old in self.PERIODS
                ])
                self.constraint_batches[0].append(count == 1)

        # Each team plays at most twice in the same period
        for t in self.TEAMS:
            for p in self.PERIODS:
                count = Sum([
                    If(And(self.new_periods[p_old][w] == p,
                           Or(self.teams[p_old][w][0] == t, self.teams[p_old][w][1] == t)), 1, 0)
                    for p_old in self.PERIODS for w in self.WEEKS
                ])
                self.constraint_batches[0].append(count <= 2)

        # **** IMPLIED CONSTRAINTS ****
        if self.implied_constraint_mask is not None:
            pass

        # **** SYMMETRY-BREAKING CONSTRAINTS ****
        if self.symmetry_constraint_mask is not None:
            
            # The order of matches in the first week is left as is 
            if self.symmetry_constraint_mask[0]:
                for p in self.PERIODS:
                    self.constraint_batches[0].append(self.new_periods[p][0] == p)


    def format_solution(self):
        # Initialize solution
        self.sol = [[None for w in self.WEEKS] for p in self.PERIODS]

        # Populate solution
        for p_old in self.PERIODS:
            for w in self.WEEKS:
                new_p = self.model.eval(self.new_periods[p_old][w]).as_long()
                team_a = self.model.eval(self.teams[p_old][w][0]).as_long() + 1
                team_b = self.model.eval(self.teams[p_old][w][1]).as_long() + 1
                self.sol[new_p][w] = [team_a, team_b]


class BitVecRoundRobinSolver(BaseSolver):
    """Use the Round Robin method to generate an initial solution.

    Like RoundRobinSolver, but uses BitVec to represent periods.
    """

    def create_parameters(self):
        super().create_parameters()
        self.bits = math.ceil(math.log2(self.n))

    def create_variables(self):
        # Create initial solution
        self.teams = [[[Int(f"teams_{p}_{w}_{s}") for s in self.SLOTS] for w in self.WEEKS] for p in self.PERIODS]
        circle = list(self.TEAMS)
        for w in self.WEEKS:
            for p in self.PERIODS:
                team_a, team_b = circle[p], circle[self.n - p - 1]
                team_a, team_b = min(team_a, team_b), max(team_a, team_b)
                if (team_a + team_b) % 2 == 1: # Use parity rule for balancing
                    team_a, team_b = team_b, team_a
                self.solver.add(self.teams[p][w][0] == team_a, self.teams[p][w][1] == team_b)
            circle = circle[:1] + circle[-1:] + circle[1:-1]

        # Create decision variables
        # self.new_periods represents a permutation of the matches of each week across the periods
        self.new_periods = [[BitVec(f"new_periods_{p}_{w}", self.bits) for w in self.WEEKS] for p in self.PERIODS]
        for p in self.PERIODS:
            for w in self.WEEKS:
                self.solver.add(ULE(self.new_periods[p][w], self.periods - 1))

    def create_constraints(self):
        self.constraint_batches = [[]]

        # Each time slot (period, week) gets exactly one match
        for p in self.PERIODS:
            for w in self.WEEKS:
                count = Sum([
                    If(self.new_periods[p_old][w] == p, 1, 0)
                    for p_old in self.PERIODS
                ])
                self.constraint_batches[0].append(count == 1)

        # Each team plays at most twice in the same period
        for t in self.TEAMS:
            for p in self.PERIODS:
                count = Sum([
                    If(And(self.new_periods[p_old][w] == p,
                           Or(self.teams[p_old][w][0] == t, self.teams[p_old][w][1] == t)), 1, 0)
                    for p_old in self.PERIODS for w in self.WEEKS
                ])
                self.constraint_batches[0].append(count <= 2)
        
        # **** IMPLIED CONSTRAINTS ****
        if self.implied_constraint_mask is not None:
            pass

        # **** SYMMETRY-BREAKING CONSTRAINTS ****
        if self.symmetry_constraint_mask is not None:
            
            # The order of matches in the first week is left as is 
            if self.symmetry_constraint_mask[0]:
                for p in self.PERIODS:
                    self.constraint_batches[0].append(self.new_periods[p][0] == p)


    def format_solution(self):
        # Initialize solution
        self.sol = [[None for w in self.WEEKS] for p in self.PERIODS]

        # Populate solution
        for p_old in self.PERIODS:
            for w in self.WEEKS:
                new_p = self.model.eval(self.new_periods[p_old][w]).as_long()
                team_a = self.model.eval(self.teams[p_old][w][0]).as_long() + 1
                team_b = self.model.eval(self.teams[p_old][w][1]).as_long() + 1
                self.sol[new_p][w] = [team_a, team_b]