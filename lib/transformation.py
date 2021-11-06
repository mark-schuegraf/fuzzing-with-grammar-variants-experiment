#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks that transform the input grammar using tribble.
"""

import logging
import subprocess
from typing import Optional

import luigi

from lib import parametrization as par
from lib import tooling
from lib import utils
from lib import work_dir


class ProduceOriginalGrammar(luigi.ExternalTask):
    language: str = luigi.Parameter(description="The language specified by the input grammar.")

    def output(self):
        return luigi.LocalTarget(work_dir / "grammars" / par.grammars[self.language])


class TransformGrammar(luigi.Task):
    language: str = luigi.Parameter(description="The language specified by the input grammar.")
    transformation_mode: str = luigi.Parameter(description="The tribble transformation mode to use.")
    resources = {"ram": 32}

    def requires(self):
        return {
            "tribble_jar": tooling.BuildTribble(),
            "grammar_file": self._choose_prior_transformation_task()
        }

    def _choose_prior_transformation_task(self):
        if self._prerequisite_mode:
            return self.clone(TransformGrammar, transformation_mode=self._prerequisite_mode)
        else:
            return self.clone(ProduceOriginalGrammar)

    @property
    def _prerequisite_mode(self) -> Optional[str]:
        return par.transformers[self.transformation_mode]

    def run(self):
        tribble_jar = self.input()["tribble_jar"].path
        automaton_dir = work_dir / "tools" / "tribble-automaton-cache" / self.language
        grammar_file = self.input()["grammar_file"].path
        loading_strategy = utils.choose_grammar_loading_strategy_based_on_file_extension(grammar_file)
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
                    f"--grammar-file={grammar_file}",
                    f"--output-grammar-file={out}",
                    f"--loading-strategy={loading_strategy}",
                    "--storing-strategy=marshal",
                    f"--mode={self.transformation_mode}",
                    ]
            logging.info("Launching %s", " ".join(args))
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL)

    def output(self):
        return luigi.LocalTarget(
            work_dir / "transformed-grammars" / self.language / self.transformation_mode / self.language)


class SelectGrammarSource(luigi.Task):
    language: str = luigi.Parameter(description="The language specified by the input grammar.")
    transformation_name: str = luigi.Parameter(description="The transformation to conduct.")

    def requires(self):
        if self.transformation_name == "identity":
            return self.clone(ProduceOriginalGrammar)
        else:
            transformer = par.transformations[self.transformation_name]
            return self.clone(TransformGrammar, transformation_mode=transformer)

    def output(self):
        return self.input()
