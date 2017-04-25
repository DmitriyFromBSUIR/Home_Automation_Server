import ply.yacc as yacc

from Intermediate_Representation_DSL_Translator.Lexer  import tokens

import Intermediate_Representation_DSL_Translator.ParserLogger as pLogger

class Node:
    def parts_str(self):
        st = []
        for part in self.parts:
            st.append( str( part ) )
        return "\n".join(st)

    def __repr__(self):
        return self.type + ":\n\t" + self.parts_str().replace("\n", "\n\t")

    def add_parts(self, parts):
        self.parts += parts
        return self

    def __init__(self, type, parts):
        self.type = type
        self.parts = parts


__var_names = dict()


# Parsing rules
'''
def p_statement_expr(t):
    'statement : expression'
    #print(t[1])
'''

def p_programm_struct(t):
    '''
        programm_struct : STARTP COMMENT programm_body FINISHP
    '''
    #print(t[0])

def p_iot_device(t):
    'iot_device : IDENT'
    #t[0] = Node('IDENT', t[1])
    print("Hello")



def p_iot_dev_control(t):
    'iot_dev_control : IDENT'

def p_iot_command(t):
    '''
        iot_command : TURN
                    | SWITCH_STATE_TO
                    | DIMMER
    '''

def p_toggle_cmd_args(t):
    '''
        toggle_cmd_args : CMDARG_ON
                        | CMDARG_OFF
    '''

def p_iot_cmd_argument(t):
    '''
        iot_cmd_argument : toggle_cmd_args
                         | NUMBER
                         | RANGE DOT LSQB NUMBER COMMA NUMBER RSQB
    '''

def p_iot_object_expr(t):
    '''
        iot_object_expr : iot_device DOT iot_dev_control DOT iot_command DOT LSQB iot_cmd_argument RSQB
    '''

def p_get_device_info(t):
    '''
        get_device_info : GETSTATE
                        | GETVALUE
    '''

def p_iot_device_get_info(t):
    '''
        iot_device_get_info : iot_device DOT iot_dev_control DOT get_device_info
                            | iot_device DOT iot_dev_control DOT iot_command DOT LSQB RANGE DOT LSQB NUMBER COMMA NUMBER RSQB RSQB
    '''

def p_assigment(t):
    '''
        assigment : iot_object_expr ASSIGN NUMBER
                  | iot_object_expr ASSIGN toggle_cmd_args
    '''

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
    '''

def p_condition_list(t):
    '''
        condition_list : condition_list logical_operator condition
                     | condition
    '''

def p_if_stmt(t):
    '''
        if_stmt : IF LBRACE condition_list RBRACE THEN
    '''
    #print(t[1])
    __var_names.update({"if": t[0]})

def p_condition_instr(t):
    '''
        condition_instr : if_stmt BEGIN assigment_stmts END SEMICOLON
                        | if_stmt BEGIN assigment_stmts END ELSE BEGIN assigment_stmts END SEMICOLON
    '''
    #print(t[0])

def p_programm_body(p):
    '''
        programm_body : programm_body condition_instr
                      | condition_instr
    '''
    #print(p[0])



def p_error(t):
    print("Syntax error at '%s'" % t.value)



# Build the parser
#yacc.yacc()

#log = pLogger.run()[1]
log = pLogger.run()

# Use this if you want to build the parser using LALR(1) instead of SLR
#Parser = yacc.yacc(method="LALR", debug=True, debuglog=log, errorlog=yacc.NullLogger())
Parser = yacc.yacc(debug=True, debuglog=log, errorlog=yacc.NullLogger())

print(__var_names)