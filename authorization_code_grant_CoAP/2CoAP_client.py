import logging
import os
import sys
import urllib
import urlparse
import json
import signal

from multiprocessing.process import Process
from wsgiref.simple_server import make_server, WSGIRequestHandler

sys.path.insert(0, os.path.abspath(os.path.realpath(__file__) + '/../../python-oauth2'))
sys.path.insert(0, os.path.abspath(os.path.realpath(__file__) + '/../../CoAPthon'))

from oauth2 import Provider
from oauth2.error import UserNotAuthenticated
from oauth2.store.memory import ClientStore, TokenStore
from oauth2.tokengenerator import Uuid4
from oauth2.web import AuthorizationCodeGrantSiteAdapter
from oauth2.web.wsgi import Application
from oauth2.grant import AuthorizationCodeGrant

from Queue import Queue
import getopt
import random
import sys
import threading
from coapthon import defines
from coapthon.client.coap import CoAP
from coapthon.client.helperclient import HelperClient
from coapthon.messages.message import Message
from coapthon.messages.request import Request
from coapthon.utils import parse_uri
import socket

def main():  # pragma: no cover
    # global client
    try:
        op = "GET"
        path = "coap://127.0.0.1:7662/bearer"
        host, port, path = parse_uri(path)
        payload = "test"

        host = socket.gethostbyname(host)
        client = HelperClient(server=(host, port))

        # response = client.post(path, payload)

        response = client.get_with_bearer(path,"ed1bedae-a186-4301-a15f-20e466db95e9")
        #response = client.get(path)

        # print type(response)

        # print "payload: "
        # print response.payload
        print response
        print response.pretty_print()
        client.stop()

        print response.active
    except KeyboardInterrupt:
        sys.exit()

if __name__ == '__main__':  # pragma: no cover
    main()
