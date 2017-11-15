import os

import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.gen
import redis

from MongoObject import MonClient
from RedisObject import RedisObject

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

CONNECTION_POOL = redis.ConnectionPool(max_connections=100)

redis_server = "192.168.46.10"
Mongo_server = "192.168.46.10"
key = "value_count"
database = "geetest_python"
collection = "visit"

@tornado.gen.coroutine
def count_visit_times():
    # Redis Connection
    r = RedisObject.redis_connected(host=redis_server, pool=None)
    value = r.read_key_value(key)
    visit = int(value) + 1 if value is not None else 1
    r.modify_key_value(key, visit)
    return visit

class Indexhander(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        count = yield tornado.gen.Task(count_visit_times)
        self.render('index.html', visit_count=count)

class Statishander(tornado.web.RequestHandler):
    def post(self):
        DBclient = MonClient()
        r = RedisObject.redis_connected(host=redis_server, pool=None)
        DBclient.select_database_and_collection(database, collection=collection)
        data = int(r.read_key_value(key))
        DBclient.update_visit_times(data)
        r.modify_key_value(key, 0)
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

