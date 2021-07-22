#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Any, Dict

import luigi

from lib import subject_collection


class ExperimentConfig(luigi.Config):
    tool_dir: str = luigi.Parameter(description="The path to the tool sources.")
    experiment_dir: str = luigi.Parameter(
        description="The path to where all the experiments happen. Should be outside the repository.")


config = ExperimentConfig()
work_dir: Path = Path(config.experiment_dir)
tool_dir: Path = Path(config.tool_dir)
subjects: Dict[str, Dict[str, Any]] = subject_collection.Subjects().all_subjects
