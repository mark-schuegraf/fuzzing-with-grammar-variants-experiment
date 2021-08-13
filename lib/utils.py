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
from typing import Union, final, Final

import luigi
import pandas as pd
from scipy.stats import wilcoxon


def choose_grammar_loading_strategy_based_on_file_extension(grammar_file_path) -> str:
    if grammar_file_path.endswith(".scala") or grammar_file_path.endswith(".tribble"):
        return "parse"
    else:
        return "unmarshal"


def safe_wilcoxon(diffs, **kwargs):
    """Return NaN if all diffs are zero. Otherwise carry out the wilcoxon test."""
    return wilcoxon(diffs, **kwargs) if any(diffs) else (math.nan, math.nan)


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
    @final
    def get_random(seed: int, *args: str) -> random.Random:
        """Get a random.Random instance initialized with a seed derived from the the given args."""
        # compute a stable hashcode of arguments as a string
        concat = ''.join(args)
        hash_code = int(hashlib.sha1(concat.encode('utf-8')).hexdigest(), 16) % (10 ** 8)
        return random.Random(seed + hash_code)

    @staticmethod
    @final
    def random_int(seed: int, *args: str) -> int:
        """Get a random int that is uniquely derived from the given args."""
        rnd = StableRandomness.get_random(seed, *args)
        return rnd.randrange(StableRandomness.MAX_RND_INT)


class TaskWithSafeCSVWriter(luigi.Task, metaclass=ABCMeta):
    @final
    def _safe_write_to_csv(self, data: Union[pd.DataFrame, pd.Series]):
        Path(self.output().path).parent.mkdir(parents=True, exist_ok=True)
        with self.output().temporary_path() as out:
            data.to_csv(out, index=False)
