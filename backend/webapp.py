#!/usr/bin/python
# coding: utf-8

import socket
import traceback
import sys
from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler


class Router(object):
    '''Simple router'''
    route_table = {}
    @staticmethod
    def add(method, path, func, *args):
        if not Router.route_table.has_key(method):
            Router.route_table[method] = {}
        Router.route_table[method][path] = {
            "func": func,
            "args": args
        }

    @staticmethod
    def match(method, path):
        if not Router.route_table.has_key(method):
            return None
        if not Router.route_table[method].has_key(path):
            return None
        return Router.route_table[method][path]


class Context(object):
    '''Simple HTTP Request Context'''

    def __init__(self, app):
        self._method = app.command
        (url, query) = self.parse_path(app.path)
        self._path = url
        self._urldata = self.parse_kv(query)
        self._message = ""
        self._formdata = {}
        content_length = int(app.headers.getheader("Content-Length", 0))
        print content_length
        if content_length > 0:
            self._message = app.rfile.read(content_length)
            self._formdata = self.parse_kv(self._message)

    def parse_path(self, path):
        pos = path.find('?')
        if pos == -1:
            return path, ""
        return path[0:pos], path[pos+1:]

    def parse_kv(self, kvstr):
        r = {}
        m = kvstr.split('&')
        for item in m:
            v = item.split('=')
            if len(v) >= 2:
                r[v[0]] = v[1]
            else:
                r[v[0]] = ""
        return r

    @property
    def method(self):
        return self._method

    @property
    def path(self):
        return self._path

    def has_url_param(self, name):
        return self._urldata.has_key(name)

    def url_param(self, name):
        if not self.has_url_param(name):
            return ""
        return self._urldata[name]

    def has_form_param(self, name):
        return self._formdata.has_key(name)

    def form_param(self, name):
        if not self.has_form_param(name):
            return ""
        return self._formdata[name]

    @property
    def message(self):
        return self._message


class App(BaseHTTPRequestHandler):
    '''Simple application framework'''

    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def dispatch(self):
        print "piapia"
        context = Context(self)
        obj = Router.match(context.method, context.path)
        if obj is None:
            self.send_error(404, "{0} {1} not found".format(
                context.method, context.path))
            return
        kwargs = {}
        for name in obj["args"]:
            if not context.has_url_param(name):
                self.send_error(400, "missing parameters {0}".format(name))
                return
            kwargs[name] = context.url_param(name)
        print kwargs
        sys.stdout.flush()
        try:
            retinfo = obj["func"](context, **kwargs)
            print retinfo
            sys.stdout.flush()
            self.send_response(200)
            self.send_header("Content-Length", len(retinfo))
            self.end_headers()
            self.wfile.write(retinfo)
        except Exception as e:
            print traceback.format_exc()
            self.send_error(500, str(e))

    def do_GET(self):
        self.dispatch()

    def do_POST(self):
        self.dispatch()


class Web(object):
    '''Base web server'''

    def __init__(self, host, port):
        self._host = host
        self._port = port

    def run(self):
        httpd = HTTPServer((self._host, self._port), App)
        httpd.serve_forever()


def _route(method, path, *args):
    def decorator(func):
        Router.add(method, path, func, *args)

        def wrapper(ctx, *args, **kwargs):
            return func(ctx, *args, **kwargs)
        return wrapper
    return decorator


def get(path, *args):
    return _route('GET', path, *args)


def post(path, *args):
    return _route('POST', path, *args)
