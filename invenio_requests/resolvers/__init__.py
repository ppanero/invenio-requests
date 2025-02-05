# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module for entity resolvers."""

from .base import EntityResolver
from .registry import ResolverRegistry

__all__ = (
    "EntityResolver",
    "ResolverRegistry",
)
