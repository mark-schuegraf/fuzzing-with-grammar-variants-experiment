#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks executing each subject in the subject collection with the generated input set.
"""

import logging
import subprocess
from abc import ABCMeta
from typing import final

import luigi
from luigi.util import inherits

from lib import generation
from lib import modes
from lib import names
from lib import tooling
from lib import work_dir


@inherits(tooling.BuildSubject, tooling.DownloadOriginalBytecode, generation.GenerateInputsWithTribble)
class RunSubjectAndProduceCoverageReport(luigi.Task, names.WithCompoundTransformationName, modes.WithGenerationMode,
                                         metaclass=ABCMeta):
    run_number: int = luigi.IntParameter(
        description="The run number corresponding to the input set used to execute the subject.")
    resources = {"ram": 1}

    def requires(self):
        return {
            "subject_jar": self.clone(tooling.BuildSubject),
            "original_jar": self.clone(tooling.DownloadOriginalBytecode),
        }

    @final
    def run(self):
        subject_jar = self.input()["subject_jar"].path
        original_jar = self.input()["original_jar"].path
        input_path = self.input()["inputs"].path
        output_path = self.output().path
        args = ["java",
                "-Xss10m",
                "-Xms256m",
                f"-Xmx{self.resources['ram']}g",
                "-jar", subject_jar,
                "--ignore-exceptions",
                "--report-coverage", output_path,
                "--cumulative",
                "--original-bytecode", original_jar,
                input_path,
                ]
        logging.info("Launching %s", " ".join(args))
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL)

    @final
    def output(self):
        return luigi.LocalTarget(work_dir / "results" / "raw" / self.language / self.subject_name / self.generation_mode /
                                 self.compound_transformation_name / f"run-{self.run_number}" / "coverage.csv")


class RunSubjectWithRecurrent2PathNCoverageStrategyWithOriginalGrammar(RunSubjectAndProduceCoverageReport,
                                                                       generation.WithRecurrent2PathNCoverageStrategyWithOriginalGrammar):
    @final
    def requires(self):
        generation_task = generation.GenerateWithRecurrent2PathNCoverageStrategyWithOriginalGrammar
        dependencies = super(RunSubjectWithRecurrent2PathNCoverageStrategyWithOriginalGrammar, self).requires()
        dependencies["inputs"] = self.clone(generation_task)
        return dependencies


class RunSubjectWithRecurrent2PathNCoverageStrategyWithChomskyGrammar(RunSubjectAndProduceCoverageReport,
                                                                      generation.WithRecurrent2PathNCoverageStrategyWithChomskyGrammar):
    @final
    def requires(self):
        generation_task = generation.GenerateWithRecurrent2PathNCoverageStrategyWithChomskyGrammar
        dependencies = super(RunSubjectWithRecurrent2PathNCoverageStrategyWithChomskyGrammar, self).requires()
        dependencies["inputs"] = self.clone(generation_task)
        return dependencies
