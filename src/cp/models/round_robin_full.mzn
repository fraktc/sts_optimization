include "globals.mzn";

% ===========================
% PARAMETERS
% ===========================
int: n; % even number of teams
set of int: TEAMS = 1..n;
int: weeks = n - 1;
int: periods = n div 2;

% ===========================
% ROUND-ROBIN SCHEDULE
%
% Balanced Round-Robin schedule made using the circle method
% and the parity rule to balance home and away matches.
% ===========================
array[1..weeks, 1..periods] of int: rr_home =
  array2d(1..weeks, 1..periods,
    [ let {
        int: a = if p == 1 then 1 
                 else ((p + w - 2) mod (n - 1)) + 2 
                 endif;
        int: b = if p == 1 then ((n - 1 + w - 1) mod (n - 1)) + 2 
                 else ((n - p + 1 + w - 2) mod (n - 1)) + 2 
                 endif;
        int: i = min(a, b);
        int: j = max(a, b);
      } in
      if (i + j) mod 2 == 0 then i else j endif
    | w in 1..weeks, p in 1..periods ]
  );

array[1..weeks, 1..periods] of int: rr_away =
  array2d(1..weeks, 1..periods,
    [ let {
        int: a = if p == 1 then 1 
                 else ((p + w - 2) mod (n - 1)) + 2 
                 endif;
        int: b = if p == 1 then ((n - 1 + w - 1) mod (n - 1)) + 2 
                 else ((n - p + 1 + w - 2) mod (n - 1)) + 2 
                 endif;
        int: i = min(a, b);
        int: j = max(a, b);
      } in
      if (i + j) mod 2 == 0 then j else i endif
    | w in 1..weeks, p in 1..periods ]
  );


% ===========================
% DECISION VARIABLES
%
% period_slot: used to compute a permutation of matches in each week
% team_period: auxiliary variable to count, for each team and week, in which period the team plays
% ===========================

array[1..weeks, 1..periods] of var 1..periods: period_slot;
array[TEAMS, 1..weeks] of var 1..periods: team_period;


% Make sure that period_slot is a valid permutation of matches
constraint
    forall(w in 1..weeks) (
        all_different([period_slot[w,p] | p in 1..periods])
    );


% Link team_period to period_slot using fixed round-robin data
constraint
    forall(t in TEAMS, w in 1..weeks) (
        team_period[t,w] = 
            sum(p in 1..periods) (
                period_slot[w,p] * 
                bool2int(rr_home[w,p] == t \/ rr_away[w,p] == t)
            )
    );

% ===============================
% TEAM PERIOD CONSTRAINT
% Each team plays in any period at most twice
% ===============================
constraint
    forall(t in TEAMS, pr in 1..periods) (
        sum(w in 1..weeks) (bool2int(team_period[t,w] == pr)) <= 2
    );



% ===============================
% IMPLIED CONSTRAINTS
%
% teams_count_per_period: count of teams playing in each period
% ===============================

array[TEAMS, 1..periods] of var 1..2: teams_count_per_period;

% Link team_period to teams_count_per_period
constraint
    forall(t in TEAMS, pr in 1..periods) (
        sum(w in 1..weeks) (bool2int(team_period[t,w] == pr)) == teams_count_per_period[t, pr]
    );

% The number of teams playing just one match in a period are exactly 2
constraint
    forall(pr in 1..periods) (
      sum(t in TEAMS) (bool2int(teams_count_per_period[t,pr] == 1)) == 2
    );

% Each team plays only one match in exactly one period
constraint
    forall(t in TEAMS) (
      sum(pr in 1..periods) (bool2int(teams_count_per_period[t,pr] == 1)) == 1
    );



% ============================
% SYMMETRY BREAKING
% ============================

% Break symmetry by fixing first week's period assignment
constraint forall(p in 1..periods) (
  period_slot[1, p] = p
);


% =================================
% IMBALANCE COUNTING
% =================================
% Count of home matches for each team
array[TEAMS] of var 0..weeks: home_count = 
    [ sum(w in 1..weeks, p in 1..periods) (bool2int(rr_home[w,p] == t)) | t in TEAMS ];

% Count of away matches for each team
array[TEAMS] of var 0..weeks: away_count = 
    [ sum(w in 1..weeks, p in 1..periods) (bool2int(rr_away[w,p] == t)) | t in TEAMS ];

% Absolute difference between home and away games for each team
array[TEAMS] of var 0..weeks: imbalance =
    [ abs(home_count[t] - away_count[t]) | t in TEAMS ];

var 0..weeks: max_imbalance = max(t in TEAMS)(imbalance[t]);

solve satisfy;

output [
  "{",
  "\"rr_home\":", show(rr_home), ",\n",
  "\"rr_away\":", show(rr_away), ",\n",
  "\"period_slot\":", show(period_slot), ",\n",
  "\"team_period\":", show(team_period), ",\n",
  "\"periods\":", show(periods), ",\n",
  "\"weeks\":", show(weeks), ",\n",
  "\"max_imbalance\":", show(max_imbalance),
  "}"
];