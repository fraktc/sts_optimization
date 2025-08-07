from .models.smt_lib.plain import model as model_plain
from .models.smt_lib.symm_packs import model as model_symm_packs
from .smtlib_lib.solvers import *
import time
import math
import logging
logger = logging.getLogger(__name__)



def _solutionExtractor(smt_model, n):
    schedule = []
    for period in range(n//2):
        period_schedule = []
        for week in range(n-1):
            home = smt_model[home[week][period]].as_long() + 1
            away = smt_model[away[week][period]].as_long() + 1
            period_schedule.append([home, away])
        schedule.append(period_schedule)
    return schedule


def linearOptimization(instance, solver, model):
    optimality = False
    variables = None

    try:
        while True:
            status = solver.checkSat()
            if status is None: break # Timeout
            if status == "unsat": 
                optimality = (variables is not None)
                break
            variables = solver.getModel()
            solver.addConstraint(model.variables["obj"] < variables["obj"])
    except Exception as e:
        logger.error(f"Exception {e}")

    solver.terminate()
    return optimality, variables


def binaryOptimization(instance, solver, model):
    DEPOT = instance["n"]
    lower = max([ instance["D"][DEPOT][p] + instance["D"][p][DEPOT] for p in range(instance["n"]) ])
    upper = sum([ max(instance["D"][p]) for p in range(instance["n"]) ]) + 2*max(instance["D"][instance["n"]])
    optimality = False
    variables = None
    pivot_count = 0

    try:
        while lower < upper:
            pivot = round(lower + (upper / 10) )
            pivot_name = f"pivot{pivot_count}"
            pivot_count += 1
            solver.push()
            solver.addConstraint((model.variables["obj"] < pivot).named(pivot_name))
            status = solver.checkSat()
            if status is None: break # Timeout

            if status == "sat": 
                variables = solver.getModel()
                solver.pop()
                solver.addConstraint(model.variables["obj"] < variables["obj"])
            else:
                unsat_core = solver.getUnsatCore()
                solver.pop()
                if pivot_name in unsat_core:
                    lower = pivot
                    solver.addConstraint(model.variables["obj"] >= pivot)
                else:
                    optimality = True
                    break
    except Exception as e:
        logger.error(f"Exception {e}")

    solver.terminate()
    return optimality, variables


experiments = [
    {
        "name": "smt2-plain-linear-z3",
        "model": model_plain,
        "solver": Z3Solver,
        "solver_args": {},
        "sol_extractor": _solutionExtractor,
        "optimizer": linearOptimization
    },
    # {
    #     "name": "smt2-plain-binary-z3",
    #     "model": model_plain,
    #     "solver": Z3Solver,
    #     "solver_args": {},
    #     "sol_extractor": _solutionExtractor,
    #     "optimizer": binaryOptimization
    # },
    # {
    #     "name": "smt2-plain-luby-linear-z3",
    #     "model": model_plain,
    #     "solver": Z3Solver,
    #     "solver_args": {
    #         "restart": "luby"
    #     },
    #     "sol_extractor": _solutionExtractor,
    #     "optimizer": linearOptimization
    # },
    # {
    #     "name": "smt2-symm_packs-linear-z3",
    #     "model": model_symm_packs,
    #     "solver": Z3Solver,
    #     "solver_args": {},
    #     "sol_extractor": _solutionExtractor,
    #     "optimizer": linearOptimization
    # },
    {
        "name": "smt2-plain-linear-cvc5",
        "model": model_plain,
        "solver": CVC5Solver,
        "solver_args": {},
        "sol_extractor": _solutionExtractor,
        "optimizer": linearOptimization
    },
    {
        "name": "smt2-plain-linear-opensmt",
        "model": model_plain,
        "solver": OpenSMTSolver,
        "solver_args": {},
        "sol_extractor": _solutionExtractor,
        "optimizer": linearOptimization
    },
    {
        "name": "smt2-plain-linear-smtinterpol",
        "model": model_plain,
        "solver": SMTInterpolSolver,
        "solver_args": {},
        "sol_extractor": _solutionExtractor,
        "optimizer": linearOptimization
    },
    {
        "name": "smt2-plain-linear-yices2",
        "model": model_plain,
        "solver": Yices2Solver,
        "solver_args": {},
        "sol_extractor": _solutionExtractor,
        "optimizer": linearOptimization
    },
]


def solve(instance, instance_number, timeout=300, cache={}, random_seed=42, models_filter=None, **kwargs):
    results = {}

    for exp in experiments:
        if (models_filter is not None) and (exp["name"] not in models_filter):
            continue
        logger.info(f"Starting model {exp['name']}")

        # Check if in cache
        if exp["name"] in cache:
            logger.info(f"Cache hit")
            results[exp["name"]] = cache[exp["name"]]
            continue

        variables = None
        optimality = False
        objective = None
        solution = None
        solve_time = timeout
        solver = None

        try:
            start_time = time.time()
            
            model = exp["model"](instance["m"], instance["n"], instance["l"], instance["s"], instance["D"])
            model_init_time = round(time.time() - start_time)
            logger.info("Model generated")

            solver = exp["solver"](model, timeout=timeout-model_init_time, random_seed=random_seed, **exp["solver_args"])
            solver.compile()
            optimality, variables = exp["optimizer"](instance, solver, model)
        except Exception as e:
            if solver is not None:
                solver.terminate()
            logger.error(f"Exception {e}")

        if (variables is not None) and ("obj" in variables):
            solve_time = math.floor(time.time() - start_time)
            if not optimality :
                solve_time = timeout
            objective = variables["obj"]
            solution = exp["sol_extractor"](instance, variables)

        results[exp["name"]] = {
            "time": solve_time,
            "optimal": optimality,
            "obj": objective,
            "sol": solution,
        }

    return results