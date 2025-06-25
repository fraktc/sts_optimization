# from .models.z3.model_plain import SMT_plain
# from .models.z3.model_twosolver import SMT_twosolver 
# from .models.z3.model_local_search import SMT_local_search
# from .models.z3.model_plain_mtz import SMT_plain_mtz
# from .solve_smtlib import solve as solve_smtlib
import gc

import logging
logger = logging.getLogger(__name__)

# experiments = [
#     {
#         "name": "plain",
#         "model": SMT_plain,
#         "symmetry_breaking": False,
#         "implied_constraints": False,
#     },
#     {
#         "name": "plain_symm",
#         "model": SMT_plain,
#         "symmetry_breaking": True,
#         "implied_constraints": False,
#     },
#     {
#         "name": "plain_impl",
#         "model": SMT_plain,
#         "symmetry_breaking": False,
#         "implied_constraints": True,
#     },
#     {
#         "name": "twosolver",
#         "model": SMT_twosolver,
#         "symmetry_breaking": False,
#         "implied_constraints": False,
#     },
#     {
#         "name": "twosolver_symm",
#         "model": SMT_twosolver,
#         "symmetry_breaking": True,
#         "implied_constraints": False,
#     },
#     {
#         "name": "twosolver_impl",
#         "model": SMT_twosolver,
#         "symmetry_breaking": False,
#         "implied_constraints": True,
#     },
#     {
#         "name": "local_search",
#         "model": SMT_local_search,
#         "symmetry_breaking": False,
#         "implied_constraints": False,
#     }
# ]

experiments = []

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
            
        
        results[name] = model(instance["m"],
                              instance["n"],
                              instance["l"],
                              instance["s"],
                              instance["D"],
                              timeout=timeout,
                              implied_constraints=implied_constraints,
                              symmetry_breaking=symmetry_breaking,
                              **kwargs)

        gc.collect()
    smtlib_results = {}
    # smtlib_results = solve_smtlib(instance, instance_number, timeout, cache, random_seed, models_filter, **kwargs)
    for key in smtlib_results:
        results[key] = smtlib_results[key]

    return results