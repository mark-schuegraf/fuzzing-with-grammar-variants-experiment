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


class TransformGrammar(luigi.Task, metaclass=ABCMeta):
    """Transforms the input grammar using tribble's transformation mode."""
    format: str = luigi.Parameter(description="The format specified by the input grammar.")
    resources = {"ram": 16}

    @property
    @abstractmethod
    def transformation_mode(self):
        raise NotImplementedError("Must specify a transformation mode to use for transformation!")

    @property
    @abstractmethod
    def prerequisite_task(self):
        raise NotImplementedError("Must specify the preconditions that must hold before transformation!")

    @property
    @abstractmethod
    def compound_transformation(self):
        raise NotImplementedError("Must specify the overall conversion procedure that this is a substep of!")

    @property
    @abstractmethod
    def output_path(self):
        raise NotImplementedError("Must specify where to store the output grammar file!")

    def requires(self):
        return tooling.BuildTribble(), self.clone(self.prerequisite_task)

    def run(self):
        tribble_jar = self.input()[0].path
        automaton_dir = work_dir / "tools" / "tribble-automaton-cache" / self.format
        with luigi.LocalTarget(self.output_path).temporary_path() as out:
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
                    f"--loading-strategy=unmarshal",
                    f"--storing-strategy=marshal",
                    f"--mode={self.transformation_mode}",
                    ]
            logging.info("Launching %s", " ".join(args))
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


class ProduceOriginalGrammar(luigi.ExternalTask):
    """Fetches the original grammar modeling a certain format."""
    format: str = luigi.Parameter(description="The format specified by the input grammar.")

    def output(self):
        return luigi.LocalTarget(work_dir / "grammars" / subjects[self.format]["grammar"])


"""
Mixins
"""


class OutputModule(metaclass=ABCMeta):
    @property
    @abstractmethod
    def format(self):
        raise NotImplementedError("Must specify the format specified by the grammar for directory naming purposes!")

    @property
    @abstractmethod
    def compound_transformation(self):
        raise NotImplementedError("Must specify the name of the compound transformation for directory naming purposes!")

    @property
    @abstractmethod
    def output_path(self):
        raise NotImplementedError("An output module must produce the output path!")

    def output(self):
        """If the transformation is elementary, store the intermediate grammar in a subdirectory of the target path."""
        return luigi.LocalTarget(self.output_path)


class ElementaryOutputModule(OutputModule, metaclass=ABCMeta):
    @property
    @abstractmethod
    def transformation_mode(self) -> str:
        raise NotImplementedError("Must specify the transformation mode to name intermediate grammar directories!")

    @property
    def output_path(self):
        """If the transformation is elementary, store the intermediate grammar in a subdirectory of the target path."""
        return work_dir / "transformed-grammars" / self.format / self.compound_transformation / self.transformation_mode / self.format


class CompoundOutputModule(OutputModule, metaclass=ABCMeta):
    @property
    def output_path(self):
        """If the transformation is compound, store the output grammar directly in the transformation directory."""
        return work_dir / "transformed-grammars" / self.format / self.compound_transformation / self.format


"""
Chomsky.
"""


class TransformChomskyPre1(TransformGrammar, ElementaryOutputModule):
    @property
    def transformation_mode(self):
        return "backus-naur-formalizer"

    @property
    def prerequisite_task(self):
        return ProduceOriginalGrammar

    @property
    def compound_transformation(self):
        return "chomsky-normal-form"


class TransformChomsky(TransformGrammar, CompoundOutputModule):
    @property
    def transformation_mode(self):
        return "chomsky-normal-formalizer"

    @property
    def prerequisite_task(self):
        return TransformChomskyPre1

    @property
    def compound_transformation(self):
        return "chomsky-normal-form"
