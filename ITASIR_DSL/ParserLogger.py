# Set up a logging object
import logging

def lexer_logger_start(lexer_log_filename="lexerlog.txt"):
    logging.basicConfig(
        level = logging.DEBUG,
        filename = lexer_log_filename,
        filemode = "w",
        format = "%(filename)10s:%(lineno)4d:%(message)s"
    )
    log = logging.getLogger()
    return log

def parser_logger_start(parser_log_filename="parselog.txt"):
    logging.basicConfig(
        level = logging.DEBUG,
        filename = parser_log_filename,
        filemode = "w",
        format = "%(filename)10s:%(lineno)4d:%(message)s"
    )
    log = logging.getLogger()
    return log

def run(lexer_log_filename="lexerlog.txt", parser_log_filename="parselog.txt"):
    #lexer_logger = lexer_logger_start(lexer_log_filename)
    parser_logger = parser_logger_start(parser_log_filename)
    #return (lexer_logger, parser_logger)
    return parser_logger