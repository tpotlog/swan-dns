'''
Python module to hold DNS processing exceptions 
'''

class SWAN_DNS_Exception:
    '''
    General SWAN DNS exception
    '''

class SWAN_StopProcessingRequest(SWAN_DNS_Exception):
    '''
    An exception which indicates to stop the processing of a dns request.
    This shuld be thrown from a dns processing modules in order to specify that
    processing is no longer needed and an answer should be returned to the sender
    '''
    pass
