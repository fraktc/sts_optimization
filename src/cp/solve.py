from .minizinc_utils import minizincSolve, parseInstanceForMinizinc
import pathlib
import os
import math
import time
import logging
logger = logging.getLogger(__name__)



def _solutionExtractorFromForwardPath(variables):
    solution = variables["matches"]
    return solution


def _solutionExtractorFromForwardPathRoundRobin(variable):
    rr_home, rr_away, period_slot = variable["rr_home"], variable["rr_away"], variable["period_slot"]
    periods = variable["periods"]
    weeks = variable["weeks"]

    # rr_home, rr_away and period_slot have shape [weeks * periods]

    # Reshape  rr_home, rr_away and period_slot to be [weeks, periods]
    rr_home = [[rr_home[w * periods + p] for p in range(periods)] for w in range(weeks)]
    rr_away = [[rr_away[w * periods + p] for p in range(periods)] for w in range(weeks)]
    period_slot = [[period_slot[w * periods + p] for p in range(periods)] for w in range(weeks)]

    # Convert the solution to the matches format
    matches = []
    for p in range(periods):
        m = []
        for w in range(weeks):
            m.append([rr_home[w][period_slot[w][p] - 1], rr_away[w][period_slot[w][p] - 1]])
        matches.append(m)

    return matches

experiments_chuffed = [
    {
        "name": "RR_CP_plain_chuffed",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/round_robin_plain.mzn"),
        "solver": "chuffed",
        "solution_extractor_fn": _solutionExtractorFromForwardPathRoundRobin,
        "preprocessing": [],
        "free_search": False
    },
    # {
    #     "name": "RR_CP_impl_chuffed",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/round_robin_impl.mzn"),
    #     "solver": "chuffed",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPathRoundRobin,
    #     "preprocessing": [],
    #     "free_search": False
    # },
    # {
    #     "name": "RR_CP_symm_chuffed",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/round_robin_symm.mzn"),
    #     "solver": "chuffed",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPathRoundRobin,
    #     "preprocessing": [],
    #     "free_search": False
    # },
    # {
    #     "name": "RR_CP_full_chuffed",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/round_robin_full.mzn"),
    #     "solver": "chuffed",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPathRoundRobin,
    #     "preprocessing": [],
    #     "free_search": False
    # },
]

experiments_gecode = [
    {
        "name": "RR_CP_plain_gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/round_robin_plain.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPathRoundRobin,
        "preprocessing": [],
        "free_search": False
    },
    # {
    #     "name": "RR_CP_impl_gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/round_robin_impl.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPathRoundRobin,
    #     "preprocessing": [],
    #     "free_search": False
    # },
    # {
    #     "name": "RR_CP_symm_gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/round_robin_symm.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPathRoundRobin,
    #     "preprocessing": [],
    #     "free_search": False
    # },
    # {
    #     "name": "RR_CP_full_gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/round_robin_full.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPathRoundRobin,
    #     "preprocessing": [],
    #     "free_search": False
    # },
]


experiments_setup = experiments_chuffed + experiments_gecode

def solve(instance, timeout, cache={}, random_seed=42, models_filter=None, **kwargs):
    instance_path = os.path.join(pathlib.Path(__file__).parent.resolve(), ".instance.dzn")
    out_results = {}

    for experiment in experiments_setup:
        if (models_filter is not None) and (experiment["name"] not in models_filter):
            continue
        logger.info(f"Starting model {experiment['name']} with {experiment['solver']}")

        # Check if result is in cache
        if experiment["name"] in cache:
            logger.info(f"Cache hit")
            out_results[experiment["name"]] = cache[experiment["name"]]
            continue

        dzn_content = f"n = {instance};\n"
        start_time = time.time()

        # Create instance input file
        with open(instance_path, "w") as f:
            f.write(dzn_content)
        preprocess_time = time.time() - start_time
        
        # Solve instance
        outcome, solutions, statistics = minizincSolve(
            model_path = experiment["model_path"],
            data_path = instance_path,
            solver = experiment["solver"],
            timeout_ms = math.floor(timeout - preprocess_time)*1000,
            seed = random_seed,
            free_search = experiment["free_search"]
        )
        solve_time = time.time() - start_time


        if (outcome["mz_status"] is None) and (len(solutions) > 0):
            # Solver crashed before finishing but there are intermediate solutions.
            # Consider as if it timed out.
            outcome["mz_status"] = "UNKNOWN"

        # Parse results
        if (outcome["mz_status"] is None) or (len(solutions) == 0):
            if outcome['crash_reason'] is not None:
                logger.warning(f"Instance crashed. Reason: {outcome['crash_reason']}")
            overall_time = timeout
            optimality = False
            objective = None
            solution = None
            crash_reason = outcome["crash_reason"]
        else:
            overall_time = math.floor(solve_time)
            objective = solutions[-1]["variables"]["max_imbalance"]
            optimality = objective == 1
            solution = experiment["solution_extractor_fn"](solutions[-1]["variables"])
            crash_reason = outcome["crash_reason"]

        out_results[experiment["name"]] = {
            "time": overall_time,
            "optimal": optimality,
            "obj": objective,
            "sol": solution,
            "_extras": {
                "statistics": statistics,
                "crash_reason": crash_reason,
                "time_to_last_solution": None if len(solutions) == 0 else (preprocess_time + solutions[-1]["time_ms"]/1000)
            }
        }
        os.remove(instance_path)

    return out_results