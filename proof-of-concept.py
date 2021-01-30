#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks to run the grammar transformation experiments.
"""
from collections import ChainMap
import logging
from pathlib import Path
from pprint import pformat
import sys
from typing import Any, Dict, List

import luigi
import pandas as pd


class Subjects(object):
    """This class houses the available subject collection."""

    def __init__(self):
        self._json_drivers = {
            "argo": "argo",
            "fastjson": "com.alibaba.fastjson",
            "genson": "com.owlike.genson",
            "gson": "com.google.gson",
            "json-flattener": "com.github.wnameless.json",
            "json-java": "org.json",
            "json-simple": "org.json.simple",
            "json-simple-cliftonlabs": "com.github.cliftonlabs.json_simple",
            "minimal-json": "com.eclipsesource.json",
            "pojo": "org.jsonschema2pojo",
        }
        self._url_drivers = {
            "autolink": "org.nibor.autolink",
            "jurl": "com.anthonynsimon.url",
            "url-detector": "com.linkedin.urls.detection",
        }

    @property
    def all_subjects(self) -> Dict[str, Dict[str, Any]]:
        return {
            "css": self.css_subjects,
            "javascript": self.javascript_subjects,
            "json-antlr": self.json_antlr_subjects,
            "json-org": self.json_org_subjects,
            "url-antlr": self.url_antlr_subjects,
            "url-w3c": self.uwl_w3c_subjects,
            "url-rfc": self.url_rfc_subjects,
            "url-living": self.url_living_standard_subjects,
            "expr": self.expr_subjects,
        }

    @property
    def expr_subjects(self) -> Dict[str, Any]:
        return {
            "suffix": ".txt",
            "grammar": "expr.scala",
            "drivers": {
                "term-rewriter": "saarland.cispa.toys",
            }
        }

    @property
    def url_living_standard_subjects(self) -> Dict[str, Any]:
        return {
            "suffix": ".txt",
            "grammar": "url/url-living.scala",
            "drivers": self._url_drivers,
        }

    @property
    def url_rfc_subjects(self) -> Dict[str, Any]:
        return {
            "suffix": ".txt",
            "grammar": "url/url-rfc.scala",
            "drivers": self._url_drivers,
        }

    @property
    def uwl_w3c_subjects(self) -> Dict[str, Any]:
        return {
            "suffix": ".txt",
            "grammar": "url/url-w3c.scala",
            "drivers": self._url_drivers,
        }

    @property
    def url_antlr_subjects(self) -> Dict[str, Any]:
        return {
            "suffix": ".txt",
            "grammar": "url/url-antlr.scala",
            "drivers": self._url_drivers,
        }

    @property
    def json_org_subjects(self) -> Dict[str, Any]:
        return {
            "suffix": ".json",
            "grammar": "json/json-org.scala",
            "drivers": self._json_drivers,
        }

    @property
    def json_antlr_subjects(self) -> Dict[str, Any]:
        return {
            "suffix": ".json",
            "grammar": "json/json-antlr.scala",
            "drivers": self._json_drivers,
        }

    @property
    def javascript_subjects(self) -> Dict[str, Any]:
        return {
            "suffix": ".js",
            "grammar": "javascript.scala",
            "drivers": {
                "closure": "com.google.javascript.jscomp",
                "rhino": "org.mozilla.javascript",
            }
        }

    @property
    def css_subjects(self) -> Dict[str, Any]:
        return {
            "suffix": ".css",
            "grammar": "css.scala",
            "drivers": {
                "batik-css": "org.apache.batik.css",
                "flute": "org.w3c.flute",
                "jstyleparser": "jstylepanet.sf.cssbox",
            }
        }


class ExperimentConfig(luigi.Config):
    experiment_dir: str = luigi.Parameter(description="The path to where all the experiments happen. Should be outside the repository.")
    tool_dir: str = luigi.Parameter(description="The path to the tool sources.")
    use_grammar_caching: bool = luigi.BoolParameter(description="Let tribble cache grammar files so it does not have to re-parse them on each invocation.")
    input_generation_mode: str = luigi.Parameter(description="Which mode to use when generating the inputs from the transformed grammars.")
    remove_randomly_generated_files: bool = luigi.BoolParameter(description="Remove the randomly generated files after we have acquired the execution metrics to save space.")

config = ExperimentConfig()
work_dir: Path = Path(config.experiment_dir)
tool_dir: Path = Path(config.tool_dir)

subjects: Dict[str, Dict[str, Any]] = Subjects().all_subjects  # Change subject subset selection statically here

drivers = ChainMap(*[d["drivers"] for d in subjects.values()])


class Experiment(luigi.Task):
    """Transform all input grammars of the requested format in the specified way. Then evaluate the coverage achieved by inputs generated from them."""
    transformation: int = luigi.IntParameter(description="The transformation to be performed. Must match a valid tribble transformation regex pattern.", positional=False)
    report_name: str = luigi.Parameter(description="The name of the report file.", positional=False, default="report")
    only_format: str = luigi.Parameter(description="Only run experiments for formats starting with this prefix.", positional=False, default="")


class ComputeCoverageStatistics(luigi.Task):
    """Computes conventional statistics on the coverage files."""

    # requires ReportCoverage for name in subject names

    #def output(self):
    #    return luigi.LocalTarget(work_dir / "median-coverages.csv" /)


#class ReportCoverage(luigi.Task):


#class RunSubject(luigi.Task):
# requires BuildSubject, DownloadOriginalBytecode, GenerateInputs


#class BuildSubject(luigi.Task):


#class DownloadOriginalBytecode(luigi.Task):


#class GenerateInputs(luigi.Task):
# requires RunTribbleGenerationMode


#class RunTribbleGenerationMode(luigi.Task):
# requires TransformGrammar


#class TransformGrammar(luigi.Task):
# requires RunTribbleGenerationMode


#class RunTribbleTransformationMode(luigi.Task):
# requires BuildTribble


#class BuildTribble(luigi.Task):


# TODO add run monitoring later
if __name__ == '__main__':
    luigi.BoolParameter.parsing = luigi.BoolParameter.EXPLICIT_PARSING # TODO: why do we / do we need this?
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", datefmt="%d.%m.%Y %H:%M:%S", level=logging.INFO, stream=sys.stdout)
    luigi.run(main_task_cls=Experiment)
