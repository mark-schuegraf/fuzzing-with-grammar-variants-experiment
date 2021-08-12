#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains possible parameter values to experiment with.
"""

from lib import config

# TODO populate these collections
languages = [
    "json"
]

subjects = {
    "json": {"argo": "argo"}
}

fuzzing_strategies = [
    f"recurrent-2-path-{config.number_of_files_to_generate}"
]

"""Contains transformers with no prerequisite transformations."""
base_transformers = ["identity",
                     "backus-naur-formalizer"]

"""Maps transformers with prerequisite transformations to their required base transformers."""
follow_up_transformers = {
    "chomsky-normal-formalizer": "backus-naur-formalizer"
}

grammars = {
    "json": "json/json-org.scala"
}
