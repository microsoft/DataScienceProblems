# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import fire
import sys

from data_science_problems.execution import evaluate_dsp


def entry_point(
    sample_file: str,
    k: str = "1,10,100",
):
    """
    Evaluates the functional correctness of generated samples.
    """
    k = list(map(int, k.split(",")))
    results = evaluate_dsp(sample_file, k)
    print(results)


def main():
    fire.Fire(entry_point)

sys.exit(main())
