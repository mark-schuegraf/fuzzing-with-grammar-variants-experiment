#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module represents the main entry point to running the grammar transformation experiments.
"""

import logging
import sys

import luigi

from lib import task_dispatch

if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", datefmt="%d.%m.%Y %H:%M:%S", level=logging.INFO,
                        stream=sys.stdout)
    luigi.run(main_task_cls=task_dispatch.DispatchLanguages)
