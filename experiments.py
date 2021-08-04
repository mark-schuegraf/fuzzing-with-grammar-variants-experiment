#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks to run the grammar transformation experiments.
"""

import logging
import sys
from typing import final

import luigi

from lib import evaluation
from lib import utils


class Experiment(luigi.WrapperTask, utils.StableRandomness):
    """Vertical prototype of the full experiment."""
    random_seed: int = luigi.IntParameter(
        description="The main seed for this experiment. All other random seeds will be derived from this one.",
        positional=False)
    total_number_of_runs: int = luigi.IntParameter(
        description="The number of runs to conduct per combination of transformation, fuzzer and subject.")
    subject_name: str = luigi.Parameter(description="The name of the subject to run.")
    language: str = luigi.Parameter(description="The language specified by the input grammar.")

    @final
    def requires(self):
        language_seed = self.random_int(self.random_seed, self.language)
        return [self.clone(evaluation.AggregateCoverageWithRecurrent2PathWithChomskyGrammar,
                           subject_name="argo", language_seed=language_seed),
                self.clone(evaluation.AggregateCoverageGrowthRateWithRecurrent2PathWithChomskyGrammar,
                           subject_name="argo", language_seed=language_seed)]


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", datefmt="%d.%m.%Y %H:%M:%S", level=logging.INFO,
                        stream=sys.stdout)
    # TODO: add run monitoring later
    luigi.run(main_task_cls=Experiment)
