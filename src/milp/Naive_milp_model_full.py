import pulp
import time

def create_milp_model(n, timeout=60):
    """
    Naive MIP model for Sports Tournament Scheduling (STS)
    - Direct assignment of teams to (period, week, slot)
    - Minimize max home-away imbalance
    n: number of teams (even)
    timeout: time limit in seconds
    Returns: dict with results for different solvers
    """
    assert n % 2 == 0, "n must be even"
    weeks = n - 1
    periods = n // 2
    TEAMS = list(range(1, n + 1))
    WEEKS = list(range(1, weeks + 1))
    PERIODS = list(range(1, periods + 1))
    SLOTS = [1, 2]  # 1 = home, 2 = away

    # ===========================
    # MILP MODEL
    # ===========================
    prob = pulp.LpProblem("STS_Naive", pulp.LpMinimize)

    # ---------------------------
    # DECISION VARIABLES
    # ---------------------------

    # x[p, w, s, t] = 1 if team t is assigned to period p, week w, slot s
    x = pulp.LpVariable.dicts("x",
                              [(p, w, s, t) for p in PERIODS for w in WEEKS for s in SLOTS for t in TEAMS],
                              cat='Binary')

    # y[t] = number of home games for team t
    y_home = pulp.LpVariable.dicts("home_count", TEAMS, lowBound=0, cat='Integer')
    y_away = pulp.LpVariable.dicts("away_count", TEAMS, lowBound=0, cat='Integer')

    # z[t] = |home - away| for team t (absolute value, linearized)
    z = pulp.LpVariable.dicts("imbalance", TEAMS, lowBound=0, cat='Integer')

    # Max imbalance (to minimize)
    max_imbalance = pulp.LpVariable("max_imbalance", lowBound=0, cat='Integer')

    # ===========================
    # CONSTRAINTS
    # ===========================

    # 1. Each (period, week, slot) has exactly one team
    for p in PERIODS:
        for w in WEEKS:
            for s in SLOTS:
                prob += pulp.lpSum(x[p, w, s, t] for t in TEAMS) == 1

    # 2. Each team plays exactly once per week
    for t in TEAMS:
        for w in WEEKS:
            prob += pulp.lpSum(x[p, w, s, t] for p in PERIODS for s in SLOTS) == 1

    # 3. No team plays itself: in each (p,w), the two teams are different
    for p in PERIODS:
        for w in WEEKS:
            for t in TEAMS:
                # Cannot have team t in both slots
                prob += x[p, w, 1, t] + x[p, w, 2, t] <= 1

    # 4. Count home and away games per team
    for t in TEAMS:
        prob += y_home[t] == pulp.lpSum(x[p, w, 1, t] for p in PERIODS for w in WEEKS)
        prob += y_away[t] == pulp.lpSum(x[p, w, 2, t] for p in PERIODS for w in WEEKS)

    # 5. Imbalance per team: z[t] >= |home - away|, using linearization
    for t in TEAMS:
        prob += z[t] >= y_home[t] - y_away[t]
        prob += z[t] >= y_away[t] - y_home[t]

    # 6. Max imbalance
    for t in TEAMS:
        prob += max_imbalance >= z[t]

    # 7. Each team plays at most twice in each period
    for t in TEAMS:
        for p in PERIODS:
            prob += pulp.lpSum(x[p, w, s, t] for w in WEEKS for s in SLOTS) <= 2

    # 8. Symmetry breaking: Fix first week
    # Assign team p to home in period p of week 1
    for p in PERIODS:
        # matches[p,1,1] = p  --> home team in period p, week 1 is team p
        prob += x[p, 1, 1, p] == 1
        # Optionally: force away team ≠ p, but already enforced by (3)

    #9. IMPLIED CONSTRAINTS
    # Tighter bound: max times a team can play in any single period
    max_times_per_period = (weeks + periods - 1) // periods  # == ceil(weeks / periods)
    for t in TEAMS:
        for p in PERIODS:
            # Total times team t appears in period p across all weeks
            prob += pulp.lpSum(x[p, w, s, t] for w in WEEKS for s in SLOTS) <= max_times_per_period

    # ===========================
    # OBJECTIVE
    # ===========================
    prob += max_imbalance

    # ===========================
    # SOLVE WITH MULTIPLE SOLVERS
    # ===========================
    solvers = {
        'CBC': pulp.PULP_CBC_CMD(msg=0, timeLimit=timeout),
        'HiGHS': pulp.COIN_CMD(msg=0, timeLimit=timeout) if pulp.COIN_CMD().available() else pulp.PULP_CBC_CMD(msg=0, timeLimit=timeout)
    }

    # Remove HiGHS if not available
    solvers = {k: v for k, v in solvers.items() if v is not None}

    results = {}

    for solver_name, solver in solvers.items():
        start_time = time.time()
        prob.solve(solver)
        solve_time = time.time() - start_time

        if pulp.LpStatus[prob.status] == "Optimal":
            # Extract assignment
            # Build matches: matches[p][w] = [home, away]
            matches = {}
            for p in PERIODS:
                for w in WEEKS:
                    home = None
                    away = None
                    for t in TEAMS:
                        if pulp.value(x[p, w, 1, t]) > 0.5:
                            home = t
                        if pulp.value(x[p, w, 2, t]) > 0.5:
                            away = t
                    matches[p, w] = [home, away]

            # Reconstruct solution in output format: [period][week] = [home, away]
            sol = []
            for p in PERIODS:
                period_weeks = []
                for w in WEEKS:
                    period_weeks.append(matches[p, w])
                sol.append(period_weeks)

            # Compute home/away counts and imbalance
            home_count = {t: 0 for t in TEAMS}
            away_count = {t: 0 for t in TEAMS}
            for p in PERIODS:
                for w in WEEKS:
                    h, a = matches[p, w]
                    home_count[h] += 1
                    away_count[a] += 1
            imbalance = {t: abs(home_count[t] - away_count[t]) for t in TEAMS}
            max_imb = max(imbalance.values())

            results[solver_name] = {
                "time": solve_time,
                "optimal": True,
                "obj": max_imb,
                "sol": sol,
                "_extras": {"runner": "naive_mip"}
            }
        else:
            results[solver_name] = {
                "time": solve_time,
                "optimal": False,
                "obj": None,
                "sol": None,
                "_extras": {"runner": "naive_mip"}
            }

    return results


# ===========================
# Helper: Print Schedule
# ===========================
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


# ===========================
# Example Usage
# ===========================
if __name__ == "__main__":
    n = 10 
    results = create_milp_model(n, timeout=60)

    for solver_name, result in results.items():
        print(f"\n=== {solver_name} SOLVER ===")
        if result['optimal']:
            print(f"Solved in {result['time']:.2f}s, Max Imbalance: {result['obj']}")
            print_schedule(result)
        else:
            print(f"No solution found in {result['time']:.2f}s")