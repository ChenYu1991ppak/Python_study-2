import os

import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.gen

import motor

import asyncio
import asyncio_redis

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

host = "192.168.80.128"
port = 6379
mongo_server = "192.168.80.128"
mongo_port = 27017
key = "value_count"
database = "geetest_python"
collection = "visit"

loop = asyncio.get_event_loop()

@asyncio.coroutine
def get_visit_times():
    connection = yield from asyncio_redis.Connection.create(host=host, port=port)
    f = yield from connection.get(key)
    connection.close()
    return f

@asyncio.coroutine
def reset_visit_times():
    connection = yield from asyncio_redis.Connection.create(host=host, port=port)
    f = yield from connection.set(key, "0")
    connection.close()

@asyncio.coroutine
def count_visit_times():
    # Redis Connection
    connection = yield from asyncio_redis.Connection.create(host=host, port=port)
    yield from connection.incr(key)
    f = yield from get_visit_times()
    connection.close()
    return f

@tornado.gen.coroutine
def Add_into_loop(fun):
    result = loop.run_until_complete(fun)
    return result

# Indexhander
class Indexhander(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        count = yield tornado.gen.Task(Add_into_loop, count_visit_times())
        self.render('index.html', visit_count=count)

# Statishander
class Statishander(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        data = yield tornado.gen.Task(Add_into_loop, get_visit_times())

        db = motor.MotorClient(mongo_server)[database]
        db[collection].update({'title': 'visit_count'}, {'$set': {'visit_count': data}}, callback=None)
        yield tornado.gen.Task(Add_into_loop, reset_visit_times())
        self.redirect("/")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', Indexhander),
            (r'/statis', Statishander)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates")
        )
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

