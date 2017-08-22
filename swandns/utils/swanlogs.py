'''
Define logging 
'''
import logging

#TODO: Better Flexiable loggers

LOGGERNAME='swan-dns'

swan_logger=None 

def start_logger(filename,level):
    global swan_logger
    if swan_logger is not None:
        return swan_logger
    level=getattr(logging,level.upper())
    log_handler=logging.FileHandler(filename=filename)
    log_handler.setLevel(level)
    logger=logging.getLogger(LOGGERNAME)
    logger.setLevel(level)
    logger.addHandler(log_handler)
    swan_logger=logger
    return logger

def get_logger():
    """Get the current logger object

    :returns: logger 
    :rtype: logging.logger

    """
    global swan_logger
    return swan_logger
    
    
