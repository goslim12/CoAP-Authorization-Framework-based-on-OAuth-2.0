import logging
import os
import sys
import urllib
import urlparse
import json
import signal

from multiprocessing.process import Process
from wsgiref.simple_server import make_server, WSGIRequestHandler
import urllib2
import json

sys.path.insert(0, os.path.abspath(os.path.realpath(__file__) + '/../../python-oauth2'))
sys.path.insert(0, os.path.abspath(os.path.realpath(__file__) + '/../../CoAPthon'))

from oauth2 import Provider
from oauth2.error import UserNotAuthenticated
from oauth2.store.memory import ClientStore, TokenStore
from oauth2.tokengenerator import Uuid4
from oauth2.web import AuthorizationCodeGrantSiteAdapter
from oauth2.web.wsgi import Application
from oauth2.grant import AuthorizationCodeGrant
from oauth2.compatibility import parse_qs, urlencode
from oauth2 import Provider
from oauth2.error import UserNotAuthenticated
from oauth2.store.memory import ClientStore, TokenStore
from oauth2.tokengenerator import Uuid4
from oauth2.web import ResourceOwnerGrantSiteAdapter
from oauth2.web.wsgi import Application
from oauth2.web.wsgi import Request
from oauth2.grant import ResourceOwnerGrant

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

    # INTROSPECT_TEMPLATE = """<html>
    #             <body>
    #                 <div>active: {active}</div>
    #             </body>
    #         </html>"""
    def __init__(self):
        # self.authenticate_request = False  #It will change in the future.
        self.access_token = None
        self.auth_token = None
        self.token_type = ""
        self.active = ""

    def __call__(self, env, start_response):

        # print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
        # print env["PATH_INFO"]
        # print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"

        # if env["PATH_INFO"] == "/introspect":
        #     status, body, headers = self.introspection(env)
        # el
        if env["PATH_INFO"] == "/resource":
            status, body, headers = self.receive_request_resource(env)

        start_response(status,
                       [(header, val) for header,val in headers.iteritems()])
        return body

    def receive_request_resource(self, env):

        # result = json.loads(content)
        # self.access_token = result["access_token"]
        # self.token_type = result["token_type"]

        # request = Request(env)
        #
        # self.access_token = request.post_param("token")
        # print "````````````````````````````"
        # print self.access_token
        # print "````````````````````````````"
        # self.token_type = request.post_param("token_type")
        # print "````````````````````````````"
        # print self.token_type
        # print "````````````````````````````"
        # post_params = {"token": self.access_token,
        #                           "token_type": self.token_type}
        #
        # # result = urllib.urlopen(self.api_server_url+"/introspect",
        # #                         urllib.urlencode(post_params))
        #
        # # query = urllib.urlencode({"token": self.access_token,
        # #                           "token_type": self.token_type})
        # # result = urllib2.urlopen(self.api_server_url+"/introspect", query)
        # result = urllib.urlopen(self.api_server_url + "/introspect", urllib.urlencode(post_params))
        # return urllib.urlopen(self.api_server_url+"/introspect", urllib.urlencode(post_params))
        #return result
        # content = ""
        # for line in result:
        #     content += line
        #
        # self.active = result["active"]


        content = ""
        for line in result:
            content += line

        result = json.loads(content) #json decoding

        #json.dumps(result) json encoding(python object -> JSon string)
        print result
        #print result.headers
        # result.body.encode('utf-8')
        # json_success_response(data=introspect_data, response=response)
        # json.dumps(result.read()).encode('utf-8')
        return "200 OK", json.dumps(result), {"Content-Type": "text/html"}
        # return "200 OK", result.body.encode('utf-8'), {}

def run_app_server():
    app = ClientApplication()

    try:
        httpd = make_server('', 1111, app, handler_class=ClientRequestHandler)

        print("Starting Client app on http://localhost:1111/...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

def main():

    app_server = Process(target=run_app_server)
    app_server.start()
    print("Access http://localhost:1111/app in your browser")

    def sigint_handler(signal, frame):
        print("Terminating servers...")
        app_server.terminate()
        app_server.join()

    signal.signal(signal.SIGINT, sigint_handler)

if __name__ == "__main__":
    main()
