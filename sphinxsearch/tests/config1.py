# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .utils import (get_api, get_servers, get_indexers,
                    get_schemas, get_valid_indexes)

from tempfile import gettempdir
from os.path import join

from sphinxsearch import SearchServer


class settings:
    HOST = 'localhost'
    PORT = '4321'
    TMP_ROOT = join(gettempdir(), 'sphinxsearch_tmp')
    MAX_MATCHES = 10000
    LOG_DIR = join(TMP_ROOT, 'logs')


class MySearchServer(SearchServer):
    listen = '%s:%s' % (settings.HOST, settings.PORT)
    read_timeout = 5
    client_timeout = 300
    max_children = 0
    pid_file = join(settings.TMP_ROOT, 'searchd.pid')
    max_matches = settings.MAX_MATCHES
    log = join(settings.LOG_DIR, 'searchd.log')
    workers = 'prefork'
    max_filter_values = 8192

    preopen_indexes = True
    seamless_rotate = True
