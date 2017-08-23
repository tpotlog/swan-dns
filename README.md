# swan-dns
 
```
   (o_
\\\_\
<____)    
 ```
Swan DNS is a python based DNS server taking the concept of plug-ins to the next level.
The entire idea is to create a DNS server where writing a costume DNS resolver is not more than writing a simple small plug-in.

More than this plug-ins can be reused and concatenate together to provide a simple way for a very complex to achive DNS resolution
with commonly used dns servers/tools.

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
![Rolling Response](/images/Diag2.png)
