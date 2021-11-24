# Data Science Problems

Execution framework as a part of the paper [Training and Evaluating a Jupyter Notebook Data Science Assistant](). Data Science Problems is a collection of various data-science problems in jupyter notebooks designed to test university students' mastery of various Python implementations of Math and Data Science.

## Installation

Clone this repository to your local machine.

```
$ git clone https://shubhamchandel@dev.azure.com/shubhamchandel/jupyter/_git/DataScienceProblems
$ cd DataScienceProblems
$ pip install -e .
```

## Usage

### Reading the problems

An example problem from the dataset looks like below. It includes the `prompt` which is the question to be asked to the student, `solution` which is the answer to the question and `test` which is the test case to be run on the student's code.

```python
{
    'notebook_path': '/path/to/the/notebook.ipynb',
    'notebook_problem_index': 0,
    'prompt': '%matplotlib inline\n'
            'import matplotlib.pyplot as plt\n'
            'import numpy as np\n'
            'import scipy.optimize as opt\n'
            '## Hat potential\n'
            'The following potential is often used in Physics and other fields '
            'to describe symmetry breaking and is often known as the "hat '
            'potential":\n'
            '\n'
            '$$ V(x) = -a x^2 + b x^4 $$\n'
            '\n'
            'Write a function `hat(x,a,b)` that returns the value of this '
            'function:\n',
    'solution': 'def hat(x,a=5.0,b=1.0):\n    return -a* x*x + b*x**4',
    'task_id': 'DSP/414',
    'test': 'assert hat(0.0, 1.0, 1.0)==0.0\n'
            'assert hat(0.0, 1.0, 1.0)==0.0\n'
            'assert hat(1.0, 10.0, 1.0)==-9.0'
}
```

We provide a `read_problems` function that can be used to read the problems from the jupyter notebooks. 

Below is an example of how to use the `read_problems` function and use your generated code samples to save the samples to a file.


```python
from data_science_problems.read import read_problems
from data_science_problems.utils import write_jsonl

problems = read_problems()

num_samples = 2
samples = [
    dict(task_id=task_id, completion=generate_code(problems[task_id]["prompt"]))
    for task_id in problems
    for _ in range(num_samples)
]
write_jsonl("samples.jsonl", samples)
```


### Executing the problems

Once you have saved the generated samples in the `samples.jsonl` file, you can use the cli `evaluate_dsp` to execute the generated samples.

`evaluate_dsp` will perform the following things:

- It will read the samples from the `samples.jsonl` file.
- It will create new notebooks with the generated code samples. The list of new notebooks is saved in the `generates-notebooks.txt` file.
- It will execute these new notebooks.
- It will compute `pass@k` for generated samples. 

> **WARNING: Running the `evaluate_dsp` command with 1 `num_samples` will create with ~1000 new notebooks and save them on your disk. This may take a while.**

```
$ evaluate_dsp samples.jsonl
2021-11-02 09:11:11,847 INFO services.py:1164 -- View the Ray dashboard at http://127.0.0.1:8265
Reading the generated samples.
100%|███████████████████████████████████████████████| 305/305 [00:03<00:00, 97.34it/s]
Saving to new notebooks with generated samples.
100%|███████████████████████████████████████████████| 305/305 [00:36<00:00,  8.47it/s]
Execute the new notebooks with generated samples.
100%|███████████████████████████████████████████████| 2192/2192 [05:17<00:40,  9.49it/s]
Complute pass@k for the executed notebooks.
100%|███████████████████████████████████████████████| 2192/2192 [00:28<00:00, 76.73it/s]
{'pass@1': ..., 'pass@100': ...}
```

### Contaniner

To build container run
docker build --pull --rm -f "Dockerfile" -t datascienceproblems:latest "."

To execute, run:
docker run -it --rm -v ~/DataScienceProblems/juice-github-repos:/app/juice-github-repos -v ~/DataScienceProblems/samples.jsonl:/samples/samples.jsonl datascienceproblems /samples/samples.jsonl