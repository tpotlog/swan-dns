from swandns.modules import BaseResolvingModule
from swandns.swan_errors.exceptions import SWAN_ModuleConfigurationError
import os
import dnslib

class ZoneFileResolverModule(BaseResolvingModule):
    def __init__(self,conf,zone_resolver=True):
        super(ZoneFileResolverModule,self).__init__(conf=conf,zone_resolver=zone_resolver)
        
    def setup(self):
        self.rrmap={}
        
    def _set_rr_map_record(self,rr_record):
        """Add a value to the rr records to the rrmap, Evaluate the zone given options

        :param rr_record: The resource record to add which is from the type of dnslib.DNSRecord
        :returns: None
        :rtype: None
        """
        
        if not rr_record.rname.matchSuffix(self._label):
            raise SWAN_ModuleConfigurationError('Dns record %s does not match this module dns zone %s'
                                                %(str(rr_record),str(self._label)))
                
        if '.' in str(rr_record.rname.stripSuffix(self._label))[:-1]:
            raise SWAN_ModuleConfigurationError('This dns module is an authoretive module only resocrds from subdomains could not be added "%s"' %(str(rr_record.rname)))

        rtype=dnslib.QTYPE[rr_record.rtype]

        self.rrmap.setdefault(rtype,{})[str(rr_record.rname)]=rr_record
       
    def inital_validate(self):
        self._label=dnslib.DNSLabel(self.conf['zone'])
        
        if not 'zone_file' in self.conf:
            raise SWAN_ModuleConfigurationError('zone_file attribute is missing from module configuration')
        
        if not os.path.isfile(self.conf['zone_file']):
            raise SWAN_ModuleConfigurationError('The zone file defined %s does not exists or is not a file' %self.conf['zone_file'])
        
        try:
            zfile=open(self.conf['zone_file'],'r').read()
            self.zone_parser=list(dnslib.ZoneParser(zfile))
        except:
            raise SWAN_ModuleConfigurationError('Failed to load zone file %s' %self.conf['zone_file'])

        for rr in self.zone_parser:
            self._set_rr_map_record(rr)

        
    def _resolve(dns_request,dns_response,request_info):
        import pdb
        pdb.set_trace()
        
        
resolver=ZoneFileResolverModule
