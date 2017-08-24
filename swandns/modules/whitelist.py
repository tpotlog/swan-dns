from  swandns.modules.blacklist import BlackListResolverModule
import ipcalc

def WhiteListResolverModule(BlackListResolverModule):
    '''
    The WhiteListResolverModule is a module which will hold 2 white lists of ips (one for ipv4 & one for ipv6).
    The module implements white list from a lists of networks provided in configurations.

    * iplist4 - List of ipv4 network ranges (Ex: 192.168.0.0/24).
    * iplist6 - List of ipv4 network ranges (Ex: fe80::7c05:543:55de:f483/64).
     
    Every time a request comes trough the ip of the client is validated aginst the appropriate list
    according to the client ip address type.
    if it does not matches one of the network ranges than according to the on_detect attribute an action is taken.

    the on_detect attribute can take 2 values.
    * drop - in this case when a client ip addresses doe not  matches one of the networks in one of the whitelist.
             Than te DNS response is dropped and no response is returned to the client.
    * stop - in this case when a client ip addresses does not matches one of the networks in one of the whitelist.
             Than te DNS response processing stopped and whatever the value of the DNS response is returned to the client    
    '''

    def _resolve(self,dns_request,dns_response,request_info):
        
        clientip=ipcalc.IP(request_info.client_address[0])
        if clientip.version()==4:
            for blv4 in self._iplist4:
                if clientip in blv4:
                    return 
        else:
            for blv6 in self._iplist6:
                if clientip in blv6:
                    return
                
        #if we reached so far than we could not find a matching range so we will stop the processing.
        raise self.on_detect

resolver=WhiteListResolverModule
