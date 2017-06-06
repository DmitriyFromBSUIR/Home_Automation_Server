DEVICES_TYPES = ["lamp", "smart_power_jack", "temperature_sensor", "light_sensor", "electric_driver", "smoke_detector",
                  "water_leakage_sensor", "gas_sensor", "motion_or_sound_sensor", "door_sensor", "unknown_device",
                  "unknown_controller"]

toggle = ["on", "off"]

ACTIONS = [toggle, "switch_state", "dimmer", "num_value", "sym_value"]

ACTIONS_NAMES = ["toggle", "switch_state", "dimmer", "num_value", "sym_value"]

MEASURE_UNITS = ["Celsius", "Fahrenheit", "Kelvin", "Lux", "kg", "g", "oz", "lb", "Pa", "hPa", "g/cm3", "kg/m3", "%"]

PACKETS_TYPES = ["dev_hello", "dev_changes", "ack", "link", "user_script", "dev_statistics_query", "dev_statistics",
                 "dev_status", "script_changes", "error"]


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



HELLO_PACK_JSON_SHEME_C5 = '''
    {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "definitions": {},
        "id": "http://example.com/example.json",
        "properties": {
            "changes_packet": {
                "id": "/properties/changes_packet",
                "properties": {
                    "controls": {
                        "id": "/properties/changes_packet/properties/controls",
                        "items": {
                            "id": "/properties/changes_packet/properties/controls/items",
                            "properties": {
                                "ctrl_id": {
                                    "id": "/properties/changes_packet/properties/controls/items/properties/ctrl_id",
                                    "type": "integer"
                                },
                                "state": {
                                    "id": "/properties/changes_packet/properties/controls/items/properties/state",
                                    "type": "string"
                                }
                            },
                            "type": "object"
                        },
                        "type": "array"
                    },
                    "dev_id": {
                        "id": "/properties/changes_packet/properties/dev_id",
                        "type": "string"
                    },
                    "time_stamp": {
                        "id": "/properties/changes_packet/properties/time_stamp",
                        "type": "string"
                    },
                    "type": {
                        "id": "/properties/changes_packet/properties/type",
                        "type": "string"
                    }
                },
                "type": "object"
            },
            "controls": {
                "id": "/properties/controls",
                "items": {
                    "id": "/properties/controls/items",
                    "properties": {
                        "ctrl_id": {
                            "id": "/properties/controls/items/properties/ctrl_id",
                            "type": "integer"
                        },
                        "name": {
                            "id": "/properties/controls/items/properties/name",
                            "type": "string"
                        },
                        "type": {
                            "id": "/properties/controls/items/properties/type",
                            "properties": {
                                "name": {
                                    "id": "/properties/controls/items/properties/type/properties/name",
                                    "type": "string"
                                },
                                "optional": {
                                    "id": "/properties/controls/items/properties/type/properties/optional",
                                    "properties": {},
                                    "type": "object"
                                }
                            },
                            "type": "object"
                        }
                    },
                    "type": "object"
                },
                "type": "array"
            },
            "dev_id": {
                "id": "/properties/dev_id",
                "type": "string"
            },
            "label": {
                "id": "/properties/label",
                "type": "string"
            },
            "time_stamp": {
                "id": "/properties/time_stamp",
                "type": "string"
            },
            "type": {
                "id": "/properties/type",
                "type": "string"
            }
        },
        "type": "object"
    }
'''

HELLO_PACK_JSON_SHEME_C4 = '''

'''

HELLO_PACK_JSON_SHEME_C3 = '''

'''

HELLO_PACK_JSON_SHEME_C2 = '''

'''

HELLO_PACK_JSON_SHEME_C1 = '''

'''

DATA_PACK_JSON_SHEME_C5 = '''

'''

DATA_PACK_JSON_SHEME_C4 = '''

'''

DATA_PACK_JSON_SHEME_C3 = '''

'''

DATA_PACK_JSON_SHEME_C2 = '''

'''

DATA_PACK_JSON_SHEME_C1 = '''

'''