#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi tasks corresponding to each tribble transformation mode.
"""

import logging
import subprocess
from abc import ABCMeta, abstractmethod
from typing import Any, Dict

import luigi

from lib import subjects
from lib import tooling
from lib import work_dir


class TransformGrammar(luigi.Task, metaclass=ABCMeta):
    """Transforms the input grammar using tribble's transformation mode."""
    format: str = luigi.Parameter(description="The format specified by the input grammar.")
    resources = {"ram": 16}

    @abstractmethod
    def transformation_info(self) -> Dict[str, Any]:
        return {"transformation_mode": None,
                "prerequisite_task": None,
                "is_intermediate_step": None,
                "compound_transformation": None,
                }

    def requires(self):
        return tooling.BuildTribble(), self.clone(self.transformation_info()["prerequisite_task"])

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
                    f"--loading-strategy=unmarshal",
                    f"--storing-strategy=marshal",
                    f"--mode={self.transformation_info()['transformation_mode']}",
                    ]
            logging.info("Launching %s", " ".join(args))
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL)

    def output(self):
        """If the transformation is elementary, store the intermediate grammar in a subdirectory of the target path."""
        grammars_subdir = self.transformation_info()["transformation_mode"] if self.transformation_info()[
            "is_intermediate_step"] else ""
        return luigi.LocalTarget(
            work_dir / "transformed-grammars" / self.format / self.transformation_info()[
                "compound_transformation"] / grammars_subdir / self.format)


class ProduceOriginalGrammar(luigi.ExternalTask):
    """Fetches the original grammar modeling a certain format."""
    format: str = luigi.Parameter(description="The format specified by the input grammar.")

    def output(self):
        return luigi.LocalTarget(work_dir / "grammars" / subjects[self.format]["grammar"])


"""
Chomsky.
"""


class TransformChomskyPre1(TransformGrammar):
    def transformation_info(self) -> Dict:
        return {"transformation_mode": "backus-naur-formalizer",
                "prerequisite_task": ProduceOriginalGrammar,
                "is_intermediate_step": True,
                "compound_transformation": "chomsky-normal-form",
                }


class TransformChomsky(TransformGrammar):
    def transformation_info(self) -> Dict:
        return {"transformation_mode": "chomsky-normal-formalizer",
                "prerequisite_task": TransformChomskyPre1,
                "is_intermediate_step": False,
                "compound_transformation": "chomsky-normal-form",
                }
