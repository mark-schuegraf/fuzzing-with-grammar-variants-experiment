#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains a luigi task that generates inputs using the tribble fuzzer on a transformed grammar.
"""

import logging
import subprocess
from pathlib import Path

import luigi
from luigi.util import inherits

from lib import parametrization as par
from lib import tooling
from lib import transformation
from lib import utils
from lib import work_dir


@inherits(transformation.SelectGrammarSource)
class GenerateInputs(luigi.Task, utils.StableRandomness):
    generation_mode: str = luigi.Parameter(description="The tribble generation mode to use.")
    run_number: int = luigi.IntParameter(description="The run number of the produced input set.")
    language_seed: int = luigi.IntParameter(description="The seed from which seeds for this language are derived.")
    resources = {"ram": 4}

    def requires(self):
        return {
            "tribble_jar": tooling.BuildTribble(),
            "grammar_file": self.clone(transformation.SelectGrammarSource)
        }

    def run(self):
        tribble_jar = self.input()["tribble_jar"].path
        random_seed = self._derive_tribble_generation_seed_from_language_seed()
        automaton_dir = work_dir / "tools" / "tribble-automaton-cache" / self.language
        grammar_file = self.input()["grammar_file"].path
        loading_strategy = utils.choose_grammar_loading_strategy_based_on_file_extension(grammar_file)
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
                    f'--suffix={par.suffixes[self.language]}',
                    f"--out-dir={out}",
                    f"--grammar-file={grammar_file}",
                    f"--loading-strategy={loading_strategy}",
                    f"--mode={self.generation_mode}",
                    ]
            logging.info("Launching %s", " ".join(args))
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL)

    def _derive_tribble_generation_seed_from_language_seed(self):
        # also make the seed depend on the output path starting from work_dir
        rel_output_path = Path(self.output().path).relative_to(work_dir)
        return self.random_int(self.language_seed, self.generation_mode, self.language, str(self.run_number),
                               *rel_output_path.parts)

    def output(self):
        return luigi.LocalTarget(
            work_dir / "inputs" / self.language / self.transformation_name / self.generation_mode / f"run-{self.run_number}")
