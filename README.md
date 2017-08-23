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

![Processing Flow](/images/Diag1.png)
