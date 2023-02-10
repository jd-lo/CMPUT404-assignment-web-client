from urllib.parse import urlparse
from config import mapping
from abc import ABC
from email.utils import formatdate
from headers import *

class R(ABC):
    '''Parent class for Request and Response'''
    #Class attribute used to generalize the from_str method that both Request and Response use
    initial_header = StdHeader

    @classmethod
    def from_bytes(cls, data: bytes, charset: str):
        '''Constructs R from a stream of bytes.'''
        decoded = data.decode(charset)
        return cls.from_str(decoded)

    @classmethod
    def from_str(cls, data: str):
        header_strs, body = cls.hb_split(data)
        headers = []

        intl_hdr_str = header_strs.pop(0)
        headers.append(cls.initial_header.from_str(intl_hdr_str))

        for std_hdr_str in header_strs:
            headers.append(StdHeader.from_str(std_hdr_str))

        return cls(headers, body)

    @staticmethod
    def hb_split(data: str) -> tuple:
        '''Splits an R into its header strings and body strings'''

        data = data.split('\r\n\r\n')
        headers = [header for header in data[0].split('\r\n')]
        #No body since terminator is \r\n
        try:
            body = data[1]
        except IndexError:
            body = ''

        return (headers, body)

    def __init__(self, headers = [], body = None):
        self.headers = headers
        self.body = body

    def __str__(self):
        '''Returns an HTTP/1.1 compliant string-representation of an R, with headers and a body.'''
        r_content = ''

        for header in self.headers:
            r_content += str(header)
        #Header-body delimiter
        r_content += '\r\n'
        r_content += self.body
        
        return r_content

    def encode(self, charset) -> bytes:
        return bytearray(self.__str__, charset)
    
    def get(self, field: str) -> str:
        for header in self.headers:
            #This inefficient method allows us to get attributes from the irregular headers
            h_dict = header.to_dict()
            if field.capitalize() in h_dict.keys():
                return h_dict[field]

        return None
    
class Request(R):
    initial_header = IntlReqHeader

    def __init__(self, headers: list, body: str):
        super().__init__(headers, body)

    @classmethod
    def from_args(cls, method, url, args):
        '''Constructs a request from a CLI input.'''

        #Break url into elementary components
        url = urlparse(url)
        body = cls._get_body(method, url, args)
        headers = cls._get_headers(method, url, body)

        return cls(headers, body)

    @classmethod
    def _get_body(cls, method: str, url: tuple, args: object) -> str:
        '''Helper method to construct a request body from CLI'''

        #match and case keywords not compatible with python 3.6 (min requirements)
        body = ''
        #If the user inputs both a query and arguments with GET the arguments are ignored.
        if method.upper() == 'GET':
            #If there is no query it will be an empty string
            body = url.query
        #POST methods will ignore the query
        elif method.upper() == 'POST':
            if type(args) is dict:
                #Unit tests pass in dict, while CLI passes in a list (or None)
                for i, (key, value) in enumerate(args.items(), start = 1):
                    body += f'{key}={value}'
                    if i < len(args):
                        body += '&'
            elif type(args) is list:
                for i, arg in enumerate(args, start = 1):
                    body += arg
                    if i < len(args):
                        body += '&'
            elif type(args) is None:
                body = ''

        return body

    @classmethod
    def _get_headers(cls, method: str, url: tuple, body: str) -> list:
        '''Helper method to construct request headers from CLI'''

        #Some servers like slashdot won't fill this in for us
        path = url.path if url.path != '' else '/'
        date = f'{formatdate(timeval = None, localtime = False, usegmt = False)}'
        #According to unit tests, even empty POST requests have a content-length header
        body_length = str(len(body))

        #Initial Headers (dynamic)
        headers = [
            IntlReqHeader(method, path, 'HTTP/1.1'),
            StdHeader('Host', url.netloc),
            StdHeader('Date', date),
            StdHeader('Content-Length', body_length)
        ]

        #All static headers based on config file
        for field, value in mapping.items():
            #Ignore Content-Type header if not a POST
            if field == 'Content-Type' and method.upper() != 'POST':
                continue
            headers.append(StdHeader(field, value))

        return headers

class Response(R):
    initial_header = IntlResHeader

    def __init__(self, headers: list, body: str):
        super().__init__(headers, body)