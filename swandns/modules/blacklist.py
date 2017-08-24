'''
The blacklist resolution module is a module which implements a blacklist of ip addresses which will not recive answer
'''


from swandns.modules import BaseResolvingModule
from swandns.swan_errors.exceptions import SWAN_ConfigurationError,SWAN_StopProcessingRequest,SWAN_DropAnswer
import ipcalc 

class BlackListResolverModule(BaseResolvingModule):
    '''
    The BlackListResolverModule is a module which will hold 2 black lists of ips (one for ipv4 & one for ipv6).
    The module implements black list from a lists of networks provided in configurations.

    * iplist4 - List of ipv4 network ranges (Ex: 192.168.0.0/24).
    * iplist6 - List of ipv4 network ranges (Ex: fe80::7c05:543:55de:f483/64).
     
    Every time a request comes trough the ip of the client is validated aginst the appropriate list
    according to the client ip address type.
    if it matches one of the network ranges than according to the on_detect attribute an action is taken.

    the on_detect attribute can take 2 values.
    * drop - in this case when a client ip addresses matches one of the networks in one of the blacklist.
             Than te DNS response is dropped and no response is returned to the client.
    * stop - in this case when a client ip addresses matches one of the networks in one of the blacklist.
             Than te DNS response processing stopped and whatever the value of the DNS response is returned to the client    
    '''
    def __init__(self,conf):
        self._iplist4=[] # list of blocked ipv4 addreses 
        self._iplist6=[] # list of blocked ipv6 addreses
        self.on_detect=SWAN_DropAnswer
        
        super(BlackListResolverModule,self).__init__(conf=conf,zone_resolver=True,lock_reslution=True)

    def inital_validate(self):
        if (not 'iplist4' in  self.conf)  and (not 'iplist6' in self.conf):
            raise SWAN_ConfigurationError('iplist4 or iplist6 must be defined')
        if 'on_detect' in self.conf:
            if self.conf['on_detect'] not in ['drop','stop']:
                raise SWAN_ConfigurationError('The value of on_detect must be "drop" or "stop"')
            if self.conf['on_detect']=='drop':
                self.on_detect=SWAN_DropAnswer
            else:
                self.on_detect=SWAN_StopProcessingRequest
            
        if 'iplist4' in self.conf:
            #populate v4 addreses 
            for v4 in self.conf['iplist4'].split(','):
                net=ipcalc.Network(v4)
                if net.version() != 4:
                    raise SWAN_ConfigurationError('%s is not an ipv4 network' %v4)
                self._iplist4.append(net)
        if 'iplist6' in self.conf:
            for v6 in self.conf['iplist6'].split(','):
                net=ipcalc.Network(v4)
                if net.version() != 6:
                    raise SWAN_ConfigurationError('%s is not an ipv6 network' %v6)
                self._iplist6.append(v6)
        
    def _resolve(self,dns_request,dns_response,request_info):
        
        clientip=ipcalc.IP(request_info.client_address[0])
        if clientip.version()==4:
            for blv4 in self._iplist4:
                if clientip in blv4:
                    raise self.on_detect
        else:
            for blv6 in self._iplist6:
                if clientip in blv6:
                    raise self.on_detect
        
resolver=BlackListResolverModule

