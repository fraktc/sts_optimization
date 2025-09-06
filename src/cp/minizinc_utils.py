from subprocess import Popen, PIPE
import os
import json
import logging
logger = logging.getLogger(__name__)
import time
from pathlib import Path


def __formatCommand(model_path, data_path, solver, timeout_ms, seed, free_search):
    cmd = [
        "minizinc",
        "--json-stream",
        "--output-mode", "json",
        # "--all",
        "--statistics",
        "--solver", f"{solver}",
        "--time-limit", f"{timeout_ms}",
        "--random-seed", f"{seed}",
        "--output-time",
        "--output-objective",
        "--model", f"{os.path.abspath(model_path)}",
        "--data", f"{os.path.abspath(data_path)}",
    ]
    if free_search:
        cmd.append("-f")
    return cmd


def minizincSolve(model_path: str, data_path: str, solver: str, timeout_ms: int, seed: int, free_search: bool=False):
    """
        Calls MiniZinc on a model and returns solving statistics and all solutions.
    """
    solutions = []
    outcome = {
        "mz_status": None,
        "time_ms": None,
        "crash_reason": None
    }
    statistics = {
        "compiler": None,
        "solver": None,
        "solution": None
    }
    minizinc_cmd = __formatCommand(model_path, data_path, solver, timeout_ms, seed, free_search)

    with Popen(minizinc_cmd, stdout=PIPE, stderr=PIPE) as pipe:
        while True:
            out_stream = pipe.stdout.readline().decode("utf-8")
            if len(out_stream) <= 0: break
            data = json.loads(out_stream)

            if data["type"] == "statistics":
                if solver in ["gecode", "chuffed"]:
                    # Gecode/Chuffed outputs 3 statistics at different times.
                    if statistics["compiler"] is None: 
                        statistics["compiler"] = data["statistics"]
                    elif statistics["solver"] is None: 
                        statistics["solver"] = data["statistics"]
                    elif statistics["solution"] is None: 
                        statistics["solution"] = data["statistics"]
                    else: 
                        logger.warning("Unexpected statistics from Gecode/Chuffed")
                elif "ortools" in solver:
                    if statistics["compiler"] is None: 
                        statistics["compiler"] = data["statistics"]
                    else:
                        pass # OR-tools sends statistics for each intermediate solution
                else:
                    logger.warning("Unknown solver")
            elif data["type"] == "solution":
                # MiniZinc's automatic decision-variable JSON
                vars_auto = data["output"].get("json", {})

                # Your manual output block (string from `output [...]`)
                text_output = data["output"].get("default", "").strip()
                
                # If your output is valid JSON text, parse it
                try:
                    manual_vars = json.loads(text_output) if text_output.startswith("{") else {}
                except json.JSONDecodeError:
                    manual_vars = {}

                # Merge both sources (manual overrides automatic if keys match)
                merged_vars = {**vars_auto, **manual_vars}
                
                sol = {
                    "variables": merged_vars,
                    "time_ms": data["time"]
                }
                solutions.append(sol)

            elif data["type"] == "status":
                outcome["mz_status"] = data["status"]
                outcome["time_ms"] = data["time"]

        pipe.wait()
        stderr_output = pipe.stderr.read().decode("utf-8")
        if pipe.returncode in [-6, -11]:
            outcome["crash_reason"] = "out-of-memory"
        elif pipe.returncode != 0:
            outcome["crash_reason"] = f"minizinc_error: {stderr_output.strip()}"

    return outcome, solutions, statistics
