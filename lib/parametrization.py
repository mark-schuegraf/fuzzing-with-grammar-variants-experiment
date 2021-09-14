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
    "ini",
    "dot",
]

suffixes = {
    "json": ".json",
    "url": ".txt",
    "markdown": ".md",
    "csv": ".csv",
    "javascript": ".js",
    "css": ".css",
    "ini": ".ini",
    "dot": ".dot",
}

# TODO find ini and dot grammars
grammars = {
    "json": "json-antlr.scala",
    "url": "url-antlr.scala",
    "markdown": "markdown-peg.scala",
    "csv": "csv-antlr.scala",
    "javascript": "js-antlr.scala",
    "css": "css3-antlr.scala",
    "ini": None,
    "dot": None,
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
        "nashorn-sandbox": "delight.nashornsandbox",
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
    "ini": {
        "fastini": "com.github.onlynight.fastini",
        "ini4j": "org.ini4j",
        "java-configparser": "ca.szc.configparser",
    },
    "dot": {
        "digraph-parser": "com.paypal.digraph.parser",
        "graphstream": "org.graphstream",
        "graphviz-java": "guru.nidi",
    },
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
