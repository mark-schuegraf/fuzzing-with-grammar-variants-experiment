#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains possible parameter values to experiment with.
"""

from lib import config

# TODO populate these collections
languages = [
    "json",
    "url",
]

suffixes = {
    "json": ".json",
    "url": ".txt",
}

grammars = {
    "json": "json/json-org.scala",
    "url": "url/url-rfc.scala",
}

subjects = {
    "json": {
        "argo": "argo",
        "json-simple": "org.json.simple",
    },
    "url": {
        "jurl": "com.anthonynsimon.url",
    }
}

fuzzing_strategies = [
    f"200-random-{config.number_of_files_to_generate}",
    f"recurrent-2-path-{config.number_of_files_to_generate}",
]

"""Contains transformers with no prerequisite transformations."""
base_transformers = [
    "identity",
    "backus-naur-formalizer",
]

"""Maps transformers with prerequisite transformations to their required base transformers."""
follow_up_transformers = {
    "chomsky-normal-formalizer": "backus-naur-formalizer",
}
