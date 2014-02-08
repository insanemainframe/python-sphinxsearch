# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from abc import ABCMeta, abstractproperty

from .const import CONFIG_INDENT


def options2str(**options):
    return '\n'.join(['%s = %s' % (k, v) for k, v in options.items()])


def add_indent(block_body):
    body_str_list = block_body.split('\n')
    body_str_list = ['%s%s' % (CONFIG_INDENT, s) for s in body_str_list]
    return '\n'.join(body_str_list)


class AbstractConfBlock(dict):
    __metaclass__ = ABCMeta

    @abstractproperty  # pragma: no cover
    def type():
        """"""

    def __init__(self, name, **options):
        self.name = name
        self.options = options

    def __unicode__(self):
        options_body = add_indent(options2str(**self.options))
        return '%s %s\n { \n%s\n }' % (self.type, self.name, options_body)

    def __repr__(self):  # pragma: no cover
        return ('ConfBlock<> %s' % add_indent(self.__unicode__())).encode('utf-8')


class IndexBlock(AbstractConfBlock):
    type = 'index'


class SourceBlock(AbstractConfBlock):
    type = 'source'


class IndexerBlock(AbstractConfBlock):
    type = 'indexer'


class ServerBlock(AbstractConfBlock):
    type = 'searchd'
