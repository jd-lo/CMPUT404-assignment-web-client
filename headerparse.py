from urllib.parse import urlparser
from config import mapping

class Request:
    def __init__(self):
        #Dynamically set these headers
        self.headers = []
        self.body = None

    def set_headers(self, method, url):
        #No support for adding your own headers.
        url = urlparser(url)

        self.headers.append(InitialHeader(method, url.path, url.scheme))
        self.headers.append(StandardHeader('Host', url.host))

        #Add content-type
        if method.upper() == 'POST':
            field, value = mapping['Content-Type'].items
            self.headers.append(StandardHeader('Content-Type', mapping['Content-Type']))

        #Adds the boilerplate headers based on config file
        for field, value in mapping.items():
            if field != 'Content-Type':
                self.headers.append(StandardHeader(field, value))

    def set_body(self, body):
        self.body = body

    def encode(self, charset: str):
        return bytearray(self.__str__, charset)

    def __str__(self):
        request_content = ""
        for header in self.headers:
            request_content += str(header)
        #Header delimiter
        request_content += '\r\n'
        
        if self.body:
            request_content += self.body

        return request_content

class Header:
    @classmethod
    def from_string(cls):
        '''Constructs a header object from its string representation.'''
        pass

    def encode(self, charset: str):
        '''Encodes the header as a string for a given character set.'''
        return bytearray(str(self), 'utf-8')

class StandardHeader(Header):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value

    @classmethod
    def from_string(cls, data: str):
        split_header = data.split(' ', maxsplit=1)
        return cls(split_header[0], split_header[1])

    def __str__(self):
        return f'{self.field}: {self.value}\r\n'

class InitialHeader(Header):
    def __init__(self, method: str, path: str, scheme: str):
        self.method = method
        self.path = path
        self.scheme = scheme 
    
    @classmethod
    def from_string(cls, data:str):
        split_header = data.split(' ')
        return cls(split_header[0], split_header[1], split_header[2])
        
    def __str__(self):
        #Follows a wonky format
        return f'{self.method.upper()} {self.path} {self.scheme.upper()}'