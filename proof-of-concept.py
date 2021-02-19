#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks to run the grammar transformation experiments.
"""
import hashlib
import logging
import os
import platform
import random
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Final, List

import luigi
import pandas as pd
from luigi.util import requires


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
    experiment_dir: str = luigi.Parameter(
        description="The path to where all the experiments happen. Should be outside the repository.")


config = ExperimentConfig()
work_dir: Path = Path(config.experiment_dir)
tool_dir: Path = Path(config.tool_dir)
subjects: Dict[str, Dict[str, Any]] = Subjects().all_subjects


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
    subject_name: str = luigi.Parameter(description="The name of the subject to build")

    def output(self):
        return luigi.LocalTarget(work_dir / "tools" / "build" / "subjects" / f"{self.subject_name}-subject.jar")

    def run(self):
        subprocess.run(self.gradlew("build", "-p", self.subject_name), check=True, cwd=tool_dir / "subjects",
                       stdout=subprocess.DEVNULL)
        artifact = tool_dir / "subjects" / self.subject_name / "build" / "libs" / f"{self.subject_name}-subject.jar"
        os.makedirs(os.path.dirname(self.output().path), exist_ok=True)
        shutil.copy(str(artifact), self.output().path)


class DownloadOriginalBytecode(luigi.Task, GradleTask):
    """Downloads the unmodified bytecode of the subject and places it into the working directory."""
    subject_name: str = luigi.Parameter(description="The name of the subject to build")

    def output(self):
        return luigi.LocalTarget(work_dir / "tools" / "build" / "subjects" / f"{self.subject_name}-original.jar")

    def run(self):
        subprocess.run(self.gradlew("downloadOriginalJar", "-p", self.subject_name), check=True,
                       cwd=tool_dir / "subjects", stdout=subprocess.DEVNULL)
        artifact = tool_dir / "subjects" / self.subject_name / "build" / "libs" / f"{self.subject_name}-original.jar"
        os.makedirs(os.path.dirname(self.output().path), exist_ok=True)
        shutil.copy(str(artifact), self.output().path)


class BuildTribble(luigi.Task, GradleTask):
    """Builds the tribble jar and copies it into the working directory."""

    def output(self):
        return luigi.LocalTarget(work_dir / "tools" / "build" / "tribble.jar")

    def run(self):
        subprocess.run(self.gradlew("assemble", "-p", "tribble-tool"), check=True, cwd=tool_dir / "tribble",
                       stdout=subprocess.DEVNULL)
        build_dir = tool_dir / "tribble" / "tribble-tool" / "build" / "libs"
        artifact = next(build_dir.glob("**/tribble*.jar"))
        os.makedirs(os.path.dirname(self.output().path), exist_ok=True)
        shutil.copy(str(artifact), self.output().path)


@requires(BuildTribble)
class RunTribbleTransformationMode(luigi.Task, StableRandomness):
    """Transforms one grammar into another with tribble."""
    grammar_transformation_mode: str = luigi.Parameter(description="Which mode to use when transforming grammars.")
    format: str = luigi.Parameter(description="The format corresponding to the grammar to test.")
    tribble_transformation_seed: int = luigi.IntParameter(description="The seed for this tribble transformation run",
                                                          positional=False, significant=False)

    def output(self):
        return luigi.LocalTarget(work_dir / "transformed-grammars" / self.grammar_transformation_mode
                                 / f"{self.format}.scala")

    def run(self):
        tribble_jar = self.input().path
        automaton_dir = work_dir / "tools" / "tribble-automaton-cache" / self.format
        grammar_file = work_dir / "grammars" / subjects[self.format]["grammar"]
        # also make the seed depend on the output path starting from work_dir
        rel_output_path = Path(self.output().path).relative_to(work_dir)
        random_seed = self.random_int(self.tribble_transformation_seed, self.format, self.grammar_transformation_mode,
                                      *rel_output_path.parts)
        with self.output().temporary_path() as out:
            args = ["java",
                    "-jar", tribble_jar,
                    f"--random-seed={random_seed}",
                    f"--automaton-dir={automaton_dir}",
                    "--ignore-grammar-cache",
                    "--no-check-duplicate-alts",  # transformations are allowed to produce duplicate alternatives
                    "transform-grammar",
                    f"--grammar-file={grammar_file}",
                    f"--output-grammar-file={out}",
                    f"--mode={self.grammar_transformation_mode}",
                    ]
            logging.info("Launching %s", " ".join(args))
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


@requires(BuildTribble, RunTribbleTransformationMode)
class RunTribbleGenerationMode(luigi.Task, StableRandomness):
    """Generates inputs with tribble using a transformed grammar."""
    input_generation_mode: str = luigi.Parameter(description="Which mode to use when generating inputs.")
    tribble_generation_seed: int = luigi.IntParameter(description="The seed for this tribble generation run",
                                                      positional=False, significant=False)

    def output(self):
        return luigi.LocalTarget(work_dir / "inputs" / self.grammar_transformation_mode / self.format)

    def run(self):
        tribble_jar = self.input()[0].path
        transformed_grammar_file = self.input()[1].path
        automaton_dir = work_dir / "tools" / "tribble-automaton-cache" / self.format
        format_info = subjects[self.format]
        # also make the seed depend on the output path starting from work_dir
        rel_output_path = Path(self.output().path).relative_to(work_dir)
        random_seed = self.random_int(self.tribble_generation_seed, self.format, self.input_generation_mode,
                                      *rel_output_path.parts)
        with self.output().temporary_path() as out:
            args = ["java",
                    "-jar", tribble_jar,
                    f"--random-seed={random_seed}",
                    f"--automaton-dir={automaton_dir}",
                    "--ignore-grammar-cache",
                    "--no-check-duplicate-alts",  # transformations are allowed to produce duplicate alternatives
                    "generate",
                    f'--suffix={format_info["suffix"]}',
                    f"--out-dir={out}",
                    f"--grammar-file={transformed_grammar_file}",
                    f"--mode={self.input_generation_mode}",
                    ]
            logging.info("Launching %s", " ".join(args))
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


@requires(BuildSubject, DownloadOriginalBytecode, RunTribbleGenerationMode)
class RunSubject(luigi.Task):
    """Runs the given subject with the given inputs and produces a cumulative coverage report at the given location."""

    def output(self):
        return luigi.LocalTarget(work_dir / "results" / "raw" / self.grammar_transformation_mode
                                 / f"{self.subject_name}.coverage.csv")

    def run(self):
        subject_jar = self.input()[0].path
        original_jar = self.input()[1].path
        input_path = self.input()[2].path
        output_path = self.output().path
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


class EvaluateGrammar(luigi.Task, StableRandomness):
    """Summarizes the run results of one grammars' eligible subjects."""
    format: str = luigi.Parameter(description="The format corresponding to the grammar to test.")
    grammar_transformation_mode: str = luigi.Parameter(description="Which mode to use when transforming grammars.")
    input_generation_mode: str = luigi.Parameter(description="Which mode to use when generating inputs.")
    random_seed: int = luigi.IntParameter(
        description="The main seed for this experiment. All other random seeds will be derived from it.",
        positional=False)
    remove_randomly_generated_files: bool = luigi.BoolParameter(
        description="Remove the randomly generated files after we have acquired the execution metrics to save space.",
        parsing=luigi.BoolParameter.EXPLICIT_PARSING, default=False)

    def requires(self):
        fmt_subjects = {
            driver: self.clone(RunSubject, subject_name=driver,
                               tribble_generation_seed=self.random_int(self.random_seed, "tribble_generation_seed",
                                                                       self.format, driver),
                               tribble_transformation_seed=self.random_int(self.random_seed,
                                                                           "tribble_transformation_seed", self.format,
                                                                           driver),
                               )
            for driver
            in subjects[self.format]["drivers"].keys()
        }
        return fmt_subjects

    def run(self):
        """
        Calculates the median cumulative branch coverage for each additional tested input.
        Assumes that each subject runner fed inputs to their subject in the same order.
        """
        # join coverage CSVs horizontally using input filename and retain only branch coverage
        joint_cumulative_branch_coverages = pd.concat(
            [pd.read_csv(cov_file.path, index_col="filename")["branch"] for cov_file in self.input().values()],
            axis=1, sort=False)
        # compute per-file medians of the branch coverage
        median_cumulative_branch_coverage = pd.DataFrame(joint_cumulative_branch_coverages.median(axis=1),
                                                         columns=["median-cumulative-branch"])
        # enumerate the files for pairwise difference evaluation
        filenum_annotated_medians = median_cumulative_branch_coverage.reset_index()
        # do so starting at 1
        filenum_annotated_medians.index += 1
        # rename index to "filenum"
        filenum_annotated_medians.index.rename("filenum", inplace=True)
        # write out DataFrame
        os.makedirs(os.path.dirname(self.output().path), exist_ok=True)
        with open(self.output().path, "w", newline="") as out:
            filenum_annotated_medians.to_csv(out, index=True)
        # clean up if desired
        if self.remove_randomly_generated_files:
            remove_tree(work_dir / "inputs" / self.grammar_transformation_mode / self.format)

    """ Later on, calculate further statistics on the subject runs for a single grammar here:
    1. Compute average characteristics of generated inputs
    2. Calculate other summary statistics like the mean over possibly other types of coverage
    """

    def output(self):
        return luigi.LocalTarget(work_dir / "results" / "processed" / self.grammar_transformation_mode / self.format
                                 / f"{self.format}.coverage-statistics.csv")


class EvaluateTransformation(luigi.WrapperTask, StableRandomness):
    """Computes conventional statistics on the transformation results of each grammar."""
    only_format: str = luigi.Parameter(description="Only run experiments for formats starting with this prefix.")
    grammar_transformation_mode: str = luigi.Parameter(description="Which mode to use when transforming grammars.")
    input_generation_mode: str = luigi.Parameter(description="Which mode to use when generating inputs.")
    random_seed: int = luigi.IntParameter(
        description="The main seed for this experiment. All other random seeds will be derived from it.",
        positional=False)
    remove_randomly_generated_files: bool = luigi.BoolParameter(
        description="Remove the randomly generated files after we have acquired the execution metrics to save space.",
        parsing=luigi.BoolParameter.EXPLICIT_PARSING, default=False)

    def requires(self):
        selected_fmts = {
            fmt: self.clone(EvaluateGrammar, format=fmt)
            for fmt
            in subjects.keys()
            if fmt.startswith(self.only_format)
        }
        if not selected_fmts:
            raise ValueError(f"There are no formats starting with {self.only_format}!")
        return selected_fmts

    """" Later on, calculate intergrammar statistics on the subject runs for a single transformation here:
    1. Compare the average characteristics of the per-grammar input sets to evaluate consistency of the transformation
    2. Aggregate per-grammar statistics from EvaluateGrammar to obtain more data for significance testing
    3. Move input cleanup here from EvaluateGrammar
    """


@requires(EvaluateTransformation)
class Experiment(luigi.WrapperTask):
    """Compares transformation results to judge their effectiveness."""
    report_name: str = luigi.Parameter(description="The name of the report file.", positional=False, default="report")

    """" Later on, yield out various post-processing tasks here:
    1. Invoke EvaluateTransformation on all candidate transformations as well as the test set
    2. Calculate the statistical significance of each candidate transformation
    3. Invoke the evaluation report producer / jupyter notebook renderer
    4. Write out report as {report_name}.ipynb
    """


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", datefmt="%d.%m.%Y %H:%M:%S", level=logging.INFO,
                        stream=sys.stdout)
    # TODO: add run monitoring later
    luigi.run(main_task_cls=Experiment)
