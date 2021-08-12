#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks to run the grammar transformation experiments.
"""

import logging
import sys

import luigi


class Experiment(luigi.WrapperTask):
    """Attempts to find a relationship between grammar transformations and coverage metrics."""
    pass


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", datefmt="%d.%m.%Y %H:%M:%S", level=logging.INFO,
                        stream=sys.stdout)
    # TODO: add run monitoring later
    luigi.run(main_task_cls=Experiment)
