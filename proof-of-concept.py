#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks to run the grammar transformation experiments.
"""
import logging
import os
from pathlib import Path
import platform
from pprint import pformat
import shutil
import subprocess
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
            "url-w3c": self.url_w3c_subjects,
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
    def url_w3c_subjects(self) -> Dict[str, Any]:
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
    tool_dir: str = luigi.Parameter(description="The path to the tool sources.")
    experiment_dir: str = luigi.Parameter(description="The path to where all the experiments happen. Should be outside the repository.")
    grammar_transformation_mode: str = luigi.Parameter(description="Which mode to use when transforming grammars.")
    input_generation_mode: str = luigi.Parameter(description="Which mode to use when generating inputs from the transformed grammars.")
    only_format: str = luigi.Parameter(description="Only run experiments for formats starting with this prefix.")
    remove_randomly_generated_files: bool = luigi.BoolParameter(description="Remove the randomly generated files after we have acquired the execution metrics to save space.")


config = ExperimentConfig()
work_dir: Path = Path(config.experiment_dir)
tool_dir: Path = Path(config.tool_dir)
subjects: Dict[str, Dict[str, Any]] = Subjects().all_subjects  # Change subject subset selection statically here


class GradleTask(object):
    @staticmethod
    def gradlew(*commands: str) -> List[str]:
        """Constructs a platform-appropriate gradle wrapper call string."""
        invocation = ["cmd", "/c", "gradlew.bat"] if platform.system() == "Windows" else ["./gradlew"]
        if commands:
            invocation.extend(commands)
        return invocation


class BuildSubject(luigi.Task, GradleTask):
    """Builds the given subject and copies it into the working directory."""
    subject_name: str = luigi.Parameter(description="The name of the subject to build", positional=False)

    def output(self):
        return luigi.LocalTarget(tool_dir / "build" / "subjects" / f"{self.subject_name}-subject.jar")

    def run(self):
        subprocess.run(self.gradlew("build", "-p", self.subject_name), check=True, cwd=tool_dir / "subjects", stdout=subprocess.DEVNULL)
        artifact = tool_dir / "subjects" / self.subject_name / "build" / "libs" / f"{self.subject_name}-subject.jar"
        os.makedirs(os.path.dirname(self.output().path), exist_ok=True)
        shutil.copy(str(artifact), self.output().path)


class DownloadOriginalBytecode(luigi.Task, GradleTask):
    """Downloads the unmodified bytecode of the subject and places it into the working directory."""
    subject_name: str = luigi.Parameter(description="The name of the subject to build", positional=False)

    def output(self):
        return luigi.LocalTarget(tool_dir / "build" / "subjects" / f"{self.subject_name}-original.jar")

    def run(self):
        subprocess.run(self.gradlew("downloadOriginalJar", "-p", self.subject_name), check=True, cwd=tool_dir / "subjects", stdout=subprocess.DEVNULL)
        artifact = tool_dir / "subjects" / self.subject_name / "build" / "libs" / f"{self.subject_name}-original.jar"
        os.makedirs(os.path.dirname(self.output().path), exist_ok=True)
        shutil.copy(str(artifact), self.output().path)


class BuildTribble(luigi.Task, GradleTask):
    """Builds the tribble jar and copies it into the working directory."""

    def output(self):
        return luigi.LocalTarget(tool_dir / "build" / "tribble.jar")

    def run(self):
        subprocess.run(self.gradlew("assemble", "-p", "tribble-tool"), check=True, cwd=tool_dir / "tribble", stdout=subprocess.DEVNULL)
        build_dir = tool_dir / "tribble" / "tribble-tool" / "build" / "libs"
        artifact = next(build_dir.glob("**/tribble*.jar"))
        os.makedirs(os.path.dirname(self.output().path), exist_ok=True)
        shutil.copy(str(artifact), self.output().path)


class RunTribbleTransformationMode(luigi.Task):
    """Transforms one grammar into another with tribble."""
    format: str = luigi.Parameter(description="The name of the format directory (e.g. json)", positional=False)

    def requires(self):
        return BuildTribble()

    def output(self):
        return luigi.LocalTarget(work_dir / "transformed-grammars" / config.grammar_transformation_mode
                                 / subjects[self.format]["grammar"])

    def run(self):
        automaton_dir = work_dir / "tribble-automaton-cache" / self.format
        grammar_file = Path("grammars") / subjects[self.format]["grammar"]
        tribble_jar = self.input().path
        with self.output().temporary_path() as out:
            args = ["java",
                    "-jar", tribble_jar,
                    f"--automaton-dir={automaton_dir}",
                    "--ignore-grammar-cache",
                    "--no-check-duplicate-alts",  # transformations are allowed to produce duplicate alternatives
                    "transform-grammar",
                    f"--mode={config.grammar_transformation_mode}"
                    f"--grammar-file={grammar_file}",
                    f"--output-grammar-file={out}",
                    ]
            logging.info("Launching %s", " ".join(args))
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


class RunTribbleGenerationMode(luigi.Task):
    """Generates inputs with tribble using a transformed grammar."""
    format: str = luigi.Parameter(description="The name of the format directory (e.g. json)", positional=False)

    def requires(self):
        return {
            "transformed-grammar": RunTribbleTransformationMode(self.format),
            "tribble": BuildTribble()
        }

    def output(self):
        return luigi.LocalTarget(work_dir / "inputs" / config.grammar_transformation_mode / self.format)

    def run(self):
        subject = subjects[self.format]
        automaton_dir = work_dir / "tribble-automaton-cache" / self.format
        transformed_grammar_file = self.input()["transformed-grammar"].path
        tribble_jar = self.input()["tribble"].path
        with self.output().temporary_path() as out:
            args = ["java",
                    "-jar", tribble_jar,
                    f"--automaton-dir={automaton_dir}",
                    "--ignore-grammar-cache",
                    "--no-check-duplicate-alts",  # transformations are allowed to produce duplicate alternatives
                    "generate",
                    f'--suffix={subject["suffix"]}',
                    f"--out-dir={out}",
                    f"--grammar-file={transformed_grammar_file}",
                    f"--mode={config.input_generation_mode}"
                    ]
            logging.info("Launching %s", " ".join(args))
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


class RunSubject(luigi.Task):
    """Runs the given subject with the given inputs and produces a cumulative coverage report at the given location."""
    format: str = luigi.Parameter(description="The name of the format directory (e.g. json) containing inputs", positional=False)
    subject_name: str = luigi.Parameter(description="The name of the subject to build", positional=False)

    def requires(self):
        return {
            "inputs": RunTribbleGenerationMode(self.format),
            "subject_jar": BuildSubject(self.subject_name),
            "original_jar": DownloadOriginalBytecode(self.subject_name)
        }

    def output(self):
        return luigi.LocalTarget(work_dir / "results" / "raw" / config.grammar_transformation_mode
                                 / f"{self.subject_name}.coverage.csv")

    def run(self):
        output_path = self.output().path
        input_path = self.input()["inputs"].path
        subject_jar = self.input()["subject_jar"].path
        original_jar = self.input()["original_jar"].path
        args = ["java",
                "-jar", subject_jar,
                "--ignore-exceptions",
                "--report-coverage", output_path,
                "--cumulative",
                "--original-bytecode", original_jar,
                input_path,
                ]
        logging.info("Launching %s", " ".join(args))
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


class ComputeCoverageStatistics(luigi.Task):
    """Computes conventional statistics on the coverage files."""

    @property
    def _selected_subjects(self) -> Dict[str, List[str]]:
        subject_info = {fmt: list(info["drivers"].keys()) for fmt, info in subjects.items() if fmt.startswith(config.only_format)}
        if not subject_info:
            raise ValueError(f"There are no formats starting with {config.only_format}!")
        return subject_info

    def requires(self):
        d = {
            fmt:    {
                    driver:
                    RunSubject(format=fmt,
                               subject_name=driver)
                    for driver
                    in drivers
                    }
            for fmt, drivers
            in self._selected_subjects.items()
            }
        return d

    # TODO: calculate median branch coverage here by inspecting the last line of each subject coverage file using pandas
    # TODO: clean up generated inputs after calculation, if remove_randomly_generated_files is set
    # def run(self): ...
    # def output(self): ...


# Will later coordinate several runs and call the evaluation report producer
class Experiment(luigi.WrapperTask):
    """Transform all input grammars of the requested formats in the specified way. Then evaluate the coverage achieved by inputs generated from them."""
    # For when we actually generate reports:
    # report_name: str = luigi.Parameter(description="The name of the report file.", positional=False, default="report")

    def requires(self):
        return ComputeCoverageStatistics()


# TODO: add run monitoring later
if __name__ == '__main__':
    luigi.BoolParameter.parsing = luigi.BoolParameter.EXPLICIT_PARSING
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", datefmt="%d.%m.%Y %H:%M:%S", level=logging.INFO, stream=sys.stdout)
    luigi.build([Experiment()])
