
import tornado.httpserver
import tornado.httpclient as httpClient
import tornado.websocket
import tornado.ioloop
import tornado.web
import os
import sys
import socket
import ujson
import time
import random as rnd
from tornado.escape import json_decode, json_encode

import Coordination_Management_Service as CM_Service

from tornado.options import define, options, parse_command_line

#define("port", default=8000, help="run on the given port", type=int)

# we gonna store clients in dictionary..
#clients = dict()

# for redirecting
HTTP_URI = "http://localhost:9000"

SERVER_PORT = 80

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
        self.render("index.html")
        #self.finish()

class PacketsHandler(tornado.web.RequestHandler):
    def post(self):
        print("Pack data: ", json_decode(self.request.body))
        response = {'pack_status': 'ok'}
        self.write(response)

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print('create new connection')
        print("registered new client")

    def requestToHTTPServer(self):
        # create http_client
        tornado_http_client = HTTP_Client(HTTP_URI)

    def sendAllPackets(self):
        # get all packets types without LinkAddress type
        jsonPacketsDataList = CM_Service.packetsGeneration(20)[0]
        print("log: Sending packets to Web-Server")
        # send all packets
        for jsonPacket in jsonPacketsDataList:
            self.write_message(ujson.dumps(jsonPacket))
            pauseInSec = rnd.randint(5, 100)
            time.sleep(pauseInSec)

    def on_message(self, message):
        print ('message received:  %s' % message)
        # print ('sending back message: %s' % message[::-1])
        # Reverse Message and send it back
        # print ('sending back message: %s' % message[::-1])
        print('sending back message: ' % {"status": "ok"})
        self.write_message(ujson.dumps({"status": "ok"}))
        # send pseudorandom packets
        self.sendAllPackets()

    def on_close(self):
        print ('connection closed')
        '''
        if self.id in clients:
            del clients[self.id]
        '''

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
            #(r'/websocket', WSHandler)
            (r'/ws', WSHandler),
            (r'/websocket', WSHandler),
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
        http_server = tornado.httpserver.HTTPServer(ws_app)
        http_server.listen(self._port)
        if sys.platform == 'win32':
            myIP = socket.gethostbyname(socket.gethostname())
            print('*** Websocket Server Started at IP = %s ***' % myIP, ", Port = ", self._port)
        #tornado.ioloop.IOLoop.instance().start()
        tornado.ioloop.IOLoop.current().start()

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
    #web_server_start(sys.argv[1])
    #web_server_start(9090)
    web_server_start(SERVER_PORT)