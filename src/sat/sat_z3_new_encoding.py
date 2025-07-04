### This works bad compared to set_optimization.py but may give good results with incremental SAT #################



import time
from z3 import *

def solve_sports_tournament(n, timeout):
    """
    Solve Sports Tournament Scheduling problem using Z3
    
    Args:
        n: Number of teams (must be even)
        timeout: Time limit in seconds
    
    Returns:
        Solution dictionary or None if no solution exists
    """
    if n % 2 != 0:
        raise ValueError("Number of teams must be even")
    
    # Create Z3 solver
    solver = Solver()

    start_time = time.time()
    
    # Parameters
    teams = list(range(1, n + 1))
    weeks = list(range(1, n))  # n-1 weeks
    periods = list(range(1, n//2 + 1))  # n/2 periods
    slots = [1, 2]  # home and away


                                                # For each period, week, slot — explicitly track who plays against whom:
                                                        
                                                # 	Define a Boolean variable: Y[p][w][t1][t2] = True if team t1 plays against t2 in period p, week w

    Y = {}
    for p in periods:
        Y[p] = {}
        for w in weeks:
            Y[p][w] = {}
            for t1 in teams:
                Y[p][w][t1] = {}
                for t2 in teams:
                    Y[p][w][t1][t2] = Bool(f"Y_p{p}_w{w}_t1{t1}_t2{t2}")   # Total variable count: n**4 - n**3




    # CONSTRAINTS
    # 1) Each slot has exactly one match
    # for p in periods:
    #     for w in weeks:
    #         for s in slots:
    #             solver.add(PbEq([(X[p][w][s][t], 1) for t in teams], 1))
    for p in periods:
        for w in weeks:
            solver.add(PbEq([(Y[p][w][t1][t2], 1) for t1 in teams for t2 in teams], 1))
            

    # # 2) Each team appears exactly once per week across all periods and slots
    # for t in teams:
    #     for w in weeks:
    #         solver.add(PbEq([(X[p][w][s][t], 1)
    #                     for p in periods for s in slots], 1))

    for t in teams:
        for w in weeks:
            solver.add(
                PbEq(
                    [(Y[p][w][t][t1], 1) for p in periods for t1 in teams if t1 != t] +
                    [(Y[p][w][t1][t], 1) for p in periods for t1 in teams if t1 != t],
                    1
                )
            )


    # 3) No team appears more than twice in any period (n/2 weeks) across both slots
    # for t in teams:
    #     for p in periods:
    #         solver.add(PbLe([(X[p][w][s][t], 1)
    #                     for w in weeks for s in slots], 2))
    for t in teams:
        for p in periods:
            solver.add(
                PbLe(
                    [(Y[p][w][t][t1], 1) for w in weeks for t1 in teams if t1 != t] +
                    [(Y[p][w][t1][t], 1) for w in weeks for t1 in teams if t1 != t],
                    2
                )
            )
            
    

    # # 4) No team plays against itself: disallow same t in both slots of same match
    # for p in periods:
    #     for w in weeks:
    #         for t in teams:
    #             solver.add(Not(And(X[p][w][1][t], X[p][w][2][t])))

    for p in periods:
        for w in weeks:
            for t in teams:
                solver.add(Not(Y[p][w][t][t]))


    # # 5) Each pair of teams meets exactly once (regardless of home/away)
    # for t1 in teams:
    #     for t2 in teams:
    #         if t1 < t2:
    #             meets = []
    #             for p in periods:
    #                 for w in weeks:
    #                     meets.append(Or(And(X[p][w][1][t1], X[p][w][2][t2]),
    #                                     And(X[p][w][1][t2], X[p][w][2][t1])))
    #             solver.add(PbEq([(cond, 1) for cond in meets], 1))

    for t1 in teams:
        for t2 in teams:
            if t1 < t2:
                meets = []
                for p in periods:
                    for w in weeks:
                        meets.append(Or(
                            (Y[p][w][t1][t2]),
                            (Y[p][w][t2][t1]))
                        )
                solver.add(PbEq([(cond, 1) for cond in meets], 1))

    # # 6) Symmetry breaking: fix first week's home teams to 1..n/2   
    # for p in periods:
    #     solver.add(X[p][1][1][p])

    # # 6.1) Symmetry breaking: fix first period's home teams to 1..n-1
    # for w in weeks:
    #     solver.add(X[1][w][1][w])   

    for w in weeks:
        if w <= n//2: 
            solver.add(Y[1][w][w][n + 1 - w])  # Team w plays home in week w of period 1 and team n + 1 - w plays away uptill n//2 weeks


                                 #############   DIDNT WORK  ######################

    # # 6.2) Symmetry breaking: fix first period's away teams to n..2
    # for w in weeks:
    #     solver.add(X[1][w][2][n + 1 - w])


    # 7) Lexicographic ordering of home teams across consecutive weeks
    def lex_order(vars1, vars2):
        clauses = []
        for i in range(len(vars1)):
            prefix = [vars1[j] == vars2[j] for j in range(i)]
            clauses.append(Implies(And(prefix), vars1[i] < vars2[i]))
        return Or(clauses)

    for w in range(1, len(weeks)):
        # home_w = [If(X[p][weeks[w-1]][1][t], t, 0) for p in periods for t in teams]
        home_w = [If(Y[p][weeks[w-1]][t1][t2], t1, 0) for p in periods for t1 in teams for t2 in teams if t1!=t2]
        home_w1 = [If(Y[p][weeks[w]][t1][t2], t1, 0) for p in periods for t1 in teams for t2 in teams if t1!=t2]
        solver.add(lex_order(home_w, home_w1))


    # # Apply lexicographic ordering constraint
    # for w in range(1, len(weeks)):
    #     home_w  = [Sum([If(Y[p][weeks[w-1]][t1][t2], t1, 0) for t1 in teams for t2 in teams if t1 != t2]) for p in periods]
    #     home_w1 = [Sum([If(Y[p][weeks[w]][t1][t2], t1, 0) for t1 in teams for t2 in teams if t1 != t2]) for p in periods]
    #     solver.add(lex_order(home_w, home_w1))

            
            #############   DIDNT WORK  ######################

    # # 7.1) Lexicographic ordering of home teams across consecutive periods
    # for p in range(1, len(periods)):   
    #     home_p = [If(X[periods[p-1]][w][1][t], t, 0) for w in weeks for t in teams]
    #     home_p1 = [If(X[periods[p]][w][1][t], t, 0) for w in weeks for t in teams]
    #     solver.add(lex_order(home_p, home_p1))

    
   

                         #############   DIDNT WORK  ######################
    # 8.1) Lets pick first team and fix its schedule completely. So say first period, first week, first slot is team 1,
    # and for 1st period, last week, second slot is team 1. Similar for second period, second week, first slot is
    # team 1, and for second period, second last week, second slot is team 1. and so on.  So the 
        # Pattern: For each period p:
        # - Week p: team 1 in slot 1 (home)
        # - Week (n-p): team 1 in slot 2 (away)
    # For each fixed slot for team 1 we can also fix its opponent. So for period p, week p, team 1 plays home, and team n plays away.
    
    # for p in periods:
    #         solver.add(X[p][p][1][1])  # Team 1 plays in slot 1 first time it plays in period p, week p
    #         # solver.add(X[p][p][2][n-(2*p-2)])  # Team 1 plays against team n-2*(p-1) in period p, week p
    #         if p!=n//2: # We can skip the last period as we dont want to overwrite
    #             solver.add(X[p][n-p][2][1])  # Team 1 plays in slot 2 second time it plays in period p, week n-p
    #             # solver.add(X[p][n-p][1][n-(2*p-1)]) # Team 1 plays against team n-2*(p-1) in period p, week n-p




    # Imbalance minimization: difference between home and away counts
    # Compute home and away counts via sums of Bool
    # TO-DO: NEED TO CHECK IF WE CAN USE Int FOR MAXIMIZATION PURPOSE

    imbalance_vars = []
    for t in teams:
        # Count home games for team t
        home_count = Sum([
            If(Y[p][w][t][t2], 1, 0)
            for p in periods for w in weeks for t2 in teams if t != t2
        ])

        # Count away games for team t
        away_count = Sum([
            If(Y[p][w][t2][t], 1, 0)
            for p in periods for w in weeks for t2 in teams if t != t2
        ])

        # Absolute difference between home and away counts
        diff = home_count - away_count
        abs_diff = Int(f"imb_t{t}")
        solver.add(abs_diff >= diff, abs_diff >= -diff)
        imbalance_vars.append(abs_diff)


    max_imb = Int('max_imbalance')
    solver.add([max_imb >= im for im in imbalance_vars])
    
    # Solve with optimization
    best_imbalance = None
    best_model = None
    optimality = False
    # print("Starting to solve the sports tournament scheduling problem...")
    while True:
        if best_imbalance is not None:
            solver.add(max_imb < best_imbalance)
        
        # print("Checking for a solution with current constraints...")
        remaining_time = timeout - (time.time() - start_time)
        if remaining_time <= 0:
            break

        solver.set("timeout", int(remaining_time * 1000))  # Set timeout in milliseconds

        if solver.check() == sat:
            best_model = solver.model()
            best_imbalance = best_model.evaluate(max_imb).as_long()
            print(f"Found solution with max imbalance: {best_imbalance}")
            print(f"found solution in time: {time.time() - start_time:.2f} seconds")
            if best_imbalance == 1:
                break
            # break   # Temporarily break to extract solution
        else:
            # If no more solution, we found the best one
            optimality = True
            break
        
    # print("Finished solving the sports tournament scheduling problem.")
    if best_model is None:
        return None
    
    # Extract solution


    solution = {
        "solution": [],
        "max_imbalance": best_imbalance,
        "optimality": optimality
    }

        # Extract the solution from the boolean variables
    for w in weeks:
        week_matches = []
        for p in periods:
            home_team = None
            away_team = None
            for t1 in teams:
                for t2 in teams:
                    if best_model.evaluate(Y[p][w][t1][t2]):
                        home_team = t1
                        away_team = t2

            # Add the match to the week's matches
            if home_team is not None and away_team is not None:
                week_matches.append((home_team, away_team))
        
        # Add the week's matches to the solution
        solution["solution"].append(week_matches)
    # print("Solution extracted successfully")
    return solution


if __name__ == "__main__":
    n = 10  # Number of teams (must be even)
    timeout = 300  # Timeout in seconds
    try:
        solution = solve_sports_tournament(n, timeout)
        if solution:
            print("Solution found:")
            for week in solution["solution"]:
                print(week)
            print(f"Max imbalance: {solution['max_imbalance']}")
        else:
            print("No solution found within the given timeout.")
    except Exception as e:
        print(f"Error: {e}")