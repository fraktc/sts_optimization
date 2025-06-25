import json
import os
from argparse import ArgumentParser



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("command", type=str, nargs=1)
    parser.add_argument("others", nargs="*")
    parser.add_argument("--path", type=str, required=True)
    args = parser.parse_args()

    for f_name in os.listdir(args.path):
        with open(os.path.join(args.path, f_name), "r") as f:
            res = json.load(f)
        
        if args.command[0] == "remove":
            for model in args.others:
                if model in res:
                    del res[model]
        elif args.command[0] == "submit":
            for key in res:
                res[key] = {
                    "time": res[key]["time"],
                    "optimal": res[key]["optimal"],
                    "obj": res[key]["obj"],
                    "sol": res[key]["sol"]
                }

        with open(os.path.join(args.path, f_name), "w") as f:
            json.dump(res, f, indent=3)