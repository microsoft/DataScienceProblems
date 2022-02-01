# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import numpy as np
from tqdm import tqdm
from pathlib import Path
from collections import defaultdict

import nbformat
from nbclient import NotebookClient

from data_science_problems.read import read_problems, read_filepaths, extract_initial_comments
from data_science_problems.utils import stream_jsonl, estimate_pass_at_k, reliability_guard
from data_science_problems.progress import ProgressBar


import ray
ray.init(log_to_driver=False)


def refersh_and_save(path, fout, completions, problems):
    path = Path(path.strip())
    nb = nbformat.read(path, as_version=4)

    cells_json = nb["cells"]
    cells = [''.join(cell['source']) for cell in cells_json]
    for idx in range(len(cells)-1):
        if "task_id" in cells_json[idx]["metadata"]:
            task_id = cells_json[idx]["metadata"]["task_id"]

            # verify that it is the right cell
            comment, solution = extract_initial_comments(cells_json[idx]["source"])
            assert solution == problems[task_id]["solution"]
            assert cells_json[idx+1]["source"] == problems[task_id]["test"]
            
            for completion_id, completion in enumerate(completions[task_id]):
                # fill the cell with generated code
                cells_json[idx]["source"] = "#### GENERATED\n" + completion

                # write the refreshed notebook to it's own file
                task_no = task_id.split('/')[1]
                suffix = f".{task_no}.{completion_id}.ipynb"
                outnb = path.parent / path.parts[-1].replace(".ipynb", suffix)
                print(outnb, file=fout)
                nbformat.write(nb, outnb)

                # fill the cell back with original code
                cells_json[idx]["source"] = problems[task_id]["solution"]


@ray.remote
def execute(notebook_filename, actor, ferr):
    actor.update.remote(1)
    notebook_filename = Path(notebook_filename.strip())
    nb = nbformat.read(notebook_filename, as_version=4)
    parent = notebook_filename.parent
    client = NotebookClient(nb, 
        timeout=10, 
        kernel_name="python3", 
        resources= {'metadata': {'path': parent}}, 
        allow_errors=True
    )
    try:
        enb = client.execute()
    except Exception as e:
        print(notebook_filename, file=ferr)
        return
    nbformat.write(enb, notebook_filename)
    print(notebook_filename)


def has_no_error(x):
    for element in x:
        if "ename" in element:
            return False
    return True


def evaluate(path):
    path = Path(path.strip())
    nb = nbformat.read(path, as_version=4)

    cells_json = nb["cells"]
    cells = [''.join(cell['source']) for cell in cells_json]
    for idx in range(len(cells)-1):
        if "task_id" in cells_json[idx]["metadata"]:
            task_id = cells_json[idx]["metadata"]["task_id"]
            source = cells_json[idx]["source"]
            if "#### GENERATED" in source:
#                 print(task_id)
                test = cells_json[idx+1]["outputs"]
                return has_no_error(test), task_id


def evaluate_dsp(sample_file="samples.jsonl", ks=[1, 10, 100]):

    print("Reading the generated samples.")
    problems = read_problems()
    completions = defaultdict(list)
    for s in stream_jsonl(sample_file):
        completions[s["task_id"]].append(s["completion"])


    # create new notebooks with generated code filled in
    print("Saving to new notebooks with generated samples.")
    ps = read_filepaths()
    out_file = "generated.txt"
    with open(out_file, "w") as fout:
        for path in tqdm(ps, total=len(ps)):
            refersh_and_save(path, fout, completions, problems)


    # disable functionalities that can make destructive changes to the test
    reliability_guard()

    # execute the notebooks with generated code
    print("Execute the new notebooks with generated samples.")
    with open(out_file) as f:
        ps = f.readlines()
    
    pb = ProgressBar(len(ps))
    with open("errors.txt", "w") as ferr:
        tasks_pre_launch = [execute.remote(notebook_filename, pb.actor, ferr) for notebook_filename in ps]
        pb.print_until_done()
        tasks = ray.get(tasks_pre_launch)


    # calculate pass@k.
    print("Complute pass@k for the executed notebooks.")
    with open(out_file) as f:
        ps = f.readlines()
    
    results = defaultdict(list)
    for notebook_filename in tqdm(ps):
        result, task_id = evaluate(notebook_filename)
        results[task_id].append(result)
    
    total, correct = [], []
    for result in results.values():
        result.sort()
        passed = [bool(r) for r in result]
        total.append(len(passed))
        correct.append(sum(passed))
    total = np.array(total)
    correct = np.array(correct)

    pass_at_k = {f"pass@{k}": estimate_pass_at_k(total, correct, k).mean() \
                                                for k in ks if (total >= k).all()}
    return pass_at_k


if __name__ == "__main__":
    evaluate_dsp()

