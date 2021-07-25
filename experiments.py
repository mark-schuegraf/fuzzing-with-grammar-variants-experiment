#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks to run the grammar transformation experiments.
"""

import logging
import sys

import luigi
from luigi.util import requires

from lib import generation


@requires(generation.GenerateUsingRecurrent2PathNCoverageStrategyAndChomskyGrammar)
class Experiment(luigi.WrapperTask):
    """Vertical prototype of the full experiment."""
    format: str = luigi.Parameter(description="The format specified by the input grammar.")
    number_of_files_to_generate: int = luigi.IntParameter(
        description="The number of files that the generation run should produce.")
    tribble_generation_seed: int = luigi.IntParameter(description="The seed for this tribble generation run.",
                                                      positional=False, significant=False)


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", datefmt="%d.%m.%Y %H:%M:%S", level=logging.INFO,
                        stream=sys.stdout)
    # TODO: add run monitoring later
    luigi.run(main_task_cls=Experiment)
