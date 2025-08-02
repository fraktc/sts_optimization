% two_phase_sts.mzn - Complete two-phase STS solver in one file
include "globals.mzn";

% Parameters
int: n;
bool: phase1_only = false;  % Set to true for phase 1, false for phase 2
set of int: TEAMS = 1..(n);
set of int: WEEKS = 1..(n-1);
set of int: PERIODS = 1..(n div 2);
set of int: SLOTS = 1..2;

% Decision variables
array [PERIODS, WEEKS, SLOTS] of var TEAMS: matches;

% Optional: Pre-computed pairs from phase 1 (only used in phase 2)
array [PERIODS, WEEKS, 1..2] of var opt TEAMS: fixed_pairs;

% ==== CORE STS CONSTRAINTS (both phases) ====

% Each team plays exactly once per week
constraint forall(w in WEEKS)(
  all_different([matches[p, w, s] | p in PERIODS, s in SLOTS])
);

% Each pair of teams plays exactly once
constraint forall(t1, t2 in TEAMS where t1 < t2)(
  sum(p in PERIODS, w in WEEKS)(
    (matches[p, w, 1] = t1 /\ matches[p, w, 2] = t2) +
    (matches[p, w, 1] = t2 /\ matches[p, w, 2] = t1)
  ) = 1
);

% No team plays against itself
constraint forall(w in WEEKS, p in PERIODS)(
  matches[p, w, 1] != matches[p, w, 2]
);

% Period constraint: each team plays at most 2 times per period
constraint forall(t in TEAMS, p in PERIODS)(
  sum(w in WEEKS, s in SLOTS)(matches[p, w, s] = t) <= 2
);

% ==== SYMMETRY BREAKING ====
constraint matches[1, 1, 1] = 1;  % Team 1 home in period 1, week 1
constraint matches[1, 1, 2] = 2;  % Against team 2
if n >= 6 then
  constraint matches[2, 1, 1] = 3;  % Team 3 home in period 2, week 1
  constraint matches[2, 1, 2] = 4;  % Against team 4
endif;

% ==== PHASE 2 CONSTRAINTS (optimization) ====
array [TEAMS, SLOTS] of var 0..(n-1): match_counter;
var int: max_imbalance;

% Only activate optimization in phase 2
constraint if not phase1_only then
  % Count home/away games
  forall(t in TEAMS, s in SLOTS)(
    match_counter[t, s] = sum(w in WEEKS, p in PERIODS)(matches[p, w, s] = t)
  ) /\
  % Calculate maximum imbalance
  max_imbalance = max(t in TEAMS)(
    abs(match_counter[t, 1] - match_counter[t, 2])
  )
else
  % In phase 1, just set dummy values
  max_imbalance = 0 /\
  forall(t in TEAMS, s in SLOTS)(match_counter[t, s] = 0)
endif;

% ==== SOLVE STATEMENT ====
solve if phase1_only then
  % Phase 1: Find any valid solution quickly
  :: restart_luby(100)
  :: int_search(matches, first_fail, indomain_min, complete)
  satisfy
else
  % Phase 2: Optimize home/away balance
  :: restart_luby(200)
  :: int_search(matches, dom_w_deg, indomain_random, complete)
  minimize max_imbalance
endif;

% ==== OUTPUT ====
output if phase1_only then
  % Phase 1 output: solution for inspection
  ["=== PHASE 1 COMPLETE - Valid Tournament Found ===\n"] ++
  ["Run again with phase1_only=false to optimize\n\n"] ++
  [show(matches)]
else
  % Phase 2 output: optimized solution
  ["=== PHASE 2 COMPLETE - Optimized Solution ===\n"] ++
  ["Max Imbalance: ", show(max_imbalance), "\n"] ++
  ["Home/Away counts per team:\n"] ++
  [if t = 1 then "Team " else "" endif ++
   show(t) ++ ": Home=" ++ show(match_counter[t,1]) ++ 
   " Away=" ++ show(match_counter[t,2]) ++ 
   " Imbalance=" ++ show(abs(match_counter[t,1] - match_counter[t,2])) ++
   if t = n then "\n" else "\n" endif
   | t in TEAMS] ++
  ["\nSchedule:\n"] ++
  [show(matches)]
endif;