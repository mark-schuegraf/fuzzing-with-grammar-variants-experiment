#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks corresponding to each tribble transformation mode.
"""

import logging
import subprocess
from abc import ABCMeta, abstractmethod

import luigi
from luigi.util import inherits

from lib import generation
from lib import tooling
from lib import work_dir


@inherits(tooling.BuildSubject, tooling.DownloadOriginalBytecode, generation.GenerateInputsWithTribble)
class RunSubjectAndProduceCoverageReport(luigi.Task, metaclass=ABCMeta):
    resources = {"ram": 1}

    @property
    @abstractmethod
    def generation_task(self):
        raise NotImplementedError("Must specify the input generation method to perform beforehand!")

    @property
    def generation_strategy(self):
        return self.requires()["inputs"].generation_strategy

    @property
    def transformation_name(self):
        return self.requires()["inputs"].transformation_name

    def requires(self):
        return {
            "subject_jar": self.clone(tooling.BuildSubject),
            "original_jar": self.clone(tooling.DownloadOriginalBytecode),
            "inputs": self.clone(self.generation_task)
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
            work_dir / "results" / "raw" / self.format / self.generation_strategy / self.transformation_name
            / f"{self.subject_name}.coverage.csv")


class RunSubjectOnRecurrent2PathNCoverageInputsWithChomskyGrammar(RunSubjectAndProduceCoverageReport):
    @property
    def generation_task(self):
        return generation.GenerateUsingRecurrent2PathNCoverageStrategyWithChomskyGrammar
