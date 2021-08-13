#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks that evaluate a coverage report using an evaluation metric.
"""

from abc import ABCMeta, abstractmethod
from typing import final

import luigi
import pandas as pd

from lib import execution
from lib import utils
from lib import work_dir


class EvaluateCoverageReports(utils.TaskWithSafeCSVWriter, metaclass=ABCMeta):
    language: str = luigi.Parameter(description="The language specified by the input grammar.")
    transformation_mode: str = luigi.Parameter(description="The tribble transformation mode to use.")
    generation_mode: str = luigi.Parameter(description="The tribble generation mode to use.")
    subject_name: str = luigi.Parameter(description="The name of the subject to run.")
    language_seed: int = luigi.IntParameter(description="The seed from which seeds for this language are derived.")
    total_number_of_runs: int = luigi.IntParameter(description="The number of runs to conduct per configuration.")

    @final
    def requires(self):
        run_numbers = range(self.total_number_of_runs)
        return [self.clone(execution.RunSubjectAndProduceCoverageReport, run_number=i) for i in run_numbers]

    @final
    def run(self):
        run_results = [pd.read_csv(coverage_report.path, index_col="filename")["branch"] for coverage_report in
                       self.input()]
        metrics = [self._evaluate_individual_run(run_result) for run_result in run_results]
        aggregate = pd.concat(metrics)
        self._safe_write_to_csv(aggregate)

    @abstractmethod
    def _evaluate_individual_run(self, run_result: pd.Series) -> pd.Series:
        raise NotImplementedError("Must specify the evaluation metric.")


class EvaluateCoverage(EvaluateCoverageReports):
    @final
    def _evaluate_individual_run(self, run_result: pd.Series) -> pd.Series:
        return run_result.tail(1).rename("coverage")

    @final
    def output(self):
        return luigi.LocalTarget(
            work_dir / "metrics" / self.language / self.transformation_mode / self.generation_mode / self.subject_name
            / "coverage" / "coverage.csv")


class EvaluateCoverageGrowthRate(EvaluateCoverageReports):
    @final
    def _evaluate_individual_run(self, run_result: pd.Series) -> pd.Series:
        return pd.Series(data=run_result.sum(), name="coverage-growth-rate")

    @final
    def output(self):
        return luigi.LocalTarget(
            work_dir / "metrics" / self.language / self.transformation_mode / self.generation_mode / self.subject_name
            / "coverage-growth-rate" / "coverage-growth-rate.csv")
