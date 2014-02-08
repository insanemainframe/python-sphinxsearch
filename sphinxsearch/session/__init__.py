# -*- coding: utf-8 -*-


class SessionFactory(object):
    def __init__(self, engine):
        self.engine = engine

    def __call__(self):
        return Session(self.engine)


class Session(object):

    def __init__(self, engine):
        self.engine = engine
        self.conn = engine.get_connection()

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.close()

    def close(self):
        self.conn.Close()

    def run(self, *qs_list):
        pass
