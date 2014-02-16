# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import join


def index_to_str(*index):
    if len(index) == 1:
        index = index[0]
        if isinstance(index, basestring):
            return unicode(index)
        else:
            return ' '.join(index.get_names())
    elif len(index) == 2:
        return ' '.join(index)
    else:
        raise ValueError('index must be two strings or have get_names method ')


class Executor(object):
    def __init__(self, prefix=''):
        self.search_cmd = join(prefix, 'search')
        self.searchd_cmd = join(prefix, 'searchd')
        self.indexer_cmd = join(prefix, 'indexer')
        self.spelldump_cmd = join(prefix, 'spelldump')
        self.indextool_cmd = join(prefix, 'indextool')
        self.wordbreaker_cmd = join(prefix, 'wordbreaker')

    @property
    def search(self):
        return '%s --config %s' % (self.search_cmd, self.config_path)

    @property
    def searchd(self):
        return '%s --config %s' % (self.searchd_cmd, self.config_path)

    @property
    def indexer(self):
        return '%s --config %s' % (self.indexer_cmd, self.config_path)

    @property
    def spelldump(self):
        return '%s --config %s' % (self.spelldump_cmd, self.config_path)

    @property
    def indextool(self):
        return '%s --config %s' % (self.indextool_cmd, self.config_path)

    @property
    def wordbreaker(self):
        return '%s --config %s' % (self.wordbreaker_cmd, self.config_path)

    def set_conf(self, config_path):
        self.config_path = config_path

    def reindex(self, indexes):
        cmd_splitted = [self.indexer]
        cmd_splitted.extend(map(index_to_str, indexes))
        cmd_splitted.append('--rotate')
        return ' '.join(cmd_splitted)

    def merge(self, *index):
        cmd_splitted = [self.indexer, '--merge']

        index_str = index_to_str(index)
        cmd_splitted.append(index_str)
        return ' '.join(cmd_splitted)
