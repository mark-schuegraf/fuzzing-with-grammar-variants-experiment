#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains a luigi task that plots the coverage progressions across multiple runs for a specific configuration.
It does so using a seaborn scatter plot.
"""

import os

import luigi
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from lib import execution
from lib import work_dir


class RenderCoveragePlot(luigi.Task):
    language: str = luigi.Parameter(description="The language specified by the input grammar.")
    transformation_name: str = luigi.Parameter(description="The transformation to conduct.")
    fuzzing_strategy: str = luigi.Parameter(description="The fuzzing strategy to use for generation.")
    subject_name: str = luigi.Parameter(description="The name of the subject to run.")
    language_seed: int = luigi.IntParameter(description="The seed from which seeds for this language are derived.")
    total_number_of_runs: int = luigi.IntParameter(description="The number of runs to conduct per configuration.")

    def requires(self):
        run_numbers = range(self.total_number_of_runs)
        return {
            "after_transformation": [self.clone(execution.RunSubjectAndProduceCoverageReport, run_number=i)
                                     for i in run_numbers],
            "before_transformation": [self.clone(execution.RunSubjectAndProduceCoverageReport, run_number=i,
                                                 transformation_name="identity")
                                      for i in run_numbers]
        }

    def _read_csv_and_check_nonempty(self, path):
        csv = pd.read_csv(path, usecols=["filenum", "branch"])
        if csv.empty:
            raise ValueError(f"Empty coverage report read at path {path}.")
        return csv

    def _load_coverage_reports(self):
        after_paths = [file.path for file in self.input()["after_transformation"]]
        before_paths = [file.path for file in self.input()["before_transformation"]]
        after_coverages = [self._read_csv_and_check_nonempty(path) for path in after_paths]
        before_coverages = [self._read_csv_and_check_nonempty(path) for path in before_paths]
        return after_coverages, before_coverages

    def _concat_coverage_reports(self):
        after_coverages, before_coverages = self._load_coverage_reports()
        after_df = pd.concat(after_coverages)
        before_df = pd.concat(before_coverages)
        return after_df, before_df

    def _make_comparison_df(self):
        after_df, before_df = self._concat_coverage_reports()
        after_df["transformation"] = self.transformation_name
        before_df["transformation"] = "identity"
        return pd.concat((after_df, before_df), sort=False, ignore_index=True)

    def _make_title(self):
        return f"Language {self.language}, Subject {self.subject_name}, Strategy {self.fuzzing_strategy}"

    def _plot_scatter_coverage_comparison(self):
        sns.set(font_scale=1.75)
        fig = plt.figure(figsize=(20, 8))
        comparison_df = self._make_comparison_df()
        ax = sns.scatterplot(data=comparison_df, x="filenum", y="branch", hue="transformation", style="transformation",
                             markers=["^", "."], s=10, palette=["red", "blue"], alpha=0.05)
        title = self._make_title()
        ax.set_title(title)
        ax.set_xlabel("Number of Files")
        ax.set_ylabel("Branch Coverage")
        output_path = self.output().path
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, format="png", dpi=600, bbox_inches="tight")

    def run(self):
        self._plot_scatter_coverage_comparison()

    def output(self):
        return luigi.LocalTarget(
            work_dir / "plots" / self.language / self.transformation_name / self.fuzzing_strategy / self.subject_name
            / "coverage-plot.png")
