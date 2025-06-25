import os
import json
#import subprocess
import logging 
import pathlib
#import re
# from amplpy import AMPL, add_to_path, DataFrame
#import matplotlib.pylab as plt
import warnings
import math
import time

logger = logging.getLogger(__name__)

#List of solver
SOLVERS = [
    'scip', 
    'highs'
]
#SOLVERS = ['highs']


def run_ampl_model(model_file, data_file, solver, timeout, random_seed):
    
    #add_to_path(r'c:/Users/cmaio/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/AMPL IDE.lnk') #Damodificareperreproducibilità
    # ampl = AMPL()
    ampl = None

    try:
        ampl.read(model_file)
        ampl.readData(data_file)

        if solver == 'highs':
            ampl.option['highs_options'] = "presolve=on mip_heuristic_effort=0.5 mip_rel_gap=1e-4" 
        
        ampl.setOption('solver', solver)
        ampl.setOption(solver + '_options', f'timelimit={timeout}')
        ampl.setOption('randseed', random_seed)

        start_time = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ampl.solve()
        
        solve_time = math.floor(time.time() - start_time)
        objective = round( ampl.getObjective('ObjectiveMaxDistance').value() )
        is_optimal = ampl.getValue('solve_result') == "solved"

        if (ampl.getValue('solve_result') == 'failure') or (ampl.getValue('solve_result') == 'infeasible') or (objective <= 0) : raise Exception("UNSAT")
    
        
        # Extraction of solution
        A = ampl.getVariable('A')
        X = ampl.getVariable('X')
        m = ampl.getValue('m')
        n = ampl.getValue('n')
        
        solution = []
        for couriers in range(1,m+1):
            couriers_packs = []
            packs = n + 1
            while round(X[packs, n+1, couriers].value()) == 0:
                for i in range(1, n + 1):
                    if round(X[packs, i, couriers].value()) == 1:
                        couriers_packs.append(i)
                        packs = i
                        break
            solution.append(couriers_packs)
        
    
        return {
            "time": solve_time if is_optimal else timeout,
            "optimal": is_optimal,
            "obj": objective,
            "sol": solution
        }
    except Exception as e:
        logger.error(f"Error with solver {solver} and model {model_file}: {str(e)}")
        return {
            "time": timeout,
            "optimal": False,
            "obj": None,
            "sol": None
        }
    finally:
        ampl.close()

models_setup = [
    {
        "name": "initial-model",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/initial_model.mod"),
    },
    {
        "name": "implied-model",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/model_with_implied_constraint.mod"),
    },
    {
        "name": "symmetry-model",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./models/model_with_symmetry_breaking.mod"),
    }
    
]

def solve(instance, instance_number, timeout=300, cache={}, random_seed=42, models_filter=None, **kwargs):
    
    data_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), './data')
    data_instance = sorted([f for f in os.listdir(data_dir) if f.endswith('.dat')])[instance_number-1]
    data_file = os.path.join(data_dir, data_instance)
    
    out_results = {}
    for model in models_setup:
        for solver in SOLVERS:
            model_str = model['name'] + '_' + solver
            if (models_filter is not None) and (model_str not in models_filter):
                continue
            logger.info(f"Starting model {model['name']} with {solver}")
            # Check if result is in cache
            if model_str in cache:
                logger.info(f"Cache hit")
                out_results[model_str] = cache[model_str]
                continue
        
        # Solve instance
            result = run_ampl_model(
                model_file = model["model_path"],
                data_file = data_file,
                solver = solver,
                timeout = timeout,
                random_seed = random_seed
            )
            
            out_results[model_str] = result
            #print(out_results)
    return out_results

if __name__ == '__main__':
   solve('', 1, 300)
