from pymongo import MongoClient
from RedisObject import RedisObject

host_addr = "192.168.46.10"
port = 27017
usr = None
passwd = None
list_name = "name"
database = "geetest_python"
collection = "visit"

class MonClient():
    def __init__(self, host=host_addr, p=port, u=None, pwd=None):
        self.host = host
        self.port = p
        self.mongo = MongoClient(self.host, self.port)
        self.db = None
        self.usr = u
        self.pwd = pwd
        self.collection = None

    def select_database_and_collection(self, database, collection=None):
        self.db = self.mongo[database]
        if self.usr is not None and self.pwd is not None:
            self.db.authenticate(self.usr, self.pwd)
        if collection is not None:
            self.collection = self.db.get_collection(collection)

    def write_into_database(self, data):
        assert self.collection is not None, "Collection is None!"
        record = {"title": "visit_count", "visit_count": data}
        self.collection.insert_one(record)

    def update_visit_times(self, value):
        self.collection.update_one({'title': 'visit_count'}, {'$set': {'visit_count': value}})

def pop_data_from_redislist(addr):
    re = RedisObject.redis_connected(host=addr)
    data = re.pop_line_from_list(list_name)
    while data:
        yield data
        data = re.pop_line_from_list(list_name)

if __name__ == '__main__':
    Client = MonClient(u=usr, pwd=passwd)
    Client.select_database_and_collection(database, collection=collection)
    data = pop_data_from_redislist(host_addr)
    for d in data:
        if d is not None:
            Client.write_into_database(d)


