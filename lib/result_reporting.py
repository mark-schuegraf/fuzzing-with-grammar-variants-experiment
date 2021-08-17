#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains a luigi task that produces a result report.
It contains information on the experimental setup, as well as the results of conducting a Wilcoxon signed-rank test
and computing summary statistics on the paired differences of the evaluation metrics.
"""

from abc import ABCMeta
from statistics import mean, median
from typing import final

import luigi
import pandas as pd
from luigi.util import inherits

from lib import evaluation
from lib import utils
from lib import work_dir


@inherits(evaluation.EvaluateCoverageReports)
class ProduceResultReport(utils.TaskWithTemporaryPathCSVWriter, metaclass=ABCMeta):
    @final
    def _wilcoxon_diff_report(self, metric_name: str, after_transformation: pd.Series,
                              before_transformation: pd.Series) -> pd.DataFrame:
        diffs = after_transformation - before_transformation
        w_two_sided, p_two_sided = utils.safe_wilcoxon(diffs, alternative="two-sided")
        w_greater, p_greater = utils.safe_wilcoxon(diffs, alternative="greater")
        return pd.DataFrame(data={
            "language": [self.language],
            "transformation": [self.transformation_name],
            "fuzzing strategy": [self.generation_mode],
            "subject": [self.subject_name],
            "metric": metric_name,
            "mean difference": [(mean(diffs))],
            "median difference": [(median(diffs))],
            "min difference": [(min(diffs))],
            "max difference": [(max(diffs))],
            "wilcoxon (two-sided)": [w_two_sided],
            "p-value (two-sided)": [p_two_sided],
            "wilcoxon (greater)": [w_greater],
            "p-value (greater)": [p_greater],
        })


class ProduceCoverageReport(ProduceResultReport):
    def requires(self):
        return {
            "after_transformation": self.clone(evaluation.EvaluateCoverage),
            "before_transformation": self.clone(evaluation.EvaluateCoverage, transformation_name="identity",
                                                transformation_mode="")
        }

    def run(self):
        coverages_after = pd.read_csv(self.input()["after_transformation"].path)["coverage"]
        coverages_before = pd.read_csv(self.input()["before_transformation"].path)["coverage"]
        report = self._wilcoxon_diff_report("coverage", coverages_after, coverages_before)
        self._pd_write_to_csv_using_temporary_path(report)

    def output(self):
        return luigi.LocalTarget(
            work_dir / "results" / self.language / self.transformation_name / self.generation_mode / self.subject_name
            / "coverage" / "coverage-diff-report.csv")


class ProduceCoverageGrowthRateReport(ProduceResultReport):
    def requires(self):
        return {
            "after_transformation": self.clone(evaluation.EvaluateCoverageGrowthRate),
            "before_transformation": self.clone(evaluation.EvaluateCoverageGrowthRate, transformation_name="identity",
                                                transformation_mode="")
        }

    def run(self):
        growths_after = pd.read_csv(self.input()["after_transformation"].path)["coverage-growth-rate"]
        growths_before = pd.read_csv(self.input()["before_transformation"].path)["coverage-growth-rate"]
        report = self._wilcoxon_diff_report("coverage-growth-rate", growths_after, growths_before)
        self._pd_write_to_csv_using_temporary_path(report)

    def output(self):
        return luigi.LocalTarget(
            work_dir / "results" / self.language / self.transformation_name / self.generation_mode / self.subject_name
            / "coverage-growth-rate" / "coverage-growth-rate-diff-report.csv")
