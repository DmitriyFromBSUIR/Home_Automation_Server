
import os
import sys
import ujson
import urllib3
import random as rnd
import time
import json

HTTP_URI = "http://da10c330.ngrok.io/update_automation_server"

if sys.platform == 'win32':
    LOG_FILE_DIR = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Logs"
    ONE_LINK_ADDRESS_PACK_FILEPATH = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Registration\\reg_my_edison.json"
else:
    LOG_FILE_DIR = "/home/root/Python_Workspace/iotWebServer/CM_Service/Logs"
    ONE_LINK_ADDRESS_PACK_FILEPATH = "/home/root/Python_Workspace/iotWebServer/CM_Service/Registration/reg_my_edison.json"

class HPR_Service:
    def __init__(self, URI):
        self._httpServerURI = URI
        self._httpCntx = urllib3.PoolManager()

    def readRegistrationFile(self):
        json_data = ""
        with open(ONE_LINK_ADDRESS_PACK_FILEPATH) as json_file:
            json_data = ujson.load(json_file)
            print("json_data:")
            print(json_data)
            return json_data

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
        json_file = self.readRegistrationFile()
        response = self.sendRegFile(json_file)
        self.serverAckCheckUp(response)

if __name__ == "__main__":
    hpr_service = HPR_Service(HTTP_URI)
    hpr_service.run()