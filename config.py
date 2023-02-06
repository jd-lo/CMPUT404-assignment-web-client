#This file is for setting the default settings (strings) of the headers, since custom header input isn't implemented.
#Based on specifications provided from: https://developer.mozilla.org/en-US/docs/Glossary/Request_header
mapping = {
    'Content-Type': 'application/x-www-form-urlencoded',                         #Only used for POST
    'Accept': 'text/html, application/xhtml+xml, application/xml, text/html',
    'Accept-Language': 'en, en-CA, en-US',
    'Connection': 'close',
    'User-Agent': "Jonathan's cURL Copycat/1.0",
    'Accept-Encoding': 'gzip',
    'Upgrade-Insecure-Requests': '0',                                           #No TLS allowed :>
}
          