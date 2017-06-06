
import os
import sys
import socket
import ujson
import time
import json
import random as rnd
import datetime as dt
import pickle

from os import walk

import tornado.httpclient as httpClient
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.auth
import tornado.gen
from tornado.escape import json_decode, json_encode
from enum import Enum
#import yaml
import threading as thrd

from Globals import PACKETS_TYPES
import Redis_DB_Controller as rsdb
from DB.RedisDB_Test_Client import DbNumberSelector

from Globals import *
import Coordination_Management_Service as CM_Service
import IoT_Sensors_Distribution_System.NewJSONPacksGenerator as newGen


#define("port", default=8000, help="run on the given port", type=int)

# we gonna store clients in dictionary..
#clients = dict()

# for redirecting
HTTP_URI = "http://localhost:9000"

SERVER_PORT = 8080


#queue_from_ws = list()
#queue_from_tcp = [{"type": "dev_hello"}, {"type": "dev_changes"}, {"type": "dev_changes"}]


if sys.platform == 'win32':
    # SSL_CRT_DIR = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\SSL_Certificate\\"
    SSL_CRT_DIR = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Cert\\"
else:
    SSL_CRT_DIR = "/home/pi/Projects/Python_Workspace/SSL_Certificate/"


# create http client
class HTTP_Client():
    def __init__(self, host):
        self.http_client = httpClient.HTTPClient()
        try:
            response = self.http_client.fetch(host)
            print(response.body)
        except httpClient.HTTPError as e:
            # HTTPError is raised for non-200 responses; the response
            # can be found in e.response.
            print("Error: " + str(e))
        except Exception as e:
            # Other errors are possible, such as IOError.
            print("Error: " + str(e))

class IndexPageHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        #self.write("This is your response")
        print("Client press button 'Connect'")
        #self.render("index.html")
        #self.finish()

class PacketsHandler(tornado.web.RequestHandler):
    def post(self):
        print("Pack data: ", json_decode(self.request.body))
        response = {'pack_status': 'ok'}
        self.write(response)

'''

'''
class JsonPacketsSimulator:
    def isPacketHasTransferPermission(self, key, hasTransferPermissionsList):
        result = False
        for packType in hasTransferPermissionsList:
            if key == packType:
                result = True
        return result

    #from faker import Factory
    #fake = Factory.create()

    if sys.platform == 'win32':
        DELIM = "\\"
    else:
        DELIM = "/"

    def getFilenamesList(self, path, delim=DELIM):
        filesList = list()
        for (dirpath, dirnames, filenames) in walk(path):
            filesList.extend(filenames)
            return filenames

    def read_json_packets(self, path, delim=DELIM):
        jsonFileDataList = list()
        jsonfilenames = self.getFilenamesList(path)
        for jsonfilename in jsonfilenames:
            with open(path + delim + jsonfilename) as jsonfile:
                json_file_data = ujson.load(jsonfile)
                jsonFileDataList.append(json_file_data)
        return jsonFileDataList


    def dataPacksModification(self, packetType, id_sync, listener=None, jsonPacket=None):
        # read data packets
        jsonFileDataList = list()
        if sys.platform == 'win32':
            jsonFileDataList = self.read_json_packets(
                "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Template_Packets\\DataPacket_Type")
        else:
            jsonFileDataList = self.read_json_packets(
                "/home/root/Python_Workspace/iotWebServer/CM_Service/Gen_Packets/DataPacket_Type")
        for jsonPacket in jsonFileDataList:
            self.data_pack_resetId(jsonPacket, packetType, id_sync)
        return jsonFileDataList
        '''
        # save control_id from DeviceHelloPack
        dev_ch_pack = jsonPacket["changes_packet"]
        print(dev_ch_pack)
        # controlsListOfDict = dev_ch_pack["controls"]
        controlsListOfDict = dev_ch_pack["controls"]
        controls_ids = list()
        for control in controlsListOfDict:
            controls_ids.append(control["ctrl_id"])
        # reset control_id
        for jsonDataPack in jsonFileDataList:
            # for i in range(0, len(jsonDataPack["controls"])-1):
            for i in range(0, len(jsonDataPack["controls"]) - 1):
                # jsonDataPack["controls"][i]["ctrl_id"] = controls_ids[i]
                jsonDataPack["controls"][i]["ctrl_id"] = controls_ids[i]
            listener.write_message(ujson.dumps(jsonDataPack))
            pauseInSec = rnd.randint(2, 3)
            time.sleep(pauseInSec)
        '''

    def hello_pack_resetId(self, jsonPacket, packetType, ctrl_id_type_sync, switch_state_max_cnt):
        if packetType == "dev_hello":
            controls = list()
            toggleAviableStates = ["true", "false"]
            jsonPacket["changes_packet"]["dev_id"] = ctrl_id_type_sync.get("dev_id")
            #
            del ctrl_id_type_sync["dev_id"]
            #
            for type, id in ctrl_id_type_sync.items():
                control = dict()
                control.update({"ctrl_id": id})

                if type == "toggle":

                    selector = rnd.randint(0, 1)
                    toggleState = toggleAviableStates[selector]
                    control.update({"state": toggleState})

                if type == "switch_state":

                    switch_state_st = rnd.randint(0, switch_state_max_cnt)
                    control.update({"state": switch_state_st})

                if type == "dimmer":

                    dimmerState = rnd.randint(0, 100)
                    control.update({"state": dimmerState})

                if type == "num_value":

                    numValueState = rnd.randint(0, 8196)
                    control.update({"state": numValueState})

                if type == "sym_value":

                    sym_value_selector = rnd.randint(0, 1)
                    sym_value_state = toggleAviableStates[sym_value_selector]
                    control.update({"state": sym_value_state})

                controls.append(control)
            jsonPacket["changes_packet"]["controls"] = controls
            return jsonPacket["changes_packet"]
            '''
            for i in range(0, len(ctrl_id_type_sync)-1):
                if jsonPacket["changes_packet"]["controls"][i]["type"]["name"] == "toggle":
                    jsonPacket["changes_packet"]["controls"][i]["ctrl_id"] = ctrl_id_type_sync.get("toggle")
                if jsonPacket["changes_packet"]["controls"][i]["type"]["name"] == "switch_state":
                    jsonPacket["changes_packet"]["controls"][i]["ctrl_id"] = ctrl_id_type_sync.get("switch_state")
                if jsonPacket["changes_packet"]["controls"][i]["type"]["name"] == "dimmer":
                    jsonPacket["changes_packet"]["controls"][i]["ctrl_id"] = ctrl_id_type_sync.get("dimmer")
                if jsonPacket["changes_packet"]["controls"][i]["type"]["name"] == "num_value":
                    jsonPacket["changes_packet"]["controls"][i]["ctrl_id"] = ctrl_id_type_sync.get("num_value")
                if jsonPacket["changes_packet"]["controls"][i]["type"]["name"] == "sym_value":
                    jsonPacket["changes_packet"]["controls"][i]["ctrl_id"] = ctrl_id_type_sync.get("sym_value")
            '''

    def reset_states_in_data_packet(self, dataPacket, ctrl_id_type_sync, switch_state_max_cnt):
        i = 0
        toggleAviableStates = ["true", "false"]
        for key, value in ctrl_id_type_sync.items():
            if key == "toggle":
                selector = rnd.randint(0, 1)
                toggleAviableStates = ["true", "false"]
                toggleState = toggleAviableStates[selector]
                dataPacket["controls"][i]["state"] = toggleState
            if key == "switch_state":
                switch_state_st = rnd.randint(0, switch_state_max_cnt)
                dataPacket["controls"][i]["state"] = switch_state_st
            if key == "dimmer":
                dimmerState = rnd.randint(0, 100)
                dataPacket["controls"][i]["state"] = dimmerState
            if key == "num_value":
                numValueState = rnd.randint(0, 8196)
                dataPacket["controls"][i]["state"] = numValueState
            if key == "sym_value":
                sym_value_selector = rnd.randint(0, 1)
                sym_value_state = toggleAviableStates[sym_value_selector]
                dataPacket["controls"][i]["state"] = sym_value_state
            i += 1


    def data_pack_resetId(self, jsonPacket, packetType, ctrl_id_type_sync):
        if packetType == "dev_changes":
            #print("sync id list :")
            #print(id_sync)
            jsonPacket["dev_id"] = ctrl_id_type_sync.get("dev_id")
            jsonPacket["controls"][0]["ctrl_id"] = ctrl_id_type_sync.get("toggle")
            jsonPacket["controls"][1]["ctrl_id"] = ctrl_id_type_sync.get("switch_state")
            jsonPacket["controls"][2]["ctrl_id"] = ctrl_id_type_sync.get("dimmer")
            jsonPacket["controls"][3]["ctrl_id"] = ctrl_id_type_sync.get("num_value")
            jsonPacket["controls"][4]["ctrl_id"] = ctrl_id_type_sync.get("sym_value")
            #
            selector = rnd.randint(0, 1)
            toggleAviableStates = ["true", "false"]
            toggleState = toggleAviableStates[selector]
            jsonPacket["controls"][0]["state"] = toggleState
            #
            switch_state_st = rnd.randint(0, 4096)
            jsonPacket["controls"][1]["state"] = switch_state_st
            #
            dimmerState = rnd.randint(0, 100)
            jsonPacket["controls"][2]["state"] = dimmerState
            #
            numValueState = rnd.randint(0, 8196)
            jsonPacket["controls"][3]["state"] = numValueState
            #
            sym_value_selector = rnd.randint(0, 1)
            sym_value_state = toggleAviableStates[sym_value_selector]
            jsonPacket["controls"][4]["state"] = sym_value_state


    # generate and send pseudorandom packets
    def _sendAllPackets(self, listener, jpTransferStartTimeBorder=10, jpTransferEndTimeBorder=15, hasTransferPermissionsList=["dev_hello"]):
        # get all packets types without LinkAddress type
        #isNeedPacketsRegeneration = True
        while True:
            jsonPacketsDataList = CM_Service.packetsGeneration(20)[0]
            print("LOG: Error. jsonPacketsDataList is empty!")
            if len(jsonPacketsDataList) > 0:
                break
        print("-----------------------------")
        print("Packets for sendidng:")
        print(jsonPacketsDataList)
        print("-----------------------------")
        print("log: Sending packets ")
        transferInSec = rnd.randint(jpTransferStartTimeBorder, jpTransferEndTimeBorder)
        # send all packets
        packetsCount = 3
        helloPackNo = 0
        dataPackNo = 0
        # list for dev_id and ctrl_id sync
        id_sync = list()
        ctrl_id_type = dict()
        dataPacket = dict()
        switch_state_max_cnt = 0
        for jsonPacket in jsonPacketsDataList:
            # check up the transfer permission list
            if self.isPacketHasTransferPermission(jsonPacket["type"], hasTransferPermissionsList):
                #self.write_message(ujson.dumps(jsonPacket))
                #pingPack = listener.ping(data='')
                #print("ping = ", pingPack)
                # if not ws.ws_connection or not ws.ws_connection.stream.socket:
                #self.ping(data='hey')
                #if listener.ws_connection:

                if listener in self.clients:
                    #if jsonPacket["type"] == "dev_hello":
                        #dataPacket = dict()
                        if helloPackNo < 1:
                            print("Cur Hello Pack:")
                            print(jsonPacket)
                            from faker import Faker
                            fake = Faker()
                            new_dev_id = fake.mac_address()
                            jsonPacket["dev_id"] = new_dev_id
                            '''
                            id_sync.append(jsonPacket["dev_id"])
                            id_sync.append(
                                (jsonPacket["controls"][0].get("type"), jsonPacket["controls"][0].get("ctrl_id")))
                            id_sync.append(
                                (jsonPacket["controls"][1].get("type"), jsonPacket["controls"][1].get("ctrl_id")))
                            id_sync.append(
                                (jsonPacket["controls"][2].get("type"), jsonPacket["controls"][2].get("ctrl_id")))
                            id_sync.append(
                                (jsonPacket["controls"][3].get("type"), jsonPacket["controls"][3].get("ctrl_id")))
                            id_sync.append(
                                (jsonPacket["controls"][4].get("type"), jsonPacket["controls"][4].get("ctrl_id")))
                            '''
                            ctrl_id_type.update({"dev_id": jsonPacket["dev_id"]})

                            for i in range(0, len(jsonPacket["controls"])):
                                print("DEBUG: control #", i, " name: ", jsonPacket["controls"][i].get("type").get("name"), " state: ",
                                      jsonPacket["changes_packet"]["controls"][i].get("state"))
                                if jsonPacket["controls"][i].get("type").get("name") == "switch_state":
                                    switch_state_max_cnt = len(jsonPacket["controls"][i].get("type").get("optional").get(
                                        "names"))
                                ctrl_id_type.update({jsonPacket["controls"][i].get("type").get("name"):
                                                     jsonPacket["controls"][i].get("ctrl_id")})
                            print("DEBUG: max count of switch_state:", switch_state_max_cnt)
                            dataPacket = self.hello_pack_resetId(jsonPacket, jsonPacket["type"], ctrl_id_type,
                                                                 switch_state_max_cnt)
                            listener.write_message(ujson.dumps(jsonPacket))

                            #pauseInSec = rnd.randint(20, 30)
                            #time.sleep(pauseInSec)
                            #self.reset_states_in_data_packet(dataPacket, ctrl_id_type, switch_state_max_cnt)
                            #listener.write_message(ujson.dumps(dataPacket))
                            #print("Sent Data Packet")
                            #print(dataPacket)
                            print("DEBUG: struct for sync:")
                            print(ctrl_id_type)
                            helloPackNo += 1
                        else:
                            #helloPackNo = 0
                            if dataPackNo < 3:
                                pauseInSec = rnd.randint(20, 30)
                                time.sleep(pauseInSec)
                                self.reset_states_in_data_packet(dataPacket, ctrl_id_type, switch_state_max_cnt)
                                listener.write_message(ujson.dumps(dataPacket))
                                print("Sent Data Packet:")
                                print(dataPacket)
                            else:
                                dataPackNo = 0
                                ctrl_id_type.clear()
                                dataPacket.clear()
                            break

                            #listener.write_message(ujson.dumps(dataPacket))
                            '''
                            helloPackNo = 0
                            #listener.write_message(ujson.dumps({"msg": "Please, reconnecting for new 3 packets"}))
                            sync_data_packs = self.dataPacksModification("dev_changes", ctrl_id_type)
                            # send data packs
                            for dataPacket in sync_data_packs:
                                print("id list for sync:")
                                print(id_sync)
                                print("Data_Packet")
                                print(dataPacket)
                                if dataPackNo < 3:
                                    listener.write_message(ujson.dumps(dataPacket))
                                    dataPackNo += 1
                                    print("Sent Data_Packet")
                                    print(dataPacket)
                                    #pauseInSec = rnd.randint(20, 30)
                                    pauseInSec = rnd.randint(20, 30)
                                    time.sleep(pauseInSec)
                                else:
                                    dataPackNo = 0
                                    ctrl_id_type.clear()
                                    break
                            '''
                            break


                    #else:
                        '''
                        sync_data_packs = self.dataPacksModification(jsonPacket["type"], id_sync)
                        # send data packs
                        for jsonPacket in sync_data_packs:
                            if dataPackNo < 3:
                                listener.write_message(ujson.dumps(jsonPacket))
                                dataPackNo += 1
                                pauseInSec = rnd.randint(20, 30)
                                time.sleep(pauseInSec)
                            else:
                                id_sync.clear()
                                break
                        '''
                    #self.data_received()
                else:
                    break
                    #self.clients.remove(listener)
                #pauseInSec = rnd.randint(5, 10)
                pauseInSec = rnd.randint(20, 30)
                time.sleep(pauseInSec)
                print("Sent hello-packet:")
                print(jsonPacket)
                transferInSec -= 1
                '''
                if transferInSec != 0:
                    self.write_message(ujson.dumps(jsonPacket))
                    pauseInSec = rnd.randint(5, 10)
                    time.sleep(pauseInSec)
                    print("Sent packet:")
                    print(jsonPacket)
                    transferInSec -= 1
                else:
                    self.close()
                '''

    def dateGenerate(self):
        from faker import Faker
        fake = Faker()
        startDate = dt.datetime(1970, 1, 2)
        # startDate = dt.datetime(1970, 1, 1, hour=0, minute=0, second=1, microsecond=0, tzinfo=None)
        # dt.datetime.today()
        endDate = dt.datetime.now(tz=None)
        date = fake.date_time_between_dates(datetime_start=startDate, datetime_end=endDate, tzinfo=None)
        return date



from DB.RedisDB_Test_Client import DbNumberSelector as dbNumSelector
from DB.RedisDB_Test_Client import Packet as pack

class WSHandler(tornado.websocket.WebSocketHandler):
    # general list of connected clients
    clients = []
    #handlers = []
    # list of clients sessions
    sessionsList = dict()
    # db 0 : devices
    _redis = rsdb.RedisDB_Wrapper(0)
    # db 1 : packets_from_tcp
    _redis1 = rsdb.RedisDB_Wrapper(1)
    # db 2 : packets from ws
    _redis2 = rsdb.RedisDB_Wrapper(2)
    # db 3 : all packets
    _redis3 = rsdb.RedisDB_Wrapper(3)
    # unique key for rs1
    _rs2_index = 0
    # unique key for rs3
    _rs3_index = 0
    #
    _generalPacketsTable = dict()
    #
    _statTable = dict()

    '''
        db0 : devices
        db1 : current packets from tcp-socket
        db2 : current packets from ws
        db3 : all packets
        '''
    def dbMonitoring(self, dbNumber):
        if dbNumber == DbNumberSelector.REDIS_DB_0:
            return self._redis.isRedisServerAvailable()
        if dbNumber == DbNumberSelector.REDIS_DB_1:
            return self._redis1.isRedisServerAvailable()
        if dbNumber == DbNumberSelector.REDIS_DB_2:
            return self._redis2.isRedisServerAvailable()
        if dbNumber == DbNumberSelector.REDIS_DB_3:
            return self._redis3.isRedisServerAvailable()
        return False

    def dataSerialize(self, data):
        return pickle.dumps(data.encode("utf-8"))

    def dataDeserialize(self, raw_data):
        data = pickle.loads(raw_data)
        return data

    def keyDeserialize(self, raw_key):
        return raw_key.decode("utf-8")

    def getDataFromDB3(self):
        for key in self._redis3.getAllKeys():
            packetObj = self._redis3.getObject(key)
            packet = packetObj.getPacket()
            key = self.keyDeserialize(key)
            self._generalPacketsTable.update({key: packet})

    def printDataFromDB3(self):
        print("Data from DB #3")
        for key, value in self._generalPacketsTable.items():
            print(key, " ", value)

    def sendStatPacket(self):
        if self.dbMonitoring(dbNumSelector.REDIS_DB_3):
            self.getDataFromDB3()
            self.printDataFromDB3()

    def addMeasure(self, packet):
        # find dev_id
        cur_dev_id = packet["dev_id"]
        timestamp = packet["time_stamp"]
        for dev_id, ctrl_stat_list in self._statTable.items():
            if cur_dev_id == dev_id:
                for packControl in packet["controls"]:
                    measure = dict()
                    ctrl_id_in_dataPack = packControl["ctrl_id"]
                    ctrl_index = 0
                    for control in self._statTable[dev_id]:
                        ctrl_id_in_statTab = control["ctrl_id"]
                        if ctrl_id_in_dataPack == ctrl_id_in_statTab:
                            state = packControl["state"]
                            measure.update({"state": state})
                            measure.update({"time_stamp": timestamp})
                            self._statTable[dev_id][ctrl_index]["measure"].append(measure)
                            break
                        ctrl_index += 1


    def addDevice(self, packet):
        dev_id = packet["dev_id"]
        #controls = dict()
        controls = list()
        timestamp = packet["time_stamp"]
        for control in packet["controls"]:
            ctrl_item = dict()
            ctrl_measures = list()
            measure = dict()
            ctrl_id = control["ctrl_id"]
            # find state by ctrl_id in "changes_packet" section
            for ctrl in packet["changes_packet"]["controls"]:
                if ctrl["ctrl_id"] == ctrl_id:
                    state = ctrl["state"]
                    measure.update({"state": state})
                    measure.update({"time_stamp": timestamp})
                    break
            # add measure from "changes_packet" section
            ctrl_measures.append(measure)
            # add measures for current ctrl
            ctrl_item.update({"ctrl_id": ctrl_id})
            ctrl_item.update({"measure": ctrl_measures})
            # add control to list
            controls.append(ctrl_item)
        self._statTable.update({dev_id: controls})

    def createStatTable(self):
        for index, packet in self._generalPacketsTable.items():
            if packet["type"] == "dev_hello":
                self.addDevice(packet)
            #if packet["type"] == "dev_changes":
                #self.addMeasure(packet)

    def fillupStatTable(self):
        for index, packet in self._generalPacketsTable.items():
            if packet["type"] == "dev_changes":
                self.addMeasure(packet)

    def printStatTable(self):
        self.getCurrentTime()
        print("Stat Table (Compact):")
        print(self._statTable)
        print("Stat Table:")
        for dev_id, ctrl_list in self._statTable.items():
            print("dev_id: ", dev_id, " ctrl_list: ", ctrl_list)

    def generateStatPacket(self, dev_id, ctrl_list):
        packet = dict()
        curTime = self.getCurrentTime()
        packet.update({"type": "dev_statistics"})
        packet.update({"dev_id": dev_id})
        packet.update({"stat": ctrl_list})
        packet.update({"time_stamp": curTime})
        return packet

    def packSerialize(self, packet):
        return ujson.dumps(packet)

    def packDeserialize(self, raw_data):
        return ujson.loads(raw_data)

    def sendStatForDevice(self, selected_dev_id):
        for dev_id, ctrl_list in self._statTable.items():
            if dev_id == selected_dev_id:
                print("---------------------------- Dev Stat for sending: ----------------------------")
                print("dev_id: ", dev_id, " ctrl_list: ", ctrl_list)
                packet = self.generateStatPacket(dev_id, ctrl_list)
                self.write_message(self.packSerialize(packet))
                break

    def buildStatTable(self):
        self.createStatTable()
        self.printStatTable()
        self.fillupStatTable()
        self.printStatTable()

    def getStatFor(self, dev_id):
        if self.dbMonitoring(DbNumberSelector.REDIS_DB_3):
            self.getDataFromDB3()
            self.printDataFromDB3()
            self.buildStatTable()
            dev_id_list = self._statTable.keys()
            if dev_id in dev_id_list:
                self.sendStatForDevice(dev_id)
            else:
                self.getCurrentTime()
                print("Error! Can't found device ID: ", dev_id)
        else:
            self.getCurrentTime()
            print("Error! RedisDB is not respond")

    def sendAllStat(self):
        pass

    def sendQueueStatPackets(self):
        self.createStatTable()
        self.printStatTable()
        self.fillupStatTable()
        self.printStatTable()
        self.sendAllStat()

    '''
    def __init__(self, num):
        #super.__init__()
        self.num = num
        print(num)
    

    def sendAllPacketsFromTCP(self, listener):
        if listener in self.clients:
            if len(queue_from_tcp) > 0:
                for pack in queue_from_tcp:
                    listener.write_message(ujson.dumps(pack))
                    print("Pack")
                    print(pack)
                    pauseInSec = rnd.randint(0,5)
                    time.sleep(pauseInSec)
                # del packs
                queue_from_tcp.clear()
    '''

    def sendAllPackets(self, listener, jpTransferStartTimeBorder=10, jpTransferEndTimeBorder=15,
                        hasTransferPermissionsList=["dev_hello"]):
        newPacksGen = newGen.NewJSONPackGenerator()
        t_hello_pack, t_data_pack, data_pack_2, data_pack_3 = newPacksGen.packsGeneration()
        if listener in self.clients:
            listener.write_message(ujson.dumps(t_hello_pack))
            print("Hello_Pack")
            print(t_hello_pack)
            pauseInSec = rnd.randint(20, 30)
            time.sleep(pauseInSec)
            listener.write_message(ujson.dumps(t_data_pack))
            print(t_data_pack)
            pauseInSec = rnd.randint(20, 30)
            time.sleep(pauseInSec)
            listener.write_message(ujson.dumps(data_pack_2))
            print(data_pack_2)

    def listnerService(self):
        # add new client to general clients list
        self.clients.append(self)
        # add record to sessions list
        clientHandler = thrd.Thread(target=self.sendAllPackets, args=(self,))
        #clientHandler = thrd.Thread(target=self.sendStatPacket, args=(self,))
        #clientHandler = thrd.Thread(target=self.sendAllPacketsFromTCP, args=(self,))
        self.sessionsList.update({self: clientHandler})
        # print("Status: ", self.get_status())
        print('create new connection')
        print("registered new client")
        # find client session
        for listneredSock, handler in self.sessionsList.items():
            if self == listneredSock:
                # start thread in self.sessionsList[listneredSock]
                self.sessionsList.get(listneredSock).start()

    def open(self):
        print("handle listener")
        #self.listnerService()
        '''
        for listener in self.clients:
            self.handlers.append( thrd.Thread(target=self.sendAllPackets, args=(listener,)).start() )
        '''
        '''
        for i in range(0, 10000):
            self.write_message({"status": "shit"})
        '''
        '''
        for listener in self.clients:
            self.sendAllPackets(listener)
        '''


    def requestToHTTPServer(self):
        # create http_client
        tornado_http_client = HTTP_Client(HTTP_URI)

    def getCurrentTime(self):
        curTime = dt.datetime.now()
        print("LOG: time = ", curTime)
        return curTime

    # get statistics for all devices
    def getStat(self):
        #if self.dbMonitoring(3):
        if self.dbMonitoring(DbNumberSelector.REDIS_DB_3):
            self.getDataFromDB3()
            self.printDataFromDB3()
            self.sendQueueStatPackets()
        else:
            print("Error! Redis DB #3 is not responding")

    def statQueryPacketAnalysis(self):
        print("---------------------------- Stat for All Devices ---------------------------- ")
        self.getCurrentTime()
        self.getStat()
        print("------------------------------------------------------------------------------ ")

    def statisticsQueryPacketHandler(self, sq_packet):

        if sq_packet["dev_id"] == "all":
            self.statQueryPacketAnalysis()
        else:
            print("Stat for Device that have dev_id: ", sq_packet["dev_id"])
            self.getStatFor(sq_packet["dev_id"])

    def addPacketToDB2(self, packet, isComplexObject=True):
        if isComplexObject:
            pack = Packet(packet)
            #dill.detect.errors(pack)
            self._redis1.addObjectToDB(str(self._rs2_index), pack)
        else:
            self._redis1.addRecordToDB(str(self._rs2_index), packet)
        self._rs2_index += 1

    def readAllPacketsFromDB1(self, isComplexObject=True):
        keys = self._redis1.getAllKeys()
        packets = list()
        # if keys is not None:
        if len(keys) > 0:
            for key in keys:
                if isComplexObject:
                    packet = self._redis1.getObject(key)
                else:
                    packet = self._redis1.getRecord(key)
                packets.append(packet)
            return packets
        else:
            # return None
            print("Keys list of RSDB #2 is empty!")
            return packets

    def isPacketsExists(self, packets):
        #if packets is not None:
        if len(packets) > 0:
            return True
        else:
            return False

    def addPacketToDB3(self, packet, isComplexObject=True):
        if isComplexObject:
            pack = Packet(packet)
            self._redis3.addObjectToDB(str(self._rs3_index), pack)
        else:
            self._redis3.addRecordToDB(str(self._rs3_index), packet)
        self._rs3_index += 1

    def sendPacketsFromTCP(self, packets):
        pass

    def clearDB1(self):
        self._redis1.delDataFromCurDB()

    def dataPacketsHandler(self, packet):
        # save packet to DB2
        self.addPacketToDB2(packet)
        # read packets from DB2
        packets = self.readAllPacketsFromDB1()
        # check up the packets in DB2
        if self.isPacketsExists(packets):
            # send packets from DB1 to ws client
            self.sendPacketsFromTCP(packets)
            # clear DB1
            self.clearDB1()
        # save packet to DB3
        self.addPacketToDB3(packet)

    def packetsRouting(self, packet):
        if packet["type"] == "dev_changes":
            self.dataPacketsHandler(packet)
        if packet["type"] == "dev_status":
            pass
        if packet["type"] == "user_script":
            pass
        if packet["type"] == "script_changes":
            pass
        if packet["type"] == "ack":
            print("Receive Ack Packet:")
            print(packet)
        if packet["type"] == "dev_statistics":
            pass
        if packet["type"] == "dev_statistics_query":
            #t = thrd.Thread(target=self.getStat)
            t = thrd.Thread(target=self.statisticsQueryPacketHandler, args=(packet,))
            t.start()

    def packetsHandler(self, packet):
        typesList = PACKETS_TYPES
        packType = packet["type"]
        if packType in typesList:
            self.packetsRouting(packet)
        else:
            curTime = dt.datetime.now()
            print("[", curTime, "] Receive packet with incorrect type. Packet type: ", packet["type"])

    def on_message(self, message):
        curTime = dt.datetime.now()
        print ("[", curTime, '] message received:  %s' % message)
        # send pseudo ack
        #self.write_message(ujson.dumps({"status": "ok"}))
        # deserialize
        packet = self.packDeserialize(message)
        # check up packet type
        self.packetsHandler(packet)
        # print ('sending back message: %s' % message[::-1])
        # add pack to queue
        #queue_from_ws.append(message)
        #print("queue = ", queue_from_ws)
        # send pseudorandom packets
        #self.sendAllPackets()
        #self.close()

    def on_pong(self, data):
        print("data = ", data)

    def on_close(self):
        print ('connection closed')
        timeStamp = dt.datetime.now(tz=None)
        print(timeStamp)
        '''
        if self.id in clients:
            del clients[self.id]
        '''
        if self in self.clients:
            # del client from clients list
            self.clients.remove(self)
            # get thread by websocket discriptor
            t = self.sessionsList.get(self)
            # finish thread that associate with current client
            if t.is_alive():
                t.join()
            # del record in the sessions list
            del self.sessionsList[self]
            #
            self.close()

    def check_origin(self, origin):
        return True

'''
application = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/ws', WSHandler),
])

application = tornado.web.Application([
    (r'/ws', WSHandler),
])
'''

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            #(r'/', IndexPageHandler),
            (r'/ws', WSHandler),
            #(r'/websocket', WSHandler),
            (r'/PacketsHandler', PacketsHandler),
        ]
        settings = {
            'template_path': 'templates'
        }
        tornado.web.Application.__init__(self, handlers, **settings)

'''
    Singleton
'''
class WebServer(object):
    __instance = None

    @staticmethod
    def inst(port):
        if WebServer.__instance == None:
            WebServer.__instance = WebServer(port)
        return WebServer.__instance

    def run(self):
        print("Log: Web-Server is running")
        # parse_command_line()
        # app.listen(options.port)
        ws_app = Application()
        # http_server = tornado.httpserver.HTTPServer(application)
        # non-SSL Tornado WebSockets
        http_server = tornado.httpserver.HTTPServer(ws_app)
        # SSL Tornado WebSockets
        '''
        http_server = tornado.httpserver.HTTPServer(ws_app, ssl_options = {
            "certfile": os.path.join(SSL_CRT_DIR, "certificate.pem"),
            "keyfile": os.path.join(SSL_CRT_DIR, "domain.key"),
        })
        '''
        http_server.listen(self._port)
        #
        '''
        http_server.listen(self._port, ssl_options={
            "certfile": os.path.join(lib_dir, "mydomain.crt"),
            "keyfile": os.path.join(lib_dir, "mydomain.key"),
        })
        '''
        if sys.platform == 'win32':
            myIP = socket.gethostbyname(socket.gethostname())
            print('*** Websocket Server Started at IP = %s ***' % myIP, ", Port = ", self._port)

        tornado.ioloop.IOLoop.instance().start()

        #tornado.ioloop.IOLoop.current().start()

    def __init__(self, port):
        self._port = port
        # to start the web-server
        self.run()


def web_server_start(port):
        print("================================================================")
        print("  Intelligent management analytics and monitoring web-server.")
        print("  (C) 2016-2017. IoT Home Automation Server.")
        print("  (C) 2016-2017. GreenHouse PaaS / GreenHouse Project. All rights reserved.")
        print("================================================================")
        print("")
        print("Web-Server starting ...")
        # create Web-Server Obj
        web_server = WebServer(port)

if __name__ == "__main__":
    web_server_start(sys.argv[1])
    #web_server_start(9090)
    #web_server_start(SERVER_PORT)