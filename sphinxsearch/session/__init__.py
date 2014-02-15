# -*- coding: utf-8 -*-


class Session(object):

    def __init__(self, api, host, port):
        self.api = api
        self.host = host
        self.port = port

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.close()

    def close(self):
        self.conn.Close()

    def run(self, *qs_list):
        pass
