import os
import json
import logging 
import pathlib
import warnings
import math
import time
import importlib.util

logger = logging.getLogger(__name__)

# List of solvers
SOLVERS = ['CBC']

def run_milp_model(model_file, solver, number_of_teams, timeout, random_seed):
    """
    Run the MILP model for a specific solver
    """
    try:
        # Dynamically import the model module
        spec = importlib.util.spec_from_file_location("model_module", model_file)
        model_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(model_module)
        
        # Call the create_milp_model function with timeout parameter
        all_results = model_module.create_milp_model(number_of_teams, solver, timeout)
        
        # Extract result for the specific solver
        if solver in all_results:
            result = all_results[solver]
            return {
                "time": result["time"] if result["optimal"] else timeout,
                "optimal": result["optimal"],
                "obj": result["obj"],
                "sol": result["sol"]
            }
        else:
            raise Exception(f"Solver {solver} not found in results")
            
    except Exception as e:
        logger.error(f"Error with solver {solver} and model {model_file}: {str(e)}")
        return {
            "time": timeout,
            "optimal": False,
            "obj": None,
            "sol": None
        }

# Models setup following the original structure
models_setup = [
    {
        "name": "milp-model-1",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./RR_milp_model_full.py"),
    },
    {
        "name": "milp-model-2",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./RR_milp_model_implied.py"),
    },
    {
        "name": "milp-model-3",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./RR_milp_model_plain.py"),
    },
    {
        "name": "milp-model-4",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./RR_milp_model_SB.py"),
    },
        {
        "name": "milp-model-5",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./Naive_milp_model_full.py"),
    },
        {
        "name": "milp-model-6",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./Naive_milp_model_implied.py"),
    },
        {
        "name": "milp-model-7",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./Naive_milp_model_plain.py"),
    },
        {
        "name": "milp-model-8",
        "model_path": os.path.join(pathlib.Path(__file__).parent.resolve(), "./Naive_milp_model_SB.py"),
    }
    


]

def solve(instance, timeout=10, cache={}, random_seed=42, models_filter=None, **kwargs):
    """
    Main solve function called by the framework
    
    Args:
        instance: Number representing the problem size (number of teams)
        timeout: Time limit in seconds
        cache: Cached results
        random_seed: Random seed for reproducibility
        models_filter: Filter for specific models
    """
    
    # The instance parameter represents the number of teams
    number_of_teams = instance
    
    out_results = {}
    
    for model in models_setup:
        for solver in SOLVERS:
            model_str = model['name'] + '_' + solver
            
            # Apply model filter if provided
            if (models_filter is not None) and (model_str not in models_filter):
                continue
                
            logger.info(f"Starting model {model['name']} with {solver}")
            
            # Check if result is in cache
            if model_str in cache:
                logger.info(f"Cache hit for {model_str}")
                out_results[model_str] = cache[model_str]
                continue
        
            # Solve instance
            result = run_milp_model(
                model_file=model["model_path"],
                solver=solver,
                number_of_teams=number_of_teams,
                timeout=timeout,
                random_seed=random_seed
            )
            
            out_results[model_str] = result
            logger.info(f"Completed {model_str}: optimal={result['optimal']}, obj={result['obj']}")
            
    return out_results

if __name__ == '__main__':
    # Test with 6 teams
    results = solve(6, 300)
    print(results)