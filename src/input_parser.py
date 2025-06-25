import re
import argparse
import os
from pathlib import Path
from cp.minizinc_utils import parseInstanceForMinizinc


def __cleanLine(line):
    return re.sub(r" +", " ", line.strip())

def parseInstanceFile(path):
    with open(path, "r") as f:
        num_couriers = int(__cleanLine(f.readline()))
        num_packages = int(__cleanLine(f.readline()))
        capacities = [int(l) for l in __cleanLine(f.readline()).split(" ")]
        sizes = [int(s) for s in __cleanLine(f.readline()).split(" ")]
        distances = []

        for _ in range(num_packages+1):
            distances.append( [int(d) for d in __cleanLine(f.readline()).split(" ")] )

    return {
        "m": num_couriers,
        "n": num_packages,
        "l": capacities,
        "s": sizes,
        "D": distances
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Input parser")
    parser.add_argument("--instances-path", type=str, default="./instances")
    parser.add_argument("--output-dir", type=str, required=True)
    parser.add_argument("--target", type=str, choices=["minizinc"], required=True)
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)

    for f_name in os.listdir(args.instances_path):
        instance = parseInstanceFile(os.path.join(args.instances_path, f_name))
        with open(os.path.join(args.output_dir, f"{Path(f_name).stem}.dzn"), "w") as f:
            f.write(parseInstanceForMinizinc(instance))
