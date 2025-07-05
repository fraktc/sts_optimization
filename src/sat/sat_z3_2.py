import time
from z3 import *
import random

def solve_sports_tournament(n, timeout):
    """
    Solve Sports Tournament Scheduling problem using Z3
    
    Args:
        n: Number of teams (must be even)
        timeout: Time limit in seconds
    
    Returns:
        Solution dictionary or None if no solution exists
    """
    start_time = time.time()

    if n % 2 != 0:
        raise ValueError("Number of teams must be even")
    
    luby_sequence_100 = [
        1, 1, 2, 1, 1, 2, 4, 1, 1, 2,
        1, 1, 2, 4, 8, 1, 1, 2, 1, 1,
        2, 4, 8, 16, 1, 1, 2, 1, 1, 2,
        4, 8, 16, 32, 1, 1, 2, 1, 1, 2,
        4, 8, 16, 32, 64, 1, 1, 2, 1, 2,
        2, 4, 8, 16, 32, 64, 128, 1, 1, 2,
        1, 1, 2, 4, 8, 16, 32, 64, 128, 256,
        1, 1, 2, 1, 1, 2, 4, 8, 16, 32,
        64, 128, 256, 512, 1, 1, 2, 1, 1, 2,
        4, 8, 16, 32, 64, 128, 256, 512, 1024, 1
    ]
    base_timeout = 4000

    num_teams = n
    num_weeks = n - 1
    num_periods = n // 2

    teams = range(num_teams)
    weeks = range(num_weeks)
    periods = range(num_periods)

    plays = [[[Bool(f"plays_{t}_{w}_{p}") for p in periods] for w in weeks] for t in teams]

    satisfied = False
    k = 0
    while not satisfied:
        current_timeout = base_timeout * luby_sequence_100[k]
        k += 1

        s = Solver()

        seed = random.randint(0, 1000000)
        set_param("smt.phase_selection", 6)
        set_param("sat.phase", 6)
        set_param("sat.random_seed", seed)
        s.set("smt.random_seed", seed)
        s.set("timeout", current_timeout)

        for t in teams:
            for p in periods:
                s.add(PbLe([(plays[t][w][p], 1) for w in weeks], 2))

        for t in teams:
            for w in weeks:
                s.add(PbEq([(plays[t][w][p], 1) for p in periods], 1))

        for w in weeks:
            for p in periods:
                s.add(PbEq([(And(plays[t1][w][p], plays[t2][w][p]), 1) for t1 in teams for t2 in range(t1 + 1, num_teams)], 1))

        for t1 in teams:
            for t2 in range(t1 + 1, num_teams):
                s.add(PbEq([(And(plays[t1][w][p], plays[t2][w][p]), 1) for p in periods for w in weeks], 1))

        solver_check = s.check()
        satisfied = solver_check == sat

        remaining_time = timeout - (time.time() - start_time)
        if remaining_time <= 0:
            break

    # Extract solution

    solution = {
        "solution": [],
        "max_imbalance": -1,
        "optimality": False
    }

    # Extract the solution from the boolean variables
    model = s.model()
    for p in periods:
        period_matches = []
        for w in weeks:
            home_team = None
            away_team = None
            for t in teams:
                if best_model.evaluate(plays[t][w][p]):
                    if home_team is None:
                        home_team = t
                    else:
                        away_team = t
            
            # Add the match to the week's matches
            if home_team is not None and away_team is not None:
                period_matches.append((home_team, away_team))
        
        # Add the week's matches to the solution
        solution["solution"].append(period_matches)
    # print("Solution extracted successfully")
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
            timeout: time limit in seconds
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
            # print(f"Solving sports tournament with {self.n} teams, timeout: {timeout} seconds")
            # Call the Z3 solver function
            solution = solve_sports_tournament(self.n, timeout)
        except Exception as e:
            # solver errors are propagated as no solution
            solution = None
        elapsed = time.time() - start

        if solution is None:
            return None, None, False, elapsed, None, None, None, None

        objective = solution.get('max_imbalance')
        sol = solution.get('solution')
        optimality = solution.get('optimality')
        solve_time = elapsed
        # Mark optimal as True since we search increasing imbalance
        return (
            objective,
            sol,
            optimality,
            solve_time,
            None,
            None,
            None,
            None
        )
