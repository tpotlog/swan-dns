'''
This is the main server code of the swiss knife dns
'''

import logging
import SocketServer
import dnslib
from swandns.swan_errors.exceptions import SWAN_StopProcessingRequest,SWAN_DNS_Exception,SWAN_SkipProcessing
from swandns.utils.parsing import get_qtype

 
def get_logger_name(dns_zone=None):
    '''
    Return the logger name of a dns zone
    '''
    return 'swan-dns'


_server_inet_family={'udp':
                     {'server':SocketServer.ThreadingUDPServer,
                      'handler':UDPDNSRequestHandler
                     }}
'''
Mapping between server inet family and server+handler.
To add new inet_family/handler simply add the addtional values to the dict
'''

_server=None
'''
Current running server instance 
'''

processing_d={}
'''
The processing_d is a dictionary holding all the modules which will
process each dns zone.  The overall look of the dict will look
something like.

{ 'this.is.the.zone.x':[<module object 1>,<module object 2>.....

}
'''

def dns_zone_locator(dns_zone):
       return processing_d.get(dns_zone,[])

class DNSRequestHandler(SocketServer.BaseRequestHandler):

    def log(self,msg,level):
        '''
        Log messages using python logging module 
        '''
        lgr=logging.getLogger(get_logger_name(self.get_dns_zone()))
        lgr.log(level,msg)
        
    def get_dns_zone(self):
        '''
        return the current request dns zone
        '''

        if not hasattr(self,'dns_zone'):
            return None
        
        return self.dns_zone

    def parse_request_data(self):
        '''
        Implematation of parsing request data and making it a parsed dns data
        '''
        raise NotImplemented
    
    def read_data(self):
        '''
        Read data from input stream
        '''
        self.dns_data=self.parse_request_data()

        
    def write_data(self):
        '''
        Send Data to output stream
        '''
        raise NotImplemented

    def process(self):
        '''
        Process the data provided by the user, self.dns_request is assumed to be added byt other function 
        '''
        dns_zone_modules=parsing.get_zone_from_label(self.dns_data)
        #TODO: Find better way to do this (consider record type)
        if not dns_zone_modules:
            dns_zone_modules=parsing.get_dns_label(self.dns_data)
        for dns_handler_module in dns_zone_locator(parsing.get_zone_from_label(self.dns_data)):
            try:
                dns_handler_module(self.dns_data)
            except SWAN_StopProcessingRequest:
                '''
                Stop processing and the response we have achived so far
                '''
                break
            except SWAN_SkipProcessing:
                '''
                Skip processing of this module
                '''
                pass
            except:
                self.log('Error occured processing dns label %s' parsing.get_dns_label(self.dns_data))
                #TODO:Add warn/debug stacktrace log printing
                break
    
    def handle(self):
        '''
        The actual handling code 
        '''
        self.read_data()
        self.process()
        self.write_data()

class UDPDNSRequestHandler(DNSRequestHandler):

    def parse_request_data(self):
        '''
        Parse data for udp
        '''
        return dnslib.DNSRecord.parse(self.request[0].strip())


def get_server(address='0.0.0.0',port=5053,inet_family='udp',new=False):
    '''
    return an instance of a running server or return currently running server if 
    a) This is the first time get_server is called
    b) the new attribute is set to true
    '''
    if not inet_family in _server_inet_family:
        raise SWAN_UnkownInetFamily('Unkown inet family %s' %inet_family)
        
    if (_server is None) or new:
        _server_meta=_server_inet_family[inet_family]
        new_server=_server_meta['server']((address,port),_server_meta['handler'])
        if _server is None:
            _server=new_server
        return new_server
    return _server
    
        
        
    
