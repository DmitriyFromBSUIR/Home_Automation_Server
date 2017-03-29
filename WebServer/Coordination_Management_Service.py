import sys
from os import listdir
from os.path import isfile, join
from os import walk
import ujson
import urllib3
import websocket
import IoT_Sensors_Distribution_System.JSON_Generator as JSON_Gen


#isGlobalNet = False

#if isGlobalNet:
    #WEB_APP_URI = "https://iot-tumbler.herokuapp.com/update_automation_server"
    #WEB_APP_URL = "iot-tumbler.herokuapp.com"
    #WEB_APP_PORT = 8080
#else:
WEB_APP_URL = "localhost"
WEB_APP_URI = "192.168.0.22/LinkAddressPacketsHandler"
HTTP_URI = "http://localhost/LinkAddressPacketsHandler"
WEB_APP_PORT = 80


if sys.platform == 'win32':
    SPEC_PACK_TYPE = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Template_Packets\\LinkAddressPacket_Type"
    GEN_PACK_DIR = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Template_Packets\\Gen"
    LOG_FILE_DIR = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Logs"
else:
    SPEC_PACK_TYPE = "/home/root/Python_Workspace/iotWebServer/CM_Service/Gen_Packets/LinkAddressPacket_Type"
    GEN_PACK_DIR = "/home/root/Python_Workspace/iotWebServer/CM_Service/Gen_Packets"
    LOG_FILE_DIR = "/home/root/Python_Workspace/iotWebServer/CM_Service/Logs"


class FileWorker:
    def __init__(self, GeneratedPacketsTypeDirs, LogFileDir):
        # dirs to template packets
        self._generatedPacketsTypesDirs = GeneratedPacketsTypeDirs
        # must send via websocket
        #self._packetsNamesLists = list()
        self._packetsNamesLists = dict()
        # must send via http
        self._jpNamesList = list()
        # path to log-file
        self._logFileDir = LogFileDir
        # send via websocket
        self._jsonPackDataList = list()
        # send via http
        self._jpDataList = list()

    def getFilenamesList(self, isLogging, path):
        filesList = list()
        for (dirpath, dirnames, filenames) in walk(path):
            #self._packetsNamesList.extend(filenames)
            #filesList.extend(filenames)
            return filenames
            #break
        if (isLogging):
            print("Packets Names:")
            print(self._packetsNamesLists)
        #return self._packetsNamesList
        #return filesList

    if sys.platform == 'win32':
        def getFilesList(self, isLogging=False, path="\\"):
            if path != "\\":
                filesList = list()
                for curDir in self._generatedPacketsTypesDirs:
                    filesList = self.getFilenamesList(isLogging, curDir)
                    if(curDir != SPEC_PACK_TYPE):
                        # self._packetsNamesLists.append(filesList)
                        self._packetsNamesLists.update({curDir: filesList})
                    else:
                        self._jpNamesList = filesList
                return (self._packetsNamesLists, self._jpNamesList)
            else:
                return self.getFilenamesList(isLogging, path)
    else:
        def getFilesList(self, isLogging=False, path="."):
            if path == ".":
                filesList = list()
                for curDir in self._generatedPacketsTypesDirs:
                    filesList = self.getFilenamesList(isLogging, curDir)
                    if (curDir != SPEC_PACK_TYPE):
                        #self._packetsNamesLists.append(filesList)
                        self._packetsNamesLists.update({curDir: filesList})
                    else:
                        self._jpNamesList = filesList
                return (self._packetsNamesLists, self._jpNamesList)
            else:
                return self.getFilenamesList(isLogging, path)

    def readJsonFile(self, jpTypeDir, filename, isSpecType):
        if sys.platform == 'win32':
            filepath = jpTypeDir + "\\" + filename
        else:
            filepath = jpTypeDir + "/" + filename
        with open(filepath) as json_file:
            json_data = ujson.load(json_file)
            print("filepath: ", filepath)
            print("jp name: ", filename)
            print(json_data)
            if isSpecType:
                self._jpDataList.append(json_data)
            else:
                self._jsonPackDataList.append(json_data)

    def jsonPacketsRead(self):
        for jpTypeDir in self._generatedPacketsTypesDirs:
            #for filename in self.getFilesList(True, jpTypeDir):
            if (jpTypeDir == SPEC_PACK_TYPE):
                # cycle over LinkAddressType packets
                for filename in self._jpNamesList:
                    self.readJsonFile(jpTypeDir, filename, True)
            else:
                # cycle over other packet
                for curPackTypeDir in self._packetsNamesLists:
                    for filename in self._packetsNamesLists[curPackTypeDir]:
                        self.readJsonFile(curPackTypeDir, filename, False)

        return (self._jsonPackDataList, self._jpDataList)

    def run(self):
        self.getFilesList(True, " ")
        otherJPTypes, linkAddressJPTypes = self.jsonPacketsRead()
        return (otherJPTypes, linkAddressJPTypes)


class Transceiver:
    def __init__(self, web_application_URI, web_application_PORT, jpDataList, specJPDataList):
        self.web_app_uri = web_application_URI
        self.web_app_port = web_application_PORT
        self._jpDataList = jpDataList
        self._specJPDataList = specJPDataList
        self._http = urllib3.PoolManager()

    def linkAddressTypeJsonPacketsSendTo(self):
        # read all packets
        for jsonPacket in self._specJPDataList:
            json_data = jsonPacket
            # send json-files to web-app via POST-Request
            '''
            response = self._http.request('POST', self.web_app_uri,
                                    headers={'Content-Type': 'application/json'},
                                    body=ujson.dumps(json_data))
            '''
            '''
            response = self._http.request('POST', WEB_APP_URI,
                                    headers={'Content-Type': 'application/json'},
                                    body=ujson.dumps(json_data))
            '''

            response = self._http.request('POST', HTTP_URI,
                                          headers={'Content-Type': 'application/json'},
                                          body=ujson.dumps(json_data))

            # write to log file
            print("response status = ", response.status)
            print("data in response: ", response.data)

    def jsonPacketsSendTo(self, URL):
        websocket.enableTrace(True)
        #host = self.web_app_uri
        host = URL
        # host = socket.gethostbyname(socket.gethostname())
        port = self.web_app_port
        print("log:  Host: ", host, "; Port: ", port)
        ws = websocket.create_connection("ws://" + host + ":" + str(port) + "/websocket")
        print("log: Sending packets to Web-Server")
        # send all packets
        for jsonPacket in self._jpDataList:
            ws.send(ujson.dumps(jsonPacket))
        print("log: Sent")
        print("log: Receiving...")
        result = ws.recv()
        print("Received {}".format(result))
        ws.close()

    def transmit(self):
        # send LinkAddressPackets via https
        self.linkAddressTypeJsonPacketsSendTo()
        # send other packets via websocket
        self.jsonPacketsSendTo(WEB_APP_URL)

    def run(self):
        self.transmit()

if __name__ == "__main__":
    # generate 1000 pseudorandom packets
    dirsToGenPackets = JSON_Gen.start_test(20)
    #fw = FileWorker(GEN_PACK_DIR, LOG_FILE_DIR)
    # caching/reading json-files
    fw = FileWorker(dirsToGenPackets, LOG_FILE_DIR)
    otherJPTypes, linkAddressJPTypes = fw.run()
    # send packets to web-app
    while True:
        # transfer vis https
        #linkAddressTypeJP_Transceiver = Transceiver(WEB_APP_URI, WEB_APP_PORT, otherJPTypes, linkAddressJPTypes)
        linkAddressTypeJP_Transceiver = Transceiver(HTTP_URI, WEB_APP_PORT, otherJPTypes, linkAddressJPTypes)
        linkAddressTypeJP_Transceiver.run()
        # transfer via websocket
