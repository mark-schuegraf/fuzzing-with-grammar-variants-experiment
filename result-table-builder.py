#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains post-processing functionality to concatenate result reports into a single table.
"""

import glob

import pandas as pd

from lib import work_dir


class StatisticsReportLoader:
    def __init__(self, transformation: str, metric: str, language:str):
        self._transformation = transformation
        self._metric = metric
        self._language = language

    def _create_path_pattern(self):
        transformation_subdir = f"{work_dir}/results/{self._language}/{self._transformation}/*/*"
        metric_suffix = f"{self._metric}/{self._metric}-diff-report.csv"
        return f"{transformation_subdir}/{metric_suffix}"

    def _find_matching_paths(self):
        pattern = self._create_path_pattern()
        matching_paths = glob.glob(pattern, recursive=True)
        no_paths = not matching_paths
        if no_paths:
            raise FileNotFoundError(
                f"No matching {self._metric} statistics reports found for {self._transformation}.")
        return matching_paths

    def _read_csv_and_check_nonempty(self, path):
        csv = pd.read_csv(path)
        if csv.empty:
            raise ValueError(
                f"Empty {self._metric} statistics report read for {self._transformation}, path = {path}.")
        formatted_csv = csv.drop(["metric", "transformation", "language", "wilcoxon (two-sided)",
                                  "wilcoxon (greater)"], axis=1)
        return formatted_csv

    def load_statistics_reports(self):
        report_paths = self._find_matching_paths()
        return [self._read_csv_and_check_nonempty(path) for path in report_paths]


class TableBuilder:
    def __init__(self, transformation: str, metric: str, language:str):
        self._loader = StatisticsReportLoader(transformation, metric, language)

    def _concat_statistics_reports(self):
        statistics_reports = self._loader.load_statistics_reports()
        df = pd.concat(statistics_reports)
        sorted_df = df.sort_values(["subject", "fuzzing strategy"])
        return sorted_df

    def build_metric_table_and_write_to_file(self):
        df = self._concat_statistics_reports()
        df.set_index(["subject", "fuzzing strategy"], inplace=True)
        df.to_latex("table.tex", multirow=True)


# Replace these strings to change the configuration for which a table should be built:
target_transformation = "chomsky-normal-form"
target_metric = "coverage"
target_language = "csv"

reporter = TableBuilder(target_transformation, target_metric, target_language)
reporter.build_metric_table_and_write_to_file()
