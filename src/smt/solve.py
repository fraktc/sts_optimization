from .models.z3.naive import NaiveSolver
from .models.z3.bitvec import BitVecSolver
from .models.z3.round_robin import RoundRobinSolver, BitVecRoundRobinSolver
import gc

import logging
logger = logging.getLogger(__name__)

experiments = [
    {
        "name": "round_robin",
        "model": RoundRobinSolver,
        "symmetry_breaking": False,
        "implied_constraints": [False],
    },
    {
        "name": "round_robin_bitvec",
        "model": BitVecRoundRobinSolver,
        "symmetry_breaking": False,
        "implied_constraints": [False],
    },
]

def solve(instance, timeout, cache={}, random_seed=42, models_filter=None, **kwargs):
    results = {}
    
    for experiment in experiments:
        if (models_filter is not None) and (experiment["name"] not in models_filter):
            continue
        logger.info(f"Starting model {experiment['name']}")
        name, model, symmetry_breaking, implied_constraints = experiment["name"], experiment["model"], experiment["symmetry_breaking"], experiment["implied_constraints"]

        # Check if result is in cache
        if name in cache:
            logger.info(f"Cache hit")
            results[name] = cache[name]
            continue
        
        if ("instance_limit" in experiment) and (instance >= experiment["instance_limit"]):
            logger.info(f"Model {name} skip instance {instance}")
            results[name] =  {
                "time": timeout,
                "optimal": False,
                "obj": None,
                "sol": None
            }
            continue
            
        
        results[name] = model(instance,
                              timeout=timeout,
                              implied_constraints=implied_constraints,
                              symmetry_breaking=symmetry_breaking,
                              **kwargs).solve()

        gc.collect()
    # smtlib_results = {}
    # # smtlib_results = solve_smtlib(instance, instance_number, timeout, cache, random_seed, models_filter, **kwargs)
    # for key in smtlib_results:
    #     results[key] = smtlib_results[key]

    return results