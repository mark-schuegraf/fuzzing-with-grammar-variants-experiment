#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks to run the grammar transformation experiments.
"""

import logging
import sys

import luigi
from luigi.util import requires

from lib import evaluation


@requires(evaluation.EvaluateCoverage, evaluation.EvaluateCoverageGrowthRate)
class Experiment(luigi.WrapperTask):
    """Attempts to find a relationship between grammar transformations and coverage metrics."""
    language: str = luigi.Parameter(description="The language specified by the input grammar.")
    transformation_mode: str = luigi.Parameter(description="The tribble transformation mode to use.")
    generation_mode: str = luigi.Parameter(description="The tribble generation mode to use.")
    subject_name: str = luigi.Parameter(description="The name of the subject to run.")
    run_number: int = luigi.IntParameter(description="The run number of the produced input set.")
    language_seed: int = luigi.IntParameter(description="The seed from which seeds for this language are derived.")
    total_number_of_runs: int = luigi.IntParameter(description="The number of runs to conduct per configuration.")


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", datefmt="%d.%m.%Y %H:%M:%S", level=logging.INFO,
                        stream=sys.stdout)
    # TODO: add run monitoring later
    luigi.run(main_task_cls=Experiment)
