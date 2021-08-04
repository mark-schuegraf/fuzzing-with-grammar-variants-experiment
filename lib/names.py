#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains mixins providing the names of supported compound transformations.
"""

from abc import ABCMeta, abstractmethod


class WithCompoundTransformationName(metaclass=ABCMeta):
    @property
    @abstractmethod
    def compound_transformation_name(self) -> str:
        raise NotImplementedError("You must specify the compound transformation that this belongs to!")


class WithIdentityCompoundTransformationName(WithCompoundTransformationName):
    @property
    def compound_transformation_name(self) -> str:
        return "identity"


class WithChomskyCompoundTransformationName(WithCompoundTransformationName):
    @property
    def compound_transformation_name(self) -> str:
        return "chomsky-normal-form"
