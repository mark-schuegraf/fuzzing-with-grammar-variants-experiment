#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains a luigi task executing a subject with a generated input set.
"""

import logging
import os
import subprocess

import luigi
from luigi.util import inherits

from lib import generation
from lib import tooling
from lib import work_dir


@inherits(generation.GenerateInputs)
class RunSubjectAndProduceCoverageReport(luigi.Task):
    subject_name: str = luigi.Parameter(description="The name of the subject to run.")
    resources = {"ram": 1}

    def requires(self):
        return {
            "subject_jar": self.clone(tooling.BuildSubject),
            "original_jar": self.clone(tooling.DownloadOriginalBytecode),
            "inputs": self.clone(generation.GenerateInputs)
        }

    def run(self):
        self._run_subject_with_inputs()
        self._check_coverage_report_non_empty()

    def _run_subject_with_inputs(self):
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

    def _check_coverage_report_non_empty(self):
        output_path = self.output().path
        file_size = os.path.getsize(output_path)
        if not file_size:
            raise ValueError("Subject execution produced an empty coverage report file.")

    def output(self):
        return luigi.LocalTarget(
            work_dir / "coverage-reports" / self.language / self.transformation_name / self.fuzzing_strategy
            / self.subject_name / f"run-{self.run_number}" / "coverage.csv")
