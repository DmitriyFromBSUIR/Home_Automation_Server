
import ujson
import datetime as dt
import random as rnd

from Globals import *


class NewJSONPackGenerator:
    def __init__(self):
        self.pathToHelloPackTemplate = ""
        self.pathToDataPackTemplate = ""

    def dateGenerate(self):
        from faker import Faker
        fake = Faker()
        startDate = dt.datetime(1970, 1, 2)
        # startDate = dt.datetime(1970, 1, 1, hour=0, minute=0, second=1, microsecond=0, tzinfo=None)
        # dt.datetime.today()
        endDate = dt.datetime.now(tz=None)
        date = fake.date_time_between_dates(datetime_start=startDate, datetime_end=endDate, tzinfo=None)
        return date

    def packsGeneration(self):
        t_hello_pack = dict()
        filepathToHelloPack = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Template_Packets\\DeviceHelloPacket.json"
        with open(filepathToHelloPack) as helloPack:
            t_hello_pack = ujson.load(helloPack)
            # print(t_hello_pack)
        t_data_pack = dict()
        t_data_pack_2 = dict()
        t_data_pack_3 = dict()
        filepathToDataPack = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Template_Packets\\DataPacket.json"
        with open(filepathToDataPack) as dataPack:
            t_data_pack = ujson.load(dataPack)
            #t_data_pack_2 = dict(t_data_pack)
            #t_data_pack_3 = dict(t_data_pack)
        with open(filepathToDataPack) as dataPack2:
            t_data_pack_2 = ujson.load(dataPack2)
        with open(filepathToDataPack) as dataPack3:
            t_data_pack_3 = ujson.load(dataPack3)
            # print(t_data_pack)
        #
        # dev_id
        from faker import Faker
        fake = Faker()
        new_dev_id = fake.mac_address()
        t_hello_pack["dev_id"] = new_dev_id
        # label
        devTypesCount = len(DEVICES_TYPES)
        devTypeSelector = rnd.randint(0, devTypesCount - 1)
        devices_type = DEVICES_TYPES[devTypeSelector]
        t_hello_pack["label"] = devices_type
        # time_stamp
        generatedDate = self.dateGenerate()
        t_hello_pack["time_stamp"] = generatedDate
        #
        # controls
        #
        # -------------------------------------------------------
        # toggle
        # generating name for control
        name = ""
        words = fake.words(nb=3)
        for word in words:
            name += word
        t_hello_pack["controls"][0]["name"] = name
        # ctrl_id
        toggle_ctrl_id = rnd.randint(0, 1024)
        t_hello_pack["controls"][0]["ctrl_id"] = toggle_ctrl_id
        # state
        selector = rnd.randint(0, 1)
        toggleAviableStates = ["true", "false"]
        toggle_state = toggleAviableStates[selector]
        # type
        t_hello_pack["controls"][0]["type"] = {"name": "toggle", "optional": {}}
        # -------------------------------------------------------
        # switch_state
        # name
        name = ""
        words = fake.words(nb=3)
        for word in words:
            name += word
        t_hello_pack["controls"][1]["name"] = name
        # ctrl_id
        switchstate_ctrl_id = rnd.randint(0, 1024)
        t_hello_pack["controls"][1]["ctrl_id"] = switchstate_ctrl_id
        # state
        switch_state_st = rnd.randint(0, 2)
        states = ["state_1", "state_2", "state_3"]
        switchstate_state = states[switch_state_st]
        # type
        t_hello_pack["controls"][1]["type"] = {"name": "switch_state", "optional": {"names": states}}
        # -------------------------------------------------------
        # dimmer
        # name
        name = ""
        words = fake.words(nb=3)
        for word in words:
            name += word
        t_hello_pack["controls"][2]["name"] = name
        # ctrl_id
        dimmer_ctrl_id = rnd.randint(0, 1024)
        t_hello_pack["controls"][2]["ctrl_id"] = dimmer_ctrl_id
        # state
        dimmer_state = rnd.randint(0, 100)
        # type
        t_hello_pack["controls"][2]["type"] = {"name": "dimmer", "optional": {}}
        # -------------------------------------------------------
        # num_value
        # name
        name = ""
        words = fake.words(nb=3)
        for word in words:
            name += word
        t_hello_pack["controls"][3]["name"] = name
        # ctrl_id
        numvalue_ctrl_id = rnd.randint(0, 1024)
        t_hello_pack["controls"][3]["ctrl_id"] = numvalue_ctrl_id
        # state
        #numvalue_state = rnd.randint(0, 8196)
        # type
        mu_selector = rnd.randint(0, len(MEASURE_UNITS)-1)
        measureUnit = MEASURE_UNITS[mu_selector]
        minVal = rnd.randint(0, 100)
        maxVal = rnd.randint(0, 100)
        # state
        if minVal <= maxVal:
            t_hello_pack["controls"][3]["type"] = {"name": "num_value",
                                                   "optional": {"max": maxVal, "min": minVal, "units": measureUnit}}
            numvalue_state = rnd.randint(minVal, maxVal)
        else:
            t_hello_pack["controls"][3]["type"] = {"name": "num_value",
                                                   "optional": {"max": minVal, "min": maxVal, "units": measureUnit}}
            numvalue_state = rnd.randint(maxVal, minVal)
        # -------------------------------------------------------
        # sym_value
        # name
        '''
        name = ""
        words = fake.words(nb=3)
        for word in words:
            name += word
        t_hello_pack["controls"][4]["name"] = name
        # ctrl_id
        symvalue_ctrl_id = rnd.randint(0, 1024)
        t_hello_pack["controls"][4]["ctrl_id"] = symvalue_ctrl_id
        # state
        sym_value_selector = rnd.randint(0, 1)
        symvalue_state = toggleAviableStates[sym_value_selector]
        # type
        t_hello_pack["controls"][4]["type"] = {"name": "sym_value", "optional": {}}
        '''
        #
        # changes_packet
        #
        # time_stamp
        generatedDate = self.dateGenerate()
        t_hello_pack["changes_packet"]["time_stamp"] = generatedDate
        t_hello_pack["changes_packet"]["dev_id"] = new_dev_id
        t_hello_pack["changes_packet"]["controls"][0]["ctrl_id"] = toggle_ctrl_id
        t_hello_pack["changes_packet"]["controls"][0]["state"] = toggle_state
        t_hello_pack["changes_packet"]["controls"][1]["ctrl_id"] = switchstate_ctrl_id
        # t_hello_pack["changes_packet"]["controls"][1]["state"] = switchstate_state
        t_hello_pack["changes_packet"]["controls"][1]["state"] = switch_state_st
        t_hello_pack["changes_packet"]["controls"][2]["ctrl_id"] = dimmer_ctrl_id
        t_hello_pack["changes_packet"]["controls"][2]["state"] = dimmer_state
        t_hello_pack["changes_packet"]["controls"][3]["ctrl_id"] = numvalue_ctrl_id
        t_hello_pack["changes_packet"]["controls"][3]["state"] = numvalue_state
        #t_hello_pack["changes_packet"]["controls"][4]["ctrl_id"] = symvalue_ctrl_id
        #t_hello_pack["changes_packet"]["controls"][4]["state"] = symvalue_state
        #
        #
        # changes_packet
        #
        #
        data_packs = list()
        # ---------------------------------------------------------------
        # data pack 1
        t_data_pack["dev_id"] = new_dev_id
        generatedDate = self.dateGenerate()
        t_data_pack["time_stamp"] = generatedDate
        # controls
        #
        t_data_pack["dev_id"] = new_dev_id
        t_data_pack["controls"][0]["ctrl_id"] = toggle_ctrl_id
        selector = rnd.randint(0, 1)
        toggleAviableStates = ["true", "false"]
        toggle_state = toggleAviableStates[selector]
        t_data_pack["controls"][0]["state"] = toggle_state
        #
        t_data_pack["controls"][1]["ctrl_id"] = switchstate_ctrl_id
        # t_data_pack["controls"][1]["state"] = switchstate_state
        switch_state_st = rnd.randint(0, 2)
        t_data_pack["controls"][1]["state"] = switch_state_st
        #
        t_data_pack["controls"][2]["ctrl_id"] = dimmer_ctrl_id
        dimmer_state = rnd.randint(0, 100)
        t_data_pack["controls"][2]["state"] = dimmer_state
        #
        t_data_pack["controls"][3]["ctrl_id"] = numvalue_ctrl_id
        numvalue_state = rnd.randint(0, 8196)
        t_data_pack["controls"][3]["state"] = numvalue_state
        #
        '''
        t_data_pack["controls"][4]["ctrl_id"] = symvalue_ctrl_id
        sym_value_selector = rnd.randint(0, 1)
        symvalue_state = toggleAviableStates[sym_value_selector]
        t_data_pack["controls"][4]["state"] = symvalue_state
        '''
        #
        # -----------------------------------------------------------------
        # data pack 2
        t_data_pack_2["dev_id"] = new_dev_id
        generatedDate = self.dateGenerate()
        t_data_pack_2["time_stamp"] = generatedDate
        # controls
        #
        t_data_pack_2["dev_id"] = new_dev_id
        t_data_pack_2["controls"][0]["ctrl_id"] = toggle_ctrl_id
        selector = rnd.randint(0, 1)
        toggleAviableStates = ["true", "false"]
        toggle_state2 = toggleAviableStates[selector]
        t_data_pack_2["controls"][0]["state"] = toggle_state2
        #
        t_data_pack_2["controls"][1]["ctrl_id"] = switchstate_ctrl_id
        # t_data_pack["controls"][1]["state"] = switchstate_state
        switch_state_st2 = rnd.randint(0, 2)
        t_data_pack_2["controls"][1]["state"] = switch_state_st2
        #
        t_data_pack_2["controls"][2]["ctrl_id"] = dimmer_ctrl_id
        dimmer_state2 = rnd.randint(0, 100)
        t_data_pack_2["controls"][2]["state"] = dimmer_state2
        #
        t_data_pack_2["controls"][3]["ctrl_id"] = numvalue_ctrl_id
        numvalue_state2 = rnd.randint(0, 8196)
        t_data_pack_2["controls"][3]["state"] = numvalue_state2
        #
        '''
        t_data_pack_2["controls"][4]["ctrl_id"] = symvalue_ctrl_id
        sym_value_selector = rnd.randint(0, 1)
        symvalue_state2 = toggleAviableStates[sym_value_selector]
        t_data_pack_2["controls"][4]["state"] = symvalue_state2
        '''
        #
        # --------------------------------------------------------------------
        # data pack 3
        t_data_pack_3["dev_id"] = new_dev_id
        generatedDate3 = self.dateGenerate()
        t_data_pack_3["time_stamp"] = generatedDate3
        # controls
        #
        t_data_pack_3["dev_id"] = new_dev_id
        t_data_pack_3["controls"][0]["ctrl_id"] = toggle_ctrl_id
        selector = rnd.randint(0, 1)
        toggleAviableStates = ["true", "false"]
        toggle_state3 = toggleAviableStates[selector]
        t_data_pack_3["controls"][0]["state"] = toggle_state3
        #
        t_data_pack_3["controls"][1]["ctrl_id"] = switchstate_ctrl_id
        # t_data_pack["controls"][1]["state"] = switchstate_state
        switch_state_st3 = rnd.randint(0, 2)
        t_data_pack_3["controls"][1]["state"] = switch_state_st3
        #
        t_data_pack_3["controls"][2]["ctrl_id"] = dimmer_ctrl_id
        dimmer_state3 = rnd.randint(0, 100)
        t_data_pack_3["controls"][2]["state"] = dimmer_state3
        #
        t_data_pack_3["controls"][3]["ctrl_id"] = numvalue_ctrl_id
        numvalue_state3 = rnd.randint(0, 8196)
        t_data_pack_3["controls"][3]["state"] = numvalue_state3
        #
        '''
        t_data_pack_3["controls"][4]["ctrl_id"] = symvalue_ctrl_id
        sym_value_selector = rnd.randint(0, 1)
        symvalue_state3 = toggleAviableStates[sym_value_selector]
        t_data_pack_3["controls"][4]["state"] = symvalue_state3
        '''
        #
        return (t_hello_pack, t_data_pack, t_data_pack_2, t_data_pack_3)