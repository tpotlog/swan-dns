'''
Basic class to define the basic resolution module
'''
from swandns.swan_errors.exceptions import SWAN_ModuleLoadError, SWAN_ModuleConfigurationError
import imp,os,sys,threading


class BaseResolvingModule(object):
    '''
    An object representing base DNS resolving module
    '''
    def __init__(self,conf,zone_resolver=True,lock_reslution=True):
        """
        :param conf: A python dict which holds the resolver module configurations.
        :param zone_resolver: Does this module serves as DNS resolver (if so than conf['zone'] must be defined).
        :param lock_reslution: Should the resolve function be locked?, due to the multi thread nature of the server should be lock the resolve function for one thread at a time.
        :returns: None.
        :rtype: None.

        """     
        self.conf=conf
        self.setup()
        self.inital_validate()
        self.resolving_lock=threading.RLock()
        self.lock_resolution=lock_reslution
        if zone_resolver and (not "zone" in conf):
            raise SWAN_ModuleConfigurationError('zone attribute was not provided')
        
        
    def _resolve(self,dns_request,dns_response,request_info):
        """The actual resolution code

        :param dns_request:  The dns request of object from the type of dnslib.DNSRequest.
        :param dns_response: The dns response of object from the type of dnslib.DNSRecord.
        :param request_info: The original request from the SocketServer
        :returns: None.
        :rtype: None.
        """

        raise NotImplementedError
        
    def resolve(self,dns_request,dns_response,request_info):
        """Call the _resolve functions with the paremeters recived.

        :param dns_request:  The dns request of object from the type of dnslib.DNSRequest.
        :param dns_response: The dns request of object from the typ of dnslib.DNSRequest
        :param request_info: The original request from the SocketServer
        :returns:  None.
        :rtype: None.
        """
        try:
            if self.lock_resolution:
                self.resolving_lock.acquire()
            self._resolve(dns_request,dns_response,request_info)
        finally:
            tp,ex,tb=sys.exc_info()
            if self.lock_resolution:
                self.resolving_lock.release()
            #reraise an exception of this occured
            if ex is not None:
                raise ex
    def setup(self):
        '''
        Do some initial setups if needed 
        '''
        pass
    def shutdown(self):
        '''
        Do some shutdown actions if needed when this function is called
        '''
        pass

    def inital_validate(self):
        '''
        Do some inital validation of the data
        '''
        pass


def load_module(module_name, conf):
    """Load a python module and see if it is suitable as dns module

    :param module_name: The python module name to load.
    :param conf: Python dictionary representing module configurations.
    :returns: Python module representing the module.
    :rtype: object which is from a subclass of BaseResolvingModule
    """
    md=None
    try:
        md=imp.load_module(module_name,*imp.find_module(module_name))
    except:
        raise SWAN_ModuleLoadError('Failed to load module %s' %module_name)
            
    if not hasattr(md,'resolver'):
        '''
        Was the resolver attribute defined for this module ? 
        '''
        raise SWAN_ModuleLoadError('Python module  %s have not define the "resolver" attribute' %module_name)
    resolver=md.resolver
    if not issubclass(resolver,BaseResolvingModule):
        '''
        is the resolver attribute is a referance for a class from the type of BaseResolvingModule ?
        '''
        raise SWAN_ModuleLoadError('The resolver defined at module %s is not from the type of BaseResolvingModule' %module_module)

    return resolver(conf)
    
