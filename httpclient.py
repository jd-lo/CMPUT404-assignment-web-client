#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse as parse
from socketr import *

def help():
    print('''
    httpclient.py [GET/POST] [URL] [*Args(Optional)]
    
    Args is a list of values to POST, and URL is a proper url following an HTTP 1.1 scheme

    e.g) "... http://www.mysitehere.co.nz/ ..." is valid, but
         "... www.mysitehere.co.nz/" is not.

    It is possible (but not recommended by HTTP conventions) to post with no body and get with a body.
    ''')

class HTTPResponse(Response):
    def __init__(self, headers, body):
        super().__init__(headers, body)
        self.code = int(self.get('Code'))

class HTTPClient(object):
    def get_host_port(self, url: str):
        '''Returns a host, pair tuple'''

        split_url = url.split(':')
        host = split_url[0]
        try:
            port = int(split_url[1])
        except IndexError:
            port = 80 #Default per HTTP spec.
        return (host, port)

    def connect(self, host, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
        except:
            print(f'Connection to {host}:{port} could not be made.')
            self.close()
            sys.exit(1)
        return None

    def sendall(self, data):
        encoded_data = data.encode('utf-8')
        self.socket.sendall(encoded_data)
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self):
        buffer = bytearray()
        done = False
        while not done:
            part = self.socket.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        #Some bytes (i.e continuation, gzip) cannot be read with utf-8
        return buffer.decode('ISO-8859-1')

    def communicate_r(self, host, port, data: Request) -> HTTPResponse:
        '''Opens and requests on a socket, returns the response and closes socket.'''
        
        self.connect(host, port)
        self.sendall(str(data))
        response = HTTPResponse.from_str(self.recvall())
        self.close()
        return response

    def GET(self, url: str, args = None) -> HTTPResponse:
        request = Request.from_args("Get", url, args)
        host, port = self.get_host_port(request.get("Host"))
        response = self.communicate_r(host, port, request)

        return response

    def POST(self, url: str, args = None) -> HTTPResponse:
        request = Request.from_args("POST", url, args)
        host, port = self.get_host_port(request.get("Host"))
        response = self.communicate_r(host, port, request)

        return response

    def command(self, command: str, url: str, args: list):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)
    
if __name__ == "__main__":
    client = HTTPClient()
    #Expected input: name.py [Method] [URL] [*args]
    #clargs = sys.argv

    clargs = ['httpclient.py', 'GET', 'http://www.google.com/']

    try:
        #Don't count name.py as argument to not confuse user.
        if len(clargs) == 3:
            method, url = clargs[1:]
            args = None
        elif len(clargs == 4):
            method, url, *args = clargs[1:]
        else:
            raise Exception("Incorrect amount of arguments. Expected: 2 or 3")

        assert method.upper() in ("GET", "POST"), "Method must be either GET or POST"
        response = client.command(method, url, args)
        print(response)

    except Exception as e:
        print(e)
        help()
        sys.exit(1)
