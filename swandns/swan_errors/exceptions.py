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

class SWAN_UnkownInetFamily(SWAN_DNS_Exception):
    '''
    An exception which indicate that the server was started with unkown inet_family value 
    '''

    pass

class SWAN_SkipProcessing(SWAN_DNS_Exception):
    '''
    An exception which indicates that a module processing should be skipped.
    '''
    pass
