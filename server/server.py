'''
This is the main server code of the swiss knife dns
'''

import logging
import SocketServer
import dnslib
 


def get_logger_name(dns_zone=None):
    '''
    Return the logger name of a dns zone
    '''
    return 'swan-dns'


processing_d={}
'''
The processing_d is a dictionary holding all the modules which will process each dns zone.
The overall look of the dict will look something like.

{
'this.is.the.zone.x':[<module object 1>,<module object 2>.....


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
        for dns_handler_module in dns_zone_locator():
            try:
                dns_handler_module()
        
        return self.dns_data
    def handle(self):
        '''
        The actual handling code 
        '''
        import pdb
        pdb.set_trace()
        data=self.request[0].strip()
        pdb.set_trace()
        p_data=dnslib.DNSRecord.parse(data)


class UDPDNSRequestHandler(DNSRequestHandler):
    
