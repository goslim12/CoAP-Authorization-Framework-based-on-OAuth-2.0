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

#!/usr/bin/env python

import getopt

from coapthon.resources.resource import Resource
from coapthon.server.coap import CoAP
from exampleresources import BasicResource, Long, Separate, Storage, Big, voidResource, XMLResource, ETAGResource, Child, \
    MultipleEncodingResource, BEARERResource
from plugtest_resources import ObservableResource

__author__ = 'giacomo'


class CoAPServer(CoAP):
    def __init__(self, host, port, multicast=False):
        CoAP.__init__(self, (host, port), multicast)
        self.add_resource('basic/', BasicResource())
        self.add_resource('storage/', Storage())
        self.add_resource('separate/', Separate())
        self.add_resource('long/', Long())
        self.add_resource('big/', Big())
        self.add_resource('void/', voidResource())
        self.add_resource('xml/', XMLResource())
        self.add_resource('encoding/', MultipleEncodingResource())
        self.add_resource('etag/', ETAGResource())
        self.add_resource('child/', Child())
        self.add_resource('bearer/', BEARERResource(coap_server=self))
        # self.add_resource('bearer/', ObservableResource())

        print "CoAP Server start on " + host + ":" + str(port)
        print self.root.dump()


def usage():  # pragma: no cover
    print "coapserver.py -i <ip address> -p <port>"


def main(argv):  # pragma: no cover
    ip = "127.0.0.1"
    port = 7662
    try:
        opts, args = getopt.getopt(argv, "hi:p:", ["ip=", "port="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--ip"):
            ip = arg
        elif opt in ("-p", "--port"):
            port = int(arg)

    server = CoAPServer(ip, port)
    try:
        server.listen(10)
    except KeyboardInterrupt:
        print "Server Shutdown"
        server.close()
        print "Exiting..."


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])
