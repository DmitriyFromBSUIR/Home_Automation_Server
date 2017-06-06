
import sys
import Intermediate_Representation_DSL_Translator.flexAndBison as ITASIR_DSL_Interpreter
import Intermediate_Representation_DSL_Translator.Publisher_Subscriber_Pattern as psp


if sys.platform == 'win32':
    PATH_DELIM = "\\"
    TEMPLATE_PACKS_DIR = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Template_Packets"
    GEN_PACKS_DIR = "D:\\Projects\\JetBrains\\PyCharm_Workspace\\Diploma\\WebServer\\Template_Packets\\Gen"
else:
    PATH_DELIM = "/"
    TEMPLATE_PACKS_DIR = "/home/root/Python_Workspace/iotWebServer/CM_Service/Template_Packets"
    GEN_PACKS_DIR = "/home/root/Python_Workspace/iotWebServer/CM_Service/Gen_Packets"


# user automation scripts launcher (input: translated interpreter's intermediate code representation tables and msg_center)
class UAS_Launcher:
    def __init__(self, interpreter_icrt, msg_center):
        self._translated_interpreters_icrt = interpreter_icrt
        self._msg_center = msg_center

    def subscriptionSchemeBuild(self):
        pass

    def setMsgCenterInSubcriberObjets(self):
        for translated_if_stmt in self._translated_interpreters_icrt:
            # get translated stmts of operating controls
            for comKey, value in translated_if_stmt[1].items():
                translated_if_stmt[1].get(comKey)[0].setMsgProvider(self._msg_center)
        print("debug")

    def run(self):
        self.setMsgCenterInSubcriberObjets()
        self.subscriptionSchemeBuild()

if __name__ == "__main__":
    '''
    print("tracking things:")
    print(ITASIR_DSL_Interpreter.uasInterpreter.getInterpreterTables()[0])
    print("operating things:")
    print(ITASIR_DSL_Interpreter.uasInterpreter.getInterpreterTables()[1])
    '''
    # start interpreter
    ITASIR_DSL_Interpreter.uasInterpreter.codeTranslation()
    translated_icrt = ITASIR_DSL_Interpreter.uasInterpreter.getInterpreterICRTables()
    print(translated_icrt)
    # center for messages exchanging (environment for event-driven tags, iot-controls subcribe/unscribe on event-driven tags)
    msgCenter = psp.Provider()
    # start UAS Launcher
    launcher = UAS_Launcher(translated_icrt, msgCenter)
    launcher.run()
