import ujson
from os import listdir
from os.path import isfile, join
from os import walk
from pprint import pprint
#from faker import Factory
from faker import Faker
import sys
import random as rnd
import datetime as dt
import os
import errno

from Globals import *

if sys.platform == 'win32':
    PATH_DELIM = "\\"
    CUR_DIR = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Template_Packets"
    # MAX_JSON_PACKETS_COUNT = 20
    GEN_DIR = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Template_Packets\\Gen"
else:
    PATH_DELIM = "/"
    CUR_DIR = "/home/root/Python_Workspace/iotWebServer/CM_Service/Template_Packets"
    GEN_DIR = "/home/root/Python_Workspace/iotWebServer/CM_Service/Gen_Packets"

class JSON_Packets_Parser:
    def getFilesListInCurDir(self, path):
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
        return onlyfiles

    def __init__(self, pathToIdealJsonPacket, templatesMaxCount=0):
        self._rootDir = pathToIdealJsonPacket
        self._templatesOfJsonPacketsCount = templatesMaxCount
        self._templatesOfJsonPacketsFilesList = list()
        self._jsonTPacketData = list()
        self._generalKeysList = list()

    def getJsonTPacketsData(self):
        return self._jsonTPacketData

    def getJsonTPacketsList(self):
        return self._templatesOfJsonPacketsFilesList

    def getMainKeysList(self):
        return self._generalKeysList

    def getFilenamesList(self, isLogging, path):
        for (dirpath, dirnames, filenames) in walk(path):
            self._templatesOfJsonPacketsFilesList.extend(filenames)
            break
        if (isLogging):
            print("Templates of Packets:")
            print(self._templatesOfJsonPacketsFilesList)
        return self._templatesOfJsonPacketsFilesList

    if sys.platform == 'win32':
        def getFilesList(self, isLogging=False, path="\\"):
            if path == "\\":
                return self.getFilenamesList(isLogging, self._rootDir)
            else:
                return self.getFilenamesList(isLogging, path)
    else:
        def getFilesList(self, isLogging=False, path="."):
            if path == ".":
                return self.getFilenamesList(isLogging, self._rootDir)
            else:
                return self.getFilenamesList(isLogging, path)
    '''
    def getFilesList(self, isLogging=False, path=""):
        if path == "":
            for (dirpath, dirnames, filenames) in walk(self._rootDir):
                self._templatesOfJsonPacketsFilesList.extend(filenames)
                break
            if (isLogging):
                print("Templates of Packets:")
                print(self._templatesOfJsonPacketsFilesList)
            return self._templatesOfJsonPacketsFilesList
        else:
            for (dirpath, dirnames, filenames) in walk(path):
                self._templatesOfJsonPacketsFilesList.extend(filenames)
                break
            if(isLogging):
                print("Templates of Packets:")
                print(self._templatesOfJsonPacketsFilesList)
            return self._templatesOfJsonPacketsFilesList
    '''
    def jsonPacketsParsing(self):
        for templatePacket in self._templatesOfJsonPacketsFilesList:
            filepath = self._rootDir + PATH_DELIM + templatePacket
            with open(filepath) as data_file:
                data = ujson.load(data_file)
                self._jsonTPacketData.append(data)
            pprint(data)

    def getAllJsonTPacketsKeys(self, isLogging=False):
        for templatePacketData in self._jsonTPacketData:
            keys = templatePacketData.keys()
            keysList = list()
            for key in keys:
                keysList.append(key)
            self._generalKeysList.append(keysList)
            if(isLogging):
                print("Keys:")
                print(keys)
        #print("debug")

    def run(self):
        self.getFilesList(True, CUR_DIR)
        self.jsonPacketsParsing()
        self.getAllJsonTPacketsKeys()



class JSON_Packets_Gen:
    def __init__(self, dir, jsonTPacketsList, generalKeysList, jsonTPacketData, maxJsonPacketsCount=1):
        # save generated json-files to this dir
        self._dir = dir
        # the general count of json template files
        self._jsonTemplatesCount = len(jsonTPacketsList)
        # the list of json template files
        self._jsonTPacketsList = jsonTPacketsList
        # the list of main keys
        self._generalKeysList = generalKeysList
        # data of each key
        self._jsonTPacketData = jsonTPacketData
        # total count of json packets that must be generated
        self._maxJsonPacketsCount = maxJsonPacketsCount
        # count of each JSON template packet type
        self._templatesTypesPacketCount = list()
        # separate dirs for each packet type
        self._generatedJsonPacketsDirs = list()

    def getGeneratedDirs(self):
        return self._generatedJsonPacketsDirs



    def packetsProbabilitiesCheckUp(self, packTypeProbabilitiesList, isPercentsView):
        prob_sum = 0
        for prob in packTypeProbabilitiesList:
            prob_sum += prob
        if(isPercentsView):
            if prob_sum > 100:
                raise Exception("Error! prob_sum > 100 %")
        else:
            if prob_sum > 1:
                raise Exception("Error! prob_sum > 1")
        return True

    def packetsDistributionGenerate(self, jsonPacketsProbabilitiesList):
        if (self._jsonTemplatesCount == len(jsonPacketsProbabilitiesList)):
            lastType = 0
            totalPacketsSum = 0
            for i in jsonPacketsProbabilitiesList:
                lastType += 1
                border = int(i * self._maxJsonPacketsCount)
                packetsCount = rnd.randint(0, border)
                if lastType != self._jsonTemplatesCount:
                    self._templatesTypesPacketCount.append(packetsCount)
                    totalPacketsSum += packetsCount
                else:
                    self._templatesTypesPacketCount.append(self._maxJsonPacketsCount - totalPacketsSum)
            print("Packets Count Distribution: ", self._templatesTypesPacketCount)
        else:
            print("self._jsonTemplatesCount = ", self._jsonTemplatesCount)
            print("len(jsonPacketsProbabilitiesList) = ", len(jsonPacketsProbabilitiesList))
            print("jsonPacketsProbabilitiesList = ", jsonPacketsProbabilitiesList)
            raise Exception("Error! maxJsonPacketsCount != jsonPacketsProbabilitiesList.size()")
        #print("debug")

    def dateGenerate(self):
        fake = Faker()
        startDate = dt.datetime(1970, 1, 2)
        # startDate = dt.datetime(1970, 1, 1, hour=0, minute=0, second=1, microsecond=0, tzinfo=None)
        # dt.datetime.today()
        endDate = dt.datetime.now(tz=None)
        date = fake.date_time_between_dates(datetime_start=startDate, datetime_end=endDate, tzinfo=None)
        return date

    def keyDataFromListGenerate(self, templateNumber, key):
        protocolsList = self._jsonTPacketData[templateNumber][key]
        protocolSelector = rnd.randint(0, len(protocolsList) - 1)
        generatedProto = protocolsList[protocolSelector]
        return generatedProto

    def genPacketTypeDirCreate(self, path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def writeDataToJsonFile(self, filepath, packet):
        with open(filepath, 'w') as outfile:
            ujson.dump(packet, outfile)

    def packetsGenerate(self, jsonTemplate, templateNumber, fake):
        # generate date of packet
        generatedDate = self.dateGenerate()
        # generating data for each key
        generatedData = list()
        # packet
        packet = dict()
        # parse template filename
        jtpName, fileExtension = jsonTemplate.split(".")
        # compose and save dir for current type to list
        if sys.platform == 'win32':
            packetsTypeDirectory = CUR_DIR + PATH_DELIM + jtpName + "_Type"
        else:
            packetsTypeDirectory = GEN_DIR + PATH_DELIM + jtpName + "_Type"
        # if not os.path.exists(packetsTypeDirectory):
        # os.makedirs(packetsTypeDirectory)
        self.genPacketTypeDirCreate(packetsTypeDirectory)
        isDirExist = False
        for dir in self._generatedJsonPacketsDirs:
            if dir == packetsTypeDirectory:
                isDirExist = True
                break
        if isDirExist == False:
            self._generatedJsonPacketsDirs.append(packetsTypeDirectory)
        # generate filename
        packetName = fake.file_name(category=None, extension='json')
        # for keysList in self._generalKeysList:
        # generate data for each key
        curTemplateKeysList = self._generalKeysList[templateNumber]
        for key in curTemplateKeysList:
            # generate data for current key
            if key == "type":
                # generatedData.append(self._jsonTPacketData[templateNumber][key])
                packet.update({key: self._jsonTPacketData[templateNumber][key]})
            if key == "dev_id":
                selector = rnd.randint(0, 1)
                if selector == 0:
                    keydata = fake.mac_address()
                else:
                    keydata = fake.ipv4(network=False)
                # generatedData.append(keydata)
                packet.update({key: keydata})
            '''
            if key == "data":
                # count of controls in smart device
                elementsCount = 2
                # dict for this field
                id_state_pair = dict()
                # list for states borders
                listOfStatesBorders = list()
                # list for result data construction
                dataList = list()
                for curDict in self._jsonTPacketData[templateNumber][key]:
                    listOfStatesBorders.append(curDict.get('state'))
                # generating id and states
                for i in range(0, elementsCount):
                    # generating id
                    id = ""
                    words = fake.words(nb=3)
                    for word in words:
                        id += word
                    # generating state
                    stateSelector = rnd.randint(0, len(listOfStatesBorders) - 1)
                    statesList = listOfStatesBorders[i][stateSelector]
                    isNumericState = False
                    state = 0
                    if statesList != "on" and statesList != "off":
                        isNumericState = True
                    keys = ("id", "state")
                    if isNumericState:
                        state = rnd.randint(int(listOfStatesBorders[i][0]), int(
                            listOfStatesBorders[i][1]) - 1)
                        keysData = (id, state)
                    else:
                        keysData = (id, statesList)
                    id_state_pair = dict(zip(keys, keysData))
                    # add new generated data to general list
                    # generatedData.append(id_state_pair)
                    dataList.append(id_state_pair)
                packet.update({key: dataList})
            '''
            if key == "time_stamp":
                # generatedData.append(generatedDate)
                packet.update({key: generatedDate})
            if key == "dev_type":
                devices_types = self._jsonTPacketData[templateNumber][key]
                devTypeSelector = rnd.randint(0, len(devices_types) - 1)
                devices_type = devices_types[devTypeSelector]
                # generatedData.append(devices_type)
                packet.update({key: devices_type})
            if key == "actions":
                actionsCount = len(ACTIONS)
                # dict for this field
                action_info = dict()
                # list for states borders
                listOfStatesBorders = list()
                # list for result actions list
                resultActionsList = list()
                for curDict in self._jsonTPacketData[templateNumber][key]:
                    listOfStatesBorders.append(curDict.get('state'))
                # generating id and states
                for i in range(0, actionsCount):
                    # generating name for control
                    name = ""
                    words = fake.words(nb=3)
                    for word in words:
                        name += word
                    # generate id for control
                    idBorder = self._jsonTPacketData[templateNumber][key][i].get('id')
                    id = rnd.randint(int(idBorder[0]), int(idBorder[1]) - 1)
                    # select control_type from Globals
                    controlTypeSelector = rnd.randint(0, actionsCount - 1)
                    actionName = ACTIONS_NAMES[controlTypeSelector]
                    control_type = actionName
                    # generating state
                    # stateSelector = rnd.randint(0, len(listOfStatesBorders) - 1)
                    stateBorders = self._jsonTPacketData[templateNumber][key][i].get('state')
                    stateSelector = rnd.randint(0, len(stateBorders) - 1)
                    controlTypeBordersSelector = controlTypeSelector
                    # statesList = listOfStatesBorders[i][controlTypeBordersSelector][stateSelector]
                    statesList = listOfStatesBorders[controlTypeBordersSelector][stateSelector]
                    isNumericState = False
                    state = 0
                    if statesList != "on" and statesList != "off":
                        isNumericState = True
                    #
                    keys = ("name", "id", "type", "state")
                    if isNumericState:
                        # state = rnd.randint(int(listOfStatesBorders[i][0]), int(
                        # listOfStatesBorders[i][1]) - 1)
                        state = rnd.randint(int(listOfStatesBorders[controlTypeBordersSelector][0]), int(
                            listOfStatesBorders[controlTypeBordersSelector][1]))
                        keysData = (name, id, control_type, state)
                    else:
                        keysData = (name, id, control_type, statesList)
                    action_info = dict(zip(keys, keysData))
                    # add new generated data to general list
                    # generatedData.append(action_info)
                    resultActionsList.append(action_info)
                packet.update({key: resultActionsList})
            if key == "status":
                statusList = self._jsonTPacketData[templateNumber][key]
                statusNumber = rnd.randint(0, int(len(statusList)) - 1)
                generatedStatus = statusList[statusNumber]
                # generatedData.append(generatedStatus)
                packet.update({key: generatedStatus})
            if key == "error_code":
                errorsCodesBorders = self._jsonTPacketData[templateNumber][key]
                # fake.ean(length=8)
                generatedErrorCode = rnd.randint(int(errorsCodesBorders[0]), int(errorsCodesBorders[1]))
                # generatedData.append(generatedErrorCode)
                packet.update({key: generatedErrorCode})
            if key == "details":
                # generating unique str
                # errorDetails = ""
                # fake.text(max_nb_chars=200)
                # fake.sentence(nb_words=6, variable_nb_words=True)
                # fake.paragraph(nb_sentences=3, variable_nb_sentences=True)
                # fake.paragraphs(nb=3)
                # words = fake.words(nb=3)
                # errorDetails = fake.sentences(nb=5)
                errorDetails = fake.paragraphs(nb=1)
                # generatedData.append(errorDetails)
                packet.update({key: errorDetails})
            # generatedProto = ""
            # isURLgenerated = False
            '''
            if key == "protocols":

                protocolsList = self._jsonTPacketData[templateNumber][key]
                protocolSelector = rnd.randint(0, len(protocolsList)-1)
                generatedProto = protocolsList[protocolSelector]
                generatedData.append(generatedProto)

                if isURLgenerated == False:
                    generatedProto = self.keyDataFromListGenerate(templateNumber, key)
                generatedData.append(generatedProto)
            '''
            if key == "url":
                proto = ""
                host_subdomain = ""
                generatedProto = ""
                isURLgenerated = True
                '''
                urlStructure = self._jsonTPacketData[templateNumber][key]
                if urlStructure[0] == "proto":
                    generatedProto = self.keyDataFromListGenerate(templateNumber, "protocols")
                    proto += generatedProto
                if urlStructure[2] == "host_subdomain":
                    host_subdomain = ""
                    words = fake.words(nb=2)
                    for word in words:
                        host_subdomain += word
                '''
                #
                #generatedProto = self.keyDataFromListGenerate(templateNumber, "protocols")
                aviableProtos = ["http", "https"]
                protoNum = rnd.randint(0,1)
                generatedProto = aviableProtos[protoNum]
                proto += generatedProto
                #
                words = fake.words(nb=2)
                for word in words:
                    host_subdomain += word
                #
                port = rnd.randint(1024, 64000)
                generatedUrl = proto + "://" + host_subdomain + ".ngrok.io:" + str(port)
                # generatedData.append(generatedProto)
                #packet.update({"proto": generatedProto})
                # generatedData.append(generatedUrl)
                packet.update({key: generatedUrl})
            '''
            if key == "ports":
                portsList = self._jsonTPacketData[templateNumber][key]
                portsSelector = rnd.randint(0, len(portsList) - 1)
                generatedPort = portsList[portsSelector]
                # generatedData.append(generatedPort)
                packet.update({key: generatedPort})
                # print("debug")
            '''
            if key == "token":
                token = ""
                tokenParts = rnd.randint(4, 16)
                listForFaker = [8,13]
                for i in range(0, tokenParts):
                    numberDigits = rnd.randint(0, 1)
                    number = fake.ean(length=listForFaker[numberDigits])
                    word = fake.word()
                    token += number + word
                packet.update({key: token})
        # write data to json file
        #filepath = self._generatedJsonPacketsDirs[templateNumber] + "\\" + packetName
        filepath = packetsTypeDirectory + PATH_DELIM + packetName
        self.writeDataToJsonFile(filepath, packet)

        # inc index of template numbers
        #templateNumber += 1

        print("==================== Packet Type #", templateNumber, " ====================")
        print(packet)

    def jsonPacketPseudorandomGeneration(self):
        fake = Faker()
        # index for general list of keys
        templateNumber = 0
        # cycle for JSON templates packets
        for jsonTemplate in self._jsonTPacketsList:
            for i in range (0, self._templatesTypesPacketCount[templateNumber]-1):
                self.packetsGenerate(jsonTemplate, templateNumber, fake)
            # inc index of template numbers
            templateNumber += 1
        #print("debug")

    def run(self, jsonPacketsProbabilitiesList):
        isCorectProbabilitiesSum = False
        isCorectProbabilitiesSum = self.packetsProbabilitiesCheckUp(jsonPacketsProbabilitiesList, False)
        if(isCorectProbabilitiesSum):
            self.packetsDistributionGenerate(jsonPacketsProbabilitiesList)
            self.jsonPacketPseudorandomGeneration()
        else:
            raise Exception("Error! Incorrect sum of probabilities.")
        print("debug")


#if __name__ == "__main__":
def start_test(MAX_JSON_PACKETS_COUNT):
    # fl2 = getFilesListInCurDir("D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Template_Packets")
    #     fake = Factory.create()

    print("parser and gen starting ...")
    #fake = Faker()

    '''
    CUR_DIR = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Template_Packets"
    #MAX_JSON_PACKETS_COUNT = 20
    GEN_DIR = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Template_Packets\\Gen"
    '''

    try:
        jpParser = JSON_Packets_Parser(CUR_DIR)
        jpParser.run()
        jpGen = JSON_Packets_Gen(GEN_DIR, jpParser.getJsonTPacketsList(), jpParser.getMainKeysList(),
                                 jpParser.getJsonTPacketsData(), MAX_JSON_PACKETS_COUNT)
        '''
        40% (0.4) DataPacket.json
        10% (0.1) DeviceHelloPacket.json
        30% (0.3) DeviceStatusPacket.json
        10% (0.1) ErrorServicePacket.json
        10% (0.1) LinkAddressPacket.json
        '''
        jpGen.run([0.4, 0.1, 0.3, 0.1, 0.1])
        return jpGen.getGeneratedDirs()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    finally:
        pass


    print("finish ...")