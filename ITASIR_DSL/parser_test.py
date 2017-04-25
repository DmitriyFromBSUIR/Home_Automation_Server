
import Intermediate_Representation_DSL_Translator.Parser as bison

import Intermediate_Representation_DSL_Translator.ParserLogger as pLogger

# Test it out
data = '''
    STARTP

    if ( (lamp1.turn.[on] and tempSensor1.range.[0,100]) or lamp2.turn.[off] )
    begin
        tempSensor2.turn.[off];
        lamp3.turn.[off];
        selector1.switch_state_to.[3];
        dimmer1.dimmer.[25];
    end;

    FINISHP
    '''

log = pLogger.run()

while True:
    try:
        s = input(data)
        '''
        file = open('cond.dal', 'r')
        s = file.readlines()
        print(s)
        '''
    except EOFError:
        break
    bison.Parser.parse(s, debug=log, tracking=True)
