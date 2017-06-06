from pyparsing import *

def rearrange(tks):
    T=tks[0]
    T[0],T[1] = T[1],T[0]
    return tks

def exampleTest():
    expr = Forward()
    arithOp = Word("+-*/", max=1)
    terminal = (Word(alphas, alphanums)
                | Word(nums)
                | Suppress("(") + expr + Suppress(")"))
    expr << Group(terminal + arithOp + terminal).setParseAction(rearrange)

    parseTree = expr.parseString("x+(y*z)")
    print(parseTree)

def run():
    expr = Forward()
    #arithOp = Word( "+-*/", max=1 )
    logicOp = Word( "&|", max=1 )

    compOp = ( Word("<")
             | Word(">")
             | Word("=")
             | Word("<=", exact=2)
             | Word(">=", exact=2)
             | Word("!=", exact=2) )

    ipAddress = Combine(Word(nums) + ('.' + Word(nums)) * 3)
    hexint = Word(hexnums,exact=2)
    macAddress = Combine(hexint + (':' + hexint) * 5)
    iotControl_ip = Combine(ipAddress + '#' + Word(nums))
    iotControl_mac = Combine(macAddress + '#' + Word(nums))

    terminal = ( Word(alphas, alphanums)
               | Suppress("_@") + iotControl_ip + Suppress("@_")
               | Suppress("_@") + iotControl_mac + Suppress("@_")
               | Word(nums)
               | Suppress("(") + expr + Suppress(")") )

    cond_exp = Group(Suppress("(") + terminal + compOp + terminal + Suppress(")")).setParseAction(rearrange)

    if_expr = ( cond_exp
              | Suppress("(") + expr + Suppress(")") )
    #if_expr = cond_exp

    #expr << Group(terminal + arithOp + terminal).setParseAction(rearrange)
    #expr << Group(terminal + compOp + terminal).setParseAction(rearrange)
    expr << Group(if_expr + logicOp + if_expr).setParseAction(rearrange)

    parseTree = expr.parseString("(xxx < yy) & ( (_@04:7D:7B:97:0C:9F#123@_ > _@192.168.11.109#345@_) | (_@04:7D:7B:97:0C:9F#123@_ = 55) )")
    print(parseTree)

if __name__ == "__main__":
    run()
    #exampleTest()