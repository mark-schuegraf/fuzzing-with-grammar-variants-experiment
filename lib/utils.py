#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains various utility mixins.
"""

import hashlib
import random
from pathlib import Path
from typing import Final


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


def remove_tree(path: Path) -> None:
    """Recursively removes the entire file tree under and including the given path."""
    if path.is_dir():
        for child in path.iterdir():
            remove_tree(child)
        path.rmdir()
    else:
        path.unlink()
