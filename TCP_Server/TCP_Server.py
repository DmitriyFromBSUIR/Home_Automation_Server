import os
import sys
import logging
import socket as sock
import threading as thrd
import socketserver
import json
import ujson
import datetime as dt
import json
from enum import Enum
#import yaml
import dill

import Redis_DB_Controller as rsdb
from DB.RedisDB_Test_Client import DbNumberSelector

class ForkedTCPServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass


logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s',
                    )

class TcpRequestsHandlingMode(Enum):
    SINGLETHREADING = 1
    MULTITHREADING = 2

class IoTControl:
    def __init__(self, name, ctrl_id, type):
        self.set(name, ctrl_id, type)

    def set(self, name, ctrl_id, type):
        self._name = name
        self._ctrl_id = ctrl_id
        self._type = type

    def get(self):
        return (self._name, self._ctrl_id, self._type)


class IoTDevice:
    def addAllControlsToList(self, controlsListInPack):
        for control in controlsListInPack:
            self._listOfControls.append(control)

    def createFirstChangesPacket(self, helloPack):
        self._changesPacket = helloPack["changes_packet"]

    def __init__(self, helloPack):
        self._devID = helloPack["dev_id"]
        self._label = helloPack["label"]
        self._listOfControls = list()
        self._controlsCount = len(helloPack["controls"])
        self.addAllControlsToList(helloPack["controls"])
        self._timestamp = dt.datetime.now(tz=None)
        self._changesPacket = dict()
        self.createFirstChangesPacket(helloPack)
        self._devHelloPack = helloPack

    def getChangesPackSection(self):
        return self._changesPacket

    def setChangesPackSection(self, newChangesPack):
        self._changesPacket = newChangesPack

    def printDeviceInfo(self):
        print("Dev_ID: ", self._devID)
        print("Label: ", self._label)
        print("Controls: ", self._listOfControls)
        print("Timestamp: ", self._timestamp)
        print("ChangesPackSection: ", self._changesPacket)


class DevicesInfo:
    def addIotDevicesToList(self, devices):
        for device in devices:
            self._devices.append(device)

    def __init__(self, devices=list()):
        self._devices = list()

    def getDevicesList(self):
        return self._devices

    def setDevicesList(self, devices):
        self._devices = devices

    def printDevicesData(self):
        for device in self._devices:
            print(device)


class TcpTransferStatisticsCollector:
    pass


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


class RequestsHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        #
        self.broken_packets_counter = 0
        #
        self.normal_packets_counter = 0
        #
        self.transfer_counter = 0
        #
        self.broken_packets_transfer_stat = 0.0
        # db 0 : devices
        self._redis = rsdb.RedisDB_Wrapper(0)
        # db 1 : packets_from_tcp
        self._redis1 = rsdb.RedisDB_Wrapper(1)
        # db 2 : packets from ws
        self._redis2 = rsdb.RedisDB_Wrapper(2)
        # db 3 : all packets
        self._redis3 = rsdb.RedisDB_Wrapper(3)
        # unique key for rs1
        self._rs1_index = 0
        # unique key for rs3
        self._rs3_index = 0
        self.logger = logging.getLogger('RequestHandler')
        self.logger.debug('__init__')
        socketserver.BaseRequestHandler.__init__(self, request,
                                                 client_address,
                                                 server)
        return

    def setup(self):
        self.logger.debug('setup')
        return socketserver.BaseRequestHandler.setup(self)

    def test_packets_recv_from_ESP8266(self, stopSymbol="\r"):
        raw_data = self.request.recv(4096)
        normPack = raw_data.decode("utf-8")
        print(normPack)
        # data = ujson.loads(raw_data.decode("ascii"))
        # print(data)
        # ack = "ok".encode()
        # self.request.send(ack)
        '''
        pack = {"controls": [{"state": "on", "ctrl_id": "adolorumdeleniti"},
                             {"state": 54, "ctrl_id": "voluptatibuslaboreamet"},
                             {"state": 75, "ctrl_id": "errorreruma"}, {"state": 4034, "ctrl_id": "quosquoddistinctio"},
                             {"state": "on", "ctrl_id": "necessitatibusdolorlaboriosam"}], "type": "dev_changes",
                "dev_id": "209.154.213.252", "time_stamp": 1270305449}
        '''
        pack = {"status": "ok"}
        raw_data = (ujson.dumps(pack, ensure_ascii=False) + stopSymbol).encode("utf-8")
        # raw_data = pack.encode("utf-8")
        # raw_data = ujson.dumps(pack).encode("ascii")
        self.request.send(raw_data)

    def updateDataInRSDB(self, packet):
        if packet["type"] == "dev_hello":
            key = packet["dev_id"]
            print("Cur Key = ", key)
            iot_dev = IoTDevice(packet)
            self._redis.addObjectToDB(key, iot_dev)
            iotDev = self._redis.getObject(key)
            print(iotDev.printDeviceInfo())
        if packet["type"] == "dev_changes":
            key = packet["dev_id"]
            iotDev = self._redis.getObject(key)
            if iotDev is not None:
                iotDev.setChangesPackSection(packet)
                self._redis.addObjectToDB(key, iotDev)
                print(iotDev.printDeviceInfo())

    def addPacketToDB1(self, packet, isComplexObject=True):
        if isComplexObject:
            pack = Packet(packet)
            #dill.detect.errors(pack)
            self._redis1.addObjectToDB(str(self._rs1_index), pack)
        else:
            self._redis1.addRecordToDB(str(self._rs1_index), packet)
        self._rs1_index += 1

    def addPacketToDB3(self, packet, isComplexObject=True):
        if isComplexObject:
            pack = Packet(packet)
            dill.detect.errors(pack)
            self._redis3.addObjectToDB(str(self._rs3_index), pack)
        else:
            self._redis3.addRecordToDB(str(self._rs3_index), packet)
        self._rs3_index += 1

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

    def readAllPacketsFromDB2(self, isComplexObject=True):
        keys = self._redis2.getAllKeys()
        packets = list()
        #if keys is not None:
        if len(keys) > 0:
            for key in keys:
                if isComplexObject:
                    packet = self._redis2.getObject(key)
                else:
                    packet = self._redis2.getRecord(key)
                packets.append(packet)
            return packets
        else:
            #return None
            print("Keys list of RSDB #2 is empty!")
            return packets

    def isPacketsExists(self, packets):
        #if packets is not None:
        if len(packets) > 0:
            return True
        else:
            return False

    def sendPacketsFromWS(self, packets):
        for pack in packets:
            #raw_data = (ujson.dumps(pack, ensure_ascii=False) + "\r").encode("utf-8")
            raw_data = (ujson.dumps(pack, ensure_ascii=False)).encode("utf-8")
            self.request.send(raw_data)

    def clearDB2(self):
        self._redis2.delDataFromCurDB()

    def printPacket(self, packet):
        print("Pack Type: ", packet["type"])
        print("Pack:")
        print(packet)

    def printPacketInNormalView(self, parsedPacket):
        print(json.dumps(parsedPacket, indent=4, sort_keys=True))

    def jsonPackSerialize(self, packet):
        # return ujson.dumps(pack, ensure_ascii=False).encode("utf-8")
        return json.dumps(packet, ensure_ascii=False).encode("utf-8")

    def jsonPackDeserialize(self, raw_data):
        # return ujson.loads(raw_data.decode("utf-8"))
        return json.loads(raw_data.decode("utf-8"))

    def sendAckPacket(self):
        ack = "ok".encode()
        self.request.send(ack)

    def packets_recv(self):
        #for i in range(0, 9):
        self.transfer_counter += 1
        #
        self.printCurThreadInfo()
        while True:
            # Receive hello pack from the client
            raw_data = self.request.recv(8196)
            #print(raw_data.decode("utf-8"))
            # pack deserialize
            packet = self.jsonPackDeserialize(raw_data)
            # update changes section in iot_dev objects
            #self.updateDataInRSDB(packet)
            # save packet to DB1
            self.addPacketToDB1(packet)
            # read packets from DB2
            packets = self.readAllPacketsFromDB2()
            # check up the packets in DB2
            if self.isPacketsExists(packets):
                # send packets from DB2 to tcp client
                self.sendPacketsFromWS(packets)
                # clear DB2
                self.clearDB2()
            # save packet to DB3
            self.addPacketToDB3(packet)
            '''
            if packet["type"] == "dev_hello":
                print("DEV_HELLO")
            if packet["type"] == "dev_changes":
                print("DATA")
            '''
            #data = ujson.loads(raw_data.decode())
            #data = raw_data.decode("utf-8")
            #self.logger.debug('recv()-> "%s"', data)
            self.printPacketInNormalView(packet)
            # send ack
            self.sendAckPacket()
            # successful transfer
            self.normal_packets_counter += 1

    def reluanchHandling(self, e):
        self.broken_packets_counter += 1
        #self.broken_packets_transfer_stat = (self.broken_packets_counter / self.transfer_counter) * 100
        self.broken_packets_transfer_stat = (1 - (self.normal_packets_counter / self.transfer_counter)) * 100
        print("DEBUG: broken_packets_transfer_statistics = ", self.broken_packets_transfer_stat, "%")
        print("LOG: TCP_SERVER  Time: ",
              dt.datetime.now(tz=None), "  Error_Msg: ", e)
        self.handle()

    def transferDataFromDIDS(self):
        self.logger.debug('handle')
        #
        #self.transfer_counter += 1
        #
        try:
            self.packets_recv()
        # except (simplejson.decoder.JSONDecodeError, json.decoder.JSONDecodeError) as e:
        except ValueError as e:
            self.broken_packets_counter += 1
            # self.broken_packets_transfer_stat = (self.broken_packets_counter / self.transfer_counter) * 100
            self.broken_packets_transfer_stat = (1 - (self.normal_packets_counter / self.transfer_counter)) * 100
            print("DEBUG: broken_packets_transfer_statistics = ", self.broken_packets_transfer_stat, "%")
            print("LOG: TCP_SERVER (tcp_server_crashed_counter = ", self.broken_packets_counter, " Time: ",
                  dt.datetime.now(tz=None), "  Error_Msg: ", e)
            self.handle()
        except (ConnectionAbortedError, ConnectionResetError) as e:
            #self.reluanchHandling(e)
            pass
        except Exception as e:
            self.reluanchHandling(e)
    '''
    def addClientToClientsList(self):
        print("recv data from client: ", self.client_address)
    '''

    def launchClientHandling(self):
        # add client to list
        #self.addClientToClientsList()
        # transfer data from distribution iot-devices system
        self.transferDataFromDIDS()

    def printCurThreadInfo(self):
        curThread = thrd.currentThread()
        print("Name of current thread", curThread.getName())

    def handle(self):
        # Start client handling in a thread
        #t = thrd.Thread(target=self.launchClientHandling, args=(self,))
        # t.setDaemon(True)  # don't hang on exit
        #t.start()
        #
        self.printCurThreadInfo()
        #
        self.launchClientHandling()
        return

    def finish(self):
        self.logger.debug('finish')
        return socketserver.BaseRequestHandler.finish(self)


#class TCPServer(socketserver.TCPServer, SocketServer.ForkingMixIn):
class TCPServer(socketserver.TCPServer, socketserver.ThreadingMixIn):
#class TCPServer(socketserver.TCPServer):

    def __init__(self, server_address,
                 handler_class=RequestsHandler,
                 ):
        self.logger = logging.getLogger('TCP_Server')
        self.logger.debug('__init__')
        socketserver.TCPServer.__init__(self, server_address,
                                        handler_class)
        #
        self._clients = dict()
        #
        self._clientsCount = 0
        #
        #self._handlingMode = TcpRequestsHandlingMode.SINGLETHREADING
        self._handlingMode = TcpRequestsHandlingMode.MULTITHREADING

        return

    def getClientsList(self):
        return self._clients

    def setClientsList(self, clients):
        self._clients = clients

    def add_client(self, network_addr, con_sock):
        # add client ( net_addr : list(socket, thread, datetime) )
        incomingTime = dt.datetime.now()
        self._clients.update({network_addr: [con_sock, None, incomingTime]})
        # refreash count of clients
        self._clientsCount = len(self._clients)
        print("---------------------------------------------------")
        print("add new client --- NetAddr: ", network_addr, " (Sock: ", con_sock, " , Descriptor of thread: ", None,
              ", client connecting time: ", incomingTime,
              ")")
        print("---------------------------------------------------")

    def printClientsList(self):
        print("Clients count: ", self._clientsCount)
        print("Clients list:")
        for client in self._clients:
            #print("NetAddr: ", client, " ClientCntx: sock = ", self._clients[client][0], " thread_desc = ", self._clients[client][1])
            print("NetAddr: ", client, " ClientCntx: sock = ", self._clients[client][0])
            print("                                  thread_desc = ", self._clients[client][1])
            print("                                  client connecting time = ", self._clients[client][2])

    '''
    Called by the server’s constructor to bind the socket to the desired address. May be overridden.
    '''
    def server_bind(self):
        self.logger.debug('server_bind')
        socketserver.TCPServer.server_bind(self)
        return

    '''
    Called by the server’s constructor to activate the server. The default behavior for a TCP server just invokes
    listen() on the server’s socket. May be overridden.
    '''
    def server_activate(self):
        self.logger.debug('server_activate')
        socketserver.TCPServer.server_activate(self)
        return

    '''
    Return an integer file descriptor for the socket on which the server is listening. This function is most commonly 
    passed to selectors, to allow monitoring multiple servers in the same process.
    '''
    def fileno(self):
        self.logger.debug('fileno')
        return socketserver.TCPServer.fileno(self)



    '''
    This is called in the serve_forever() loop. This method can be overridden by subclasses or mixin classes to
    perform actions specific to a given service, such as cleanup actions.
    '''
    def service_actions(self):
        # call each second (should use for redis db check up)
        self.logger.debug('servive_actions')
        # printing clients list
        self.printClientsList()
        socketserver.TCPServer.service_actions(self)
        return

    '''
    Handle requests until an explicit shutdown() request. Poll for shutdown every poll_interval seconds. Ignores
    the timeout attribute. It also calls service_actions(), which may be used by a subclass or mixin to provide
    actions specific to a given service. For example, the ForkingMixIn class uses service_actions() to clean up
    zombie child processes.
    '''
    def serve_forever(self, poll_interval=0.5):
        self.logger.debug('waiting for request')
        self.logger.info(
            'Handling requests, press <Ctrl-C> to quit'
        )
        socketserver.TCPServer.serve_forever(self, poll_interval)
        return

    '''
    Process a single request. This function calls the following methods in order: get_request(), verify_request(),
    and process_request(). If the user-provided handle() method of the handler class raises an exception, the
    server’s handle_error() method will be called. If no request is received within timeout seconds, handle_timeout()
    will be called and handle_request() will return.
    '''
    def handle_request(self):
        self.logger.debug('handle_request')
        return socketserver.TCPServer.handle_request(self)
    
    '''
    This function is called if the handle() method of a RequestHandlerClass instance raises an exception. The default 
    action is to print the traceback to standard output and continue handling further requests.
    '''    
    def handle_error(self, request, client_address):
        self.logger.debug('handle_error')
        return socketserver.TCPServer.handle_error(self, request, client_address)

    '''
    This function is called when the timeout attribute has been set to a value other than None and the timeout period 
    has passed with no requests being received. The default action for forking servers is to collect the status of any 
    child processes that have exited, while in threading servers this method does nothing.
    '''
    def handle_timeout(self):
        #self.logger.debug('handle_timeout')
        pass
        
    '''
    Must accept a request from the socket, and return a 2-tuple containing the new socket object to be used to
    communicate with the client, and the client’s address.
    '''
    def get_request(self):
        self.logger.debug('get request')
        return socketserver.TCPServer.get_request(self)
        #return

    '''
    Must return a Boolean value; if the value is True, the request will be processed, and if it’s False, the request
    will be denied. This function can be overridden to implement access controls for a server. The default
    implementation always returns True.
    '''
    def verify_request(self, request, client_address):
        self.logger.debug('verify_request(%s, %s)',
                          request, client_address)
        #
        print("client_address = ", client_address)
        self.add_client(client_address, request)

        return socketserver.TCPServer.verify_request(
            self, request, client_address,
        )

    def process_request_thread(self, request, client_address):
        pass

    def process_request_multithreading(self, request, client_address):
        print("multithreading requests handling")
        t = thrd.Thread(target=socketserver.TCPServer.process_request, args=(self, request, client_address,))
        # add descriptor of thread
        self._clients[client_address][1] = t
        return t.start()
        #return t

    def process_request_singlethreading(self, request, client_address):
        return socketserver.TCPServer.process_request(
            self, request, client_address,
        )

    '''
    Calls finish_request() to create an instance of the RequestHandlerClass. If desired, this function can create
    a new process or thread to handle the request; the ForkingMixIn and ThreadingMixIn classes do this.
    '''
    def process_request(self, request, client_address):
        self.logger.debug('process_request(%s, %s)',
                          request, client_address)
        #self.add_client(client_address, request)
        if self._handlingMode == TcpRequestsHandlingMode.SINGLETHREADING:
            return self.process_request_singlethreading(request, client_address)
        else:
            return self.process_request_multithreading(request, client_address)

    '''
    Clean up the server. May be overridden.
    '''
    def server_close(self):
        self.logger.debug('server_close')
        return socketserver.TCPServer.server_close(self)

    '''
    delete client from general client's list by ipv4 address
    '''
    def del_client(self, request_address):
        # get thread descriptor
        #t = self._clients[request_address][1]
        # thread shutdown
        #t.join()
        #print("close thread for client: ", request_address)
        #self._clients[request_address][1].join()
        # delete client
        del self._clients[request_address]
        outcomingTime = dt.datetime.now()
        print("[", outcomingTime, "] client with address [", request_address, "] was deleted from list")

    '''
    delete client from general client's list by socket descriptor
    '''
    def del_client_by_sock(self, sockDesc):
        try:
            for key, value in self._clients.items():
                if value[0] == sockDesc:
                    print("closing socket: ", value[0], " and shutdown the thread: ", value[1])
                    # get thread descriptor
                    #t = value[1]
                    # thread shutdown
                    #t.join()
                    print("client with address [", key, "] was deleted from list")
                    del self._clients[key]
                    # update the size of client's list
                    self._clientsCount = len(self._clients)
                    #
                    #print("client with address [IPv4: ", key1, " port: ", key2, "] was deleted from list")
        except RuntimeError as e:
            print(e)

    '''
    Actually processes the request by instantiating RequestHandlerClass and calling its handle() method.
    '''
    def finish_request(self, request, client_address):
        self.logger.debug('finish_request(%s, %s)',
                          request, client_address)
        return socketserver.TCPServer.finish_request(
            self, request, client_address,
        )

    '''
    close socket when client was disconnecting
    '''
    def close_request(self, request_address):
        self.logger.debug('close_request(%s)', request_address)
        # delete client
        #self.del_client(request_address)
        # del client from general list by socket descriptor
        self.del_client_by_sock(request_address)
        return socketserver.TCPServer.close_request(
            self, request_address,
        )

    '''
    delete all clients from the list
    '''
    def clearClientsList(self):
        self._clientsCount = 0
        self._clients.clear()

    '''
    Tell the serve_forever() loop to stop and wait until it does.
    '''
    def shutdown(self):
        # clear general clients list
        self.clearClientsList()
        self.logger.debug('shutdown()')
        return socketserver.TCPServer.shutdown(self)


#class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
class ThreadedTCPServer:
    def __init__(self, curServPort=3333):
        self._logger = logging.getLogger('server')
        self._curIP = sock.gethostbyname(sock.gethostname())
        # curIP = "192.168.0.27"
        # print("IP = ", curIP)
        self._curServPort = curServPort

    def run(self):
        # address = (curIP, 0)  # let the kernel assign a port
        address = (self._curIP, self._curServPort)  # custom assign a port
        # address = ("localhost", curServPort)  # custom assign a port
        server = TCPServer(address, RequestsHandler)
        ip, port = server.server_address  # what port was assigned?

        # Start the server in a thread
        t = thrd.Thread(target=server.serve_forever)
        #t.setDaemon(True)  # don't hang on exit
        t.start()
        print('Server loop running in process: PID = ', os.getpid())

        self._logger.info('Server on SERVER_IPv4: %s and PORT: %s', ip, port)

        # Clean up
        # server.shutdown()
        # logger.debug('closing socket')

        # logger.debug('done')
        # server.socket.close()


if __name__ == '__main__':
    threadingTCPServer = ThreadedTCPServer()
    threadingTCPServer.run()
