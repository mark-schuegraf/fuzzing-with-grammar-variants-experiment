#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi wrapper tasks that dispatch tasks matching a single combination of parameter values.
"""
from typing import final

import luigi
from luigi.util import inherits

from lib import result_reporting
from lib import utils
from lib.parametrization import base_transformers
from lib.parametrization import follow_up_transformers
from lib.parametrization import fuzzing_strategies
from lib.parametrization import languages
from lib.parametrization import subjects


class DispatchLanguages(luigi.WrapperTask, utils.StableRandomness):
    total_number_of_runs: int = luigi.IntParameter(description="The number of runs to conduct per configuration.")
    random_seed: int = luigi.IntParameter(
        description="The main seed for this experiment. All other random seeds will be derived from this one.")

    @final
    def requires(self):
        return [self.clone(DispatchTransformers, language=language,
                           language_seed=self._derive_language_seed_from_random_seed(language))
                for language in languages]

    @final
    def _derive_language_seed_from_random_seed(self, language):
        return self.random_int(self.random_seed, language)


class DispatchTransformers(luigi.WrapperTask):
    language: str = luigi.Parameter(description="The language specified by the input grammar.")
    language_seed: int = luigi.IntParameter(description="The seed from which seeds for this language are derived.")
    total_number_of_runs: int = luigi.IntParameter(description="The number of runs to conduct per configuration.")

    @final
    def requires(self):
        modes = [t for t in base_transformers if t != "identity"] + follow_up_transformers.keys()
        return [self.clone(DispatchFuzzingStrategies, transformation_mode=mode) for mode in modes]


@inherits(DispatchTransformers)
class DispatchFuzzingStrategies(luigi.WrapperTask):
    transformation_mode: str = luigi.Parameter(description="The tribble transformation mode to use.")

    @final
    def requires(self):
        return [self.clone(DispatchCompatibleSubjects, generation_mode=strategy) for strategy in fuzzing_strategies]


@inherits(DispatchFuzzingStrategies)
class DispatchCompatibleSubjects(luigi.WrapperTask):
    generation_mode: str = luigi.Parameter(description="The tribble generation mode to use.")

    @final
    def requires(self):
        return [self.clone(DispatchMetrics, subject_name=subject) for subject in subjects[self.language]]


@inherits(DispatchCompatibleSubjects)
class DispatchMetrics(luigi.WrapperTask):
    subject_name: str = luigi.Parameter(description="The name of the subject to run.")

    @final
    def requires(self):
        yield self.clone(result_reporting.ProduceCoverageReport)
        yield self.clone(result_reporting.ProduceCoverageGrowthRateReport)
