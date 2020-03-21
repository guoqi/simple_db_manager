#!/usr/bin/python
# coding: utf-8

from webapp import Web, get, post


@get("/home", "user")
def home(ctx, user):
    return "Hello {0}!".format(user)


@post("/hello")
def hello(ctx):
    return "Hi, {0}".format(ctx.form_param("user"))


if __name__ == "__main__":
    web = Web("127.0.0.1", 8888)
    web.run()
