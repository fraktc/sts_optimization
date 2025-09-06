include "globals.mzn";

% Parameters
int: n;
set of int: TEAMS = 1..(n);
set of int: WEEKS = 1..(n-1);
set of int: PERIODS = 1..(n div 2);
set of int: SLOTS = 1..2;

% Decision variables
array [PERIODS, WEEKS, SLOTS] of var TEAMS: matches;
array [TEAMS, PERIODS] of var WEEKS: period_counter;
array [TEAMS, SLOTS] of var WEEKS: match_counter;

% Factorization constraints
constraint forall(w in WEEKS)(
  all_different([matches[p, w, s] | p in PERIODS, s in SLOTS])
);

constraint forall(t in TEAMS)(
  all_different(
    [matches[p, w, 1] | w in WEEKS, p in PERIODS where matches[p, w, 2] == t] ++
    [matches[p, w, 2] | w in WEEKS, p in PERIODS where matches[p, w, 1] == t]
  )
);

constraint forall(w in WEEKS, p in PERIODS)(
  matches[p, w, 1] != matches[p, w, 2]
);

constraint forall(t in TEAMS, p in PERIODS)(
  period_counter[t, p] = sum(w in WEEKS, s in SLOTS)(matches[p, w, s] = t)
);

constraint forall(t in TEAMS, p in PERIODS)(
  period_counter[t, p] <= 2
);

% Symmetry breaking
constraint forall(p in PERIODS)(
  matches[p, 1, 1] = p
);

constraint forall(w in 1..(n - 2))(
  lex_less([matches[p, w, 1] | p in PERIODS], [matches[p, w+1, 1] | p in PERIODS])
);

% Imbalance minimization
constraint forall(t in TEAMS, s in SLOTS)(
  match_counter[t,s] = sum(w in WEEKS, p in PERIODS)(matches[p, w, s] = t)
);

var int: max_imbalance = max(t in TEAMS)(
  abs(match_counter[t,1] - match_counter[t,2])
);

constraint max_imbalance >= 1;

% Search strategy
solve :: restart_luby(200) :: int_search(matches, dom_w_deg, indomain_min, complete) minimize max_imbalance;

% Output
% output [
%  "HOME: \n" ++ show2d([ [matches[p, w, 1] | p in PERIODS] | w in WEEKS ]) ++ "\n" ++
%  "AWAY: \n" ++ show2d([ [matches[p, w, 2] | p in PERIODS] | w in WEEKS ]) ++ "\n" ++
%  "MAX_IMBALANCE: \n" ++ show(max_imbalance)
%];