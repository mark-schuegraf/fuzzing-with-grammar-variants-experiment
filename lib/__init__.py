#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import luigi


class ExperimentConfig(luigi.Config):
    tool_dir: str = luigi.Parameter(description="The path to the tool sources.")
    experiment_dir: str = luigi.Parameter(
        description="The path to where all the experiments happen. Should be outside the repository.")
    number_of_files_to_generate: int = luigi.IntParameter(
        description="The number of files that should be generated during each fuzzing run.")
    enable_plotting: bool = luigi.BoolParameter(description="Whether to produce coverage plots for each configuration.",
                                                default=False)


config = ExperimentConfig()
work_dir: Path = Path(config.experiment_dir)
tool_dir: Path = Path(config.tool_dir)
