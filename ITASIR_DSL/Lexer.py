import ply.lex as lex
from ply.lex import TOKEN
import re

import Intermediate_Representation_DSL_Translator.ParserLogger as pLogger

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
    'GETSTATE',
    'GETVALUE',
    'LBRACE',
    'RBRACE',
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
    'getState': 'GETSTATE',
    'getValue': 'GETVALUE',
}

literals = ['=', '+', '-', '*', '/', '(', ')', '[', ']', '{', '}', '.', ';']

def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
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
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

#log = pLogger.run()[0]

# Build the lexer
#lexer = lex.lex(reflags=re.UNICODE | re.DOTALL | re.IGNORECASE, debug=True, debuglog=log)
lexer = lex.lex(reflags=re.UNICODE | re.DOTALL | re.IGNORECASE)


