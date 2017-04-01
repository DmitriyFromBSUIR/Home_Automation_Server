import sys
import socket
import websocket
import ssl
import random as rnd

#HOST_URL = "0118d53d.ngrok.io"
HOST_URL = "0585447e.ngrok.io"
#HOST_URL = "localhost"
SERVER_PORT = 80

SECURE_HOST_URL = "27c750fc.ngrok.io"
SEC_HOST_URL = "314a613e.ngrok.io"
SECURE_SERV_PORT = 8080

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

    secure_serv_addr = "ws://" + SEC_HOST_URL + ":" + str(SERVER_PORT) + "/ws"
    print("trying connect to ", secure_serv_addr)
    ws = websocket.create_connection(secure_serv_addr)

    #websocket.connect(serv_addr, http_proxy_host="proxy_host_name", http_proxy_port=3128)
    # ws = websocket.create_connection("ws://" + host + ":" + str(port) + "/websocket")
    ssl_cntx = ssl.SSLContext(ssl.CERT_NONE)
    # ws = websocket.create_connection("wss://" + host + ":" + str(port) + "/ws", ssl=ssl_cntx)
    # ws = websocket.create_connection("wss://" + host + ":" + str(port) + "/websocket")
    print("log: Sending 'Hello, World' ... to Web-Server")
    ws.send("Hello, World")
    print("log: Sent")
    print("log: Receiving...")

    timerForGetDataInSec = rnd.randint(10,100)
    while True:
        result = ws.recv()
        print("Received {}".format(result))

        #result = ws.recv()
        #print("Received {}".format(result))

        timerForGetDataInSec -= 1

    ws.close()