'''
This is the main server code of the swiss knife dns
'''
import sys
import logging
import SocketServer
import dnslib
from swandns.swan_errors.exceptions import SWAN_StopProcessingRequest,SWAN_DNS_Exception,SWAN_SkipProcessing,SWAN_NoSuchZoneError,SWAN_DropAnswer,SWAN_UnkownInetFamily
from swandns.utils.parsing import get_qtype,get_dns_label,get_zone_from_label
from swandns.modules import BaseResolvingModule,load_module
from swandns.utils.swanlogs import get_logger


def get_logger_name():
    '''
    Return the logger name of a dns zone
    '''
    return 'swan-dns'

class DNSServerCommon(object):
    """
    Class to define functionalities need from any DNS server
    """
    def get_zones_map(self):
        if not hasattr(self,'_zones_map'):
            self._zones_map={}
        return self._zones_map

    def set_parsing_modules(self,zone,parsing_module):
        """Populate parsing module per zone

        :param zone: The zone name
        :param parsing_module: The module from the type of swandns.modules.BaseResolvingModule
        :returns: None.
        :rtype: None.
        """
        if not isinstance(parsing_module,BaseResolvingModule):
                raise SWAN_DNS_Exception('Only modules from the type of "BaseResolvingModule" could be used for resolving a module')
        self.get_zones_map().setdefault(zone,[]).append(parsing_module)

    def locate_resolving_modules(self,zone):
        """Locate the resolution modules list for this zone

        :param zone: The zone name to resolve.
        :returns: List of modules which should resolve the the DNS request.
        :rtype: List.
        """
        zones_map=self.get_zones_map()
        _zone=str(dnslib.DNSLabel(zone))

        if not _zone in zones_map:
            raise SWAN_NoSuchZoneError(
                'The DNS server can not resolve Zone "%s"' %_zone)
        
        return zones_map[_zone]

class DNS_UDPServer(SocketServer.ThreadingUDPServer,DNSServerCommon):
    '''
    Udp threaded DNS socket server
    '''
    pass
    

_server=None
'''
Current running server instance 
'''

class DNSRequestHandler(SocketServer.BaseRequestHandler):

    def log(self,msg,level=logging.INFO):
        """The log messages bby default info messages.
        This method should e used when logging default messages.

        :param msg: The message to log.
        :param level: The logging level based on python logging module (ex:logging.DEBUG).
        :returns: None.
        :rtype: None.

        """
        
        lgr=get_logger()
        lgr.log(level,msg)
    def log_debug(self,msg):
        """Log a debug message

        :param msg: The message to log.
        :returns: None.
        :rtype: None

        """
        self.log(msg,logging.DEBUG)
    def log_warn(self,msg):
        """Log a warning message.

        :param msg: The message to log.
        :returns: None.
        :rtype: None.

        """
        self.log(msg,logging.WARN)
        
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
        raise NotImplementedError
    
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

    def _gen_response_object(self):
        """Generate the DNS response module which will be sent back to the client.

        :returns: An object taht will be sent back to the client as DNS response.
        :rtype: Noner
        """

        self.dns_response=dnslib.DNSRecord(dnslib.DNSHeader(id=self.dns_data.header.id,
                                                       qr=1,
                                                       aa=1,
                                                       ra=1),
                                      q=self.dns_data.q)
        
    def close(self):
        '''
        Close the connection if needed 
        '''
        raise NotImplementedError
    
    def process(self):
        '''
        Process the data provided by the user, self.dns_request is assumed to be added byt other function 
        '''
        dns_zone_modules=get_zone_from_label(self.dns_data)
        #TODO: Find better way to do this (consider record type)
        if not dns_zone_modules:
            dns_zone_modules=get_dns_label(self.dns_data)
        self._gen_response_object()
        try:
            for dns_handler_module in self.server.locate_resolving_modules(get_zone_from_label(self.dns_data)):
                try:
                    import pdb
                    pdb.set_trace()
                    dns_handler_module.resolve(self.dns_data,self.dns_response,self.request)
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
                except SWAN_DropAnswer:
                    '''
                    Stop the loop and return from the function causing not to send response to the client
                    '''
                    return 
                except:
                    self.log('Error occured processing dns label %s' %get_dns_label(self.dns_data))
                    #TODO:Add warn/debug stacktrace log printing
                    break
        except SWAN_NoSuchZoneError:
            tp,value,tb=sys.exc_info()
            self.log_warn(str(value))

        self.write_data()
    
    def handle(self):
        '''
        The actual handling code 
        '''
        self.read_data()
        self.process()
        self.close()
        
class UDPDNSRequestHandler(DNSRequestHandler):

    def parse_request_data(self):
        '''
        Parse data for udp
        '''
        return dnslib.DNSRecord.parse(self.request[0].strip())

    def close(self):
        '''
        Closing connection in UDP is doing nothing.
        '''
        pass
    
    def write_data(self):
        """Send udp packet to the requesting client

        :returns: send results
        :rtype: 
        """
        
        return self.request[1].sendto(self.dns_response.pack(),
                                      self.client_address)


_server_inet_family= {'udp':
                      {'server':DNS_UDPServer,
                       'handler':UDPDNSRequestHandler
                     }}
'''
Mapping between server inet family and server+handler.
To add new inet_family/handler simply add the addtional values to the dict
'''

    
def get_server(address='0.0.0.0',port=5053,inet_family='udp',*k,**kargs):
    """FIXME! briefly describe function

    :param address: the ip address to bind to 0.0.0.0 means all interfaces.
    :param port: The port to listen to.
    :param inet_family: inet family avaliable now is udp
    :returns: new SocketServer object.
    :rtype: 

    """
    if not inet_family in _server_inet_family:
        raise SWAN_UnkownInetFamily('Unkown inet family %s' %inet_family)
        
    _server_meta=_server_inet_family[inet_family]
    new_server=_server_meta['server']((address,int(port)),_server_meta['handler'])
    return new_server

