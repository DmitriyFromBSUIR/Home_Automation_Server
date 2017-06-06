import sys
import logging
import socket as sock
import threading as thrd
import socketserver
import ujson
import random as rnd
import time
import datetime as dt

import IoT_Sensors_Distribution_System.NewJSONPacksGenerator as newGen

logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s',
                    )

#ip = "192.168.0.22"
ip = "192.168.100.5"

#ip = "127.0.0.1"
#ip = "192.168.0.27"
#ip = "10.10.1.135"
port = 3333

class TCP_Client:
    def __init__(self, serverIP = ip, serverPort = port):
        self._sock = None
        self._serverIP = serverIP
        self._serverPort = serverPort
        self._logger = logging.getLogger('client')
        #
        self.connectToServer()

    def connectToServer(self):
        # Connect to the server
        self._logger.debug('creating socket')
        self._sock = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        # self._sock.setblocking(False)
        self._sock.settimeout(10)
        self._logger.debug('connecting to server')
        self._sock.connect((self._serverIP, self._serverPort))
        print('connected to ', self._serverIP, " : ", self._serverPort)

    def delay(self, fromSec=0, tillSec=5):
        pauseInSec = rnd.randint(fromSec, tillSec)
        time.sleep(pauseInSec/1000)

    def send(self, msgSize=0):
        # Send the data
        #message = 'Hello, world'.encode()
        #self._logger.debug('sending data: %r', message)
        #self._msgSize = self._sock.send(message)
        packs_gen = newGen.NewJSONPackGenerator()
        hello_pack, data_pack_1, data_pack_2, data_pack_3 = packs_gen.packsGeneration()
        for pack in [hello_pack, data_pack_1, data_pack_2, data_pack_3]:
            raw_data = ujson.dumps(pack, ensure_ascii=False).encode("utf-8")
            #raw_data = ujson.dumps(pack).encode("ascii")
            self._sock.send(raw_data)
            self.delay()
            self._logger.debug("sent to the server:")
            self._logger.debug(pack)
        '''
        raw_data = ujson.dumps(hello_pack, ensure_ascii=False).encode("utf-8")
        self._sock.send(raw_data)
        self._logger.debug("sent to the server:")
        self._logger.debug(hello_pack)
        raw_data = ujson.dumps(data_pack_1, ensure_ascii=False).encode("utf-8")
        self._sock.send(raw_data)
        self._logger.debug("sent to the server:")
        self._logger.debug(data_pack_1)
        raw_data = ujson.dumps(data_pack_2, ensure_ascii=False).encode("utf-8")
        self._sock.send(raw_data)
        self._logger.debug("sent to the server:")
        self._logger.debug(data_pack_2)
        raw_data = ujson.dumps(data_pack_3, ensure_ascii=False).encode("utf-8")
        self._sock.send(raw_data)
        self._logger.debug("sent to the server:")
        self._logger.debug(data_pack_3)
        '''
        return (hello_pack, data_pack_1, data_pack_2, data_pack_3)

    def receive(self, msgSize=0):
        # Receive a response
        self._logger.debug('waiting for response')
        response = self._sock.recv(8196)
        self._logger.debug('response from server: %r', response)
        print("response from server: ", response.decode("utf-8"))

    def disconnect(self):
        #
        self._sock.close()

    def run(self):
        #self.connectToServer()
        try:
            while True:
                print(dt.datetime.now())
                #self.delay()
                #print(dt.datetime.now())
                self.send()
                self.receive()
                #print(dt.datetime.now())
                self.delay()
                #print(dt.datetime.now())
        except Exception as e:
            print(e)
            self.run()
        '''
        try:
            self.connectToServer()
            while True:
                self.send()
                #self.receive()
                pauseInSec = rnd.randint(0, 5)
                time.sleep(pauseInSec)
        except Exception as e:
            print(e)
            self.run()
        '''


        #while True:
            #self.receive()
        '''
        for i in range(0,3):
            self.send()
            #self.receive()
            pauseInSec = rnd.randint(0, 1)
            time.sleep(pauseInSec)
        '''

if __name__ == '__main__':
    client = TCP_Client()
    client.run()