import argparse
import json
import re
import os



def statusToOrdinal(status):
    if status == "optimal": return 0
    if status == "suboptimal": return 1
    if status == "timeout": return 2
    if status == "out-of-memory": return 3
    if status == "crashed": return 4
    if status == "inconsistent": return 5


def formatMethodStatusFileName(method):
    return f"{method.lower()}-status.md"


def generateOverallStatus(checks, to_display_methods, method_status_path):
    # num_instances = len(checks[to_display_methods[0]])
    instances = checks[to_display_methods[0]].keys()
    status_md = ""

    # status_md = f"| Instance | {' | '.join(to_display_methods)} |\n"
    status_md = f"| Instance | {' | '.join([f'[{m}]({os.path.join(method_status_path, formatMethodStatusFileName(m))})' for m in to_display_methods])} |\n"
    status_md += f"|:-:| {''.join([':---:|']*(len(to_display_methods)))}\n"

    # Format overall results
    for instance in instances:
        # instance = f"{i+1}"

        status_md += f"| ${instance}$ | "
        for method in to_display_methods:
            if len(checks[method][instance]) == 0:
                status_md += "| "
                continue

            instance_tests = [ 
                {
                    "name": test_name,
                    **status
                } 
                for test_name, status in checks[method][instance].items()
            ]
            instance_tests = sorted(instance_tests, key=lambda x: (statusToOrdinal(x["status"]), x["obj"], x["time"]))
            entry = ""

            best_instance_status = instance_tests[0]["status"]
            best_instance_time = instance_tests[0]["time"]
            best_instance_obj = instance_tests[0]["obj"]
            best_instance_name = instance_tests[0]["name"].replace('_', '-')

            if best_instance_status == "optimal":
                entry = (
                    f"$\\color{{green}}\\text{{{best_instance_time} s (obj: {best_instance_obj})}}$"
                    "</br>$\\color{green}"+"\\text{"+best_instance_name+"}$"
                )
            elif best_instance_status == "suboptimal":
                entry = (
                    f"$\\color{{orange}}\\text{{{best_instance_time} s (obj: {best_instance_obj})}}$"
                    "</br>$\\color{orange}"+"\\text{"+best_instance_name+"}$"
                )
            elif best_instance_status == "inconsistent":
                entry = "$\\color{red}\\text{Inconsistent}$"
            elif best_instance_status == "timeout":
                entry = "$\\color{lightgray}\\text{Timeout}$"
            elif best_instance_status == "out-of-memory":
                entry = "$\\color{pink}\\text{Out of memory}$"
            elif best_instance_status == "crashed":
                entry = "$\\color{pink}\\text{Crashed}$"
            else:
                raise Exception("Unknown status")
            
            status_md += f"{entry} | "
        status_md += "\n"

    return status_md


def generateSpecificStatus(checks, method):
    num_instances = len(checks[method])
    instances = checks[method].keys()
    status_md = ""

    # status_md = f"| Instance | {' | '.join(to_display_methods)} |\n"
    status_md = f"| $\\text{{Model}}$ | {' | '.join([f'${i+1}$' for i in range(num_instances)])} |\n"
    status_md += f"|:-:| {''.join([':---:|']*num_instances)}\n"

    models = checks[method][list(checks[method].keys())[0]].keys()
    for model in models:
        status_md += "$\\text{"+ model.replace('_', '-') +"}$ | "
        for instance in instances:
            # instance = f"{i+1}"
            entry = ""
            status = checks[method][instance][model]["status"]
            obj = checks[method][instance][model]["obj"]
            time = checks[method][instance][model]["time"]


            if status == "optimal":
                entry = f"$\\color{{green}}\\text{{{obj} ({time} s)}}$"
            elif status == "suboptimal":
                entry = f"$\\color{{orange}}\\text{{{obj} ({time} s)}}$"
            elif status == "inconsistent":
                entry = f"$\\color{{red}}\\text{{I}}$"
            elif status in ["crashed", "out-of-memory"]:
                entry = f"$\\color{{pink}}\\text{{E}}$"
            else:
                entry = f"$-$"
            status_md += f"{entry} | "
        status_md += "\n"
    
    return status_md


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Update README statuses")
    parser.add_argument("--checks-file", type=str, required=True)
    parser.add_argument("--readme-file", type=str, required=True)
    parser.add_argument("--method-status-dir", type=str, required=True)
    parser.add_argument("--method-status-git", type=str, required=True)
    args = parser.parse_args()

    to_display_methods = ["CP", "SAT", "SMT", "MIP"]
    with open(args.checks_file, "r") as f: 
        checks = json.load(f)

    for i in range(1, len(to_display_methods)):
        assert to_display_methods[i] in checks
        # print(checks[to_display_methods[i]], checks[to_display_methods[0]])
        assert len(checks[to_display_methods[i]]) == len(checks[to_display_methods[0]])

    os.makedirs((args.method_status_dir), exist_ok=True)


    # Update overall readme
    with open(args.readme_file, "r+") as f: 
        overall_status_md = generateOverallStatus(checks, to_display_methods, args.method_status_git)
        # print(overall_status_md)
        markdown = f.read()
        # print(markdown)
        f.seek(0)
        print(re.sub(
                r"<!-- begin-status -->[\s\S]*<!-- end-status -->", 
                "<!-- begin-status -->\n" + overall_status_md.replace('\\', '\\\\') + "\n<!-- end-status -->", 
                markdown
            ))
        f.write(
            re.sub(
                r"<!-- begin-status -->[\s\S]*<!-- end-status -->", 
                "<!-- begin-status -->\n" + overall_status_md.replace('\\', '\\\\') + "\n<!-- end-status -->", 
                markdown
            )
        )
        f.truncate()

    # Update method specific readme
    for method in to_display_methods:
        with open(os.path.join(args.method_status_dir, formatMethodStatusFileName(method)), "w") as f: 
            f.write(f"# {method} status\n")
            f.write(generateSpecificStatus(checks, method))
