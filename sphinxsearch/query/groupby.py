# -*- coding: utf-8 -*-


class GroupByOperator(object):
    api_option = 'SPH_GROUPBY_ATTR'

    def get_api_option(self, engine):
        return getattr(engine.api, self.api_option)

    def apply():
        pass


class Day(GroupByOperator):
    api_option = 'SPH_GROUPBY_DAY'


class Week(GroupByOperator):
    api_option = 'SPH_GROUPBY_WEEK'


class Month(GroupByOperator):
    api_option = 'SPH_GROUPBY_MONTH'


class Year(GroupByOperator):
    api_option = 'SPH_GROUPBY_YEAR'
