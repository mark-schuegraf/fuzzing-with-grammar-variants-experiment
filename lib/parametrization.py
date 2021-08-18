#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains possible parameter values to experiment with.
"""

from typing import Dict, Optional

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

"""Maps transformation names to the transformer that conducts them."""
transformations = {
    "backus-naur-form": "backus-naur-formalizer",
    "chomsky-normal-form": "chomsky-normal-formalizer",
}

"""Maps transformers to their prerequisite transformers or None if they have no preconditions."""
transformers: Dict[str, Optional[str]] = {
    "backus-naur-formalizer": None,
    "chomsky-normal-formalizer": "backus-naur-formalizer"
}
