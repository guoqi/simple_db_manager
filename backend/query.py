#!/usr/bin/python
# coding: utf-8

from webapp import get, post, Web


@get("query")
def query(ctx):
    host = ctx.form_param("host")
    port = int(ctx.form_param("port"))
    sql = ctx.form_param("sql")


if __name__ == "__main__":
    web = Web("127.0.0.1", 8888)
    web.run()
