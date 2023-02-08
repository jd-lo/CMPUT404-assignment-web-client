from urllib.parse import urlparse
from config import mapping
from abc import ABC, abstractmethod
from email.utils import formatdate

#Strictly for client-implementation
class R:
    '''Parent class for Request and Response'''

    @classmethod
    def from_bytes(cls, data: bytes, charset: str):
        '''Constructs R from a stream of bytes'''
        decoded = data.decode(charset)
        return cls.from_str(decoded)
        
    @classmethod
    def from_str(cls, data: str):
        '''Constructs R from a stream of characters'''
        raise NotImplementedError("Implement string conversion method.")

    def __init__(self):
        self.headers = {}
        self.body = ''
    
    def _hb_split(self, data: str):
        data = data.split('\r\n\r\n')
        headers = data[0].split('\r\n')
        try:
            body = data[1]
        #No body since terminator is \r\n no \r\n\r\n
        except IndexError:
            body = ''

        return headers, body

    def encode(self, charset) -> bytes:
        return bytearray(self.__str__, charset)

    def get(self, field):
        try:
            return self.headers[field]
        except KeyError:
            return None

    def __str__(self):
        pass

class Request(R):
    def __init__(self, headers = {}, body = ''):
        self.body = body
        self.headers = headers

    @classmethod
    def from_args(cls, method, url, body = ''):
        '''Constructs a Request object from a command line'''
        method = method.upper()
        headers = cls._set_headers(method, url, body)
        return Request(headers, body)

    @classmethod
    def from_str(cls, data: str):
        headers = {}

        header_strs, body = cls._hb_split(cls, data)

        intl_header = IntlReqHeader.from_string(header_strs.pop(0))
        headers.update(intl_header.to_dict())
        for header in header_strs:
            header_obj = StdHeader.from_string(header)
            headers.update(header_obj.to_dict())
        
        return cls(headers, body)

    @classmethod
    def _set_headers(self, method, url, body):
        '''Helper to construct headers based on config'''

        #No support for adding your own headers.
        headers = {}
        url = urlparse(url)
        
        #Compose initial headers based on URL
        path = url.path if url.path != '' else '/'
        headers.update(
            IntlReqHeader(method, path, mapping['Scheme']).to_dict(),
        )
        headers.update(
            StdHeader('Host', url.netloc).to_dict(),
        )

        date_value = f'{formatdate(timeval = None, localtime = False, usegmt = False)}'
        headers.update(
            StdHeader('Date', date_value).to_dict(),
        )

        #According to unit tests, even empty POSTs have a content length header.
        body_length = str(len(body))
        headers.update(
            StdHeader('Content-Length', body_length).to_dict()
        )

        if method.upper() == 'POST':
            headers.update(
                StdHeader('Content-Type', mapping['Content-Type']).to_dict()
            )

        #Adds the boilerplate headers based on config file
        for field, value in mapping.items():
            if field != 'Content-Type':
                headers.update(
                    StdHeader(field, value).to_dict()
                )
        return headers

    def __str__(self):
        req_content = ""

        #These need to go into their own line otherwise bad request
        special_fields = ["Method", "Path", "Scheme"]
        for i, field in enumerate(special_fields):
            req_content += f'{self.headers.get(field)}'
            delimiter = ' ' if i != 2 else '\r\n'
            req_content += delimiter

        for field, value in self.headers.items():
            if field not in special_fields:
                req_content += f'{field}: {value}\r\n'
        #Headers delimiter
        req_content += '\r\n'
        
        if self.body:
            req_content += self.body

        return req_content

class Response(R):
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body
        
    @classmethod
    def from_str(cls, data: str):
        headers = {}

        header_strs, body = cls._hb_split(cls, data)

        intl_header = IntlResHeader.from_string(header_strs.pop(0))
        headers.update(intl_header.to_dict())
        for header in header_strs:
            header_obj = StdHeader.from_string(header)
            headers.update(header_obj.to_dict())
        
        return cls(headers, body)

    def __str__(self):
        res_content = ""

        #These need to go into their own line otherwise bad request
        special_fields = ["Scheme", "Code", "Message"]
        for i, field in enumerate(special_fields):
            res_content += f'{self.headers.get(field)}'
            delimiter = ' ' if i != 2 else '\r\n'
            res_content += delimiter

        for field, value in self.headers.items():
            if field not in special_fields:
                res_content += f'{field}: {value}\r\n'
        #Headers delimiter
        res_content += '\r\n'
        
        if self.body:
            res_content += self.body

        return res_content

class Header(ABC):
    @classmethod
    def from_string(cls):
        '''Constructs a header object from its string representation.'''
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        '''Returns field(s) and values as dictionary'''
        pass

class StdHeader(Header):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value

    @classmethod
    def from_string(cls, data: str):
        split_header = data.split(': ', maxsplit=1)
        return cls(split_header[0], split_header[1])

    def to_dict(self):
        return {self.field: self.value}

class IntlReqHeader(Header):
    def __init__(self, method: str, path: str, scheme: str):
        self.method = method
        self.path = path
        self.scheme = scheme 
    
    @classmethod
    def from_string(cls, data:str):
        split_header = data.split(' ')
        return cls(split_header[0], split_header[1], split_header[2])
        
    def to_dict(self):
        return {'Method': self.method, 'Path': self.path, 'Scheme': self.scheme}

class IntlResHeader(Header):
    def __init__(self, scheme, code, message):
        self.scheme = scheme
        self.code = code
        self.message = message

    @classmethod
    def from_string(cls, data: str):
        #Handle code messages with spaces (e.g "I'm a teapot")
        split_header = data.split(' ', maxsplit = 2)
        return cls(split_header[0], split_header[1], split_header[2])

    def to_dict(self):
        return {'Scheme': self.scheme, 'Code': self.code, 'Message': self.message}

#Pseudo-unit testing
if __name__ == '__main__':
    #Requests
    r = Request.from_args("POST", "http://www.google.com/index", "Hello World")
    assert r.get("Code") is None #Should not have a code field
    assert r.get("Method") == 'POST'
    assert r.get("User-Agent") == "Jonathan's cURL Copycat/1.0"

    #Test case-sensitivity
    r = Request.from_args("pOsT", "http://127.0.0.1:8080", "bananananas")
    assert r.get("Method") == 'POST'

    #From a string
    r = Request.from_str("GET hehehe HTTP/1.1\r\nHost: dbrand\r\n\r\nrobots")
    assert r.body == 'robots'
    assert r.get("Method") == 'GET'
    assert r.get("Host") == 'dbrand'
    print(r)

    r = Request.from_bytes(b'GET /hehehe HTTP/1.1\r\n\r\n', 'utf-8')
    assert r.get("Method") == 'GET'

    r = Request.from_args("GET", "http://youtu.be/q=2151251251414")
    #No content-length associared with no body
    assert r.get("Content-Length") is None

    #Posts may not have a body, so don't enforce a content-length
    r = Request.from_args('POST', "totheserver")
    assert r.get("Content-Length") is None

    #Responses
    r = Response.from_str('HTTP/1.1 200 OK\r\nHost: Who knows lol\r\n\r\nHey Pal')
    assert r.get('Code') == '200'

    r = Response.from_bytes(b'HTTP/1.1 403 Forbidden\r\nHost: Who knows lol\r\n\r\n', 'utf-8')
    assert r.get('Code') == '403' and r.get('Message') == 'Forbidden'

    #A real response
    with open("google_teapot.txt", 'r') as file:
        r = Response.from_str(file.read())
        assert r.get("Code") == '418'
        #The remaining gets messed up as the file terminates lines with /n as opposed to /r/n
        #Hopefully a proper response from a request will preserve the expected formatting

    print("All tests passed!")