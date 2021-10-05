#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains luigi wrapper tasks that dispatch tasks matching a single combination of parameter values.
"""

import luigi
from luigi.util import inherits

from lib import parametrization as par
from lib import result_reporting
from lib import utils


class DispatchLanguages(luigi.WrapperTask, utils.StableRandomness):
    total_number_of_runs: int = luigi.IntParameter(description="The number of runs to conduct per configuration.")
    random_seed: int = luigi.IntParameter(
        description="The main seed for this experiment. All other random seeds will be derived from this one.")
    only_language: str = luigi.OptionalParameter(
        description="The name of the only language to test, if the full experiment should not be run.",
        default=None)
    only_transformation: str = luigi.OptionalParameter(
        description="The name of the only transformation to test, if the full experiment should not be run.",
        default=None)

    def requires(self):
        if self.only_language:
            return self.clone(DispatchTransformations, language=self.only_language,
                              language_seed=self._derive_language_seed_from_random_seed(self.only_language))
        else:
            return [self.clone(DispatchTransformations, language=language,
                               language_seed=self._derive_language_seed_from_random_seed(language))
                    for language in par.languages]

    def _derive_language_seed_from_random_seed(self, language):
        return self.random_int(self.random_seed, language)


class DispatchTransformations(luigi.WrapperTask):
    total_number_of_runs: int = luigi.IntParameter(description="The number of runs to conduct per configuration.")
    language: str = luigi.Parameter(description="The language specified by the input grammar.")
    language_seed: int = luigi.IntParameter(description="The seed from which seeds for this language are derived.")
    only_transformation: str = luigi.OptionalParameter(
        description="The name of the only transformation to test, if the full experiment should not be run.")

    def requires(self):
        if self.only_transformation:
            return self.clone(DispatchFuzzingStrategies, transformation_name=self.only_transformation)
        else:
            return [self.clone(DispatchFuzzingStrategies, transformation_name=name) for name in par.transformations]


class DispatchFuzzingStrategies(luigi.WrapperTask):
    total_number_of_runs: int = luigi.IntParameter(description="The number of runs to conduct per configuration.")
    language: str = luigi.Parameter(description="The language specified by the input grammar.")
    language_seed: int = luigi.IntParameter(description="The seed from which seeds for this language are derived.")
    transformation_name: str = luigi.Parameter(description="The transformation to conduct.")

    def requires(self):
        return [self.clone(DispatchCompatibleSubjects, fuzzing_strategy=strategy) for strategy in par.fuzzing_strategies]


@inherits(DispatchFuzzingStrategies)
class DispatchCompatibleSubjects(luigi.WrapperTask):
    fuzzing_strategy: str = luigi.Parameter(description="The fuzzing strategy to use for generation.")

    def requires(self):
        return [self.clone(DispatchMetrics, subject_name=subject) for subject in par.subjects[self.language]]


@inherits(DispatchCompatibleSubjects)
class DispatchMetrics(luigi.WrapperTask):
    subject_name: str = luigi.Parameter(description="The name of the subject to run.")

    def requires(self):
        yield self.clone(result_reporting.ProduceCoverageReport)
        yield self.clone(result_reporting.ProduceCoverageGrowthRateReport)
