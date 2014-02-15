# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def set_abstract(cls, value):
    cls.__abstract_index__ = value


def is_abstract(cls):
    return cls.__abstract_index__
