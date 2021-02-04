#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks to run the grammar transformation experiments.
"""
from collections import ChainMap
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
    tool_dir: str = luigi.Parameter(description="The path to the tool sources.")
    experiment_dir: str = luigi.Parameter(description="The path to where all the experiments happen. Should be outside the repository.")
    grammar_transformation_mode: str = luigi.Parameter(description="Which mode to use when transforming grammars.")
    input_generation_mode: str = luigi.Parameter(description="Which mode to use when generating inputs from the transformed grammars.")
    remove_randomly_generated_files: bool = luigi.BoolParameter(description="Remove the randomly generated files after we have acquired the execution metrics to save space.")


config = ExperimentConfig()
work_dir: Path = Path(config.experiment_dir)
tool_dir: Path = Path(config.tool_dir)
subjects: Dict[str, Dict[str, Any]] = Subjects().all_subjects  # Change subject subset selection statically here
drivers = ChainMap(*[d["drivers"] for d in subjects.values()])  # TODO: probably don't want this


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
        return luigi.LocalTarget(work_dir / "tools" / "subjects" / self.subject_name / f"{self.subject_name}-subject.jar")

    def run(self):
        subprocess.run(self.gradlew("build", "-p", self.subject_name), check=True, cwd=tool_dir / "subjects", stdout=subprocess.DEVNULL)
        artifact = tool_dir / "subjects" / self.subject_name / "build" / "libs" / f"{self.subject_name}-subject.jar"
        os.makedirs(os.path.dirname(self.output().path), exist_ok=True)
        shutil.copy(str(artifact), self.output().path)


class DownloadOriginalBytecode(luigi.Task, GradleTask):
    """Downloads the unmodified bytecode of the subject and places it into the working directory."""
    subject_name: str = luigi.Parameter(description="The name of the subject to build", positional=False)

    def output(self):
        return luigi.LocalTarget(work_dir / "tools" / "subjects" / self.subject_name / f"{self.subject_name}-original.jar")

    def run(self):
        subprocess.run(self.gradlew("downloadOriginalJar", "-p", self.subject_name), check=True, cwd=tool_dir / "subjects", stdout=subprocess.DEVNULL)
        artifact = tool_dir / "subjects" / self.subject_name / "build" / "libs" / f"{self.subject_name}-original.jar"
        os.makedirs(os.path.dirname(self.output().path), exist_ok=True)
        shutil.copy(str(artifact), self.output().path)


class BuildTribble(luigi.Task, GradleTask):
    """Builds the tribble jar and copies it into the working directory."""

    def output(self):
        return luigi.LocalTarget(work_dir / "tools" / "tribble.jar")

    def run(self):
        subprocess.run(self.gradlew("assemble", "-p", "tribble-tool"), check=True, cwd=tool_dir / "tribble", stdout=subprocess.DEVNULL)
        build_dir = tool_dir / "tribble" / "tribble-tool" / "build" / "libs"
        artifact = next(build_dir.glob("**/tribble*.jar"))
        os.makedirs(os.path.dirname(self.output().path), exist_ok=True)
        shutil.copy(str(artifact), self.output().path)


class RunTribbleTransformationMode(luigi.Task):
    """Transforms one grammar into another with tribble."""
    format: str = luigi.Parameter(description="The name of the format directory (e.g. json)", positional=False)
    # TODO: do we need a parameter for the output grammar file? Probably not.
    #  + At present, name output grammar like input grammar. Becomes a problem when multiple transformations are applied.
    #  + But then can also make new directory for each set of transformed grammars.
    # output_grammar_file: str = luigi.Parameter(description="Where to put the transformed grammar file.", positional=False)

    @property
    def grammar_name(self) -> str:
        subject = subjects[self.format]
        return subject["grammar"]

    def requires(self):
        return BuildTribble()

    def output(self):
        return luigi.LocalTarget(work_dir / "transformed-grammars" / self.grammar_name)

    def run(self):
        automaton_dir = work_dir / "tribble-automaton-cache" / self.format
        grammar_file = Path("grammars") / self.grammar_name
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
        return luigi.LocalTarget(work_dir / "inputs" / self.format)

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


class RunSubjectOnDirectory(luigi.Task):
    """Runs the given subject with the given inputs and produces a cumulative coverage report at the given location."""
    input_directory: str = luigi.Parameter(description="The directory with inputs to feed into the subject.", positional=False)
    subject_name: str = luigi.Parameter(description="The name of the subject to build", positional=False)
    report_file: str = luigi.Parameter(description="The path to the .csv cumulative coverage report.", positional=False)

    def requires(self):
        return {
            "inputs": RunTribbleGenerationMode(self.input_directory),
            "subject_jar": BuildSubject(self.subject_name),
            "original_jar": DownloadOriginalBytecode(self.subject_name)
        }

    def output(self):
        return luigi.LocalTarget(self.report_file)

    def run(self):
        subject_jar = self.input()["subject_jar"].path
        original_jar = self.input()["original_jar"].path
        input_path = self.input()["inputs"].path
        original_output = Path(self.output().path)
        args = ["java",
                "-jar", subject_jar,
                "--ignore-exceptions",
                "--report-coverage", original_output,
                "--cumulative",
                "--original-bytecode", original_jar,
                input_path,
                ]
        logging.info("Launching %s", " ".join(args))
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


class ComputeCoverageStatistics(luigi.Task):
    """Computes conventional statistics on the coverage files."""

    # TODO: apply bleach to eyes after reading this. WIP, broken in every regard.
    #  + What it should do: for each format, feed the corresponding inputs to all compatible drivers
    def requires(self):
        return {
                subj_name: RunSubjectOnDirectory(input_directory=str(work_dir / "inputs" / subjects[subj_name]["suffix"]),
                                                 report_file=str(work_dir / "inputs" / f"{subj_name}.coverage.csv"),
                                                 subject_name=subj_name)
                for subj_name
                in drivers
                }

    # TODO: calculate median branch coverage here by inspecting the last line of each subject coverage file using pandas
    # TODO: clean up generated inputs after calculation, if remove_randomly_generated_files is set
    # def run(self): ...

    # def output(self):
    #    return luigi.LocalTarget(work_dir / "evaluation" / "median-coverages.csv" )


# Currently does nothing, will later coordinate several runs
class Experiment(luigi.WrapperTask):
    """Transform all input grammars of the requested formats in the specified way. Then evaluate the coverage achieved by inputs generated from them."""
    # TODO support these later:
    # only_format: str = luigi.Parameter(description="Only run experiments for formats starting with this prefix.", positional=False, default="")
    # report_name: str = luigi.Parameter(description="The name of the report file.", positional=False, default="report")

    def requires(self):
        return ComputeCoverageStatistics()


# TODO: add run monitoring later
if __name__ == '__main__':
    luigi.BoolParameter.parsing = luigi.BoolParameter.EXPLICIT_PARSING
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", datefmt="%d.%m.%Y %H:%M:%S", level=logging.INFO, stream=sys.stdout)
    luigi.build([Experiment])
