import time
from z3 import *

def solve_sports_tournament(n):
    """
    Solve Sports Tournament Scheduling problem using Z3
    
    Args:
        n: Number of teams (must be even)
    
    Returns:
        Solution dictionary or None if no solution exists
    """
    if n % 2 != 0:
        raise ValueError("Number of teams must be even")
    
    # Create Z3 solver
    solver = Solver()
    
    # Parameters
    teams = list(range(1, n + 1))
    weeks = list(range(1, n))  # n-1 weeks
    periods = list(range(1, n//2 + 1))  # n/2 periods
    slots = [1, 2]  # home and away
    
    # Decision variables: matches[period][week][slot] = team
    matches = {}
    for p in periods:
        matches[p] = {}
        for w in weeks:
            matches[p][w] = {}
            for s in slots:
                matches[p][w][s] = Int(f'match_p{p}_w{w}_s{s}')
                # Domain constraint: each variable must be a valid team
                solver.add(And(matches[p][w][s] >= 1, matches[p][w][s] <= n))
    
    # Auxiliary variables for counting
    period_counter = {}
    match_counter = {}
    
    for t in teams:
        period_counter[t] = {}
        for p in periods:
            period_counter[t][p] = Int(f'period_counter_t{t}_p{p}')
            solver.add(period_counter[t][p] >= 0)
        
        match_counter[t] = {}
        for s in slots:
            match_counter[t][s] = Int(f'match_counter_t{t}_s{s}')
            solver.add(match_counter[t][s] >= 0)
    
    # Constraint 1: Every team plays with every other team only once
    # For each pair of teams, they should play exactly once
    for t1 in teams:
        for t2 in teams:
            if t1 != t2:
                # Count how many times t1 and t2 play against each other
                plays_together = []
                for w in weeks:
                    for p in periods:
                        # t1 home, t2 away OR t1 away, t2 home
                        plays_together.append(
                            Or(
                                And(matches[p][w][1] == t1, matches[p][w][2] == t2),
                                And(matches[p][w][1] == t2, matches[p][w][2] == t1)
                            )
                        )
                
                # Exactly one of these should be true
                solver.add(PbEq([(condition, 1) for condition in plays_together], 1))
    
    # Constraint 2: Every team plays once a week
    for t in teams:
        for w in weeks:
            plays_in_week = []
            for p in periods:
                for s in slots:
                    plays_in_week.append(matches[p][w][s] == t)
            
            # Exactly one of these should be true
            solver.add(PbEq([(condition, 1) for condition in plays_in_week], 1))
    
    # Constraint 3: Every team plays at most twice in the same period
    for t in teams:
        for p in periods:
            plays_in_period = []
            for w in weeks:
                for s in slots:
                    plays_in_period.append(matches[p][w][s] == t)
            
            # At most 2 of these should be true
            solver.add(PbLe([(condition, 1) for condition in plays_in_period], 2))
    
    # Constraint 4: No team plays against itself
    for w in weeks:
        for p in periods:
            solver.add(matches[p][w][1] != matches[p][w][2])
    
    # Constraint 5: All teams in a week must be different
    for w in weeks:
        all_teams_in_week = []
        for p in periods:
            for s in slots:
                all_teams_in_week.append(matches[p][w][s])
        solver.add(Distinct(all_teams_in_week))
    
    # Define period_counter constraints
    for t in teams:
        for p in periods:
            count_expr = Sum([If(matches[p][w][s] == t, 1, 0) 
                            for w in weeks for s in slots])
            solver.add(period_counter[t][p] == count_expr)
    
    # Define match_counter constraints (for home/away balance)
    for t in teams:
        for s in slots:
            count_expr = Sum([If(matches[p][w][s] == t, 1, 0) 
                            for w in weeks for p in periods])
            solver.add(match_counter[t][s] == count_expr)
    
    # Symmetry breaking constraints
    # Fix first week home teams to be 1, 2, ..., n/2
    for p in periods:
        solver.add(matches[p][1][1] == p)
    
    # Lexicographic ordering for weeks
    for w in range(1, len(weeks)):
        home_teams_w = [matches[p][w][1] for p in periods]
        home_teams_w_plus_1 = [matches[p][w+1][1] for p in periods]
        
        # Create lexicographic constraint
        lex_constraints = []
        for i in range(len(periods)):
            prefix_equal = [home_teams_w[j] == home_teams_w_plus_1[j] for j in range(i)]
            if prefix_equal:
                lex_constraints.append(
                    Implies(And(prefix_equal), home_teams_w[i] < home_teams_w_plus_1[i])
                )
            else:
                lex_constraints.append(home_teams_w[i] < home_teams_w_plus_1[i])
        
        solver.add(Or(lex_constraints))
    
    # Optimization: minimize maximum imbalance
    max_imbalance = Int('max_imbalance')
    solver.add(max_imbalance >= 0)
    
    for t in teams:
        imbalance = If(match_counter[t][1] >= match_counter[t][2], 
                      match_counter[t][1] - match_counter[t][2],
                      match_counter[t][2] - match_counter[t][1])
        solver.add(max_imbalance >= imbalance)
    
    # Solve with optimization
    best_imbalance = None
    best_model = None
    
    # Try to find solutions with increasing imbalance until we find one
    for target_imbalance in range(0, n):
        solver.push()
        solver.add(max_imbalance <= target_imbalance)
        
        if solver.check() == sat:
            best_model = solver.model()
            best_imbalance = target_imbalance
            print(f"Found solution with max imbalance: {target_imbalance}")
            break
        
        solver.pop()
    
    if best_model is None:
        return None
    
    # Extract solution
    solution = {
        'home_schedule': {},
        'away_schedule': {},
        'max_imbalance': best_imbalance,
        'match_counter': {}
    }
    
    for w in weeks:
        solution['home_schedule'][w] = {}
        solution['away_schedule'][w] = {}
        for p in periods:
            solution['home_schedule'][w][p] = best_model.evaluate(matches[p][w][1]).as_long()
            solution['away_schedule'][w][p] = best_model.evaluate(matches[p][w][2]).as_long()
    
    for t in teams:
        solution['match_counter'][t] = {
            'home': best_model.evaluate(match_counter[t][1]).as_long(),
            'away': best_model.evaluate(match_counter[t][2]).as_long()
        }
    
    return solution

class Unified_Z3_Model:
    """
    Wrapper for the Z3-based sports tournament solver to fit the unified interface.
    Instance can be either an integer (number of teams) or a dict with key 'n'.
    """
    def __init__(self, instance):
        # Allow instance as int or dict
        if isinstance(instance, dict):
            if 'n' not in instance:
                raise ValueError("Instance dict must provide 'n' key for number of teams")
            self.n = instance['n']
        elif isinstance(instance, int):
            self.n = instance
        else:
            raise ValueError("Instance must be int or dict with key 'n'")
        # store solution placeholder
        self.solution = None

    def solve(self, timeout, random_seed=None):
        """
        Solve tournament scheduling with a time limit.

        Args:
            timeout: time limit in seconds (ignored internally)
            random_seed: ignored for Z3 solver

        Returns:
            objective: max imbalance
            solution: schedule dict as returned by solve_sports_tournament
            optimality: True if a solution is found
            solve_time: total time taken (seconds)
            restart: None (not tracked)
            max_memory: None (not tracked)
            mk_bool_var: None (not tracked)
            conflicts: None (not tracked)
        """
        start = time.time()
        solution = None
        try:
            solution = solve_sports_tournament(self.n)
        except Exception as e:
            # solver errors are propagated as no solution
            solution = None
        elapsed = time.time() - start

        if solution is None:
            return None, None, False, elapsed, None, None, None, None

        objective = solution.get('max_imbalance')
        # Mark optimal as True since we search increasing imbalance
        return (
            objective,
            solution,
            True,
            elapsed,
            None,
            None,
            None,
            None
        )
