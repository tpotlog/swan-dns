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
![Processing Flow](/images/Diag2.png)
