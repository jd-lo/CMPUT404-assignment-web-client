from abc import ABC, abstractmethod

class Header(ABC):
    @abstractmethod
    def from_str(cls, data: str):
        '''Constructs a header object from its string representation.'''
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        '''Returns field(s) and values as dictionary.'''
        pass
    
    #Doesn't consider children as implementing this when abstract
    @classmethod
    def __str__(cls):
        raise NotImplementedError

class StdHeader(Header):
    @classmethod
    def from_str(cls, data: str):
        key, value = data.split(': ', maxsplit = 1)
        return cls(key, value)

    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value

    def to_dict(self) -> dict:
        return {self.field: self.value}

    def __str__(self):
        return f'{self.field}: {self.value}\r\n'

class IntlReqHeader(Header):
    @classmethod
    def from_str(cls, data: str):
        method, path, scheme = data.split(' ')
        return cls(method, path, scheme)

    def __init__(self, method: str, path: str, scheme: str):
        self.method = method.upper()
        self.path = path
        self.scheme = scheme

    def to_dict(self) -> dict:
        return {"Method": self.method, "Path": self.path, "Scheme": self.scheme}

    def __str__(self):
        return f'{self.method} {self.path} {self.scheme}\r\n'

class IntlResHeader(Header):
    @classmethod
    def from_str(cls, data: str):
        #Accomodate for code messages with multiple words (e.g Bad Request)
        scheme, code, response = data.split(' ', maxsplit = 2)
        return cls(scheme, code, response)

    def __init__(self, scheme: str, code: str, response: str):
        self.scheme = scheme
        self.code = code
        self.response = response

    def to_dict(self) -> dict:
        return {"Scheme": self.scheme, "Code": self.code, "Response": self.response}

    def __str__(self):
        return f'{self.scheme} {self.code} {self.response}\r\n'