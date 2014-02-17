# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from six import string_types

from .groupby import GroupByOperator
from .filters import BaseFilterOperator, Any
from .orderby import AbtractSortMode, Attr


class QueryBackend(object):
    def __init__(self, indexes_str):
        self.indexes_str = indexes_str
        self.term = ''

        self.filters = {}
        self.sort_modes = []
        self.select = '*'

    def set_filter(self, attr_name, filter_op):
        self.filters


class Query(object):

    def __init__(self, index):
        if isinstance(index, string_types):
            indexes_str = unicode(index)
        else:
            self.index = index
            indexes_str = index.get_index_names()

        self._index = index
        self.query = QueryBackend(indexes_str)

    def filter(self, **filters):
        """
        """
        for attr_name, attr_filter in filters:
            if not isinstance(attr_filter, BaseFilterOperator):
                attr_filter = Any(attr_filter)

            self.query.add_filter(attr_name, attr_filter)

        return self._clone()

    def orderby(self, value):
        if not isinstance(value, AbtractSortMode):
            value = Attr(value)

        self.query.set_sort_mode(value)
        return self._clone()

    def groupby(self, field):
        if not isinstance(field, GroupByOperator):
            field = GroupByOperator(field)

        self.query.set_group_by(field)
        return self._clone()

    def geo(self, lat_field, long_field, lat, long):
        """
            SetGeoAnchor
        """
        self.query.set_geo_anchor(lat_field, long_field, lat, long)
        return self._clone()

    def like(self, query):
        pass

    def __getitem__(self, i):
        """
            SetLimits
        """
        pass

    def __getslice__(self, start, step):
        """
            SetLimits
        """
        pass

    def max(self, number):
        """
            SetLimits
        """

    def timeout(self, milliseconds):
        """
            SetMaxQueryTime
        """

    def values(self, *fields):
        pass

    def values_list(self, *fields, **kwargs):
        flat = kwargs.get('flat')
        assert not flat or len(fields) == 1


