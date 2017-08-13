from swandns.modules import BaseResolvingModule
from swandns.swan_errors.exceptions import SWAN_ModuleConfigurationError
import os
import dnslib

class ZoneFileResolverModule(BaseResolvingModule):

    def setup(self):
        self.rrmap={}
    def _set_rr_map_record(self,rr_record):
        """Add a value to the rr records to the rrmap, Evaluate the zone given options

        :param rr_record: The resource record to add which is from the type of dnslib.DNSRecord
        :returns: None
        :rtype: None
        """

        import pdb
        pdb.set_trace()
        
       
    def inital_validate(self):
        self._label=dnslib.DNSLabel(self.conf['zone'])
        
        if not 'zone_file' in self.conf:
            raise SWAN_ModuleConfigurationError('zone_fine attribute is missing from module configuration')
        
        if not os.path.isfile(self.conf['zone_file']):
            raise SWAN_ModuleConfigurationError('The zone file defined %s does not exists or is not a file' %self.conf['zone_file'])
        
        try:
            zfile=open(self.conf['zone_file'],'r').read()
            self.zone_parser=list(dnslib.ZoneParser(zfile))
        except:
            raise SWAN_ModuleConfigurationError('Failed to load zone file %s' %self.conf['zone_file'])

        for rr in zone_parser:
            self._set_rr_map_record(rr)
#           if len(rr.rname.label)>1 and (not rr.name.matchSuffix(self._label)):
#               raise SWAN_ModuleConfigurationError('Resource record %s label "%s" does not match this zone module label "%s"' %(rr.))

        
