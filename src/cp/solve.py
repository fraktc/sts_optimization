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



experiments_gecode = [
    {
        "name": "plain-gecode",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./gecode/plain.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [],
        "free_search": False
    },
    {
        "name": "plain-gecode-symm",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./gecode/plain_symm.mzn"),
        "solver": "gecode",
        "solution_extractor_fn": _solutionExtractorFromForwardPath,
        "preprocessing": [],
        "free_search": False
    },
    # {
    #     "name": "vrp-luby-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-luby.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns50-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(50) ],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns80-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(80) ],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns90-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(90) ],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns95-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(95) ],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns97-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(97) ],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns99-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(99) ],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns90-symm_amount-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-symm_amount.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(90) ],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns90-symm_packs-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-symm_packs.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(90) ],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns95-symm_amount-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-symm_amount.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(95) ],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns95-symm_packs-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-symm_packs.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(95) ],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns95-symm_amount_strong-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-symm_amount_strong.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(95) ],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns95-symm_packs_strong-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-symm_packs_strong.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(95) ],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-plain-ff-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-plain-ff.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns95-ff-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-ff.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(95) ],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns95-symm_amount-ff-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-symm_amount-ff.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(95) ],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-lns95-symm_packs-ff-gecode",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/gecode/vrp-lns-symm_packs-ff.mzn"),
    #     "solver": "gecode",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [ _setLNSPercentage(95) ],
    #     "free_search": False
    # },
]

experiments_chuffed = [
    # {
    #     "name": "vrp-plain-chuffed",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/chuffed/vrp-plain.mzn"),
    #     "solver": "chuffed",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-plain-fs-chuffed",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/chuffed/vrp-plain.mzn"),
    #     "solver": "chuffed",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [],
    #     "free_search": True
    # },
    # {
    #     "name": "vrp-luby-chuffed",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/chuffed/vrp-luby.mzn"),
    #     "solver": "chuffed",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-symm_amount-chuffed",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/chuffed/vrp-symm_amount.mzn"),
    #     "solver": "chuffed",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [],
    #     "free_search": False
    # },
    # {
    #     "name": "vrp-symm_packs-chuffed",
    #     "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/chuffed/vrp-symm_packs.mzn"),
    #     "solver": "chuffed",
    #     "solution_extractor_fn": _solutionExtractorFromForwardPath,
    #     "preprocessing": [],
    #     "free_search": False
    # },
]
experiments_setup = (
    experiments_gecode +
    experiments_chuffed
)


def solve(instance, timeout, cache={}, random_seed=42, models_filter=None, **kwargs):
    instance_path = os.path.join(pathlib.Path(__file__).parent.resolve(), ".instance.dzn")
    out_results = {}

    return {
        "time": -1,
        "optimal": None,
        "obj": -1,
        "sol": None,
    }

    for experiment in experiments_setup:
        if (models_filter is not None) and (experiment["name"] not in models_filter):
            continue
        logger.info(f"Starting model {experiment['name']} with {experiment['solver']}")

        # Check if result is in cache
        if experiment["name"] in cache:
            logger.info(f"Cache hit")
            out_results[experiment["name"]] = cache[experiment["name"]]
            continue

        # dzn_content = parseInstanceForMinizinc(instance)
        dzn_content = f"n = {instance};\n"
        start_time = time.time()

        # Create instance input file
        # if len(experiment["preprocessing"]) > 0:
        #     for prepro_fn in experiment["preprocessing"]:
        #         dzn_content += prepro_fn(experiment, instance, random_seed)
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
            overall_time = timeout if outcome["mz_status"] in ["UNKNOWN", "SATISFIED"] else math.floor(solve_time)
            optimality = outcome["mz_status"] == "OPTIMAL_SOLUTION"
            objective = solutions[-1]["variables"]["_objective"]
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