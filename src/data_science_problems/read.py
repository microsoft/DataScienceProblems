# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from pathlib import Path
from tqdm import tqdm

import os
import nbformat
from shutil import copyfile


ROOT = Path(os.path.abspath(__file__)).parent.parent
DSP = ROOT / "data-science-notebooks.txt"


def extract_initial_comments(tgt):
    tgt = tgt.strip().split("\n")
    for idx, t in enumerate(tgt):
        if t.strip() == "":
            continue
        if not t.startswith("#"):
            break
    return "\n".join(tgt[:idx]), "\n".join(tgt[idx:])


def build_examples(path, context_len=3):
    path = Path(path.strip())

    try:
        nb = nbformat.read(path, as_version=4)
    except:
        copyfile("/storage/data/" / path, path)
        nb = nbformat.read(path, as_version=4)

    cells_json = nb["cells"]
    cells = [''.join(cell['source']) for cell in cells_json]
    
    examples = []
    notebook_problem_index = 0
    for idx in range(len(cells)-1):
        cell_type = cells_json[idx]["cell_type"]
        i, j = max(0, idx-context_len), idx

        target = cells[idx]
        source = "\n".join(cells[i:j])

        # a number of times, the inital comments in the target
        # contains the problem statement. need that to solve the problem
        comment, target = extract_initial_comments(target)
        source = source + "\n" + comment
        
        next = cells[idx+1]

        try:
            if cells_json[idx]["metadata"]["nbgrader"]["solution"]:
                if "assert" in "".join(cells_json[idx+1]["source"]):
                    if cell_type == "code":
                        example = {
                            "prompt": source,
                            "test": next,
                            "solution": target,
                            "notebook_path": path,
                            "notebook_problem_index": notebook_problem_index
                        }
                        notebook_problem_index += 1
                        yield example
        # catch if the key metadata.nbgrader.solution do not exist
        except Exception as e:
            pass   
    return examples


def build_examples_new(path, context_len=3):
    path = ROOT.parent / Path(path.strip())
    # try:
    nb = nbformat.read(path, as_version=4)
    # except:
    #     copyfile("/storage/data/" / path, path)
    #     nb = nbformat.read(path, as_version=4)

    cells_json = nb["cells"]
    cells = [''.join(cell['source']) for cell in cells_json]
    
    examples = []
    notebook_problem_index = 0
    for idx in range(len(cells)-1):
        cell_type = cells_json[idx]["cell_type"]
        i, j = max(0, idx-context_len), idx

        target = cells[idx]
        source = "\n".join(cells[i:j])

        # a number of times, the inital comments in the target
        # contains the problem statement. need that to solve the problem
        comment, target = extract_initial_comments(target)
        source = source + "\n" + comment
        
        next = cells[idx+1]

        try:
            task_id = cells_json[idx]["metadata"]["task_id"]
            example = {
                "task_id": task_id,
                "prompt": source,
                "solution": target,
                "test": next,
                "notebook_path": str(path),
                "notebook_problem_index": notebook_problem_index,
            }
            notebook_problem_index += 1
            yield example
        except Exception as e:
            pass   
    return examples


def read_filepaths():
    with open(DSP) as f:
        return f.readlines()


def read_problems(context_len=3):
    ps = read_filepaths()
    examples = {}
    for path in tqdm(ps, total=len(ps)):
        for example in build_examples_new(path, context_len=context_len):
            examples[example["task_id"]] = example
    return examples


