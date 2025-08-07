import time
import logging
from z3 import *

logger = logging.getLogger(__name__)

def SMT_plain(instance, timeout=300, implied_constraints=False, 
              symmetry_breaking=False, optimization=False, **kwargs):
    """
    Plain SMT model for Sports Tournament Scheduling problem
    
    Args:
        instance: Instance number (determines n_teams = instance * 2)
        timeout: Time limit in seconds
        implied_constraints: Whether to add implied constraints
        symmetry_breaking: Whether to add symmetry breaking constraints
        optimization: Whether to solve optimization version
        
    Returns:
        dict: Result dictionary with keys 'time', 'optimal', 'obj', 'sol'
              'sol' is organized as [period][week] = [home_team, away_team]
    """
    start_time = time.time()
    n_teams = instance * 2  # Assuming instance number corresponds to n_teams/2
    
    # Handle edge cases
    if n_teams < 4 or n_teams % 2 != 0:
        logger.error(f"Invalid number of teams: {n_teams}")
        return {
            "time": 0,
            "optimal": False,
            "obj": None,
            "sol": None
        }
    
    n_weeks = n_teams - 1
    n_periods = n_teams // 2
    
    try:
        logger.info(f"Building SMT model for {n_teams} teams, {n_weeks} weeks, {n_periods} periods")
        
        # Create solver
        solver = Solver()
        solver.set("timeout", timeout * 1000)  # Z3 expects milliseconds
        
        # Decision variables: home[p][w] and away[p][w] for period p, week w
        home = [[Int(f"home_{p}_{w}") for w in range(n_weeks)] for p in range(n_periods)]
        away = [[Int(f"away_{p}_{w}") for w in range(n_weeks)] for p in range(n_periods)]
        
        # Basic domain constraints: teams are numbered 1 to n_teams
        for p in range(n_periods):
            for w in range(n_weeks):
                solver.add(And(home[p][w] >= 1, home[p][w] <= n_teams))
                solver.add(And(away[p][w] >= 1, away[p][w] <= n_teams))
                solver.add(home[p][w] != away[p][w])  # A team can't play itself
        
        # Constraint 1: Every team plays with every other team exactly once
        for t1 in range(1, n_teams + 1):
            for t2 in range(t1 + 1, n_teams + 1):
                # Exactly one match between t1 and t2 (either t1 home vs t2 away or vice versa)
                match_conditions = []
                for p in range(n_periods):
                    for w in range(n_weeks):
                        match_conditions.append(And(home[p][w] == t1, away[p][w] == t2))
                        match_conditions.append(And(home[p][w] == t2, away[p][w] == t1))
                solver.add(PbEq([(cond, 1) for cond in match_conditions], 1))
        
        # Constraint 2: Every team plays exactly once per week
        for w in range(n_weeks):
            for t in range(1, n_teams + 1):
                week_appearances = []
                for p in range(n_periods):
                    week_appearances.append(home[p][w] == t)
                    week_appearances.append(away[p][w] == t)
                solver.add(PbEq([(cond, 1) for cond in week_appearances], 1))
        
        # Constraint 4: All teams in each period of each week must be different
        for w in range(n_weeks):
            for p in range(n_periods):
                all_teams_in_period = []
                for pp in range(n_periods):
                    all_teams_in_period.extend([home[pp][w], away[pp][w]])
                solver.add(Distinct(all_teams_in_period))
        
        # Solve the problem
        logger.info("Starting to solve...")
        result = solver.check()
        
        elapsed_time = time.time() - start_time
        
        if result == sat:
            logger.info("Solution found!")
            model = solver.model()
            
            # Extract solution organized by periods and weeks
            solution = []
            for p in range(n_periods):
                period_solution = []
                for w in range(n_weeks):
                    home_team = model[home[p][w]].as_long()
                    away_team = model[away[p][w]].as_long()
                    period_solution.append([home_team, away_team])
                solution.append(period_solution)
            
            # Calculate objective value for optimization version
            obj_value = None
            if optimization:
                # Calculate balance of home/away games per team
                home_counts = [0] * n_teams
                for p in range(n_periods):
                    for w in range(n_weeks):
                        home_team = model[home[p][w]].as_long()
                        home_counts[home_team - 1] += 1
                
                # Objective: minimize maximum deviation from perfect balance
                target = n_weeks // 2
                max_deviation = max(abs(count - target) for count in home_counts)
                obj_value = max_deviation
            
            return {
                "time": int(elapsed_time),
                "optimal": True,
                "obj": obj_value,
                "sol": solution
            }
        
        elif result == unsat:
            logger.info("No solution exists")
            return {
                "time": int(elapsed_time),
                "optimal": False,
                "obj": None,
                "sol": None
            }
        
        else:  # timeout or unknown
            logger.info("Timeout or unknown result")
            return {
                "time": timeout,
                "optimal": False,
                "obj": None,
                "sol": None
            }
    
    except Exception as e:
        logger.error(f"Error in SMT model: {e}")
        elapsed_time = time.time() - start_time
        return {
            "time": timeout if elapsed_time >= timeout else int(elapsed_time),
            "optimal": False,
            "obj": None,
            "sol": None
        }