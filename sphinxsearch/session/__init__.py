# -*- coding: utf-8 -*-


class SessionFactory(object):
    def __init__(self):
        pass

    def set_server(self, server):
        self.server = server

    def __call__(self):
        api = self.server.api
        host = self.server.host
        port = self.server.port
        return Session(api, host, port)


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
