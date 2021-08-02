#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains mixins describing evaluation metrics for coverage time series.
The time series are expected to be pandas series containing cumulative branch coverages.
"""
from abc import ABCMeta, abstractmethod

import pandas as pd


class WithEvaluationMetric(metaclass=ABCMeta):
    @property
    @abstractmethod
    def metric_name(self) -> str:
        raise NotImplementedError("Must specify the name of the metric!")

    @abstractmethod
    def evaluate_metric_on_coverage_series(self, coverages: pd.Series) -> pd.Series:
        raise NotImplementedError("Must specify the implementation of the metric!")


class WithCoverageEvaluationMetric(WithEvaluationMetric):
    @property
    def metric_name(self) -> str:
        return "coverage"

    def evaluate_metric_on_coverage_series(self, coverages: pd.Series) -> pd.Series:
        return coverages.tail(1)


class WithCoverageGrowthRateEvaluationMetric(WithEvaluationMetric):
    @property
    def metric_name(self) -> str:
        return "coverage-growth-rate"

    def evaluate_metric_on_coverage_series(self, coverages: pd.Series) -> pd.Series:
        return coverages.sum()
