#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains a luigi task that produces a result report.
It contains information on the experimental setup, as well as the results of conducting a Wilcoxon signed-rank test
and computing summary statistics on the paired differences of the evaluation metrics.
"""

from abc import ABCMeta
from typing import final

import luigi
import pandas as pd
from luigi.util import inherits

from lib import evaluation
from lib import utils
from lib import work_dir


@inherits(evaluation.EvaluateCoverageReports)
class ProduceResultReport(utils.TaskWithTemporaryPathCSVWriter, utils.Statistics, metaclass=ABCMeta):
    @final
    def _produce_diff_report(self, metric_name: str, after_transformation: pd.Series,
                             before_transformation: pd.Series) -> pd.DataFrame:
        diffs = after_transformation - before_transformation
        return pd.DataFrame(data={
            **self._make_report_header(metric_name),
            **self.make_summary_statistics_report(diffs),
            **self.make_wilcoxon_report(diffs)
        })

    @final
    def _make_report_header(self, metric_name: str):
        return {
            "metric": [metric_name],
            "transformation": [self.transformation_name],
            "language": [self.language],
            "fuzzing strategy": [self.generation_mode],
            "subject": [self.subject_name],
        }


class ProduceCoverageReport(ProduceResultReport):
    def requires(self):
        return {
            "after_transformation": self.clone(evaluation.EvaluateCoverage),
            "before_transformation": self.clone(evaluation.EvaluateCoverage, transformation_name="identity")
        }

    def run(self):
        coverages_after = pd.read_csv(self.input()["after_transformation"].path)["coverage"]
        coverages_before = pd.read_csv(self.input()["before_transformation"].path)["coverage"]
        report = self._produce_diff_report("coverage", coverages_after, coverages_before)
        self._pd_write_to_csv_using_temporary_path(report)

    def output(self):
        return luigi.LocalTarget(
            work_dir / "results" / self.language / self.transformation_name / self.generation_mode / self.subject_name
            / "coverage" / "coverage-diff-report.csv")


class ProduceCoverageGrowthRateReport(ProduceResultReport):
    def requires(self):
        return {
            "after_transformation": self.clone(evaluation.EvaluateCoverageGrowthRate),
            "before_transformation": self.clone(evaluation.EvaluateCoverageGrowthRate, transformation_name="identity")
        }

    def run(self):
        growths_after = pd.read_csv(self.input()["after_transformation"].path)["coverage-growth-rate"]
        growths_before = pd.read_csv(self.input()["before_transformation"].path)["coverage-growth-rate"]
        report = self._produce_diff_report("coverage-growth-rate", growths_after, growths_before)
        self._pd_write_to_csv_using_temporary_path(report)

    def output(self):
        return luigi.LocalTarget(
            work_dir / "results" / self.language / self.transformation_name / self.generation_mode / self.subject_name
            / "coverage-growth-rate" / "coverage-growth-rate-diff-report.csv")
