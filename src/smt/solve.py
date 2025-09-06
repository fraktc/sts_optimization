from .models.z3.naive import NaiveSolver
from .models.z3.round_robin import RoundRobinSolver, BitVecRoundRobinSolver
import gc

import logging
logger = logging.getLogger(__name__)

experiments = [
    {
        "name": "naive",
        "model": NaiveSolver,
        "symmetry_constraint_mask": [False],
        "implied_constraint_mask": [False],
        "optimization": False,
    },
    {
        "name": "naive_symm",
        "model": NaiveSolver,
        "symmetry_constraint_mask": [True],
        "implied_constraint_mask": [False],
        "optimization": False,
    },
    {
        "name": "naive_implied",
        "model": NaiveSolver,
        "symmetry_constraint_mask": [False],
        "implied_constraint_mask": [True],
        "optimization": False,
    },
    {
        "name": "naive_full",
        "model": NaiveSolver,
        "symmetry_constraint_mask": [True],
        "implied_constraint_mask": [True],
        "optimization": False,
    },
    {
        "name": "naive_optim",
        "model": NaiveSolver,
        "symmetry_constraint_mask": [False],
        "implied_constraint_mask": [False],
        "optimization": True,
    },
    {
        "name": "naive_symm_optim",
        "model": NaiveSolver,
        "symmetry_constraint_mask": [True],
        "implied_constraint_mask": [False],
        "optimization": True,
    },
    {
        "name": "naive_implied_optim",
        "model": NaiveSolver,
        "symmetry_constraint_mask": [False],
        "implied_constraint_mask": [True],
        "optimization": True,
    },
    {
        "name": "naive_full_optim",
        "model": NaiveSolver,
        "symmetry_constraint_mask": [True],
        "implied_constraint_mask": [True],
        "optimization": True,
    },
    {
        "name": "round_robin",
        "model": RoundRobinSolver,
        "symmetry_constraint_mask": [False],
        "implied_constraint_mask": [False],
        "optimization": False,
    },
    {
        "name": "round_robin_symm",
        "model": RoundRobinSolver,
        "symmetry_constraint_mask": [True],
        "implied_constraint_mask": [False],
        "optimization": False,
    },
    {
        "name": "round_robin_implied",
        "model": RoundRobinSolver,
        "symmetry_constraint_mask": [False],
        "implied_constraint_mask": [True],
        "optimization": False,
    },
    {
        "name": "round_robin_full",
        "model": RoundRobinSolver,
        "symmetry_constraint_mask": [True],
        "implied_constraint_mask": [True],
        "optimization": False,
    },
    {
        "name": "round_robin_bitvec",
        "model": BitVecRoundRobinSolver,
        "symmetry_constraint_mask": [False],
        "implied_constraint_mask": [False],
        "optimization": False,
    },
    {
        "name": "round_robin_bitvec_symm",
        "model": BitVecRoundRobinSolver,
        "symmetry_constraint_mask": [True],
        "implied_constraint_mask": [False],
        "optimization": False,
    },
    {
        "name": "round_robin_bitvec_implied",
        "model": BitVecRoundRobinSolver,
        "symmetry_constraint_mask": [False],
        "implied_constraint_mask": [True],
        "optimization": False,
    },
    {
        "name": "round_robin_bitvec_full",
        "model": BitVecRoundRobinSolver,
        "symmetry_constraint_mask": [True],
        "implied_constraint_mask": [True],
        "optimization": False,
    },
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