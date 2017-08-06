'''
Utils to make the work of extracting information from DNS queries.
'''
import dnslib

def get_qtype(dns_query):
    '''
    Return the query type from a DNS query.
    If the type is not found None is returned
    '''
    return dnslib.QTYPE(dns_query.q.qtype,None)

def get_dns_label(dns_query):
    '''
    Return the dns label 
    '''
    return str(dns_query.q.qname)

def get_zone_from_label(dns_query):
    return '.'.join(dns_query.q.qname.label[1:])+'.'

def get_record_name_from_label(dns_query):
    return dns_query.q.qname.label[0]

