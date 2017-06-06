import ply.lex as lex
from ply.lex import TOKEN
import re

#import Intermediate_Representation_DSL_Translator.ParserLogger as pLogger

# List of token names.   This is always required
tokens = (
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'SPACE',
    'COMMENT',
    'STARTP',
    'FINISHP',
    'ASSIGN',
    'LSQB',
    'RSQB',
    'SEMICOLON',
    'ELESS',
    'LESS',
    'EGREATER',
    'GREATER',
    'EQUAL',
    'NOTEQUAL',
    'DOT',
    'COMMA',
    'LOGIC_AND',
    'LOGIC_OR',
    'LOGIC_NOT',
    'IF',
    'THEN',
    'ELSE',
    'WHILE',
    'FOR',
    'DO',
    'BEGIN',
    'END',
    'RANGE',
    'TURN',
    'CMDARG_ON',
    'CMDARG_OFF',
    'SWITCH_STATE_TO',
    'DIMMER',
    'IDENT',
    'NUMBER',
    #'GETSTATE',
    #'GETVALUE',
    'STATE',
    'LBRACE',
    'RBRACE',
    'OCTOTHORPE',
)

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_SPACE   = '[ \n\t]+'
#t_COMMENT = r'#[^\n]*'
t_ASSIGN  = r'\:='
t_LSQB    = r'\['
t_RSQB    = r'\]'
t_LBRACE  = r'{'
t_RBRACE  = r'}'
t_SEMICOLON   = r';'
t_ELESS   = r'<='
t_LESS    = r'<'
t_EGREATER = r'>='
t_GREATER = r'>'
t_EQUAL = r'='
t_NOTEQUAL = r'!='
t_DOT = r'\.'
t_COMMA = r'\,'
t_OCTOTHORPE = r'#'
'''
t_PSTART   = r'PSTART'
t_PFINISH  = r'PFINISH'
t_LOGICAND = r'and'
t_LOGICOR = r'or'
t_LOGICNOT = r'not'
t_IF = r'if'
t_THEN = r'then'
t_ELSE = r'else'
t_WHILE = r'while'
t_FOR = r'for'
t_DO = r'do'
t_BEGIN = r'begin'
t_END = r'end'
t_RANGE = r'range'
t_TURN = r'turn'
t_CMDTOGGLEARG1 = r'on'
t_CMDTOGGLEARG2 = r'off'
t_SWITCH = r'switch_state_to'
t_DIMMER = r'dimmer'
'''
#t_IDENT = r'[A-Za-z][A-Za-z0-9_]*'
#t_NUMBER = r'[0-9]+'

reserved = {
    # keyword - token type
    'STARTP': 'STARTP',
    'FINISHP': 'FINISHP',
    'and' : 'LOGIC_AND',
    'or' : 'LOGIC_OR',
    'not' : 'LOGIC_NOT',
    'if' : 'IF',
    'then' : 'THEN',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'for' : 'FOR',
    'do' : 'DO',
    'begin' : 'BEGIN',
    'end' : 'END',
    'range' : 'RANGE',
    'turn' : 'TURN',
    'on' : 'CMDARG_ON',
    'off' : 'CMDARG_OFF',
    'switch_state_to' : 'SWITCH_STATE_TO',
    'dimmer': 'DIMMER',
    'state': 'STATE',
    #'getState': 'GETSTATE',
    #'getValue': 'GETVALUE',
}

#literals = ['=', '+', '-', '*', '/', '(', ')', '[', ']', '{', '}', '.', ';']

def t_IDENT(t):
    r'[a-zA-Z_0-9\:\.][a-zA-Z_0-9\:\.]*'
    t.type = reserved.get(t.value,'IDENT')    # Check for reserved words
    return t

# игнорируем комментарии
def t_comment(t):
    r'(/\*(.|\n)*?\*/)|(//.*)'
    pass

# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
# Ignored characters (whitespace)
t_ignore  = ' \t\n'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

#log = pLogger.run()[0]

# Build the lexer
#lexer = lex.lex(reflags=re.UNICODE | re.DOTALL | re.IGNORECASE, debug=True, debuglog=log)
lexer = lex.lex(reflags=re.UNICODE | re.DOTALL | re.IGNORECASE)



import ply.yacc as yacc
import ujson

#from Intermediate_Representation_DSL_Translator.Lexer  import tokens

import Intermediate_Representation_DSL_Translator.ParserLogger as pLogger
import Intermediate_Representation_DSL_Translator.Publisher_Subscriber_Pattern as psp

# controls of iot-devices that are tracked by the UAS Launcher (complex key: (iotDeviceID, controlID), value: state or value of cntrl)
__tracking_iot_device_controls = dict()
_trackingCompositeKey = list()
_trackingValues = list()

# controls of iot-devices that have event-tag subscribtion (complex key: (iotDeviceID, controlID), value: list(Subscriber Object, operatingFutureValue))
__active_operating_iot_device_controls = dict()
_activeOperatingCompositeKey = list()
_activeOperatingValues = list()

# if_stmt in Translated View
__if_stmts_list = list()

# user automation scripts (key: script name, value: tracking and operating controls)
#__uas_names = dict()

# funcs for create the Interpreter's Intermediate Code Representation Tables (Interpreter_ICRT)
def user_automation_scripts_interpreting(id_delim="_"):
    # controls in the tracking iot-devices
    for trackingCompositeKey, trackingValue in zip(_trackingCompositeKey, _trackingValues):
        __tracking_iot_device_controls.update({trackingCompositeKey: trackingValue})
    # controls in the operating iot-devices
    for operatingCompositeKey, operatingValue in zip(_activeOperatingCompositeKey, _activeOperatingValues):
        subscriberName = str(operatingCompositeKey[0]) + id_delim + str(operatingCompositeKey[1])
        # msg_center will be set in the future by the Interpreter or UAS_Launcher
        msg_center = None
        subscriber = psp.Subscriber(subscriberName, msg_center)
        __active_operating_iot_device_controls.update({operatingCompositeKey: [subscriber, operatingValue]})
    translated_if_stmt = (dict(__tracking_iot_device_controls), dict(__active_operating_iot_device_controls))
    __if_stmts_list.append(translated_if_stmt)
    return translated_if_stmt

# clear structures for new "if statement"
def reallocGlobalStructuresMem():
    _trackingCompositeKey = list()
    _trackingValues = list()
    _activeOperatingCompositeKey = list()
    _activeOperatingValues = list()

# clear structures for new "if statement"
def clearGlobalStructures():
    _trackingCompositeKey.clear()
    _trackingValues.clear()
    _activeOperatingCompositeKey.clear()
    _activeOperatingValues.clear()
    __tracking_iot_device_controls.clear()
    __active_operating_iot_device_controls.clear()

# Parsing rules
'''
def p_statement_expr(t):
    'statement : expression'
    #print(t[1])
'''

def p_programm_struct(t):
    '''
        programm_struct : COMMENT programm_body
                        | programm_body
    '''

def p_iot_device(t):
    'iot_device : IDENT'
    #print(t[1])
    t[0] = t[1]

def p_iot_dev_control(t):
    'iot_dev_control : IDENT'
    #print(t[1])
    t[0] = t[1]

def p_iot_command(t):
    '''
        iot_command : TURN
                    | SWITCH_STATE_TO
                    | DIMMER
    '''
    #print(t[1])
    t[0] = t[1]

def p_toggle_cmd_args(t):
    '''
        toggle_cmd_args : CMDARG_ON
                        | CMDARG_OFF
    '''
    #print(t[1])
    t[0] = t[1]

def p_iot_cmd_argument(t):
    '''
        iot_cmd_argument : toggle_cmd_args
                         | NUMBER
                         | RANGE DOT LSQB NUMBER COMMA NUMBER RSQB
    '''
    t[0] = t[1]

def p_iot_object_expr(t):
    '''
        iot_object_expr : iot_device OCTOTHORPE iot_dev_control
    '''
    _activeOperatingCompositeKey.append((t[1], t[3]))
    t[0] = _activeOperatingCompositeKey

def p_get_device_info(t):
    '''
        get_device_info : STATE
    '''

def p_iot_device_get_info(t):
    '''
        iot_device_get_info : iot_device OCTOTHORPE iot_dev_control OCTOTHORPE get_device_info
                            | iot_device DOT iot_dev_control DOT iot_command DOT LSQB RANGE DOT LSQB NUMBER COMMA NUMBER RSQB RSQB
    '''
    _trackingCompositeKey.append( (t[1], t[3]) )
    t[0] = _trackingCompositeKey

def p_assigment(t):
    '''
        assigment : iot_object_expr ASSIGN NUMBER
                  | iot_object_expr ASSIGN toggle_cmd_args
    '''
    _activeOperatingValues.append(t[3])

def p_assigment_stmts(t):
    '''
        assigment_stmts : assigment_stmts assigment SEMICOLON
                        | assigment SEMICOLON
    '''

def p_logical_comp(t):
    '''
        logical_comp : EGREATER
                   | GREATER
                   | ELESS
                   | LESS
                   | EQUAL
                   | NOTEQUAL
    '''

def p_logical_operator(t):
    '''
        logical_operator : LOGIC_AND
                         | LOGIC_OR
    '''

def p_logical_cond(t):
    '''
        logical_cond : logical_comp
                     | logical_operator
    '''

def p_condition(t):
    '''
        condition : LPAREN iot_device_get_info logical_comp iot_device_get_info RPAREN
                  | LPAREN iot_device_get_info logical_comp NUMBER RPAREN
                  | LPAREN iot_device_get_info logical_comp toggle_cmd_args RPAREN
    '''

    #_trackingValues.append(t[4])

def p_condition_list(t):
    '''
        condition_list : condition_list logical_operator condition
                       | condition
                       | LPAREN condition_list RPAREN
    '''

def p_if_stmt(t):
    '''
        if_stmt : IF LBRACE condition_list RBRACE THEN
    '''

def p_end_if(t):
    '''
        end_if : END
    '''
    user_automation_scripts_interpreting()
    #reallocGlobalStructuresMem()
    clearGlobalStructures()
    '''
    print("if_stmt list:")
    print(__if_stmts_list)
    for if_stmt in __if_stmts_list:
        print(if_stmt)
    '''

def p_condition_instr(t):
    '''
        condition_instr : if_stmt BEGIN assigment_stmts end_if SEMICOLON
                        | if_stmt BEGIN assigment_stmts end_if ELSE BEGIN assigment_stmts end_if SEMICOLON
    '''

def p_programm_body(p):
    '''
        programm_body : programm_body condition_instr
                      | condition_instr
                      | programm_body assigment_stmts
                      | assigment_stmts
    '''

def p_error(t):
    #print("Syntax error at '%s'" % t.value)
    print("Syntax error at '%s'" % t)
    '''
    print("Whoa. You are seriously hosed.")
    if not p:
        print("End of File!")
        return

    # Read ahead looking for a closing '}'
    while True:
        tok = parser.token()             # Get the next token
        if not tok or tok.type == 'RBRACE':
            break
    parser.restart()
    '''
    if t:
        print("Syntax error at token", t.type, "   Line #: ", t.lineno, "   Lexem pos: ", t.lexpos)
        # Just discard the token and tell the parser it's okay.
        Parser.errok()
    else:
        print("Syntax error at EOF")


# Build the parser
#yacc.yacc()

#log = pLogger.run()[1]
log = pLogger.run(lexer_log_filename="fab_lexerlog.txt", parser_log_filename="fab_parselog.txt")

# Use this if you want to build the parser using LALR(1) instead of SLR
#Parser = yacc.yacc(method="LALR", debug=True, debuglog=log, errorlog=yacc.NullLogger())
Parser = yacc.yacc(debug=True, debuglog=log, errorlog=yacc.NullLogger())


# Test it out
data = '''
    STARTP

    /* my_script */

    if { ((lamp1.lamp1contr.getState = on) and (tempSensor1.tempSensor1contr.getValue = 0) ) or (lamp2.lamp2contr.getState = off) } then
    begin
        tempSensor2.ts2c.turn.[off] := on;
        lamp3.l3c.turn.[off] := on;
        selector1.s1c.switch_state_to.[3] := 5;
        dimmer1.d1c.dimmer.[25] := 50;
    end;

    if { ((lamp11.lamp11contr.getState = on) and (tempSensor11.tempSensor11contr.getValue = 0) ) or (lamp22.lamp22contr.getState = off) } then
    begin
        tempSensor22.ts22c.turn.[off] := on;
        lamp33.l33c.turn.[off] := on;
        selector11.s11c.switch_state_to.[3] := 5;
        dimmer11.d11c.dimmer.[25] := 50;
    end;

    FINISHP
    '''

parser_runtime_log = pLogger.run(parser_log_filename="parser_logfle.txt")

while True:
    try:
        s = input('> ')
        Parser.parse("if { (192.168.2.76#1198#state = on) and (A4:7D:7B:97:0C:9F#557#state = on) } then begin A3:7D:7B:97:0C:9F#43 := on; end; ")
#        file = open('cond.dal', 'r')
#        s = file.readlines()
#        print(s)
    except EOFError:
        break


import Intermediate_Representation_DSL_Translator.Publisher_Subscriber_Pattern as psp

class Interpreter:

    #def __init__(self, tracking_iot_device_controls, active_operating_iot_device_controls, interpreter_icrt, msg_center, id_delim="_"):
    def __init__(self, interpreter_icrt, msg_center, id_delim="_"):
        #self._tracking_iot_device_controls = tracking_iot_device_controls
        #self._active_operating_iot_device_controls = active_operating_iot_device_controls
        self._msg_center = msg_center
        self._id_delim = id_delim
        # Interpreter's Intermediate Code Representation Tables (Interpreter_ICRT)
        self._interpreter_icrt = interpreter_icrt

    def getInterpreterICRTables(self):
        return self._interpreter_icrt

    '''
    def getInterpreterTables(self):
        return (self._tracking_iot_device_controls, self._active_operating_iot_device_controls)
    '''

    '''
    def user_automation_scripts_interpreting(self):
        # controls in the tracking iot-devices
        for trackingCompositeKey, trackingValue in zip(_trackingCompositeKey, _trackingValues):
            self._tracking_iot_device_controls.update({trackingCompositeKey: trackingValue})
        # controls in the operating iot-devices
        for operatingCompositeKey, operatingValue in zip(_activeOperatingCompositeKey, _activeOperatingValues):
            subscriberName = str(operatingCompositeKey[0]) + self._id_delim + str(operatingCompositeKey[1])
            subscriber = psp.Subscriber(subscriberName, self._msg_center)
            self._active_operating_iot_device_controls.update({operatingCompositeKey: [subscriber, operatingValue]})
    '''

    def codeTranslation(self, inputCode = data, log = parser_runtime_log, isDebuggingPrint=False):
        #yacc.parse(s, debug=log, tracking=True)
        Parser.parse(inputCode, debug=log, tracking=True)
        # create interpreting tables
        #self.user_automation_scripts_interpreting()
        #print("if_stmt list:")
        #print(self._interpreter_icrt)
        if isDebuggingPrint:
            print("if_stmt list:")
            for if_stmt in self._interpreter_icrt:
                print(if_stmt)
        '''
        print("tracking iot-dev controls (ComKeys): ", _trackingCompositeKey)
        print("operating iot-dev controls (ComKeys): ", _activeOperatingCompositeKey)
        print("tracking Values/States: ", _trackingValues)
        print("operating Values/States: ", _activeOperatingValues)
        print(self._tracking_iot_device_controls)
        print(self._active_operating_iot_device_controls)
        '''

# center for messages exchanging
msgCenter = psp.Provider()
# create Interpreter for user automation scripts translating
#uasInterpreter = Interpreter(__tracking_iot_device_controls, __active_operating_iot_device_controls, __if_stmts_list, msgCenter)
uasInterpreter = Interpreter(__if_stmts_list, msgCenter)