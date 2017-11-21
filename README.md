# Python_study-2
 Some exercises about Python studying

 This project establish a http server using Tornado.
 Two interfaces have been completed. 
  1.Recording the access times in Redis.
  2.writing the number into MongoDB.

 The access times recorded in Redis could be written into MongoDB and reset when the botton be clicked.

Revision
2017.11.21:
 1. Nesting asynchronous call of Redis and Mongo in Tornado Requesthander.
 2. Conbining Redis and Mongo models into TornadoServer.
