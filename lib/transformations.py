#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks corresponding to each tribble transformation mode.
"""

import logging
import subprocess
from abc import ABCMeta, abstractmethod

import luigi

from lib import subjects
from lib import tooling
from lib import work_dir


class TransformGrammarWithTribble(luigi.Task, metaclass=ABCMeta):
    format: str = luigi.Parameter(description="The format specified by the input grammar.")
    resources = {"ram": 16}

    @property
    @abstractmethod
    def tribble_transformation_mode(self):
        raise NotImplementedError("Must specify a transformation mode to use for transformation!")

    @property
    @abstractmethod
    def prerequisite_transformation_task(self):
        raise NotImplementedError("Must specify the preconditions that must hold before transformation!")

    @property
    @abstractmethod
    def transformation_name(self):
        raise NotImplementedError("Must specify the name of the compound transformation that this is a substep of!")

    def requires(self):
        return tooling.BuildTribble(), self.clone(self.prerequisite_transformation_task)

    def run(self):
        tribble_jar = self.input()[0].path
        automaton_dir = work_dir / "tools" / "tribble-automaton-cache" / self.format
        with self.output().temporary_path() as out:
            args = ["java",
                    "-Xss100m",
                    "-Xms256m",
                    f"-Xmx{self.resources['ram']}g",
                    "-jar", tribble_jar,
                    f"--automaton-dir={automaton_dir}",
                    "--ignore-grammar-cache",
                    "--no-check-duplicate-alts",
                    "transform-grammar",
                    f"--grammar-file={self.input()[1].path}",
                    f"--output-grammar-file={out}",
                    f"--loading-strategy={self.choose_loading_strategy_based_on_file_extension}",
                    "--storing-strategy=marshal",
                    f"--mode={self.tribble_transformation_mode}",
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


class ElementaryTransformGrammarWithTribble(TransformGrammarWithTribble, metaclass=ABCMeta):
    def output(self):
        """If the transformation is elementary, store the intermediate grammar in a subdirectory of the target path."""
        return luigi.LocalTarget(
            work_dir / "transformed-grammars" / self.format / self.transformation_name / self.tribble_transformation_mode / self.format)


class CompoundTransformGrammarWithTribble(TransformGrammarWithTribble, metaclass=ABCMeta):
    def output(self):
        """If the transformation is compound, store the output grammar directly in the transformation directory."""
        return luigi.LocalTarget(
            work_dir / "transformed-grammars" / self.format / self.transformation_name / self.format)


class ProduceOriginalGrammar(luigi.ExternalTask):
    format: str = luigi.Parameter(description="The format specified by the input grammar.")

    def output(self):
        return luigi.LocalTarget(work_dir / "grammars" / subjects[self.format]["grammar"])


"""
Chomsky.
"""


class TransformGrammarChomskyStep1(ElementaryTransformGrammarWithTribble):
    @property
    def tribble_transformation_mode(self):
        return "backus-naur-formalizer"

    @property
    def prerequisite_transformation_task(self):
        return ProduceOriginalGrammar

    @property
    def transformation_name(self):
        return "chomsky-normal-form"


class TransformGrammarChomsky(CompoundTransformGrammarWithTribble):
    @property
    def tribble_transformation_mode(self):
        return "chomsky-normal-formalizer"

    @property
    def prerequisite_transformation_task(self):
        return TransformGrammarChomskyStep1

    @property
    def transformation_name(self):
        return "chomsky-normal-form"
