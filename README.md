# swan-dns
 
```
   (o_
\\\_\
<____)    
 ```
Swan DNS is a python based DNS server taking the concept of modules to the next level.
The entire idea is to create a DNS server where writing a costume DNS resolver is not more than writing a simple small module.

More than this a modules can be reused and concatenate together to provide a simple way for a very complex to achive DNS resolution scenarios ,with commonly used dns servers/tools.

Swan-dns stands for Swiss Army Knife DNS Server (yes I know I am missing the K) and got nothing to do with the magnificent bird called swan. 


## Requests Flow

The swan-dns handle requests with a multiplexing approach.
Once a request recived it tries to identify if a zone defined for this server can handle the request.
If no zone was found than an empty request is returned.
The following diagram describe that flow.
The numbers are indicating the resolution order.

![Processing Flow](/images/Diag1.png)

## Resolving modules 
Resolving modules are the actual resolution code parts of the DNS server.
Each resolution module is designed to be an zone indpendent code that will do it's work to whatever zone it will need to resolve requests for.

At server startup according to the configuration a resolving module with it's configurations is attached to a chain of processing modules for a specific zone.

The structure of zone relation to the resolution module is described at the following diagram.
![Zone resolvers structure](/images/Diag2.png)

!!! please note that a zone without any resolution module is a possiable scenario but pretty useless since nothing will be resolved.

## Rolling response 
As mentioned before the resolving modules for each zone are chained together but the code of each does some work related to the resoltion.
The only connection between the modules chaned together is that the response (and request) data is rolled from one module to the other.
This means several things.

* Each resoltion module recives the response object which might have been changed by all the modules in front of him in the chain.
* Each change made by the resolution module is reflected to all the modules following him in the chain.
* The First module always get an empty response object.
* After the last module in the chain finished it's work the response will be sent back to the client.

The following diagram describes the process.
![Rolling Response](/images/Diag3.png)

Modules can also stop the chain of processing in 2 ways: 
* Stop the chain and return the dns reponse object which was built so far.
* Stop the chain and drop the response returning nothing to the client.

For example if we would like to have some whitelist module which filters ip addreses , we should put it as our first module which will stop the chain if a certain ip is not allowed to query the dns server.

# Installation.

## Prerequsites 

Swan-dns requieres the following python packages to work 

* dnslib 
* ipcalc

Install then anyway you like as long as they are avaliable to load.
A good option is to use pip form installation.

`pip install dnslib ipcalc`

The swan-dns was written as a complete python package so in theory you can just check out the code add `<path to swan-dns dir>` to your PYTHONPATH.
Next you will be able to import the swandns package or an other sub package of it.

To make things a little bit more easy a setup.py script was written.

## Using the setup.py 

The setup.py script was written with python [distutils.core.setup](https://docs.python.org/2/distutils/setupscript.html).
So all the setup.py options are avaliable.

1. ```git clone https://github.com/tpotlog/swan-dns.git``` 
2. ```cd swan-dns``` 
3. ```python setup.py install [intallation options]``` 

# Running The server

Currently the server supports loading it's configurations from an ini file.

## Ini configuration file format.
The ini format is as follows.

```ini
[server]
###This section holds all the server configurations### 
address=0.0.0.0 # the ip address to bind to "0.0.0.0" means bind to all.
port=53 # The dns port to listen to (please make sure you got the right user permissions to user port 53).
logfile=/var/log/swan-dns.log #path to the log file
loglevel=info # logging level avaliable are info,warn,debug (case in-sesitive).
modules_paths=<list of os paths to search for mudules "," is used as delimiter> # those directories are added to the PYTHONPATH
##Define dns zones this server will resolve at the following format.
#zone.<dns zone fqdn>=<list of zones section to load "," is used as delimiter>.
zone.example.com=zonefile.example.com

[zonefile.example.com]
###This section represent a module###
type=module
#the format is as follows 
#module option:
#opt1=val1
#opt2=val2
##options are documented at module code.
module_name=zonefile #name of the python module to load.
zone_file=<path to the zone file>
```
**Module Loading:**

The module_name value is passed to the python imp module to the imp.find_module to search the module file so make sure that a python
so make sure that a python module with the file name <modulename>.py is avaliable at your PYTHONPATH.
however since the data is passed to the imp module you can use anything that will satisfy the imp.find_module function will work.

**Example**

This example demostrates a server with the following charesteristics.

1. Listen on port 5053
2. Binds to all interfaces.
3. serving zone example.com using the zone file module.

***zone file (/var/tmp/example.com.zonefile)***
```zonefile
$ORIGIN example.com.
$TTL 3h
;Define records.
example.com. IN SOA ns.example.com username.example.com ( 2007120710 1d 2h 4w 1h )
example.com. IN NS ns
@	     IN NS ns2.example2.com.
@	     IN MX 10  mail01.example.com.
example.com. IN MX 20 mail02
; A Records
example.com. IN A 192.0.2.11 ;IPv4 for example.com.
example.com. IN A 192.0.2.12 ;IPv4 another for example.com.
	     IN AAAA 2001:db8:10::1 ; IPv6 for example.com.
ns 14000     IN A 192.0.2.12 ; IPv4 Address for the ns record.
	     IN AAAA 2001:db8:10::2 IPv4 Address for ns resord.
www	     IN CNAME example.com. ; cname for example.com record.
www2 3600 IN CNAME www ; cname for www cname which leads to example.com.
```

***ini file (/var/tmp/swan-dns.ini)***
```ini
[server]
port=5053
address=0.0.0.0
logfile=/var/tmp/swan-dns.log
zone.example.com=zonefile.example.com

[zonefile.example.com]
type=module
module_name=swandns/modules/zonefile
zone_file=/var/tmp/example.com.zonefile
```
Using the python shell 

```shell
$ python
Python 2.7.13 (default, Jan 19 2017, 14:48:08) 
[GCC 6.3.0 20170118] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from swandns.utils.config import load_from_ini_file
>>> dnsserver=load_from_ini_file('/var/tmp/swan-dns.ini')
>>> dnsserver.serve_forever()

```

Using dig to query the server

```shell
$ dig example.com -p 5053 @127.0.0.1

; <<>> DiG 9.10.3-P4-Ubuntu <<>> example.com -p 5053 @127.0.0.1
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 5420
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;example.com.			IN	A

;; ANSWER SECTION:
example.com.		10800	IN	A	192.0.2.12

;; Query time: 0 msec
;; SERVER: 127.0.0.1#5053(127.0.0.1)
;; WHEN: Wed Aug 30 10:43:48 IDT 2017
;; MSG SIZE  rcvd: 45
```

```shell
$ dig example.com -p 5053 -t ns  @127.0.0.1

; <<>> DiG 9.10.3-P4-Ubuntu <<>> example.com -p 5053 -t ns @127.0.0.1
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 28368
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;example.com.			IN	NS

;; ANSWER SECTION:
example.com.		10800	IN	NS	ns2.example2.com.

;; Query time: 0 msec
;; SERVER: 127.0.0.1#5053(127.0.0.1)
;; WHEN: Wed Aug 30 10:44:43 IDT 2017
;; MSG SIZE  rcvd: 56
```

```shell
$ dig www.example.com -p 5053  @127.0.0.1

; <<>> DiG 9.10.3-P4-Ubuntu <<>> www.example.com -p 5053 @127.0.0.1
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 53210
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;www.example.com.		IN	A

;; ANSWER SECTION:
www.example.com.	10800	IN	CNAME	example.com.

;; Query time: 0 msec
;; SERVER: 127.0.0.1#5053(127.0.0.1)
;; WHEN: Wed Aug 30 10:45:03 IDT 2017
;; MSG SIZE  rcvd: 47
```

# SWAN-DNS Modules

The following modules are avaliable for swan-dns 
* zonefile - load a file at the [zone file format](https://en.wikipedia.org/wiki/Zone_file).
* blacklist - blacklist a list of network ips resulting in blacklisting a range of network ips.
* whitelist - whitelist a list of network ips resulting in serviceing only specific netwok ranges.
* delay - Generate a random delay (within a specific range of miliseconds) while processing a resaponse this of course will result in a delay for answerig to the client , mostly used for testing DNS clients functionalities at long delays.

# Writing s SWAN-DNS module

Every SWAN-DNS module is baiclly a class which inherits from swandns.modules.BaseResolvingModule

## The swandns.modules.BaseResolvingModule class

The swandns.modules.BaseResolvingModule class has several things to notice when creating a resolver class which inherits it.

### The __init__ methods
The ```__init__``` method recives 3 attributes.
1. **conf** - A dict that holds all the module configurations , the zone attribute is automaticlly populated by the server and overrun if already defined.
2. **zone_resolver** - By default is set to True , if defined than the module will check if the zone key was defined at the conf dict.
3. **lock_reslution** - should the resolution function lock thereads until resolution is done (or error occured).

### The ```setup``` function ###
The setup method is called right after configurations have been saven at the ```__init__``` method.
This is the place to do some initial setups, to do so simply overrid it.

### The ```inital_validate``` method ###
The ```inital_validate``` method is called after the setup method have been called at the ```__init__``` method.
This is the place to do some inital validation of th configuration input (the configurations are stored at self.conf).

### The ```_resolve``` method ###
The ```_resolve``` method is a method where you should write your resolution code.
It is called for every resolution request and will get 3 attributes.
1. **dns_request** - The dns request object (an object from the type of dnslib.DNSRequest).
2. **dns_response** - The response object (an object from the type of dnslib.DNSRequest).
3. **request_info** - The original request handler which is based on SocketServer handler.

You do not have to worry about locking threads since if the lock_resolution attribute was specified at the ```__init__``` method this function is thread safe.

## Export your resolver module ##
Every resolver module should exists in one python module and one python module can hold (more exact exports) only one resolution module.

This is done by setting the module attribute resolver to the class that implements the resolution.

### Things To notice ###

* When the server loads the modules it actually loads the class and create an object from this class with a specifc attributes for each zone.

* During resolution please take into account that you are working on the same python object as the next thread than will work on so please make sure to be very careful about object changes.

## Exceptions handling ##
Any exception whihc will be raised by the module during resolution will be cought and process by the server.
While most exceptions will be logged a module can raise several exceptions which will detarmain the response sent back to the client.

1. **swandns.swan_errors.exceptions.SWAN_StopProcessingRequest** - If this exception is throwen while requesting a process than the DNS server will stop the processing and return the dns response object to the client.
2. **swandns.swan_errors.exceptions.SWAN_DropAnswer** - If this exception is throwen while requesting a process than the DNS server will stop the processing and will not return the dns response object to the client.
3. **swandns.swan_errors.exceptions.SWAN_SkipProcessing** - If this exception is throwen while requesting a process than the DNS server will just ignore it and continue to process to the other module.

## Example: A module which filter requests according to the record type ##
This module will filter requests which only matches a specific record types if the module detects that the query type is not according to a given record types than nothing is returned to the client.


Module code resides under /home/tpotlog/swan-modules/records_filter.py 

```python
from swandns.modules import BaseResolvingModule
from swandns.swan_errors.exceptions import SWAN_ConfigurationError,SWAN_DropAnswer
from dnslib import QTYPE as qtypes

class RecordTypeFilterResolver(BaseResolvingModule):

    def __init__(self,conf):
        super(RecordTypeFilterResolver,self).__init__(conf=conf,zone_resolver=False,lock_reslution=False)

    def inital_validate(self):
        """Verify configuration input.

        * allowed_record_types - List of record types which are allowed to be processed, "," is to be used as delimiter. 

        :returns: None.
        :rtype: None.

        """
        if not 'allowed_record_types' in self.conf:
            raise SWAN_ConfigurationError('allowed_record_types must be defined for this module')
        self.allowed_record_types=self.conf['allowed_record_types'].split(',')

    def _resolve(self,dns_request,dns_response,request_info):
        if not qtypes[dns_request.q.qtype] in self.allowed_record_types:
            #if the record does not match drop the answer
            raise SWAN_DropAnswer

#export the resolving module
resolver=RecordTypeFilterResolver
```

The ini configuration file /var/tmp/swan-dns.ini.
Please pay attenton to the modules_paths=/home/tpotlog/swan-modules/ server attribute this means that modules will be also searched in this directory.
 
```ini
[server]
port=5053
address=0.0.0.0
logfile=/var/tmp/swan-dns.log
modules_paths=/home/tpotlog/swan-modules/
zone.example.com=limit-records,zonefile.example.com
loglevel=debug
[zonefile.example.com]
type=module
module_name=swandns/modules/zonefile
zone_file=/var/tmp/example.com.zonefile

[limit-records]
type=module
module_name=records_filter
allowed_record_types=A,CNAME,NS
```


Running the server
```shell
$ python
Python 2.7.13 (default, Jan 19 2017, 14:48:08) 
[GCC 6.3.0 20170118] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from swandns.utils.config import load_from_ini_file
>>> srv=load_from_ini_file('/var/tmp/swan-dns.ini')
>>> srv.serve_forever()
```

Asking for records which can be resolved

```shell
$ dig example.com -p 5053 -t a @127.0.0.1

; <<>> DiG 9.10.3-P4-Ubuntu <<>> example.com -p 5053 -t a @127.0.0.1
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 29692
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;example.com.			IN	A

;; ANSWER SECTION:
example.com.		10800	IN	A	192.0.2.12

;; Query time: 1 msec
;; SERVER: 127.0.0.1#5053(127.0.0.1)
;; WHEN: Sat Sep 02 15:17:17 IDT 2017
;; MSG SIZE  rcvd: 45
```
```shell
$ dig example.com -p 5053 -t NS @127.0.0.1

; <<>> DiG 9.10.3-P4-Ubuntu <<>> example.com -p 5053 -t NS @127.0.0.1
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 22445
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;example.com.			IN	NS

;; ANSWER SECTION:
example.com.		10800	IN	NS	ns2.example2.com.

;; Query time: 0 msec
;; SERVER: 127.0.0.1#5053(127.0.0.1)
;; WHEN: Sat Sep 02 15:17:46 IDT 2017
;; MSG SIZE  rcvd: 56
```
Asking for records which can be resolved
```shell
$ dig example.com -p 5053 -t SRV  @127.0.0.1

; <<>> DiG 9.10.3-P4-Ubuntu <<>> example.com -p 5053 -t SRV @127.0.0.1
;; global options: +cmd
;; connection timed out; no servers could be reached
```

# TO DO
* ~~Documentation on how to write a module.~~
* Write tests
* Support Python3
