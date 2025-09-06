from cp.solve import solve as cp_solve
from sat.solve import solve as sat_solve
from smt.solve import solve as smt_solve
from milp.solve import solve as milp_solve
import argparse
import os
import json
import platform
import logging
logger = logging.getLogger(__name__)

#check if the platform is not Windows
if platform.system() != "Windows":
    import resource

def __loadCache(results_file_path):
    if not os.path.isfile(results_file_path): return {}

    with open(results_file_path, "r") as f:
        return json.load(f)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Instance solver")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    parser.add_argument("--output-path", type=str, default="./res", help="Results directory")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--overwrite-old", action="store_true", help="If set, old results with the same name will be run again")
    parser.add_argument("--models", type=lambda arg: arg.split(","), required=False, default=None, 
                        help="Name of the models to run, comma separated")
    parser.add_argument("--seed", type=int, required=False, default=42, help="Seed for random operations")
    parser.add_argument("--mem-limit", type=int, required=False, default=-1, help="Memory usage limit in MB")
    parser.add_argument("--runner-label", type=str, required=False, default="", help="Name of the machine that is executing")
    parser.add_argument("--methods", type=lambda arg: arg.split(","), required=False, default=["cp", "sat", "smt", "milp"], 
                        help="Methods to run, comma separated")
    parser.add_argument("--submit-mode", action="store_true", help="If set, the output results will be in the format required for submission")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARN,
        format = "%(asctime)s %(levelname)-5s %(message)s",
        datefmt = "%d-%m-%Y %H:%M:%S"
    )

    INSTANCES = [6,8,10,12,14,16,18,20]

    # Set memory limit if needed
    if args.mem_limit >= 0 and platform.system() != "Windows":
        resource.setrlimit(resource.RLIMIT_AS, (args.mem_limit*1024*1024, args.mem_limit*1024*1024))

    # Create output directories
    results_dir = args.output_path
    cp_dir = os.path.join(results_dir, "CP/")
    sat_dir = os.path.join(results_dir, "SAT/")
    smt_dir = os.path.join(results_dir, "SMT/")
    milp_dir = os.path.join(results_dir, "MILP/")

    for dir in [results_dir, cp_dir, sat_dir, smt_dir, milp_dir]:
        os.makedirs((dir), exist_ok=True)


    logger.info("-"*50)
    logger.info("Running with the following configuration:")
    logger.info(f"Methods: {args.methods}")
    logger.info(f"Memory limit: {args.mem_limit} MB")
    logger.info(f"Timeout: {args.timeout} s")
    logger.info("-"*50)

    
    experiments_setup = []
    if "cp" in args.methods: experiments_setup.append((cp_dir, cp_solve))
    if "sat" in args.methods: experiments_setup.append((sat_dir, sat_solve))
    if "smt" in args.methods: experiments_setup.append((smt_dir, smt_solve))
    if "milp" in args.methods: experiments_setup.append((milp_dir, milp_solve))

    for out_dir, solve_fn in experiments_setup:
        logger.info(f"Starting processing for {out_dir}")

        for instance in INSTANCES:
            # Init cache
            if args.overwrite_old:
                cached_results = {}
            else:
                cached_results = __loadCache(os.path.join(out_dir, f"{instance}.json"))

            # Solving instance
            logger.info(f"Starting instance {instance}")
            instance_results = solve_fn(
                instance = instance,
                timeout = args.timeout,
                cache = cached_results,
                random_seed = args.seed,
                models_filter = args.models
            ) 
            
            # Adding missing cached results
            if (not args.overwrite_old) and (args.models is None):
                for key in cached_results:
                    if key not in instance_results:
                        instance_results[key] = cached_results[key]

            # Adding runner label
            for key in instance_results:
                if "_extras" not in instance_results[key]: instance_results[key]["_extras"] = {}
                if "runner" not in instance_results[key]["_extras"]: instance_results[key]["_extras"]["runner"] = args.runner_label

            # Remove extra fields for submission
            if args.submit_mode:
                for key in instance_results:
                    instance_results[key] = {
                        "time": instance_results[key]["time"],
                        "optimal": instance_results[key]["optimal"],
                        "obj": instance_results[key]["obj"],
                        "sol": instance_results[key]["sol"]
                    }

            # Saving instance results
            results_file_path = os.path.join(out_dir, f"{instance}.json")
            with open(results_file_path, "w") as f:
                logger.info(f"Saving results in {results_file_path}")
                json.dump(instance_results, f, indent=3)
