
import os
import sys
import ujson
import urllib3
import random as rnd
import time
import json
import datetime as dt

import LAN_Tunnel as tunneling

HTTP_URI = "http://c586d48b.ngrok.io/automation_server"
#HTTP_URI = "http://f6f7086b.ngrok.io:80/PacketsHandler"

GEOLOC_SERVICE_URL = "http://ip-api.com/json"

if sys.platform == 'win32':
    LOG_FILE_DIR = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Logs"
    ONE_LINK_ADDRESS_PACK_FILEPATH = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Registration\\reg_my_edison.json"

else:
    LOG_FILE_DIR = "/home/root/Python_Workspace/iotWebServer/CM_Service/Logs"
    ONE_LINK_ADDRESS_PACK_FILEPATH = "/home/root/Python_Workspace/iotWebServer/CM_Service/Registration/reg_my_edison.json"

'''
elif sys.platform == 'linux':
    LOG_FILE_DIR = "/media/shared_folder/My_Projects/Home_Automation_Server/WebServer/Logs"
    ONE_LINK_ADDRESS_PACK_FILEPATH = "/media/shared_folder/My_Projects/Home_Automation_Server/WebServer/Registration/reg_my_intel_edison.json"
'''

class HPR_Service:
    def __init__(self, URI):
        self._httpServerURI = URI
        self._httpCntx = urllib3.PoolManager()
        self.packet = dict()
        self._publicURL = ""
        #self.curTume = None

    def readRegistrationFile(self):
        json_data = ""
        with open(ONE_LINK_ADDRESS_PACK_FILEPATH) as json_file:
            json_data = ujson.load(json_file)
            print("json_data:")
            print(json_data)
            return json_data

    def getGeolocationInfo(self):
        response = self._httpCntx.request('GET', GEOLOC_SERVICE_URL)
        print("Response status: ", response.status)
        print("Response status: ", response.data)
#        return (response.status, (response.data).decode("utf-8") )
        return (response.status, ujson.decode(response.data))

    def getUrl(self):
        tunnel = tunneling.TunnelingCatcher()
        return tunnel.catchTunnelingTelemetry()

    def refreshUrl(self):
        self._publicURL = self.getUrl()
        substr = self._publicURL.split("\n")[1]
        substr = substr.split(":")[1]
        ws_url = "ws:" + substr + "/ws"
        self._publicURL = ws_url
        print("generated url for web-app: ", self._publicURL)

    def modifyUrlInPacket(self, urlKey="url"):
        self.packet[urlKey] = self._publicURL

    def writeGeneratedUrlToPacket(self):
        self.refreshUrl()
        self.modifyUrlInPacket()

    def mergeLinkAddrPackAndGeoloc(self, geolocData):
        self.packet.update({"geoloc": geolocData})
        #self.curTume = dt.datetime.now(tz=None)
        self.packet.update({"timeStamp": dt.datetime.now(tz=None)})

    def sendRegFile(self, json_data):
        response = self._httpCntx.request('POST', self._httpServerURI,
                                      headers={'Content-Type': 'application/json'},
                                      body=ujson.dumps(json_data))
        print("LOG: response status = ", response.status)
        print("LOG: data in response: ", response.data)
        return response

    def serverAckCheckUp(self, http_server_response):
        pass

    def run(self):
        json_file_data = self.readRegistrationFile()
        self.packet = json_file_data
        # get info from geolocatioin service
        geolocData = self.getGeolocationInfo()[1]
        # write ngrok url to packet
        self.writeGeneratedUrlToPacket()
        # merge src packet and geoloc
        self.mergeLinkAddrPackAndGeoloc(geolocData)
        # send packet to web-app
        #response = self.sendRegFile(json_file_data)
        response = self.sendRegFile(self.packet)
        self.serverAckCheckUp(response)

if __name__ == "__main__":
    hpr_service = HPR_Service(HTTP_URI)
    hpr_service.run()