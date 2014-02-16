# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import unittest

from tempfile import gettempdir
from os.path import join


from sphinxsearch.models import Index, Int, String, Bool, TimeStamp, MVA, Float, PgsqlSource


HOST = 'localhost'
PORT = '4321'
TMP_ROOT = join(gettempdir())
MAX_MATCHES = 10000
LOG_DIR = join(TMP_ROOT, 'logs')


def get_indexer():
    from sphinxsearch.engine.indexer import Indexer

    indexer = Indexer()
    indexer.mem_limit = '32M'

    return indexer


def get_server():
    from sphinxsearch import SearchServer

    my_server = SearchServer(host=HOST, port=PORT)

    my_server.read_timeout = 5
    my_server.client_timeout = 300
    my_server.max_children = 0
    my_server.pid_file = join(TMP_ROOT, 'searchd.pid')
    my_server.max_matches = MAX_MATCHES
    my_server.log = join(LOG_DIR, 'searchd.log')
    my_server.workers = 'prefork'
    my_server.preopen_indexes = True
    my_server.seamless_rotate = True

    my_server.set_option('max_filter_values', 8192)

    return my_server


def get_engine(api, server, indexer, models):
    from sphinxsearch.engine import Engine

    engine = Engine()
    engine.api = api
    engine.server = server
    engine.indexer = indexer
    engine.set_conf('sphinx.conf')

    return engine


class AbstractProductsIndex(Index):
    __abstract__ = True
    __source__ = PgsqlSource(host=HOST,
                             port=5432, db='nazya_db',
                             user='nazya', password='pass')

    path = '/var/www/nazya/nazya/var/sphinx/index_data/data_anyshop_products'
    docinfo = 'extern'
    mlock = 0
    morphology = 'stem_enru'
    min_word_len = 2

    charset_type = 'utf-8'
    charset_table = '0..9, A..Z->a..z, _, a..z, U+410..U+42F->U+430..U+44F, U+430..U+44F'
    min_infix_len = 2
    enable_star = 1
    query_info = 'SELECT * FROM "base_nazyaproduct" WHERE id=$id'


class AnyshopProducts(AbstractProductsIndex):
    __abstract__ = True

    nazyacategory_id = Int()
    type = Int()
    seller_id = Int()

    tree_id = Int()
    lft = Int()
    rght = Int()

    name = String()
    orig_name = String()
    item_id = String()
    thumbs = String()
    images = String()
    nazyacategory__item_id = String()

    post_fee = Float()
    current_price = Float()
    orig_price = Float()

    in_stock = Bool()

    modified_at = TimeStamp()
    created_at = TimeStamp()

    property_values_ids = MVA(Int, query='SELECT "base_nazyaproduct_property_values"."nazyaproduct_id"')


class RakutenProducts(AnyshopProducts):
    pass


class Test(unittest.TestCase):
    def setUp(self):
        import sphinxapi

        self.server = get_server()
        self.api = sphinxapi
        self.indexer = get_indexer()

    @property
    def engine(self):
        engine = get_engine(self.api, self.server, self.indexer, set())
        conf_file_path = join(TMP_ROOT, 'sphinx.conf')
        engine.set_conf(conf_file_path)
        return engine

    @property
    def engine_with_schema(self):
        engine = self.engine
        engine.add_index(RakutenProducts)
        engine.extend_indexes((AnyshopProducts, AbstractProductsIndex))

        return engine

    def test_server_cmd(self):
        engine = self.engine
        engine.set_conf('sphinx.conf')
        engine.save()
        print(engine.executor.status())

        print(engine.executor.start())
        for i in range(0, 4):
            print(engine.executor.start(logdebug=i))
        print(engine.executor.start(index=RakutenProducts))
        print(engine.executor.start(index='main'))

        print(engine.executor.stop())
        print(engine.executor.stop(block=True))
        print(engine.executor.stop(block=True, pidfile='/tmp/custom.pid'))

        print(engine.executor.restart())
        print(engine.executor.restart(pidfile='/tmp/custom.pid'))
        print(engine.executor.restart(pidfile='/tmp/custom.pid',
                                      new_pidfile='/tmp/custom_new.pid',
                                      logdebug=i))

        print(engine.executor.start(port=1234))
        print(engine.executor.start(listen='localhost:4321:mysql41'))
        print(engine.executor.start(listen='localhost:4321:mysql41', port=1234))

    def test(self):
        engine = self.engine_with_schema

        print(engine.get_session())

        print(engine.create_config())

        engine.save()

        print(engine.executor.reindex(RakutenProducts))
        print(engine.executor.buildstops(RakutenProducts,
                                              outputfile='/tmp/stops.txt',
                                              limit=100))
        print(engine.executor.buildstops(RakutenProducts,
                                              outputfile='/tmp/stops.txt',
                                              limit=100,
                                              freqs=True))

        engine.set_conf('sphinx.conf')
        self.assertEquals(engine.executor.get_conf(), 'sphinx.conf')

        print(engine.executor.buildstops(RakutenProducts,
                                              'arena_products',
                                              outputfile='tmp/bar.txt',
                                              limit=1000,
                                              freqs=True))

        session = engine.get_session()


