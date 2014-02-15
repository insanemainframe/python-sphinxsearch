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
        self.engine = get_engine(self.api, self.server, self.indexer, set())

    def test(self):
        print(self.engine.session())

        self.engine.add_index(RakutenProducts)

        print(self.engine.create_config())

        conf_file_path = join(TMP_ROOT, 'sphinx.conf')

        self.engine.set_conf(conf_file_path)

        self.engine.save()


