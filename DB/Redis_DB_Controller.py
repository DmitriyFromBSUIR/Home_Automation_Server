import redis
import hiredis
import pickle
from redis.sentinel import Sentinel
from Globals import Packet as pack

class RedisDB_Wrapper:
    def __init__(self, db_number, host_IP='127.0.0.1', port=6379):
        self._isDbConnectionActive = False
        self._hostIP = host_IP
        self._port = port
        self._dbNumber = db_number
        self._rs = redis.StrictRedis(host=self._hostIP, port=self._port, db=self._dbNumber)
        #pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        #r = redis.Redis(connection_pool=pool)
        # buffering DB commands

        #self._redisPipeline = self._rs.pipeline()

        #self._redisPipeline.execute()

    def is_redisDB_available(self, hostIP='127.0.0.1'):
        # ... get redis connection here, or pass it in. up to you.
        try:
            self._rs.get(None)  # getting None returns None or throws an exception
        except (redis.exceptions.RedisError,
                redis.exceptions.ConnectionError,
                redis.exceptions.BusyLoadingError):
            return False
        return True

    def isRedisServerAvailable(self):
        self._isDbConnectionActive = self._rs.ping()
        return self._isDbConnectionActive

    def getClientsList(self):
        return self._rs.client_list()

    def addRecordToDB(self, key, value):
        self._rs.set(key, value)

    def getRecord(self, key):
        return self._rs.get(key)

    def addObjectToDB(self, key, customObj):
        self._rs.set(key, pickle.dumps(customObj))

    def getObject(self, key):
        return pickle.loads(self._rs.get(key))

    def getAllKeys(self):
        return self._rs.keys()

    def printAllKeys(self):
        for key in self._rs.scan_iter():
            print(key)

    # Remove all keys from all databases
    def clearAllDB(self):
        self._rs.flushall()

    # Remove all keys from the current database
    def delDataFromCurDB(self):
        self._rs.flushdb()

    def writeMultipleRecords(self, ip_iotDevObj):
        pass

    def printRedisNodesInfoViaSentinel(self, master_name, slave_name):
        sentinel = Sentinel([('localhost', 26379)], socket_timeout=0.1)
        sentinel.discover_master(master_name)
        sentinel.discover_slaves(slave_name)

class TestObj:
    def __init__(self, digit):
        self._dict = {"some_info": digit}

    def getInfo(self):
        return self._dict



'''
def func1():
    while True:
        time.sleep(5)
        r = redis.StrictRedis(host = '127.0.0.1', port = 6379, db = 0)
        r2 = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)
        r.append("key1", "data1")
        r.append("key4", "data1")
        print("Func1 write to db1")
        print("Func1 print db1")
        for key in r.keys():
            print(key)
        print("Func1 read db2")
        for key in r2.keys():
            print(key)
        print("Func1 delete db2")
        r2.flushdb()

def func2():
    while True:
        time.sleep(10)
        r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
        r2 = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)
        print("Func2 read db1:")
        for key in r.keys():
            print(key)
        print("Func2 delete db1:")
        r.flushdb()
        r2.append("key2", "data2")
        r2.append("key3", "data2")
        print("Func2 write keys to db2:")
        print("Func2 print db2")
        for key in r2.keys():
            print(key)


import threading as thrd
import time
t1 = thrd.Thread(target=func1)
t2 = thrd.Thread(target=func2)
t1.start()
t2.start()





r = redis.StrictRedis(host = '127.0.0.1', port = 6379, db = 0)
ping = r.ping()
print(ping)
res = r.get("key1")
if res is not None:
    print(res)

r = redis.StrictRedis(host = '127.0.0.1', port = 6379, db = 0)
obj = r.get('23:98:d0:fa:2b:66')
pack = pickle.loads(obj)
print(pack)

4f:0e:e2:cb:43:bb
23:98:d0:fa:2b:66
ee:bf:06:7b:de:db
3f:21:b4:d4:5d:ed
27:78:25:80:0b:1e
c9:74:14:12:fb:31


r = redis.StrictRedis(host = '127.0.0.1', port = 6379, db = 0)
ping = r.ping()
print(ping)
#obj = {'key1': {"key2": 888}}
#r.set('192.168.0.40', obj)

obj = Obj(4)
#r.set('key1', pickle.dumps(obj))
obj2 = r.get('key1')
#r.delete('key1')
#print(pickle.loads(obj2).getInfo())

#print((r.get("192.168.0.40")).decode('UTF-8'))

#deleteditemscnt = r.delete("some_IP")
#print((r.get('some_IP')).decode('UTF-8'))



r = redis.StrictRedis(host='localhost', port=6379, db=0)
print(r)
status = r.set('foo', 'bar')
getStatus = r.get('foo')
print(getStatus)
'''