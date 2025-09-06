import os
import re
import sys
import json
from itertools import combinations


TIMEOUT = 300

OPTIMAL_STR = "optimal"
SUBOPTIMAL_STR = "suboptimal"
INCONSISTENT_STR = "inconsistent"
TIMEOUT_STR = "timeout"
OUT_OF_MEMORY_STR = "out-of-memory"
CRASHED_STR = "crashed"


def read_json_file(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Unable to parse JSON from file '{file_path}'.")
        return None


def didTimeout(result):
    return (result["time"] >= TIMEOUT) and (result["sol"] is None)


def isOutOfMemory(result):
    if ("_extras" in result) and ("crash_reason" in result["_extras"]):
        return (result["_extras"]["crash_reason"] == "out-of-memory") and (result["sol"] is None)
    return False


def didCrash(result):
    if ("_extras" in result) and ("crash_reason" in result["_extras"]):
        return (result["_extras"]["crash_reason"] != None) and (result["sol"] is None)
    return False


def isInconsistent(result):
    if "sol" not in result or not result["sol"] or result["sol"] == "N/A":
        return True

    solution = result["sol"]

    res, errors = check_solution(solution)

    if not res:
        return True
    else:
        return False

def get_elements(solution, list_condition_funct, n=None):
    elements = []
    if list_condition_funct(solution, n):
        elements += solution
    else:
        for sol in solution:
            elements += get_elements(sol, list_condition_funct, n)
    return elements


def get_teams(solution):
    return get_elements(solution, lambda s,n: all([type(i) == int for i in s]))


def get_periods(solution, n):
    return get_elements(solution, lambda s,n: all([type(i) == list and len(i) == n for i in s]), n)


def get_matches(solution):
    return get_elements(solution, lambda s,n: all([type(i) == list and len(i) == 2 and all([type(ii) == int for ii in i]) for i in s]))


def get_weeks(periods, n):
    return [[p[i] for p in periods] for i in range(n-1)]


def fatal_errors(solution):
    fatal_errors = []

    if len(solution) == 0:
        fatal_errors.append('The solution cannot be empty')
        return fatal_errors

    teams = get_teams(solution)
    n = max(teams)

    if any([t not in set(teams) for t in range(1,n+1)]):
        fatal_errors.append(f'Missing team in the solution or team out of range!!!')

    if n%2 != 0:
        fatal_errors.append(f'"n" should be even!!!')

    if len(solution) != n//2:
        fatal_errors.append(f'the number of periods is not compliant!!!')

    if any([len(s) != n - 1 for s in solution]):
        fatal_errors.append(f'the number of weeks is not compliant!!!')


    return fatal_errors


def check_solution(solution: list):

    errors = fatal_errors(solution)

    if len(errors) == 0:

        teams = get_teams(solution)
        n = max(teams)

        teams_matches = combinations(set(teams),2)
        solution_matches = get_matches(solution)

        # every team plays with every other teams only once
        if any([solution_matches.count([h,a]) + solution_matches.count([a,h]) > 1 for h,a in teams_matches]):
            errors.append('There are duplicated matches!!!')

        # each team cannot play against itself
        if any([h==a for h,a in solution_matches]):
            errors.append('There are self-playing teams')

        periods = get_periods(solution, n - 1)
        weeks = get_weeks(periods, n)

        # every team plays once a week
        teams_per_week = [get_teams(i) for i in weeks]
        if any([len(tw) != len(set(tw)) for tw in teams_per_week]):
            errors.append('Some teams play multiple times in a week')

        teams_per_period = [get_teams(p) for p in periods]

        # every team plays at most twice during the period
        if any([teams_per_period.count(tp) > 2 for tp in teams_per_period]):
            errors.append('Some teams play more than twice in the period')
    
    return (True, None) if len(errors) == 0 else (False, errors)

def isSuboptimal(result):
    return (not result["optimal"]) and (result["sol"] is not None)


def isOptimal(result):
    return (result["optimal"]) and (result["sol"] is not None)



def main(args):
    """
    check_solution.py <results folder>
    """
    # errors = []
    # warnings = []

    instances_status = {}

    results_folder = args[1]
    for subfolder in os.listdir(results_folder):
        if subfolder.startswith("."):
            # Skip hidden folders.
            continue
        folder = os.path.join(results_folder, subfolder)

        instances_status[subfolder] = {}

        for instance in [4,6,8,10,12,14,16,18,20]:
            instances_status[subfolder][instance] = {}


        # print(f"\nChecking results in {folder} folder")
        for results_file in sorted(os.listdir(folder)):
            if results_file.startswith("."):
                # Skip hidden folders.
                continue
            results = read_json_file(folder + "/" + results_file)
            # print(f"\tChecking results for instance {results_file}")
            inst_number = re.search(r"\d+", results_file).group()


            inst_number_int = int(inst_number)
            instances_status[subfolder][inst_number_int] = {}

            for solver, result in results.items():
                if isOutOfMemory(result):
                    instances_status[subfolder][inst_number_int][solver] = {
                        "status": OUT_OF_MEMORY_STR,
                        "time": -1,
                        "obj": 2**31-1
                    }
                elif didCrash(result):
                    instances_status[subfolder][inst_number_int][solver] = {
                        "status": CRASHED_STR,
                        "time": -1,
                        "obj": 2**31-1
                    }
                elif didTimeout(result):
                    instances_status[subfolder][inst_number_int][solver] = {
                        "status": TIMEOUT_STR,
                        "time": -1,
                        "obj": 2**31-1
                    }
                elif isInconsistent(result):
                    instances_status[subfolder][inst_number_int][solver] = {
                        "status": INCONSISTENT_STR,
                        "time": -1,
                        "obj": 2**31-1
                    }
                elif isSuboptimal(result):
                    instances_status[subfolder][inst_number_int][solver] = {
                        "status": SUBOPTIMAL_STR,
                        "time": result["time"],
                        "obj": result["obj"]
                    }
                elif isOptimal(result):
                    instances_status[subfolder][inst_number_int][solver] = {
                        "status": OPTIMAL_STR,
                        "time": result["time"],
                        "obj": result["obj"]
                    }
                else:
                    raise Exception("Case not handled")

    print(json.dumps(instances_status, indent=4))


if __name__ == "__main__":
    main(sys.argv)