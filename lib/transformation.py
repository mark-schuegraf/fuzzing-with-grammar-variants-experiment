#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks that transform the input grammar using tribble.
"""

import logging
import subprocess
from typing import final

import luigi

from lib import parametrization as par
from lib import tooling
from lib import utils
from lib import work_dir


class ProduceOriginalGrammar(luigi.ExternalTask):
    language: str = luigi.Parameter(description="The language specified by the input grammar.")

    @final
    def output(self):
        return luigi.LocalTarget(work_dir / "grammars" / par.grammars[self.language])


class TransformGrammar(luigi.Task):
    language: str = luigi.Parameter(description="The language specified by the input grammar.")
    transformation_mode: str = luigi.Parameter(description="The tribble transformation mode to use.")
    resources = {"ram": 16}

    @final
    def requires(self):
        return {
            "tribble_jar": tooling.BuildTribble(),
            "grammar_file": self._choose_transformation_task()
        }

    @final
    def _choose_transformation_task(self):
        if self.transformation_mode in par.base_transformers:
            return self.clone(ProduceOriginalGrammar)
        else:
            prerequisite_mode = par.follow_up_transformers[self.transformation_mode]
            return self.clone(TransformGrammar, transformation_mode=prerequisite_mode)

    @final
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

    @final
    def output(self):
        return luigi.LocalTarget(work_dir / "transformed-grammars" / self.language / self.transformation_mode)
