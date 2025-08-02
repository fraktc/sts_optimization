# Current Milp Model for STS Optimization

from pulp import *
from timeit import default_timer as timer

def create_milp_model(number_of_teams, timeout=300):
    n = number_of_teams  # Number of teams

    teams = range(n)
    weeks = range(n - 1)
    periods = range(n // 2)

    # Define solvers with timeout parameter
    solvers = {
        "CBC": PULP_CBC_CMD(timeLimit=timeout, msg=False),
        "HiGHS": PULP_CBC_CMD(timeLimit=timeout, msg=False)  # You can use HiGHS_CMD if installed
    }

    # Round robin
    week_matchups = []
    for w in weeks:
        current_week_games = []
        current_week_games.append(tuple(sorted([n - 1, w])))
        for p in range(1, n // 2):
            team1 = (p + w) % (n - 1)
            team2 = (n - p + w - 1) % (n - 1)
            current_week_games.append(tuple(sorted([team1, team2])))
        week_matchups.append(current_week_games)

    final_results = {}

    for solver_name, solver in solvers.items():
        # Define the problem
        prob = LpProblem(f"STS_problem_{solver_name}", LpMinimize)

        # Decision variables
        period_assign = LpVariable.dicts(
            "PeriodAssignment", ((w, p, g) for w in weeks for p in periods for g in periods), cat="Binary"
        )
        home_away_assign = LpVariable.dicts(
            "HomeAwayAssignment", ((w, p) for w in weeks for p in periods), cat="Binary"
        )
        team_home_games = LpVariable.dicts(
            "HomeGamesCount", teams, lowBound=0, upBound=n - 1, cat="Integer"
        )
        team_play_period = LpVariable.dicts(
            "TeamPlayerPeriod", ((t, w, p) for t in teams for w in weeks for p in periods), cat="Binary"
        )

        # Constraints

        # Each period is assigned one game per week
        for w in weeks:
            for p in periods:
                prob += lpSum([period_assign[(w, p, g)] for g in periods]) == 1

        # Each game is assigned to one period
        for w in weeks:
            for g in periods:
                prob += lpSum([period_assign[(w, p, g)] for p in periods]) == 1

        # Link team_play_period to period_assign and week_matchups
        for t in teams:
            for w in weeks:
                for p in periods:
                    # team t plays in week w, period p if it plays in a game assigned to p
                    prob += team_play_period[(t, w, p)] == lpSum([
                        period_assign[(w, p, g)]
                        for g in periods
                        if t in week_matchups[w][g]
                    ])

        # Each team plays at most twice in the same period
        for t in teams:
            for p_scheduled in periods:
                prob += lpSum([team_play_period[(t, w, p_scheduled)] for w in weeks]) <= 2

        # Objective variable
        max_imbalance = LpVariable("MaxImbalance", lowBound=1, upBound=n - 1, cat="Integer")
        prob += max_imbalance

        # Home game assignment and imbalance constraint
        for t in teams:
            prob += team_home_games[t] == lpSum([
                (1 - home_away_assign[(w, p)])
                for w in weeks for p in periods
                if week_matchups[w][p][0] == t
            ]) + lpSum([
                home_away_assign[(w, p)]
                for w in weeks for p in periods
                if week_matchups[w][p][1] == t
            ])
            prob += max_imbalance >= 2 * team_home_games[t] - (n - 1)
            prob += max_imbalance >= -(2 * team_home_games[t] - (n - 1))

        # Solve
        start = timer()
        prob.solve(solver)
        end = timer()

        result = {
            "time": end - start,
            "optimal": LpStatus[prob.status] == "Optimal",
            "obj": value(prob.objective) if prob.status == LpStatusOptimal else None,
            "sol": []
        }

        if result["optimal"]:
            for w in weeks:
                week_solution = []
                for p in periods:
                    for g in periods:
                        if value(period_assign[(w, p, g)]) == 1:
                            match = week_matchups[w][g]
                            if value(home_away_assign[(w, p)]) == 0:
                                week_solution.append([match[0], match[1]])  # match[0] is home
                            else:
                                week_solution.append([match[1], match[0]])  # match[1] is home
                result["sol"].append(week_solution)

        final_results[solver_name] = result

    return final_results


# Example call
if __name__ == "__main__":
    output = create_milp_model(6)
    for solver, res in output.items():
        print(f"\n=== Solver: {solver} ===")
        print(f"Optimal: {res['optimal']}")
        print(f"Objective value: {res['obj']}")
        print(f"Time taken: {res['time']:.2f}s")
        print("Schedule:")
        for week_idx, week in enumerate(res["sol"]):
            print(f"  Week {week_idx + 1}: {week}")
