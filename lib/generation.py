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
from luigi.util import inherits

from lib import modes
from lib import names
from lib import subjects
from lib import tooling
from lib import transformations
from lib import utils
from lib import work_dir


@inherits(transformations.TransformGrammarWithTribble)
class GenerateInputsWithTribble(luigi.Task, utils.StableRandomness, names.WithCompoundTransformationName,
                                modes.WithGenerationMode, metaclass=ABCMeta):
    run_number: int = luigi.IntParameter(
        description="The run number corresponding to the input set produced during generation.")
    format_seed: int = luigi.IntParameter(
        description="The random seed from which tribble generation seeds for this format are derived.")
    resources = {"ram": 4}

    @property
    @abstractmethod
    def transformation_task(self):
        raise NotImplementedError("Must specify the transformation of the input grammar to perform beforehand!")

    def requires(self):
        return tooling.BuildTribble(), self.clone(self.transformation_task)

    def run(self):
        tribble_jar = self.input()[0].path
        automaton_dir = work_dir / "tools" / "tribble-automaton-cache" / self.format
        transformed_grammar_file = self.input()[1].path
        format_info = subjects[self.format]
        random_seed = self._derive_tribble_generation_seed_from_format_seed()
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
                    f"--loading-strategy={utils.choose_grammar_loading_strategy_based_on_file_extension(transformed_grammar_file)}",
                    f"--mode={self.generation_mode}",
                    ]
            logging.info("Launching %s", " ".join(args))
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL)

    def _derive_tribble_generation_seed_from_format_seed(self):
        # also make the seed depend on the output path starting from work_dir
        rel_output_path = Path(self.output().path).relative_to(work_dir)
        return self.random_int(self.format_seed, self.generation_mode, self.format,
                               str(self.run_number), *rel_output_path.parts)

    def output(self):
        return luigi.LocalTarget(
            work_dir / "inputs" / self.format / self.generation_mode / self.compound_transformation_name / f"run-{self.run_number}")


"""
Recurrent k-path coverage.
"""


class WithRecurrent2PathNCoverageStrategyWithOriginalGrammar(
    names.WithIdentityCompoundTransformationName, modes.WithRecurrent2PathNCoverageGenerationMode): pass


class GenerateWithRecurrent2PathNCoverageStrategyWithOriginalGrammar(GenerateInputsWithTribble,
                                                                     WithRecurrent2PathNCoverageStrategyWithOriginalGrammar):
    @property
    def transformation_task(self):
        return transformations.ProduceOriginalGrammar


class WithRecurrent2PathNCoverageStrategyWithChomskyGrammar(
    names.WithChomskyCompoundTransformationName, modes.WithRecurrent2PathNCoverageGenerationMode): pass


class GenerateWithRecurrent2PathNCoverageStrategyWithChomskyGrammar(GenerateInputsWithTribble,
                                                                    WithRecurrent2PathNCoverageStrategyWithChomskyGrammar):
    @property
    def transformation_task(self):
        return transformations.TransformGrammarChomsky
