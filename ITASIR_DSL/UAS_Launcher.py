import Intermediate_Representation_DSL_Translator.flexAndBison as ITASIR_DSL_Interpreter
import Intermediate_Representation_DSL_Translator.Publisher_Subscriber_Pattern as psp

ITASIR_DSL_Interpreter.uasInterpreter.codeTranslation()

print("tracking things:")
print(ITASIR_DSL_Interpreter.uasInterpreter.getInterpreterTables()[0])
print("operating things:")
print(ITASIR_DSL_Interpreter.uasInterpreter.getInterpreterTables()[1])

