#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains possible parameter values to experiment with.
"""

from typing import Dict, Optional

from lib import config

languages = [
    "json",
    "url",
    "markdown",
    "csv",
    "javascript",
    "css",
]

suffixes = {
    "json": ".json",
    "url": ".txt",
    "markdown": ".md",
    "csv": ".csv",
    "javascript": ".js",
    "css": ".css",
}

grammars = {
    "json": "json-antlr.scala",
    "url": "url-antlr.scala",
    "markdown": "markdown-peg.scala",
    "csv": "csv-antlr.scala",
    "javascript": "js-antlr.scala",
    "css": "css3-antlr.scala",
}

subjects = {
    "json": {
        "argo": "argo",
        "fastjson": "com.alibaba.fastjson",
        "genson": "com.owlike.genson",
        "gson": "com.google.gson",
        "jackson-databind": "com.fasterxml.jackson",
        "json-flattener": "com.github.wnameless.json",
        "json-java": "org.json",
        "json-simple-cliftonlabs": "com.github.cliftonlabs.json_simple",
        "json-simple": "org.json.simple",
        "json2flat": "com.github.opendevl",
        "minimal-json": "com.eclipsesource.json",
        "pojo": "org.jsonschema2pojo",
    },
    "url": {
        "autolink": "org.nibor.autolink",
        "galimatias-nu": "io.mola.galimatias",
        "galimatias": "io.mola.galimatias",
        "jurl": "com.anthonynsimon.url",
        "url-detector": "com.linkedin.urls.detection",
    },
    "markdown": {
        "commonmark": "org.commonmark",
        "flexmark": "com.vladsch.flexmark",
        "markdown-papers": "org.tautua.markdownpapers",
        "markdown4j": "org.markdown4j",
        "markdownj": "org.markdownj",
        "txtmark": "com.github.rjeschke.txtmark",
    },
    "csv": {
        "commons-csv": "org.apache.commons.csv",
        "jackson-dataformat-csv": "com.fasterxml.jackson.dataformat",
        "jcsv": "com.googlecode.jcsv",
        "sfm-csv": "org.simpleflatmapper.csv",
        "simplecsv": "net.quux00.simplecsv",
        "super-csv": "org.supercsv",
    },
    "javascript": {
        "closure": "com.google.javascript.jscomp",
        # "nashorn-sandbox": "delight.nashornsandbox",  deprecated
        "rhino-sandbox": "delight.rhinosandox",
        "rhino": "org.mozilla.javascript",
    },
    "css": {
        "batik-css": "org.apache.batik.css",
        # "css-validator": "org.w3c.css.css",           unsupported due to Jacoco Error
        # "cssparser": "net.sourceforge.cssparser",     unsupported due to Jacoco Error
        "flute": "org.w3c.flute",
        "jstyleparser": "net.sf.cssbox",
        # "ph-css": "com.helger.css",                   unsupported due to Jacoco Error
    },
}

# does not contain tree-size-limited random, because tree size is arbitrary
fuzzing_strategies = [
    # uses arbitrary depth limit to solve bloating problem
    "depth-limited-random",
    # Grammarinator-like, but no cooldown 0.9
    "grammarinator",
    # sentence generator, covers all productions
    "purdom",
    # most successful k-path coverage strategy
    "3-path-coverage",
    # estimates full path coverage
    "5-path-coverage",
]

"""Maps fuzzing strategies to tribble generation modes."""
fuzzers = {
    "depth-limited-random": f"10-depth-random-{config.number_of_files_to_generate}",
    "grammarinator": f"10-depth-random-{config.number_of_files_to_generate}",
    "purdom": f"recurrent-2-path-{config.number_of_files_to_generate}",
    "3-path-coverage": f"recurrent-3-path-{config.number_of_files_to_generate}",
    "5-path-coverage": f"recurrent-5-path-{config.number_of_files_to_generate}",
}

"""Maps fuzzing strategies to tribble-supported heuristics."""
heuristics = {
    "depth-limited-random": "random",
    "grammarinator": "least-recently-used",
    "purdom": "random",
    "3-path-coverage": "random",
    "5-path-coverage": "random",
}

# does not contain normal form substeps as well as most elementary transformations:
# although supported by tribble, their effect is largely summarized by their containing normal forms
"""Maps transformation names to the transformer that conducts them."""
transformations = {
    # normal forms
    "backus-naur-form": "backus-naur-formalizer",
    "chomsky-normal-form": "chomsky-normal-formalizer",
    "extended-chomsky-normal-form": "extended-chomsky-normal-formalizer",
    "greibach-normal-form": "greibach-normal-formalizer",
    "extended-greibach-normal-form": "extended-greibach-normal-formalizer",
    # grammar adaptation framework
    "1-level-rule-inlining": "1-level-rule-inlining",
}

"""Maps transformers to their prerequisite transformers or None if they have no preconditions."""
transformers: Dict[str, Optional[str]] = {
    # normal forms
    "backus-naur-formalizer": None,
    "extended-chomsky-normal-formalizer": "backus-naur-formalizer",
    "chomsky-normal-formalizer": "backus-naur-formalizer",
    "extended-greibach-normal-formalizer": "extended-chomsky-normal-formalizer",
    "greibach-normal-formalizer": "chomsky-normal-formalizer",
    # grammar adaptation framework
    "1-level-rule-inlining": None,
}
