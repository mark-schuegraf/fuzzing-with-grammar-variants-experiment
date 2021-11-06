#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains various utility mixins.
"""

import hashlib
import math
import random
from abc import ABCMeta
from pathlib import Path
from statistics import mean, median
from typing import Union, final, Final

import luigi
import pandas as pd
from scipy.stats import wilcoxon


def choose_grammar_loading_strategy_based_on_file_extension(grammar_file_path) -> str:
    # the "compile" loading strategy is not used for .scala files, because it is currently broken in tribble
    if grammar_file_path.endswith(".scala") or grammar_file_path.endswith(".tribble"):
        return "parse"
    else:
        return "unmarshal"


def remove_tree(path: Path) -> None:
    """Recursively removes the entire file tree under and including the given path."""
    if path.is_dir():
        for child in path.iterdir():
            remove_tree(child)
        path.rmdir()
    else:
        path.unlink()


class StableRandomness(object):
    """This mixin provides a method for generating random ints from a seed and a list of strings."""
    # For use with random.randrange()
    # Not using sys.maxsize because it might differ depending on the environment
    MAX_RND_INT: Final[int] = 2 ** 32 - 1

    @staticmethod
    def get_random(seed: int, *args: str) -> random.Random:
        """Get a random.Random instance initialized with a seed derived from the the given args."""
        # compute a stable hashcode of arguments as a string
        concat = ''.join(args)
        hash_code = int(hashlib.sha1(concat.encode('utf-8')).hexdigest(), 16) % (10 ** 8)
        return random.Random(seed + hash_code)

    @staticmethod
    def random_int(seed: int, *args: str) -> int:
        """Get a random int that is uniquely derived from the given args."""
        rnd = StableRandomness.get_random(seed, *args)
        return rnd.randrange(StableRandomness.MAX_RND_INT)


class Statistics(object):
    @staticmethod
    def make_summary_statistics_report(diffs: pd.Series):
        return {
            "mean difference": [(mean(diffs))],
            "median difference": [(median(diffs))],
            "min difference": [(min(diffs))],
            "max difference": [(max(diffs))],
        }

    @staticmethod
    def make_wilcoxon_report(diffs: pd.Series):
        w_two_sided, p_two_sided = Statistics.safe_wilcoxon(diffs, alternative="two-sided")
        w_greater, p_greater = Statistics.safe_wilcoxon(diffs, alternative="greater")
        return {
            "wilcoxon (two-sided)": [w_two_sided],
            "p-value (two-sided)": [p_two_sided],
            "wilcoxon (greater)": [w_greater],
            "p-value (greater)": [p_greater],
        }

    @staticmethod
    def safe_wilcoxon(diffs, **kwargs):
        """Return NaN if all diffs are zero. Otherwise carry out the wilcoxon test."""
        return wilcoxon(diffs, **kwargs) if any(diffs) else (math.nan, math.nan)


class TaskWithTemporaryPathCSVWriter(luigi.Task, metaclass=ABCMeta):
    @final
    def _pd_write_to_csv_using_temporary_path(self, data: Union[pd.DataFrame, pd.Series]):
        Path(self.output().path).parent.mkdir(parents=True, exist_ok=True)
        with self.output().temporary_path() as out:
            data.to_csv(out, index=False)
