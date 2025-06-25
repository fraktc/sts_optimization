import sys
import os
from pathlib import Path
import json



def formatObjective(res):
    if res["obj"] is None:
        return "--"
    elif res["optimal"]:
        return f"\\textbf{{{res['obj']}}}"
    else:
        return f"{res['obj']}"


if __name__ == "__main__":
    res_dir = sys.argv[1]
    results = {}

    for res_name in os.listdir(res_dir):
        instance_num = int(Path(res_name).stem)

        with open(os.path.join(res_dir, res_name), "r") as f:
            results[instance_num] = json.load(f)

    models = [ *results[1].keys() ]
    models_latex = [ m.replace("_", "-") for m in models ]
    instances = sorted([ *results.keys() ])

    print(
        "\\begin{table}[h]\n" +
            "\t\\centering\n" +
            "\t\\caption{Caption}\n" +
            f"\t\\begin{{tabular}}{{c{'c'*len(models)}}}\n" +
                "\t\t\\toprule\n" +
                "\t\tId & " + " & ".join(models_latex) + " \\\\ \n" +
                "\t\t\\midrule\n" +
                "\t\t" + " \\\\ \n\t\t".join([
                    f"{i} & " + " & \t".join([ formatObjective(results[i][m]) for m in models])
                    for i in instances
                ]) + " \\\\ \n" +
                "\t\t\\bottomrule\n" +
        "\t\\end{tabular}\n"
        "\\end{table}\n"
    )