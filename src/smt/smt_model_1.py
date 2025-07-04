from z3 import *


def lex_less(vec1, vec2):
    """
    Lexicographic less-than: vec1 <lex vec2
    Returns True if vec1 is lexicographically strictly less than vec2
    """
    n = len(vec1)
    assert len(vec2) == n, "Vectors must have same length"

    conditions = []

    # For each position i: prefix equal AND current position less
    for i in range(n):
        prefix_equal = And([vec1[j] == vec2[j] for j in range(i)])
        current_less = vec1[i] < vec2[i]

        if i == 0:
            conditions.append(current_less)
        else:
            conditions.append(And(prefix_equal, current_less))

    return Or(conditions)

n = 6
teams = 2 * n
weeks = teams - 1
periods = n
slots = 2

solver = Solver()

matches = [[[Int(f"match_{w + 1}_{p + 1}_{s + 1}") for s in range(slots)] for p in range(periods)] for w in range(weeks)]

# Domain definition
for w in range(weeks):
    for p in range(periods):
        for s in range(slots):
            solver.add(1 <= matches[w][p][s], matches[w][p][s] <= teams)


# ---- MAIN CONSTRAINTS ----

# Every team plays once a week
for w in range(weeks):
    solver.add(Distinct([matches[w][p][s] for p in range(periods) for s in range(slots)]))

# Every team plays against every other team
for t1 in range(teams):
    for t2 in range(t1+1, teams):
        match_count = Sum([
            If(Or(
                And(matches[w][p][0] == t1 + 1, matches[w][p][1] == t2 + 1),
                And(matches[w][p][0] == t2 + 1, matches[w][p][1] == t1 + 1)),
            1, 0)
            for w in range(weeks)
            for p in range(periods)
        ])
        solver.add(match_count == 1)

# No team plays against itself
for w in range(weeks):
    for p in range(periods):
        solver.add(matches[w][p][0] != matches[w][p][1])

# No teams shall play more than twice in the same period
for t in range(teams):
    for p in range(periods):
        match_count = Sum([
            If(matches[w][p][s] == t + 1, 1, 0)
            for w in range(weeks)
            for s in range(slots)
        ])
        solver.add(match_count <= 2)

# ---- SYMMETRY BREAKING CONSTRAINTS ----
for p in range(periods):
    solver.add(matches[0][p][0] == p + 1)

for w in range(weeks - 1):
    solver.add(lex_less([matches[w][p][0] for p in range(periods)], [matches[w+1][p][0] for p in range(periods)]))

if solver.check() == sat:
    model = solver.model()

    print("MATCHES:")
    for w in range(weeks):
        print([(model.eval(matches[w][p][0]), model.eval(matches[w][p][1])) for p in range(periods)])
else:
    print("No solution found!")
