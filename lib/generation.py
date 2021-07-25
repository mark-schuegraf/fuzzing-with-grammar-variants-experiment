#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks corresponding to tribble generation modes.
"""

import logging
import subprocess
from abc import ABCMeta, abstractmethod
from pathlib import Path

import luigi

from lib import subjects
from lib import tooling
from lib import transformations
from lib import utils
from lib import work_dir


class GenerateInputsWithTribble(luigi.Task, utils.StableRandomness, metaclass=ABCMeta):
    format: str = luigi.Parameter(description="The format specified by the input grammar.")
    number_of_files_to_generate: int = luigi.IntParameter(
        description="The number of files that the generation run should produce.")
    tribble_generation_seed: int = luigi.IntParameter(description="The seed for this tribble generation run.",
                                                      positional=False, significant=False)
    resources = {"ram": 4}

    @property
    @abstractmethod
    def tribble_generation_mode(self):
        raise NotImplementedError("Must specify a generation mode to use for fuzzing!")

    @property
    @abstractmethod
    def prerequisite_transformation_task(self):
        raise NotImplementedError("Must specify the transformation of the input grammar to perform beforehand!")

    @property
    def prerequisite_transformation_name(self):
        return self.requires()[1].transformation_name

    def requires(self):
        return tooling.BuildTribble(), self.clone(self.prerequisite_transformation_task)

    def run(self):
        tribble_jar = self.input()[0].path
        automaton_dir = work_dir / "tools" / "tribble-automaton-cache" / self.format
        transformed_grammar_file = self.input()[1].path
        format_info = subjects[self.format]
        # also make the seed depend on the output path starting from work_dir
        rel_output_path = Path(self.output().path).relative_to(work_dir)
        random_seed = self.random_int(self.tribble_generation_seed, self.format, self.tribble_generation_mode,
                                      *rel_output_path.parts)
        with self.output().temporary_path() as out:
            args = ["java",
                    "-Xss100m",
                    "-Xms256m",
                    f"-Xmx{self.resources['ram']}g",
                    "-jar", tribble_jar,
                    f"--random-seed={random_seed}",
                    f"--automaton-dir={automaton_dir}",
                    "--ignore-grammar-cache",
                    "--no-check-duplicate-alts",
                    "generate",
                    f'--suffix={format_info["suffix"]}',
                    f"--out-dir={out}",
                    f"--grammar-file={transformed_grammar_file}",
                    f"--loading-strategy={self.choose_loading_strategy_based_on_file_extension()}",
                    f"--mode={self.tribble_generation_mode}",
                    ]
            logging.info("Launching %s", " ".join(args))
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL)

    def choose_loading_strategy_based_on_file_extension(self):
        grammar_file_path = self.input()[1].path
        if grammar_file_path.endswith(".scala"):
            return "compile"
        elif grammar_file_path.endswith(".tribble"):
            return "parse"
        else:
            return "unmarshal"

    def output(self):
        return luigi.LocalTarget(work_dir / "inputs" / self.format / self.prerequisite_transformation_name)


class GenerateUsingRecurrentKPathNCoverageStrategy(GenerateInputsWithTribble, metaclass=ABCMeta):
    @property
    @abstractmethod
    def k(self):
        raise NotImplementedError("Must specify k to use recurrent k-path coverage strategy!")

    @property
    def tribble_generation_mode(self):
        return f"recurrent-{self.k}-path-{self.number_of_files_to_generate}"


class GenerateUsingRecurrent2PathNCoverageStrategy(GenerateUsingRecurrentKPathNCoverageStrategy, metaclass=ABCMeta):
    @property
    def k(self):
        return "2"

    @property
    @abstractmethod
    def prerequisite_transformation_task(self):
        return transformations.TransformGrammarChomsky


class GenerateUsingRecurrent2PathNCoverageStrategyAndChomskyGrammar(GenerateUsingRecurrent2PathNCoverageStrategy):
    @property
    def prerequisite_transformation_task(self):
        return transformations.TransformGrammarChomsky
