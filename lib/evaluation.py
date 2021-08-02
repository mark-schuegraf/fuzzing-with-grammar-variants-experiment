#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks evaluating the coverage reports produced during subject execution.
"""

from abc import ABCMeta, abstractmethod
from typing import List

import luigi
import pandas as pd
from luigi.util import inherits

from lib import execution
from lib import metrics, work_dir
from lib import tooling
from lib import transformations
from lib import utils


@inherits(tooling.BuildSubject, transformations.TransformGrammarWithTribble)
class AggregateReducedCoverageReports(luigi.Task, utils.StableRandomness, metaclass=ABCMeta):
    total_number_of_runs: int = luigi.IntParameter(
        description="The number of runs to conduct per combination of transformation, fuzzer and subject.")

    def requires(self):
        # TODO move this out of here, have as parameter and then invoke with this on top level?
        format_seed = self.random_int(self.random_seed, self.format)
        run_numbers = range(self.total_number_of_runs)
        run_results = [self.clone(self.reduction_task, run_number=i, tribble_generation_seed=format_seed) for i in
                       run_numbers]
        return run_results

    @property
    @abstractmethod
    def reduction_task(self):
        raise NotImplementedError("Must specify the reduction task evaluating a metric on a single run's results!")

    def run(self):
        metric_values = self._read_metric_values_from_files()
        metric_series = self._concatenate_values_into_series(metric_values)
        self._safe_write_series_to_csv(metric_series)

    def _read_metric_values_from_files(self) -> List:
        return [pd.read_csv(file.path) for file in self.input()]

    @staticmethod
    def _concatenate_values_into_series(values: List) -> pd.Series:
        return pd.concat(values)

    def _safe_write_series_to_csv(self, series: pd.Series):
        with self.output().temporary_path() as out:
            series.to_csv(out, index=False)

    def output(self):
        return luigi.LocalTarget(
            work_dir / "results" / "processed" / self.format / self.subject_name / self.generation_mode /
            self.compound_transformation_name / self.metric_name / "values.csv")


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


class AggregateCoverageOverMultipleRuns(AggregateReducedCoverageReports,
                                        metrics.WithCoverageEvaluationMetric, metaclass=ABCMeta): pass


class AggregateCoverageWithRecurrent2PathWithOriginalGrammar(AggregateCoverageOverMultipleRuns):
    @property
    def reduction_task(self):
        return ReduceToCoverageWithRecurrent2PathWithOriginalGrammar


class AggregateCoverageWithRecurrent2PathWithChomskyGrammar(AggregateCoverageOverMultipleRuns):
    @property
    def reduction_task(self):
        return ReduceToCoverageWithRecurrent2PathWithChomskyGrammar


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


class AggregateCoverageGrowthRateOverMultipleRuns(AggregateReducedCoverageReports,
                                                  metrics.WithCoverageGrowthRateEvaluationMetric,
                                                  metaclass=ABCMeta): pass


class AggregateCoverageGrowthRateWithRecurrent2PathWithOriginalGrammar(AggregateCoverageGrowthRateOverMultipleRuns):
    @property
    def reduction_task(self):
        return ReduceToCoverageGrowthRateWithRecurrent2PathWithOriginalGrammar


class AggregateCoverageGrowthRateWithRecurrent2PathWithChomskyGrammar(AggregateCoverageGrowthRateOverMultipleRuns):
    @property
    def reduction_task(self):
        return ReduceToCoverageGrowthRateWithRecurrent2PathWithChomskyGrammar


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
