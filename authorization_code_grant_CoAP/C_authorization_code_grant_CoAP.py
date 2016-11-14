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

logging.basicConfig(level=logging.DEBUG)


class ClientRequestHandler(WSGIRequestHandler):
    """
    Request handler that enables formatting of the log messages on the console.

    This handler is used by the client application.
    """
    def address_string(self):
        return "client app"


class OAuthRequestHandler(WSGIRequestHandler):
    """
    Request handler that enables formatting of the log messages on the console.

    This handler is used by the python-oauth2 application.
    """
    def address_string(self):
        return "python-oauth2"

class ClientApplication(object):
    """
    Very basic application that simulates calls to the API of the
    python-oauth2 app.
    """
    callback_url = "http://localhost:8081/callback"
    client_id = "abc"
    client_secret = "xyz"
    api_server_url = "http://localhost:8080"
    RS_url = "http://localhost:5683"

    # GRANT_TEMPLATE = """<html>
    #     <body>
    #         <div>Client Web</div>
    #         <div>
    #             <a href="/request_auth_token">GRANT</a>
    #         </div>
    #     </body>
    # </html>"""

    LOGIN_TEMPLATE = """<html>
        <body>
            <h1>Test Login</h1>
            <div style="color: red;">
                {failed_message}
            </div>
            <form method="POST" name="confirmation_form" action="/id_check">
                <div>
                    Username (foo): <input name="username" type="text" />
                </div>
                <div>
                    Password (bar): <input name="password" type="password" />
                </div>
                <div>
                    <input type="submit" value="submit" />
                </div>
            </form>
        </body>
    </html>"""

    SERVER_ERROR_TEMPLATE = """<html>
                <body>
                    <h1>OAuth2 server responded with an error</h1>
                    Error type: {error_type}
                    Error description: {error_description}
                </body>
            </html>"""

    AUTH_TEMPLATE = """<html>
                <body>
                    <div>Auth token: {auth_token}</div>
                </body>
                <div>
                    <a href="/request_access_token">request_access_token</a>
                </div>
            </html>"""

    TOKEN_TEMPLATE = """<html>
                <body>
                    <div>Access token: {access_token}</div>
                </body>
                <div>
                    <a href="/reset">reset</a>
                </div>
                <div>
                    <a href="/resource">resource request</a>
                </div>
            </html>"""
    DEFAULT_TEMPLATE = """<html>
                <body>
                    <div>grant_request</div>
                </body>
                <div>
                    <a href="/id_check">Login to the athorization server</a>
                </div>
            </html>"""

    RESOURCE_TEMPLATE = """<html>
                <body>
                    <div>Resource: {payload}</div>
                    <div><a href="/resource">resource request</a></div>
                </body>
            </html>"""

    def __init__(self):
        # self.authenticate_request = False  #It will change in the future.
        self.access_token = None
        self.auth_token = None
        self.refresh_token = {}
        self.scope = None
        self.token_type = ""

        self.path = "coap://127.0.0.1:5683/basic"
        self.host, self.port, self.path = parse_uri(self.path)
        self.payload = "test"

        self.host = socket.gethostbyname(self.host)
        self.client = HelperClient(server=(self.host, self.port))

    def __call__(self, env, start_response):

        # print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
        # print env["PATH_INFO"]
        # print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"

        if env["PATH_INFO"] == "/request_auth_token":
            status, body, headers = self._request_auth_token(env)

        elif env["PATH_INFO"] == "/callback":
            status, body, headers = self._read_auth(env)

        elif env["PATH_INFO"] == "/id_check":
            status, body, headers = self._id_check(env)

        elif env["PATH_INFO"] == "/":
            status, body, headers = self._grant_request()

        elif env["PATH_INFO"] == "/request_access_token":
            status, body, headers = self._request_access_token(env)

        elif env["PATH_INFO"] == "/reset":
            status, body, headers = self._reset(env)

        elif env["PATH_INFO"] == "/resource":
            status, body, headers = self._request_resource(env)

        else:
            status = "301 Moved"
            body = ""
            headers = {"Location": "/"}

        start_response(status,
                       [(header, val) for header,val in headers.iteritems()])
        return body

    def _request_auth_token(self, env):
        print("Requesting authorization token...")


        auth_endpoint = self.api_server_url + "/authorize"
        print"1"
        query = urllib.urlencode({"client_id": "abc",
                                  "redirect_uri": self.callback_url,
                                  "response_type": "code"})
        # query = urllib.urlencode({"response_type": "code"})
        print"2"
        location = "%s?%s" % (auth_endpoint, query)
        print "3"
        return "302 Found", "", {"Location": location}

    def _read_auth(self, env):
        if self.auth_token is None and self.access_token is None:
            print("Receiving authorization token...")

            query_params = urlparse.parse_qs(env["QUERY_STRING"])
            if "error" in query_params:
                print"%%%"
                print"%%%"
                print"%%%"
                location = "/app?error=" + query_params["error"][0]

                return "302 Found", "", {"Location": location}

            print query_params
            self.auth_token = query_params["code"][0]

            print query_params["code"][0]
            print self.auth_token
            print("Received temporary authorization token '%s'" % (self.auth_token,))


            return ("200 OK",
                    self.AUTH_TEMPLATE.format(
                        auth_token=self.auth_token),
                    {"Content-Type": "text/html"})

        elif self.auth_token is not None and self.access_token is not None:
            print"((("
            print"((("
            print"((("
            return ("200 OK",
                    self.TOKEN_TEMPLATE.format(
                        access_token=self.access_token),
                    {"Content-Type": "text/html"})


    def _grant_request(self):
        content = self.DEFAULT_TEMPLATE.format()
        return "200 OK", content, {"Content-Type": "text/html"}

    def _request_access_token(self, env):
        print("Requesting access token...")

        query_params = urlparse.parse_qs(env["QUERY_STRING"])
        print query_params
        post_params = {"client_id": self.client_id,
                       "client_secret": self.client_secret,
                       "code": self.auth_token,
                       "grant_type": "authorization_code",
                       "redirect_uri": self.callback_url}
        token_endpoint = self.api_server_url + "/token"

        result = urllib.urlopen(token_endpoint,
                                urllib.urlencode(post_params))
        content = ""
        for line in result:
            print line
            content += line

        result = json.loads(content)
        print "ddd"
        print "ddd"
        print "ddd"
        print "ddd"
        print "ddd"
        print "ddd"
        print "ddd"
        print "ddd"
        for i in result:
            print i+" : ",
            print result[i]
            print type(result[i])
        self.access_token = result["access_token"]
        self.token_type = result["token_type"]
        self.refresh_token = result["refresh_token"]
        self.scope = result["scope"]

        confirmation = "Received access token '%s' of type '%s'" % (self.access_token, self.token_type)
        print(confirmation)
        return "302 Found", "", {"Location": "/callback"}

    def _reset(self, env):
        self.access_token = None
        self.auth_token = None
        self.token_type = ""

    def _request_resource(self, env):
        # print("Requesting resource...")
        #
        # post_params = {"token": self.access_token,
        #                "token_type": self.token_type}
        #
        # resource_endpoint = self.RS_url + "/resource"
        #
        # result = urllib.urlopen(resource_endpoint,
        #                         urllib.urlencode(post_params))
        # content = ""
        # for line in result:
        #     content += line
        #
        # result = json.loads(content)
        #
        #
        # return ("200 OK",
        #         self.RESOURCE_TEMPLATE.format(
        #             active=result["active"]),
        #         {"Content-Type": "text/html"})

        # path = "coap://127.0.0.1:5683/basic"
        # host, port, path = parse_uri(path)
        # payload = "test"
        #
        # host = socket.gethostbyname(host)
        # client = HelperClient(server=(host, port))

        # response = client.get(path)
        # app_server.r
        print "????????????"
        print "????????????"
        print "????????????"
        print "????????????"
        print "????????????"
        print "????????????"
        print "????????????"
        print "????????????"
        print "????????????"
        print "????????????"
        print "????????????"
        print self.access_token
        response = self.client.get_with_bearer(self.path, str(self.access_token))

        # print response.active
        print response.pretty_print()


        #token is expired
        if response.payload == "invalid_token" :
            print "!!!!!!!!!!!!!!!!!!"
            print "!!!!!!!!!!!!!!!!!!"
            print "!!!!!!!!!!!!!!!!!!"
            print "!!!!!!!!!!!!!!!!!!"
            print "!!!!!!!!!!!!!!!!!!"
            print "!!!!!!!!!!!!!!!!!!"
            print "!!!!!!!!!!!!!!!!!!"
            print "!!!!!!!!!!!!!!!!!!"
            print self.scope
            print type(self.scope)
            print str(self.scope)
            print str(self.scope) == "basic long"
            post_params = {"grant_type": "refresh_token",
                           "refresh_token": self.refresh_token,
                           "client_id": "abc",
                           "client_secret": "xyz",
                           "scope": str(self.scope)}
            # ,"data": (None,"goslim")}
            token_endpoint = self.api_server_url + "/token"
            refresh_token_result = urllib.urlopen(token_endpoint,
                                                  urllib.urlencode(post_params))

            content = ""
            for line in refresh_token_result:
                print line
                content += line
            result = json.loads(content)

            self.access_token = result["access_token"]
            self.token_type = result["token_type"]
            self.refresh_token = result["refresh_token"]
            # self.scope = result["scope"]
            response = self.client.get_with_bearer(self.path, str(self.access_token))

        # client.stop()

        return ("200 OK",
                self.RESOURCE_TEMPLATE.format(
                    payload=response.payload),
                {"Content-Type": "text/html"})

    def _id_check(self, env):
        auth_endpoint = self.api_server_url + "/id_check"
        query = urllib.urlencode({"client_id": "abc",
                                  "redirect_uri": self.callback_url,
                                  "response_type": "code"})

        # query = urllib.urlencode({"response_type": "code"})

        location = "%s?%s" % (auth_endpoint, query)

        return "302 Found", "", {"Location": location}

def run_app_server():
    app = ClientApplication()

    try:
        httpd = make_server('', 8081, app, handler_class=ClientRequestHandler)

        print("Starting Client app on http://localhost:8081/...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

def main():
    app_server = Process(target=run_app_server)
    app_server.start()
    print("Access http://localhost:8081/app in your browser")

    def sigint_handler(signal, frame):
        print("Terminating servers...")
        app_server.terminate()
        app_server.join()

    signal.signal(signal.SIGINT, sigint_handler)

if __name__ == "__main__":
    main()
