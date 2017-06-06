import redis
import hiredis
import pickle
from redis.sentinel import Sentinel
from enum import Enum
import json
import ujson

#from TCP_Server import Packet

class Packet:
    def __init__(self, packet):
        self._packet = packet
        self._packType = packet["type"]
        self._timestamp = packet["time_stamp"]

    def setPacketData(self, packData, packType, packTimestamp):
        self._packet = packData
        self._packType = packType
        self._timestamp = packTimestamp

    def getPacketData(self):
        return (self._packType, self._timestamp, self._packet)

    def getMainPackData(self):
        return (self._packType, self._timestamp)

    def getPacket(self):
        return self._packet

    def setPacket(self, packet):
        self._packet = packet

class DbNumberSelector(Enum):
    REDIS_DB_0 = 0
    REDIS_DB_1 = 1
    REDIS_DB_2 = 2
    REDIS_DB_3 = 3

class RedisDbMiniCluster:
    def __init__(self, maxRecordCountLimit=27000):
        # for devices
        self._rsdb_0 = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
        # for current packets from tcp-socket
        self._rsdb_1 = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)
        # for current packets from websocket
        self._rsdb_2 = redis.StrictRedis(host='127.0.0.1', port=6379, db=2)
        # for all packets
        self._rsdb_3 = redis.StrictRedis(host='127.0.0.1', port=6379, db=3)
        # max records count limit for redis db (if 1 record = 10 KB then 26214 records = 256 MB)
        self._maxRecordCountLimit = maxRecordCountLimit
        self._rsdb_0_recordsCount = 0
        self._rsdb_1_recordsCount = 0
        self._rsdb_2_recordsCount = 0
        self._rsdb_3_recordsCount = 0

    def clusterConnectionMonitoring(self):
        print("PING rsdb_0: ", self._rsdb_0.ping())
        # for current packets from tcp-socket
        print("PING rsdb_1: ", self._rsdb_1.ping())
        # for current packets from websocket
        print("PING rsdb_2: ", self._rsdb_2.ping())
        # for all packets
        print("PING rsdb_3: ", self._rsdb_3.ping())

    def printPacketInNormalView(self, parsedPacket):
        print(json.dumps(parsedPacket, indent=4, sort_keys=True))

    def packSerialize(self, packet):
        #return ujson.dumps(packet)
        #return json.dumps(packet, ensure_ascii=False).encode("utf-8")
        #return pickle.dumps(packet.encode("utf-8"))
        return pickle.dumps(packet)

    def packDeserialize(self, packet):
        #return ujson.loads(packet)
        #return json.loads(packet).decode("utf-8")
        return pickle.loads(packet)

    def clearAllDBsInCluster(self):
        #
        self._rsdb_0.flushdb()
        self._rsdb_1.flushdb()
        self._rsdb_2.flushdb()
        self._rsdb_3.flushdb()

    '''
    
    '''
    def redisDbRecordsCountLimitCheckUp(self):
        self._rsdb_0_recordsCount = len(self._rsdb_0.keys())
        self._rsdb_1_recordsCount = len(self._rsdb_1.keys())
        self._rsdb_2_recordsCount = len(self._rsdb_2.keys())
        self._rsdb_3_recordsCount = len(self._rsdb_3.keys())
        curTotalRecordsCount = self._rsdb_0_recordsCount + self._rsdb_1_recordsCount + self._rsdb_2_recordsCount + \
                               self._rsdb_3_recordsCount
        if curTotalRecordsCount == self._maxRecordCountLimit:
            self.clearAllDBsInCluster()

    def printClusterInfo(self):
        print("Keys in RSDB 0 (count = ", len(self._rsdb_0.keys()), "):")
        print(self._rsdb_0.keys())
        print("Keys in RSDB 1 (count = ", len(self._rsdb_1.keys()), "):")
        print(self._rsdb_1.keys())
        print("Keys in RSDB 2 (count = ", len(self._rsdb_2.keys()), "):")
        print(self._rsdb_2.keys())
        print("Keys in RSDB 3 (count = ", len(self._rsdb_3.keys()), "):")
        print(self._rsdb_3.keys())
        print("Values in RSDB 3:")

        # rsdb_1.flushdb()
        # rsdb_3.flushdb()

        for key in self._rsdb_3.keys():
            raw_packet = self._rsdb_3.get(key.decode("utf-8"))
            print(pickle.loads(raw_packet))
            packet = self.packDeserialize(raw_packet)
            # packet = (raw_packet).decode("UTF-8")
            self.printPacketInNormalView(packet.getPacket())

    def test_record(self, dev_id="b7:9b:2f:ff:d1:fb"):
        print("======================== Test Record ========================")
        for key in self._rsdb_3.keys():
            raw_packet = self._rsdb_3.get(key.decode("utf-8"))
            print(pickle.loads(raw_packet))
            pack = self.packDeserialize(raw_packet)
            packet = pack.getPacket()
            if packet["dev_id"] == dev_id:
                # packet = (raw_packet).decode("UTF-8")
                self.printPacketInNormalView(packet)

    def run(self):
        self.clusterConnectionMonitoring()
        self.printClusterInfo()
        self.test_record()


if __name__ == '__main__':
    #
    redisMiniCluster = RedisDbMiniCluster()
    redisMiniCluster.run()