# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from six import string_types

from ..models.attrs import AbstractAttr
from ..utils.cmd_tools import requires_kwarg
from .groupby import GroupByOperator
from .filters import BaseFilterOperator, Any
from .orderby import AbtractSortMode, Attr


class QuerySettingsMixin(object):
    def setUp(self):
        self.offset = 0
        self.limit = 0
        self.max_matches = 0
        self.cutoff = 0

        self.timeout = 0
        self.overrides = {}
        self.select = '*'

    def set_override(self, attr_name, attr_type, update_dict):
        self.overrides[(attr_name, attr_type)] = update_dict

    def set_limit(self, offset, limit, max_matches, cutoff):
        self.offset = offset
        self.limit = limit
        self.max_matches = max_matches
        self.cutoff = cutoff

    def set_timeout(self, milliseconds):
        self.timeout = milliseconds

    def set_select(self, fields):
        self.select = fields


class FilterMixin(object):
    def setUp(self):
        self.filters = {}
        self.geo_anchor = None

    def add_filter(self, attr_name, filter_op):
        self.filters[attr_name] = filter_op

    def set_geo_anchor(self, lat_field, long_field, lat, long):
        self.geo_anchor = (lat_field, long_field, lat, long)


class SearchSettingsMixin(object):
    def setUp(self):
        self.sort_modes = []

    def set_sort_mode(self, sort_mode):
        self.sort_mode = sort_mode


class GroupBySettingsMixin(object):
    def setUp(self):
        self.group_by = None
        self.group_by_distinct = None

    def set_group_by(self, field):
        self.group_by = field

    def set_group_by_distinct(self, field):
        self.group_by_distinct = field


class UpdateMixin(object):
    def setUp(self):
        self.update = False

    def set_update(self, attrs, values):
        self.update = True
        self.attrs = attrs
        self.values = values


class QueryBackend(QuerySettingsMixin, FilterMixin, GroupBySettingsMixin, UpdateMixin):
    def __init__(self, indexes_str):
        self.indexes_str = indexes_str
        self.term = ''

        QuerySettingsMixin.setUp(self)
        FilterMixin.setUp(self)
        SearchSettingsMixin.setUp(self)
        GroupBySettingsMixin.setUp(self)
        UpdateMixin.setUp(self)

    def result_handler(self, *args, **kwargs):
        if self.handler:
            return self.handler(*args, **kwargs)

    def build_excerpts(self, docs, words, **options):
        pass



def clone_method(method):
    def wrapper(self, *args, **kwargs):
        if self._clonable:
            raise RuntimeError('Not clonable')
        method(self, *args, **kwargs)
        return self.clone()
    return wrapper


class Query(object):

    def __init__(self, index):
        if isinstance(index, string_types):
            indexes_str = unicode(index)
        else:
            self.index = index
            indexes_str = index.get_index_names()

        self._index = index
        self.query = QueryBackend(indexes_str)
        self._clonable = True

    @clone_method
    def filter(self, **filters):
        """
        """
        for attr_name, attr_filter in filters:
            if not isinstance(attr_filter, BaseFilterOperator):
                attr_filter = Any(attr_filter)

            self.query.add_filter(attr_name, attr_filter)

    @clone_method
    def orderby(self, value):
        if not isinstance(value, AbtractSortMode):
            value = Attr(unicode(value))
        self.query.set_sort_mode(value)

    @clone_method
    def groupby(self, field):
        if not isinstance(field, GroupByOperator):
            field = GroupByOperator(field)

        self.query.set_group_by(field)

    @clone_method
    def geo(self, lat_field, long_field, lat, long):
        """
            SetGeoAnchor
        """
        self.query.set_geo_anchor(unicode(lat_field),
                                  unicode(long_field),
                                  float(lat),
                                  float(long))

    @clone_method
    def like(self, query):
        pass

    @clone_method
    def __getitem__(self, i):
        """
            SetLimits
        """
        self.query.set_limit(int(i), int(i) + 1)

    @clone_method
    def __getslice__(self, start, end):
        """
            SetLimits
        """
        offset = self.query.offset + start
        limit = self.query.limit - (end - start)
        max_matches = self.query.max_matches
        cutoff = self.query.cutoff
        self.query.set_limit(offset, limit, max_matches, cutoff)

    @clone_method
    def max(self, value):
        """
            SetLimits
        """
        offset = self.query.offset
        limit = self.query.limit
        max_matches = int(value)
        cutoff = self.query.cutoff
        self.query.set_limit(offset, limit, max_matches, cutoff)

    @clone_method
    def add_max(self, value):
        max_matches = self.query.max_matches + int(value)
        self.max(max_matches)

    @clone_method
    def pop_max(self, value):
        max_matches = self.query.max_matches - int(value)
        assert max_matches
        self.max(max_matches)

    @clone_method
    def cutoff(self, value):
        offset = self.query.offset
        limit = self.query.limit
        max_matches = self.max_matches
        cutoff = int(value)
        self.query.set_limit(offset, limit, max_matches, cutoff)

    @clone_method
    def add_cutoff(self, value):
        cutoff = self.query.cutoff + int(value)
        self.cutoff(cutoff)

    @clone_method
    def pop_cutoff(self, value):
        cutoff = self.query.cutoff - int(value)
        assert cutoff
        self.cutoff(cutoff)

    @clone_method
    # query result options
    def values(self, *fields):
        self.query.set_select(fields)

    @clone_method
    def values_list(self, *fields):
        self.query.set_select(fields)

    @clone_method
    def ids(self):
        self.query.set_select(('id',))

    @clone_method
    def only(self, *fields):
        self.query.set_select(fields)

    @clone_method
    def populate(self):
        pass

    @clone_method
    def override(self, attr, attr_type=None, **update_dict):
        if isinstance(attr, AbstractAttr):
            attr_name = attr.name
            attr_type = attr.get_type()
        else:
            attr_name = unicode(attr_name)
            if not isinstance(attr_type):
                raise TypeError('Argument attr_type required')
            attr_type = unicode(attr_type)

        if not update_dict:
            self.query.set_override(attr, attr_type, update_dict)

    def update(self, **update_dict):
        new_inctance = self._clone()
        new_inctance.parent = self
        new_inctance._clonable = False

        attrs = tuple(update_dict.keys())
        attrs_values = tuple(update_dict.values())
        index = self.index

        def handler(matches, *args):
            ids = matches.keys()
            values = {id: attrs_values for id in ids}
            return type(self)(index).raw_update(attrs, values).query

        new_inctance.query.handler = handler
        return new_inctance

    def raw_update(self, index, attrs, values):
        self._clonable = False
        self.query.set_update(attrs, values)
        return self
        return self

    def keywords(self, query, hits=False):
        self._clonable = False
        self.query.set_keywords()

    def excerpts(self, docs, words, **options):
        self._clonable = False
        self.query.build_excerpts(docs, words, options)
        return self

    @clone_method
    # quering options
    def timeout(self, milliseconds):
        """
            SetMaxQueryTime
        """
        self.query.set_timeout(int(milliseconds))
