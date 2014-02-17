# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from six import with_metaclass

from .base import OptionableMeta, OptionableBase


class _IndexerMeta(OptionableMeta):
    OPTIONS = ['mem_limit',
               'max_iops',
               'max_iosize',
               'max_xmlpipe2_field',
               'write_buffer',
               'max_file_field_buffer',
               'on_file_field_error',
               'lemmatizer_cache']


class Indexer(with_metaclass(_IndexerMeta, OptionableBase)):
    option_block_name = 'indexer'
