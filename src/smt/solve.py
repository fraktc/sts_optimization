from .models.z3.naive import Naive
import gc

import logging
logger = logging.getLogger(__name__)

experiments = [
    {
        "name": "naive",
        "model": Naive,
        "symmetry_breaking": False,
        "implied_constraints": [False],
        "incremental": False
    },
    {
        "name": "naive incremental",
        "model": Naive,
        "symmetry_breaking": False,
        "implied_constraints": [False],
        "incremental": True
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