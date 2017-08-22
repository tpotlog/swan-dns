'''
Python module to hold DNS processing exceptions 
'''

class SWAN_DNS_Exception(Exception):
    '''
    General SWAN DNS exception
    '''
    pass

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

class SWAN_ModuleConfigurationError(SWAN_DNS_Exception):
    '''
    An exception which indicates that a module configuration is invalid
    '''
    pass

class SWAN_ModuleLoadError(SWAN_DNS_Exception):
    '''
    An exception which indicate that there was a problem loading a module
    '''
    pass

class SWAN_NoSuchZoneError(SWAN_DNS_Exception):
    '''
    An exception which indicate that a dns server can not resolve a specific zone.
    '''
    pass

class SWAN_DropAnswer(SWAN_DNS_Exception):
    '''
    An exception which indicates to drop the response and not provide answers to the client 
    '''
    pass

class SWAN_ConfigurationError(SWAN_DNS_Exception):
    '''
    An exception which indicates that loading the configuration of a server is not valid
    '''
    pass
