import Intermediate_Representation_DSL_Translator.Lexer as lex

# Test it out
data = '''
STARTP

if ( (lamp1.turn.[on] and tempSensor1.range.[0,100]) or (lamp2.turn.[off]) )
begin
	tempSensor2.turn.[off];
	lamp3.turn.[off];
	selector1.switch_state_to.[3];
	dimmer1.dimmer.[25];
end;

FINISHP
'''


# Give the lexer some input
lex.lexer.input(data)

# Tokenize
while True:
    tok = lex.lexer.token()
    if not tok:
        break      # No more input
    print("token type: ", tok.type, "   token val: ", tok.value, "   Line #: ", tok.lineno, "   Lexem pos: ", tok.lexpos)