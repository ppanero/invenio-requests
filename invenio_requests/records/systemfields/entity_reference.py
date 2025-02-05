# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Systemfield for managing referenced entities in request."""

from functools import partial

from invenio_records.systemfields import SystemField

from ...resolvers.base import EntityProxy
from ...resolvers.registry import ResolverRegistry


class ReferencedEntityField(SystemField):
    """Systemfield for managing the request type."""

    def __init__(self, key=None, reference_check_func=None):
        """Constructor."""
        super().__init__(key=key)
        self._ref_check = reference_check_func

    def _check_reference(self, instance, ref_dict):
        """Check if the reference is accepted."""
        if self._ref_check is None:
            return True

        return self._ref_check(instance, ref_dict)

    def set_obj(self, instance, obj):
        """Set the referenced entity."""
        # allow the setter to be used with a reference dict,
        # an entity proxy, or an actual entity
        if not isinstance(obj, dict):
            if isinstance(obj, EntityProxy):
                obj = obj.reference_dict
            elif obj is not None:
                obj = ResolverRegistry.reference_entity(obj, raise_=True)

        # check if the reference is allowed
        if not self._check_reference(instance, obj):
            raise ValueError(f"Invalid reference for '{self.key}': {obj}")

        # set dictionary key and reset the cache
        self.set_dictkey(instance, obj)
        self._set_cache(instance, None)

    def __set__(self, record, value):
        """Set the referenced entity."""
        assert record is not None
        self.set_obj(record, value)

    def obj(self, instance):
        """Get the referenced entity as an `EntityProxy`."""
        obj = self._get_cache(instance)
        if obj is not None:
            return obj

        reference_dict = self.get_dictkey(instance)
        if reference_dict is None:
            # TODO maybe use a `NullProxy` instead?
            return None

        obj = ResolverRegistry.resolve_entity_proxy(reference_dict)
        self._set_cache(instance, obj)
        return obj

    def __get__(self, record, owner=None):
        """Get the referenced entity as an `EntityProxy`."""
        if record is None:
            # access by class
            return self

        return self.obj(record)


def check_allowed_references(get_allows_none, get_allowed_types, request, ref_dict):
    """Check the reference according to rules specific to requests.

    In case the ``ref_dict`` is ``None``, it will check if this is allowed for the
    reference at hand.
    Otherwise, it will check if the reference dict's key (i.e. the TYPE) is allowed.
    """
    if ref_dict is None:
        return get_allows_none(request)

    ref_type = list(ref_dict.keys())[0]
    return ref_type in get_allowed_types(request)


check_allowed_creators = partial(
    check_allowed_references,
    lambda r: r.type.creator_can_be_none,
    lambda r: r.type.allowed_creator_ref_types,
)
"""Check function specific for the ``created_by`` field of requests."""

check_allowed_receivers = partial(
    check_allowed_references,
    lambda r: r.type.receiver_can_be_none,
    lambda r: r.type.allowed_receiver_ref_types,
)
"""Check function specific for the ``receiver`` field of requests."""

check_allowed_topics = partial(
    check_allowed_references,
    lambda r: r.type.topic_can_be_none,
    lambda r: r.type.allowed_topic_ref_types,
)
"""Check function specific for the ``topic`` field of requests."""
