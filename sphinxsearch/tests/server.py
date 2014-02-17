# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from sphinxsearch.engine.server import SearchServer
from sphinxsearch.engine.indexer import Indexer
from sphinxsearch.engine import Engine
from sphinxsearch.session import Session
from sphinxsearch.exceptions import ConfigError


class Test(unittest.TestCase):
    def setUp(self):
        import sphinxapi
        self.api = sphinxapi

        server = SearchServer(host='0.0.0.0', port=1234)
        server.log = 'logpath'

        self.server = server

        indexer = Indexer()
        indexer.mem_limit = '32M'

        self.indexer = indexer

    def test_server(self):
        print self.server.get_options()

        with self.assertRaises(ConfigError):
            self.assertIsInstance(self.server.get_session(), Session)

    def test_indexer(self):
        print self.indexer.get_options()

    def test_engine(self):
        engine = Engine()
        engine.api = self.api

        engine.indexer = self.indexer

        engine.server = self.server

        self.assertIsInstance(engine.get_session(), Session)




