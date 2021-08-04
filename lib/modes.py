#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains mixins describing tribble transformation and generation modes.
"""

from abc import ABCMeta, abstractmethod

from lib import config

"""
Transformation.
"""


class WithTransformationMode(metaclass=ABCMeta):
    @property
    @abstractmethod
    def transformation_mode(self) -> str:
        raise NotImplementedError("Must specify a transformation mode to use for grammar transformation!")


class WithBackusNaurTransformationMode(WithTransformationMode):
    @property
    def transformation_mode(self) -> str:
        return "backus-naur-formalizer"


class WithChomskyTransformationMode(WithTransformationMode):
    @property
    def transformation_mode(self) -> str:
        return "chomsky-normal-formalizer"


"""
Generation.
"""


class WithGenerationMode(metaclass=ABCMeta):
    @property
    @abstractmethod
    def generation_mode(self) -> str:
        raise NotImplementedError("Must specify a generation mode to use for fuzzing!")


class WithRecurrentKPathNCoverageGenerationMode(WithGenerationMode, metaclass=ABCMeta):
    @property
    @abstractmethod
    def k(self):
        raise NotImplementedError("Must specify k to use recurrent k-path coverage strategy!")

    @property
    def generation_mode(self):
        return f"recurrent-{self.k}-path-{config.number_of_files_to_generate}"


class WithRecurrent2PathNCoverageGenerationMode(WithRecurrentKPathNCoverageGenerationMode, metaclass=ABCMeta):
    @property
    def k(self):
        return "2"
