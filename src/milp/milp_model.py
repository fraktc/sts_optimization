# We start by copying the code from SAT file to create a MILP model.

from pulp import *

def create_milp_model(number_of_teams):
    n  = number_of_teams
    teams = range(1, n + 1)
    weeks = range(1,n)
    periods = range(1, n//2 +1)
    slots = [1,2]



    # Create the MILP model
    prob = LpProblem("Sports_Tournament", LpMinimize)

    # Decision variables
    X = LpVariable.dicts("x", (periods, weeks, slots, teams), cat=LpBinary)
    M = LpVariable.dicts("Match", (periods, weeks, teams, teams), 0, 1, cat="Binary")

    # imbalance = LpVariable.dicts("imbalance", teams, cat=LpInteger)
    # max_imb = LpVariable("max_imbalance", cat=LpInteger)


    # 1. Each slot has exaclty one team 
    for p in periods:
        for w in weeks:
            for s in slots:
                prob += lpSum(X[p][w][s][t] for t in teams) == 1



    # 2. Each team appears once per week
    for t in teams:
        for w in weeks:
            prob += lpSum(X[p][w][s][t] for p in periods for s in slots) == 1


    # 3. No team more than twice in any period
    for p in periods:
        for t in teams:
            prob += lpSum(X[p][w][s][t] for w in weeks for s in slots) <= 2
    
    # 4. No self matches i.e no team plays against itself
    for t in teams:
        for p in periods:
            for w in weeks:
                    prob += lpSum(X[p][w][s][t] for s in slots) <= 1

    # 5. Each pair meets exactly once

         # Add linearization constraints:
    for p in periods:
        for w in weeks:
            for t1 in teams:
                for t2 in teams:
                    if t1 != t2:
                        prob += M[p][w][t1][t2] <= X[p][w][1][t1]
                        prob += M[p][w][t1][t2] <= X[p][w][2][t2]
                        prob += M[p][w][t1][t2] >= X[p][w][1][t1] + X[p][w][2][t2] - 1
        
         # Add final constraint: each pair meets once
    for t1 in teams:
        for t2 in teams:
            if t1 < t2:
                prob += lpSum(M[p][w][t1][t2] + M[p][w][t2][t1] for p in periods for w in weeks) == 1




    # 6. Symmetry breaking: Fix first period's home teams to 1..n-1
    for w in weeks:
            prob += (X[1][w][1][w] == 1)

    # 7. Lexicographic ordering of home teams, for each period
    for p in periods:
        for w in weeks:
            for s in slots:
                prob += lpSum(X[p][w][s][t] * t for t in teams) <= lpSum(X[p][w][s][t+1] * (t+1) for t in teams if t < n)
        



    # 8. Balance the number of home and away games for each team
   

    prob.solve()


    print("Decision Variables:")
    for v in prob.variables():
        print(f"{v.name} = {v.varValue}")


if __name__ == "__main__":    # Imbalance variables

    number_of_teams = 10  # Example number of teams
    create_milp_model(number_of_teams)