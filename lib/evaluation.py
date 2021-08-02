#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks evaluating the coverage reports produced during subject execution.
"""

from abc import ABCMeta, abstractmethod

import luigi
import pandas as pd
from luigi.util import inherits

from lib import execution
from lib import metrics, work_dir


class AggregateReducedCoverageReports(luigi.Task, metaclass=ABCMeta): pass
    #TODO implement this

@inherits(execution.RunSubjectAndProduceCoverageReport)
class ReduceIndividualCoverageReport(luigi.Task, metrics.WithEvaluationMetric, metaclass=ABCMeta):
    def requires(self):
        return self.clone(self.execution_task)

    @property
    @abstractmethod
    def execution_task(self):
        raise NotImplementedError("Must specify the execution task that runs the subject to produce a coverage report!")

    def run(self):
        coverages = self._read_coverages_into_series()
        value = self.evaluate_metric_on_coverage_series(coverages)
        self._write_metric_value_to_csv(value)

    def _read_coverages_into_series(self) -> pd.Series:
        coverage_file = self.input()
        return pd.read_csv(coverage_file.path, index_col="filename")["branch"]

    def _write_metric_value_to_csv(self, value: pd.Series):
        output_file = self.output()
        value.to_csv(output_file.path, index=False)

    def output(self):
        return luigi.LocalTarget(
            work_dir / "results" / "processed" / self.format / self.subject_name / self.generation_mode /
            self.compound_transformation_name / f"run-{self.run_number}" / self.metric_name / "value.csv")


"""
Achieved coverage evaluation.
"""


class ReduceReportWithCoverageMetric(ReduceIndividualCoverageReport,
                                     metrics.WithCoverageEvaluationMetric, metaclass=ABCMeta): pass


class ReduceToCoverageWithRecurrent2PathWithOriginalGrammar(ReduceReportWithCoverageMetric):
    @property
    def execution_task(self):
        return execution.RunSubjectWithRecurrent2PathNCoverageStrategyWithOriginalGrammar


class ReduceToCoverageWithRecurrent2PathWithChomskyGrammar(ReduceReportWithCoverageMetric):
    @property
    def execution_task(self):
        return execution.RunSubjectWithRecurrent2PathNCoverageStrategyWithChomskyGrammar


"""
Coverage growth rate evaluation.
"""


class ReduceReportWithCoverageGrowthRateMetric(ReduceIndividualCoverageReport,
                                               metrics.WithCoverageGrowthRateEvaluationMetric, metaclass=ABCMeta): pass


class ReduceToCoverageGrowthRateWithRecurrent2PathWithOriginalGrammar(ReduceReportWithCoverageGrowthRateMetric):
    @property
    def execution_task(self):
        return execution.RunSubjectWithRecurrent2PathNCoverageStrategyWithOriginalGrammar


class ReduceToCoverageGrowthRateWithRecurrent2PathWithChomskyGrammar(ReduceReportWithCoverageGrowthRateMetric):
    @property
    def execution_task(self):
        return execution.RunSubjectWithRecurrent2PathNCoverageStrategyWithChomskyGrammar
