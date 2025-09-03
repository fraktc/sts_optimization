from .slot_based import SlotBasedSolver, SlotBasedOptimizer
import gc

import logging
logger = logging.getLogger(__name__)

at_most_one_encodings = ["z3", "pairwise", "sequential", "heule", "bitwise"]
at_most_k_encodings = ["z3", "pairwise", "sequential"]

experiments = [
    {
        "name": f"solver_{one_enc}_{k_enc}",
        "model": SlotBasedSolver,
        "at_most_one_encoding": one_enc,
        "at_most_k_encoding": k_enc
    }
    for one_enc in at_most_one_encodings
    for k_enc in at_most_k_encodings
] + [
    {
        "name": f"optimizer_{one_enc}_{k_enc}",
        "model": SlotBasedOptimizer,
        "at_most_one_encoding": one_enc,
        "at_most_k_encoding": k_enc
    }
    for one_enc in at_most_one_encodings
    for k_enc in at_most_k_encodings
]

def solve(instance, timeout, cache={}, random_seed=42, models_filter=None, **kwargs):
    results = {}
    
    for experiment in experiments:
        if (models_filter is not None) and (experiment["name"] not in models_filter):
            continue
        logger.info(f"Starting model {experiment['name']}")
        name, model, symmetry_constraint_mask, implied_constraint_mask, optimization = experiment["name"], experiment["model"], experiment["symmetry_constraint_mask"], experiment["implied_constraint_mask"], experiment["optimization"]

        # Check if result is in cache00
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
                              implied_constraint_mask=implied_constraint_mask,
                              symmetry_constraint_mask=symmetry_constraint_mask,
                              **kwargs).solve()

        gc.collect()

    return results