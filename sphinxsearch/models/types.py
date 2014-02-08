# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod, abstractproperty

from .const import RT_SOURCE_TYPE, SQL_SOURCE_TYPE, XML_SOURCE_TYPE
from ..utils import IndexBlock, SourceBlock


__all__ = ['RT', 'DB', 'ODBC', 'XML']


class AbstractIndexType(object):
    __metaclass__ = ABCMeta

    @abstractmethod  # pragma: no cover
    def get_conf_blocks(index, attrs_conf):
        """"""

    @abstractproperty  # pragma: no cover
    def source_type():
        """"""


class RT(AbstractIndexType):
    source_type = RT_SOURCE_TYPE

    def get_conf_blocks(self, index, attrs_options):
        index_name = index.get_name()

        return IndexBlock(index_name, type=self.source_type, **attrs_options)


class AbstractSourceType(AbstractIndexType):

    def get_conf_blocks(self, index, attrs_options):
        index_name = index.get_name()
        source_name = index_name

        index_options = self.get_index_options(index)
        index_block = IndexBlock(index_name, source=source_name, **index_options)
        source_block = self.get_source_block_conf(index, attrs_options)
        source_block['source'] = source_name

        return index_block, source_block

    def get_source_block_conf(self, index, attrs_conf):
        source_name = index.get_name()
        source_options = self.get_source_options()
        return SourceBlock(source_name, **source_options)

    def get_index_options(self, index):
        return {}

    @abstractmethod  # pragma: no cover
    def get_source_options(self):
        """"""


class DB(AbstractSourceType):
    source_type = SQL_SOURCE_TYPE

    def __init__(self, type=None, host=None, port=None,
                 sock=None, db=None, user=None, password=None):
        self.host = host
        self.port = port
        self.sock = sock
        self.db = db
        self.user = user
        self.password = password
        self.type = type

    def get_source_options(self):
        source_options = {'type': self.type}
        source_type = self.source_type

        if self.sock:
            source_options['%s_sock' % source_type] = self.sock
        else:
            source_options['%s_host' % source_type] = self.host
            source_options['%s_port' % source_type] = self.port

        source_options['%s_db' % source_type] = self.db
        source_options['%s_user' % source_type] = self.user
        source_options['%s_password' % source_type] = self.password

        return source_options


class ODBC(AbstractSourceType):
    source_type = SQL_SOURCE_TYPE

    def __init__(self, dsn):
        self.dsn = dsn

    def get_source_options(self):
        return {'%s_dsn' % self.source_type: self.dsn}


class XML(AbstractSourceType):
    source_type = XML_SOURCE_TYPE

    def __init__(self, command):
        self.command = command

    def get_source_options(self):
        return {'%s_command' % self.source_type: self.command}
