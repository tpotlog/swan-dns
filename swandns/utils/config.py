'''
This module will hold utils to load a server and setup environment from a configuration source
'''

import ConfigParser,os,sys
from swandns.swan_errors.exceptions import SWAN_ConfigurationError
from swandns.utils.swanlogs import start_logger
from swandns.server.server import get_server
from swandns.modules import load_module

'''
Default server configurations
'''
_server_defaults={
    'port':53,
    'address':'0.0.0.0',
    'loglevel':'info',
    'logfile':'/var/log/swan-dns.log',
    'modules_paths':''
}



def load_from_ini_file(config_file):
    """Return a DNS server loaded from a configuration ini file.


    The Expected format of the ini file is as follows.

    [server]
    #This is the default DNS server configurations.
    address=0.0.0.0 # Which address to bind to 0.0.0.0 means listen on all interfaces
    port=53 # Which port to listen on 
    logfile=/var/log/swan-dns.log #log file location
    loglevel=info # logging level avaliable are info,warn,debug (case in-sesitive).
    modules_paths=<list of os paths to search for mudules "," is used as delimiter>
    #Define dns zones this server will resolve at the following format.
    #zone.<dns zone fqdn>=<list of zones to load "," is used as delimiter>.
    # 
    zone.example.com = zonefile.example.com #assign resolution modules to zone
    ##################################LOAD RESOLUTION MODULES###############################
    #prepare resolution modules to be loaded.
    #[module1]
    #type=module
    #module_name=<python module name to load>
    
    ##all the keys and valued defined here will be passed as configurations to the module.
    ##If the zone attribute is defined it will be replaced with the right zone of the dns zone 
    ##this module is assigned to
    #
    #key1=value1
    #key2=value2
    #.
    #.
    #.
    [zonefile.example.com]
    type=module
    module_name=zonefile
    zone_file=<path to the zone file>
    
    

    :param config_file: The configuration file to read data from
    :returns: A SocketServer instance ready to run with all configuration loaded.
    :rtype: instance of a pytchon class from the type of SocketServer.BaseServer

    """

    server_config={}
    server_config.update(_server_defaults)
    
    conf=ConfigParser.ConfigParser()
    conf.optionxform=str

    fh=open(config_file,'r')
    conf.readfp(fh)
    fh.close()

    if not conf.has_section('server'):
        raise SWAN_ConfigurationError('Error detected in configuration file [server] section is missing')
    zones={}
    modules={}
    for k in conf.items('server'):
        if k[0] in server_config:
            server_config[k[0]]=k[1]
        elif k[0].startswith('zone.'):
            _zn=k[0][5:]
            if not _zn.endswith('.'):
                _zn+='.'
            zones[_zn]=k[1].split(',')
    if server_config.get('modules_paths'):
        for pth in server_config['modules_paths'].split(','):
            if not pth in sys.path:
                sys.path.append(pth)
    if server_config['loglevel'].lower() not in ['info','warn','debug']:
        raise SWAN_ConfigurationError('"loglevel" attribute values musr be info,warn or debug %s level is not an acceptable level' %server_config['loglevel'])
    logger=start_logger(filename=server_config['logfile'],level=server_config['loglevel'])
    
    logger.info('Starting server with configuration: Address: %(address)s, Port: %(port)s,' %server_config)
    dns_server = get_server(**server_config)

    for sec in conf.sections():
        if sec=='server':
            continue
        if not conf.has_option(sec,'type'):
            logger.warn('Section "[%s] has not type skipping"' %sec)
        elif conf.get(sec,'type')!='module':
            logger.warn('Section ["%s"] type is %s , unkown type skip parsing' %conf.get(sec,'type'))
        modules[sec]=dict(conf.items(sec))
        modules[sec].pop('type')
        
    if not modules:
        logger.warn('No modules were defined for this server it will do nothing')
    if not zones:
        logger.warn('No zones were defined This server will do nothing')
    for zone in zones:
        for mod in zones[zone]:
            if not mod in modules:
                raise SWAN_ConfigurationError('A module with the name of %s was not defined at the configuration file' %mod)
            modconf={}
            #create a copy in case that the module is being reused
            modconf.update(modules[mod])
            #setup the zone
            modconf['zone']=zone
            #load the module
            md=load_module(module_name=modconf.get('module_name',None),conf=modconf)
            dns_server.set_parsing_modules(zone=zone,parsing_module=md)
            
    return dns_server
        
    
    

    
