'''
A resolution module that do not really does resolution just create a small 
configurable delay of the dns response.
'''

from swandns.modules import BaseResolvingModule
from swandns.swan_errors.exceptions import SWAN_ConfigurationError
import random
import ctypes
import time

class DelayResponseResolverModule(BaseResolvingModule):

    def __init__(self,conf,zone_resolver=False):
        super(DelayResponseResolverModule,self).__init__(conf=conf,zone_resolver=zone_resolver)

    def inital_validate(self):
        """Verify configuration input.
        Verify several thinga about the configurations 

        * min_delay & max_delay are defined.
        * min_delay & max_delay are integers.
        * min_delay & max_delay are both non-negative integers.

        :returns: None.
        :rtype: None.

        """
        if not 'min_delay' in self.conf:
            raise SWAN_ConfigurationError('min_delay is not defined')
        if not 'max_delay' in self.conf:
            raise SWAN_ConfigurationError('max_delay is not defined')

        if not self.conf['min_delay'].isdigit():
            raise SWAN_ConfigurationError('min_delay must be an integer')

        if not self.conf['max_delay'].isdigit():
            raise SWAN_ConfigurationError('max_delay must be an integer')

        self.min_delay=int(self.conf['min_delay'])
        self.max_delay=int(self.conf['max_delay'])

        if self.min_delay<0:
            raise SWAN_ConfigurationError(
                'min_delay is smaller than 0 only positive integers are allowed')
                                    
        if self.max_delay<0:
            raise SWAN_ConfigurationError(
                'max_delay is smaller than 0 only positive integers are allowed')

        if self.max_delay<self.min_delay:
            raise SWAN_ConfigurationError(
                'max_delay is smaller than min_delay this is not a valid configuration')
        
    def _delay(self):
        """Do nothing for some time and return.
        The length of the delay is in miliseconds and is controlled by 2 variables.

        self.min_delay - The minimum number of miliseconds to wait.
        self.max_delay - The maximum number of miliseconds to wait.        

        if the they are the same than min_delay number of miliseconds is waited.
        :returns: None.
        :rtype: None.

        """

        rand_wait=random.randint(self.min_delay,self.max_delay)
        time.sleep(rand_wait/1000.0)
            
    def _resolve(self,*k,**kargs):
        self._delay()

resolver=DelayResponseResolverModule
