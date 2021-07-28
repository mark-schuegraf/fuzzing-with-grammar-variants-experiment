#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks executing each subject in the subject collection with the generated input set.
"""

import logging
import subprocess
from abc import ABCMeta

import luigi
from luigi.util import inherits

from lib import generation
from lib import modes
from lib import names
from lib import tooling
from lib import work_dir


@inherits(tooling.BuildSubject, tooling.DownloadOriginalBytecode)
class RunSubjectAndProduceCoverageReport(luigi.Task, names.WithCompoundTransformationName, modes.WithGenerationMode,
                                         metaclass=ABCMeta):
    resources = {"ram": 1}

    def requires(self):
        return {
            "subject_jar": self.clone(tooling.BuildSubject),
            "original_jar": self.clone(tooling.DownloadOriginalBytecode),
        }

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

    def output(self):
        return luigi.LocalTarget(
            work_dir / "results" / "raw" / self.format / self.generation_mode / self.compound_transformation_name
            / f"{self.subject_name}.coverage.csv")


@inherits(generation.GenerateUsingRecurrent2PathNCoverageStrategyWithChomskyGrammar)
class RunSubjectOnRecurrent2PathNCoverageInputsWithChomskyGrammar(RunSubjectAndProduceCoverageReport,
                                                                  names.WithChomskyCompoundTransformationName,
                                                                  modes.WithRecurrent2PathNCoverageGenerationMode):
    def requires(self):
        generation_task = generation.GenerateUsingRecurrent2PathNCoverageStrategyWithChomskyGrammar
        dependencies = super(RunSubjectOnRecurrent2PathNCoverageInputsWithChomskyGrammar, self).requires()
        dependencies["inputs"] = self.clone(generation_task)
        return dependencies
