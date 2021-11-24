# Copyright (C) Microsoft Corporation. All rights reserved.

FROM continuumio/miniconda3


WORKDIR /app
COPY src /app

RUN pip install -e .

ENTRYPOINT ["evaluate_dsp"]