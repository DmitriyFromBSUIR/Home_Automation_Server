import os
import sys
import time
import datetime as dt
import socket
import websocket
import ssl
import random as rnd
import ujson
import IoT_Sensors_Distribution_System.NewJSONPacksGenerator as newGen

HOST_URL = "75440215.ngrok.io"
#HOST_URL = "localhost"

SERVER_PORT = 80
#SERVER_PORT = 2201

SECURE_HOST_URL = "27c750fc.ngrok.io"

SEC_HOST_URL = "d99556e8.ngrok.io"
#SEC_HOST_URL = "1acdff49.ngrok.io"
SECURE_SERV_PORT = 8080


if sys.platform == 'win32':
    #SSL_CRT_DIR = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\SSL_Certificate\\"
    SSL_CRT_DIR = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Cert\\"
else:
    SSL_CRT_DIR = "/home/pi/Projects/Python_Workspace/SSL_Certificate/"


def delay(fromSec=0, tillSec=5):
    pauseInSec = rnd.randint(fromSec, tillSec)
    time.sleep(pauseInSec)

def getCurrentTime():
    curTime = dt.datetime.now()
    #print("LOG: time = ", curTime)
    return curTime

def serialize(packet):
    return ujson.dumps(packet)

def deserialize(packet):
    return ujson.loads(packet)

def printPacketInNormalView(parsedPacket):
    print(ujson.dumps(parsedPacket, indent=4, sort_keys=True))


def statisticsTest():
    curTime = getCurrentTime()
    # for stat\
    queryStatPacket_alldev = {
        "type": "dev_statistics_query",
        "query_type": "realtime",
        "dev_id": "all",
        "time_stamp": curTime
    }
    queryStatPacket = {
        "type": "dev_statistics_query",
        "query_type": "realtime",
        "dev_id": "b7:9b:2f:ff:d1:fb",
        "time_stamp": curTime
    }
    while True:
        #ws.send("stat")
        ws.send(serialize(queryStatPacket))
        delay()
        raw_stat_pack = ws.recv()
        statPack = deserialize(raw_stat_pack)
        printPacketInNormalView(statPack)

def devChangesPacksTest():
    for i in range(0, 1):
        newPacksGen = newGen.NewJSONPackGenerator()
        t_hello_pack, data_pack_1, data_pack_2, data_pack_3 = newPacksGen.packsGeneration()
        packs = [data_pack_1, data_pack_2, data_pack_3]
        for pack in packs:
            ws.send(ujson.dumps(pack))
            print("Sent ", pack)
            '''
            ws.send(ujson.dumps(data_pack_1))
            print("Sent ", data_pack_1)
            ws.send(ujson.dumps(data_pack_2))
            print("Sent ", data_pack_2)
            ws.send(ujson.dumps(data_pack_3))
            print("Sent ", data_pack_3)
            '''


if __name__ == "__main__":
    websocket.enableTrace(True)
    #host = sys.argv[1]
    host = HOST_URL
    #host = socket.gethostbyname(socket.gethostname())
    #port = sys.argv[2]
    port = SERVER_PORT
    #print("log:  Host: ", host, "; Port: ", str(port))

    serv_addr = "ws://" + host + ":" + str(port) + "/ws"
    #print("trying connect to ", serv_addr)
    #ws = websocket.create_connection(serv_addr)

    secure_serv_addr = "ws://" + SECURE_HOST_URL + ":" + str(SERVER_PORT) + "/ws"
    #print("trying connect to ", secure_serv_addr)
    #ws = websocket.create_connection(secure_serv_addr)

    #secure_serv_addr = "wss://" + SEC_HOST_URL + ":" + str(SERVER_PORT) + "/ws"
    secure_serv_addr = "ws://" + SEC_HOST_URL + ":" + str(SERVER_PORT) + "/ws"
    print("trying connect to ", secure_serv_addr)
    ws = websocket.create_connection(secure_serv_addr)
    #ssl_cntx = ssl.SSLContext(ssl.CERT_NONE)
    ssl_cntx = ssl.SSLContext(ssl.CERT_REQUIRED)
    #ssl_cntx.load_cert_chain( os.path.join(SSL_CRT_DIR + "certificate.pem"), os.path.join(SSL_CRT_DIR, "domain.key"))
    #ssl_cntx.load_cert_chain(os.path.join(os.path.join(SSL_CRT_DIR, "pubkey.pem")))

    sslcontext = {"cert_reqs": ssl_cntx}
    #ws = websocket.create_connection(secure_serv_addr, ssl="pubkey.pem")

    #websocket.connect(serv_addr, http_proxy_host="proxy_host_name", http_proxy_port=3128)
    # ws = websocket.create_connection("ws://" + host + ":" + str(port) + "/websocket")
    #ssl_cntx = ssl.SSLContext(ssl.CERT_NONE)
    # ws = websocket.create_connection("wss://" + host + ":" + str(port) + "/ws", ssl=ssl_cntx)
    # ws = websocket.create_connection("wss://" + host + ":" + str(port) + "/websocket")
    print("log: Sending 'Hello, World' ... to Web-Server")
    #ws.send("Hello, World")
    print("log: Sent")
    print("log: Receiving...")

    #timerForGetDataInSec = rnd.randint(10,100)
    #while True:
    packs = list()

    #statisticsTest()

    '''
    for i in range(0, 2):
        packet = ws.recv()
        packs.append(packet)
        print("Received {}".format(packet))
    for pack in packs:
        ws.send((ujson.dumps(pack)).encode("utf-8"))
        print("Sent ", pack)
    '''

        #result = ws.recv()
        #print("Received {}".format(result))

        #timerForGetDataInSec -= 1

    ws.close()