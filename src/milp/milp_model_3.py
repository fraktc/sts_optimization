import pulp
import json
import time

def create_milp_model(n, timeout=60):
    """
    Create MILP model for round-robin scheduling problem
    n: even number of teams
    timeout: time limit in seconds
    Returns: dict with results for different solvers
    """
    
    # Parameters
    weeks = n - 1
    periods = n // 2
    TEAMS = list(range(1, n + 1))
    
    # ===========================
    # ROUND-ROBIN SCHEDULE GENERATION
    # ===========================
    def generate_round_robin(n):
        """Generate balanced round-robin schedule using circle method"""
        weeks = n - 1
        periods = n // 2
        
        rr_home = {}
        rr_away = {}
        
        for w in range(1, weeks + 1):
            for p in range(1, periods + 1):
                if p == 1:
                    a = 1
                    b = ((n - 1 + w - 1) % (n - 1)) + 2
                else:
                    a = ((p + w - 2) % (n - 1)) + 2
                    b = ((n - p + 1 + w - 2) % (n - 1)) + 2
                
                i = min(a, b)
                j = max(a, b)
                
                # Parity rule for home/away assignment
                if (i + j) % 2 == 0:
                    rr_home[w, p] = i
                    rr_away[w, p] = j
                else:
                    rr_home[w, p] = j
                    rr_away[w, p] = i
        
        return rr_home, rr_away
    
    rr_home, rr_away = generate_round_robin(n)
    
    # ===========================
    # MILP MODEL
    # ===========================
    prob = pulp.LpProblem("RoundRobinSchedule", pulp.LpMinimize)
    
    # Decision Variables
    # period_slot[w,p] = final period for match p in week w
    # period_slot = {}
    # for w in range(1, weeks + 1):
    #     for p in range(1, periods + 1):
    #         for pr in range(1, periods + 1):
    #             period_slot[w, p, pr] = pulp.LpVariable(f"period_slot_{w}_{p}_{pr}", cat='Binary')
    
    # # team_period[t,w] = period when team t plays in week w
    # team_period = {}
    # for t in TEAMS:
    #     for w in range(1, weeks + 1):
    #         for pr in range(1, periods + 1):
    #             team_period[t, w, pr] = pulp.LpVariable(f"team_period_{t}_{w}_{pr}", cat='Binary')

    # Decision Variables - use more efficient variable creation
    period_slot = pulp.LpVariable.dicts("period_slot", 
                                    [(w, p, pr) for w in range(1, weeks + 1) 
                                        for p in range(1, periods + 1) 
                                        for pr in range(1, periods + 1)], 
                                    cat='Binary')

    team_period = pulp.LpVariable.dicts("team_period",
                                    [(t, w, pr) for t in TEAMS 
                                        for w in range(1, weeks + 1) 
                                        for pr in range(1, periods + 1)],
                                    cat='Binary')
    
    # ===========================
    # CONSTRAINTS
    # ===========================
    
    # Each match in a week gets exactly one period slot
    for w in range(1, weeks + 1):
        for p in range(1, periods + 1):
            prob += pulp.lpSum(period_slot[w, p, pr] for pr in range(1, periods + 1)) == 1
    
    # Each period in a week is assigned to exactly one match
    for w in range(1, weeks + 1):
        for pr in range(1, periods + 1):
            prob += pulp.lpSum(period_slot[w, p, pr] for p in range(1, periods + 1)) == 1
    
    # Each team plays in exactly one period per week
    for t in TEAMS:
        for w in range(1, weeks + 1):
            prob += pulp.lpSum(team_period[t, w, pr] for pr in range(1, periods + 1)) == 1
    
    # Link team_period to period_slot using round-robin data
    for t in TEAMS:
        for w in range(1, weeks + 1):
            for pr in range(1, periods + 1):
                # team_period[t,w,pr] = 1 iff the match involving team t in week w is assigned to period pr
                match_in_period = []
                for p in range(1, periods + 1):
                    if rr_home[w, p] == t or rr_away[w, p] == t:
                        match_in_period.append(period_slot[w, p, pr])
                
                if match_in_period:  # Should always be true since each team plays once per week
                    prob += team_period[t, w, pr] == pulp.lpSum(match_in_period)
    
    # Each team plays in any period at most twice across all weeks
    for t in TEAMS:
        for pr in range(1, periods + 1):
            prob += pulp.lpSum(team_period[t, w, pr] for w in range(1, weeks + 1)) <= 2

        # Tighter bound: Teams can play at most ceil(weeks/periods) times in any period
    max_times_per_period = (weeks + periods - 1) // periods
    for t in TEAMS:
        for pr in range(1, periods + 1):
            prob += pulp.lpSum(team_period[t, w, pr] for w in range(1, weeks + 1)) <= max_times_per_period
    
    # Symmetry breaking: fix first week's period assignment
    for p in range(1, periods + 1):
        prob += period_slot[1, p, p] == 1
    

    
    # Objective: just find a feasible solution
    prob += 0
    
    # Test with different solvers
    solvers = {
        'CBC': pulp.PULP_CBC_CMD(msg=0, timeLimit=timeout),
        'HiGHS': pulp.COIN_CMD(msg=0, timeLimit=timeout) if pulp.COIN_CMD().available() else pulp.PULP_CBC_CMD(msg=0, timeLimit=timeout)
    }
    
    results = {}
    
    for solver_name, solver in solvers.items():
        start_time = time.time()
        
        # Solve with current solver
        prob.solve(solver)
        
        solve_time = time.time() - start_time
        
        if prob.status == pulp.LpStatusOptimal:
            # Extract solution
            solution_period_slot = {}
            for w in range(1, weeks + 1):
                for p in range(1, periods + 1):
                    for pr in range(1, periods + 1):
                        if period_slot[w, p, pr].varValue == 1:
                            solution_period_slot[w, p] = pr
            
            solution_team_period = {}
            for t in TEAMS:
                for w in range(1, weeks + 1):
                    for pr in range(1, periods + 1):
                        if team_period[t, w, pr].varValue == 1:
                            solution_team_period[t, w] = pr
            
            # Calculate imbalance
            home_count = {}
            away_count = {}
            
            for t in TEAMS:
                home_count[t] = 0
                away_count[t] = 0
                for w in range(1, weeks + 1):
                    for p in range(1, periods + 1):
                        if rr_home[w, p] == t:
                            home_count[t] += 1
                        if rr_away[w, p] == t:
                            away_count[t] += 1
            
            imbalance = {t: abs(home_count[t] - away_count[t]) for t in TEAMS}
            max_imbalance = max(imbalance.values())
            
            # Format solution as 2D array: [period][week] = [home, away]
            sol = []
            for pr in range(1, periods + 1):
                period_matches = []
                for w in range(1, weeks + 1):
                    # Find which original match is assigned to this period in this week
                    for p in range(1, periods + 1):
                        if solution_period_slot[w, p] == pr:
                            period_matches.append([rr_home[w, p], rr_away[w, p]])
                            break
                sol.append(period_matches)
            
            results[solver_name] = {
                "time": solve_time,
                "optimal": True,
                "obj": max_imbalance,
                "sol": sol,
                "_extras": {"runner": ""}
            }
            
        else:
            results[solver_name] = {
                "time": solve_time,
                "optimal": False,
                "obj": None,
                "sol": None,
                "_extras": {"runner": ""}
            }
    
    return results

def print_schedule(result):
    """Helper function to print the schedule table"""
    if result and result.get('sol'):
        sol = result['sol']
        periods = len(sol)
        weeks = len(sol[0]) if sol else 0
        
        print(f"{'Period':<8}", end="")
        for w in range(1, weeks + 1):
            print(f"Week {w:<10}", end="")
        print()
        print("-" * (8 + weeks * 10))
        
        for pr in range(periods):
            print(f"P{pr+1:<7}", end="")
            for w in range(weeks):
                home_team, away_team = sol[pr][w]
                print(f"{home_team}v{away_team:<9}", end="")
            print()
    else:
        print("No solution found!")

# Example usage
if __name__ == "__main__":
    n = 16  # Number of teams (must be even)
    results = create_milp_model(n, timeout=30)
    
    # Print results for each solver
    for solver_name, result in results.items():
        print(f"\n=== {solver_name} SOLVER ===")
        if result['optimal']:
            print(f"Solved in {result['time']:.2f}s, Objective: {result['obj']}")
            print_schedule(result)
        else:
            print(f"No solution found in {result['time']:.2f}s")