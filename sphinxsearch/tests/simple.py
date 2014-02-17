# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest


class Test(unittest.TestCase):
    def test(self):
        from .config1 import RakutenProducts

        print RakutenProducts
