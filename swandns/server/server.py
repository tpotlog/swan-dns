'''
This is the main server code of the swiss knife dns
'''
import sys
import logging
import SocketServer
import dnslib
import traceback
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
        _zone=zone.q.qname.idna()
        if _zone in zones_map:
            return zones_map[_zone]
        elif _zone.split('.',1)[-1] in zones_map:
            return zones_map[_zone.split('.',1)[-1]]
        raise SWAN_NoSuchZoneError(
                'The DNS server can not resolve "%s"' %_zone)

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
    def dump_dns_packets(self,response=True,request=True):
        """Helper function to dump the content of dns request + response 

        :returns: String of the DNS response & Request
        :rtype: string

        """

        
        dump=''
        if request:
            if hasattr(self,'dns_data'):
                dump+='DNS Request:\n----------\n%s' %self.dns_data.toZone()
        if response:
            if hasattr(self,'dns_response'):
                dump+='DNS Response:\n----------\n%s' %self.dns_response.toZone()
        return dump
        

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
    def _unexpected_error(self):
        """This function should be called when we encounter unexpected error.
           It will dump the stack trace for future debugging.

        :returns: None.
        :rtype: None.

        """
        self.log('Unexpected error occured probably a bug')
        tp,value,tb=sys.exc_info()
        self.log('\n'.join([str(t) for t in traceback.extract_stack()]))
                
    def process(self):
        '''
        Process the data provided by the user, self.dns_request is assumed to be added byt other function 
        '''
        self.log_debug('Request From %s ' %str(self.client_address))
        self._gen_response_object()
        self.log_debug(self.dump_dns_packets(response=False))
        try:
            for dns_handler_module in self.server.locate_resolving_modules(self.dns_data):
                try:
                    dns_handler_module.resolve(self.dns_data,self.dns_response,self)
                except SWAN_StopProcessingRequest:
                    '''
                    Stop processing and the response we have achived so far
                    '''
                    self.log_warn(
                        'Module %s called SWAN_StopProcessingRequest, No other modules will be called' %str(dns_handler_module))
                    break
                except SWAN_SkipProcessing:
                    '''
                    Skip processing of this module
                    '''
                    self.log_warn(
                        'Module %s called SWAN_SkipProcessing'
                        %str(dns_handler_module))
                    pass
                except SWAN_DropAnswer:
                    '''
                    Stop the loop and return from the function causing not to send response to the client
                    '''
                    self.log_warn(
                        'Module %s called SWAN_DropAnswer, No response will be sent to the client'
                        %str(dns_handler_module))
                    return 
                except:
                    self.log('Error occured processing dns label %s' %get_dns_label(self.dns_data))
                    raise 
                
        except SWAN_NoSuchZoneError:
            self.log_warn('DNS zone for dns request %s was not found' %(self.dns_data.q.qname.idna()))
        except:
            '''
            Unkown exception occured this is a bug, server will not return answer 
            to the client we might provide The worng data
            '''
            self._unexpected_error()
            return
        
        #if we reached here sata will be written back to the client.
        self.log_debug(self.dump_dns_packets(request=False))
        self.write_data()
    
    def handle(self):
        '''
        The actual handling code 
        '''
        try:
            self.read_data()
            self.process()
            self.close()
        except:
            '''
            Handle unexpected errors occured during handling
            '''
            self._unexpected_error()
        
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

