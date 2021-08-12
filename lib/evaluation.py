#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks evaluating the coverage reports produced during subject execution.
"""

from abc import ABCMeta, abstractmethod
from pathlib import Path
from statistics import mean, median
from typing import List, final, Union

import luigi
import pandas as pd
from luigi.util import inherits

from lib import execution
from lib import generation
from lib import metrics
from lib import modes
from lib import names
from lib import utils
from lib import work_dir


class TaskWithSafeCSVWriter(luigi.Task, metaclass=ABCMeta):
    @final
    def _safe_write_to_csv(self, data: Union[pd.DataFrame, pd.Series]):
        Path(self.output().path).parent.mkdir(parents=True, exist_ok=True)
        with self.output().temporary_path() as out:
            data.to_csv(out, index=False)


@inherits(execution.RunSubjectAndProduceCoverageReport)
class ReduceIndividualCoverageReport(TaskWithSafeCSVWriter, metrics.WithEvaluationMetric,
                                     names.WithCompoundTransformationName,
                                     modes.WithGenerationMode, metaclass=ABCMeta):
    @final
    def requires(self):
        return self.clone(self.execution_task)

    @property
    @abstractmethod
    def execution_task(self):
        raise NotImplementedError("Must specify the execution task that runs the subject to produce a coverage report!")

    @final
    def run(self):
        coverages = self._read_coverages_into_series()
        value = self.evaluate_metric_on_coverage_series(coverages)
        self._safe_write_to_csv(value)

    @final
    def _read_coverages_into_series(self) -> pd.Series:
        coverage_file = self.input()
        return pd.read_csv(coverage_file.path, index_col="filename")["branch"]

    @final
    def output(self):
        return luigi.LocalTarget(
            work_dir / "results" / "processed" / self.language / self.subject_name / self.generation_mode /
            self.compound_transformation_name / f"run-{self.run_number}" / self.metric_name / "value.csv")


class AggregateReducedCoverageReports(TaskWithSafeCSVWriter, utils.StableRandomness, metrics.WithEvaluationMetric,
                                      names.WithCompoundTransformationName, modes.WithGenerationMode,
                                      metaclass=ABCMeta):
    total_number_of_runs: int = luigi.IntParameter(
        description="The number of runs to conduct per combination of transformation, fuzzer and subject.")
    subject_name: str = luigi.Parameter(description="The name of the subject to run.")
    language: str = luigi.Parameter(description="The language specified by the input grammar.")
    language_seed: int = luigi.IntParameter(
        description="The random seed from which tribble generation seeds for this language are derived.")

    @final
    def requires(self):
        run_numbers = range(self.total_number_of_runs)
        run_results = [self.clone(self.reduction_task, run_number=i) for i in
                       run_numbers]
        return run_results

    @property
    @abstractmethod
    def reduction_task(self):
        raise NotImplementedError("Must specify the reduction task evaluating a metric on a single run's results!")

    @final
    def run(self):
        metric_values = self._read_metric_values_from_files()
        metric_series = self._concatenate_values_into_series(metric_values)
        self._safe_write_to_csv(metric_series)

    @final
    def _read_metric_values_from_files(self) -> List:
        return [pd.read_csv(file.path) for file in self.input()]

    @staticmethod
    def _concatenate_values_into_series(values: List) -> pd.Series:
        return pd.concat(values)

    @final
    def output(self):
        return luigi.LocalTarget(
            work_dir / "results" / "processed" / self.language / self.subject_name / self.generation_mode /
            self.compound_transformation_name / self.metric_name / "aggregated" / "values.csv")


class ProduceEvaluationReport(TaskWithSafeCSVWriter, metrics.WithEvaluationMetric, names.WithCompoundTransformationName,
                              modes.WithGenerationMode, metaclass=ABCMeta):
    subject_name: str = luigi.Parameter(description="The name of the subject to run.")
    language: str = luigi.Parameter(description="The language specified by the input grammar.")

    @final
    def requires(self):
        return {
            "after_transformation": self.clone(self.after_aggregation_task),
            "before_transformation": self.clone(self.before_aggregation_task)
        }

    @property
    @abstractmethod
    def after_aggregation_task(self):
        raise NotImplementedError(
            "Must specify the aggregation task collecting the metric values of all runs after transformation!")

    @property
    @abstractmethod
    def before_aggregation_task(self):
        raise NotImplementedError(
            "Must specify the aggregation task collecting the metric values of all runs before transformation!")

    @final
    def run(self):
        inputs = self.input()
        report = self._wilcoxon_diff_report(inputs["after_transformation"], inputs["before_transformation"])
        self._safe_write_to_csv(report)

    @final
    def _wilcoxon_diff_report(self, after_transformation, before_transformation) -> pd.DataFrame:
        diffs = [a - b for a, b in zip(after_transformation, before_transformation)]
        w_two_sided, p_two_sided = utils.safe_wilcoxon(diffs, alternative="two-sided")
        w_greater, p_greater = utils.safe_wilcoxon(diffs, alternative="greater")
        w_less, p_less = utils.safe_wilcoxon(diffs, alternative="less")
        return pd.DataFrame(data={
            "language": [self.language],
            "subject": [self.subject_name],
            "transformation": [self.compound_transformation_name],
            "fuzzing strategy": [self.generation_mode],
            "mean difference": [(mean(diffs))],
            "median difference": [(median(diffs))],
            "min difference": [(min(diffs))],
            "max difference": [(max(diffs))],
            "wilcoxon (two-sided)": [w_two_sided],
            "p-value (two-sided)": [p_two_sided],
            "wilcoxon (greater)": [w_greater],
            "p-value (greater)": [p_greater],
            "wilcoxon (less)": [w_less],
            "p-value (less)": [p_less],
        })

    @final
    def output(self):
        return luigi.LocalTarget(
            work_dir / "results" / "processed" / self.language / self.subject_name / self.generation_mode /
            self.compound_transformation_name / self.metric_name / "report" / "wilcoxon-diff-report.csv")


"""
Achieved coverage evaluation.
"""


class ReduceReportWithCoverageMetric(ReduceIndividualCoverageReport,
                                     metrics.WithCoverageEvaluationMetric, metaclass=ABCMeta): pass


class ReduceToCoverageWithRecurrent2PathWithOriginalGrammar(ReduceReportWithCoverageMetric,
                                                            generation.WithRecurrent2PathNCoverageStrategyWithOriginalGrammar):
    @property
    def execution_task(self):
        return execution.RunSubjectWithRecurrent2PathNCoverageStrategyWithOriginalGrammar


class ReduceToCoverageWithRecurrent2PathWithChomskyGrammar(ReduceReportWithCoverageMetric,
                                                           generation.WithRecurrent2PathNCoverageStrategyWithChomskyGrammar):
    @property
    def execution_task(self):
        return execution.RunSubjectWithRecurrent2PathNCoverageStrategyWithChomskyGrammar


class AggregateCoverageOverMultipleRuns(AggregateReducedCoverageReports,
                                        metrics.WithCoverageEvaluationMetric, metaclass=ABCMeta): pass


class AggregateCoverageWithRecurrent2PathWithOriginalGrammar(AggregateCoverageOverMultipleRuns,
                                                             generation.WithRecurrent2PathNCoverageStrategyWithOriginalGrammar):
    @property
    def reduction_task(self):
        return ReduceToCoverageWithRecurrent2PathWithOriginalGrammar


class AggregateCoverageWithRecurrent2PathWithChomskyGrammar(AggregateCoverageOverMultipleRuns,
                                                            generation.WithRecurrent2PathNCoverageStrategyWithChomskyGrammar):
    @property
    def reduction_task(self):
        return ReduceToCoverageWithRecurrent2PathWithChomskyGrammar


"""
Coverage growth rate evaluation.
"""


class ReduceReportWithCoverageGrowthRateMetric(ReduceIndividualCoverageReport,
                                               metrics.WithCoverageGrowthRateEvaluationMetric, metaclass=ABCMeta): pass


class ReduceToCoverageGrowthRateWithRecurrent2PathWithOriginalGrammar(ReduceReportWithCoverageGrowthRateMetric,
                                                                      generation.WithRecurrent2PathNCoverageStrategyWithOriginalGrammar):
    @property
    def execution_task(self):
        return execution.RunSubjectWithRecurrent2PathNCoverageStrategyWithOriginalGrammar


class ReduceToCoverageGrowthRateWithRecurrent2PathWithChomskyGrammar(ReduceReportWithCoverageGrowthRateMetric,
                                                                     generation.WithRecurrent2PathNCoverageStrategyWithChomskyGrammar):
    @property
    def execution_task(self):
        return execution.RunSubjectWithRecurrent2PathNCoverageStrategyWithChomskyGrammar


class AggregateCoverageGrowthRateOverMultipleRuns(AggregateReducedCoverageReports,
                                                  metrics.WithCoverageGrowthRateEvaluationMetric,
                                                  metaclass=ABCMeta): pass


class AggregateCoverageGrowthRateWithRecurrent2PathWithOriginalGrammar(AggregateCoverageGrowthRateOverMultipleRuns,
                                                                       generation.WithRecurrent2PathNCoverageStrategyWithOriginalGrammar):
    @property
    def reduction_task(self):
        return ReduceToCoverageGrowthRateWithRecurrent2PathWithOriginalGrammar


class AggregateCoverageGrowthRateWithRecurrent2PathWithChomskyGrammar(AggregateCoverageGrowthRateOverMultipleRuns,
                                                                      generation.WithRecurrent2PathNCoverageStrategyWithChomskyGrammar):
    @property
    def reduction_task(self):
        return ReduceToCoverageGrowthRateWithRecurrent2PathWithChomskyGrammar
