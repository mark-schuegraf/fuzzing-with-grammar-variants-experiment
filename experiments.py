#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks to run the grammar transformation experiments.
"""

import logging
import sys

import luigi
from luigi.util import requires

from lib import task_dispatch


# TODO import DispatchLanguages directly, if there ends up being no other behavior that this task is responsible for
@requires(task_dispatch.DispatchLanguages)
class Experiment(luigi.WrapperTask):
    """Attempts to find a relationship between grammar transformations and coverage metrics."""


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", datefmt="%d.%m.%Y %H:%M:%S", level=logging.INFO,
                        stream=sys.stdout)
    luigi.run(main_task_cls=Experiment)
