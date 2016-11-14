import logging
import os
import sys
import urllib
import urlparse
import json
import signal

from multiprocessing.process import Process
from wsgiref.simple_server import make_server, WSGIRequestHandler

sys.path.insert(0, os.path.abspath(os.path.realpath(__file__) + '/../../../'))

from oauth2 import Provider
from oauth2.error import UserNotAuthenticated

from oauth2.tokengenerator import Uuid4
from oauth2.web import AuthorizationCodeGrantSiteAdapter
from oauth2.web.wsgi import Application
from oauth2.grant import AuthorizationCodeGrant, RefreshToken

# from oauth2.store.memory import ClientStore, TokenStore
from pymongo import MongoClient
from oauth2.store.mongodb import MongodbStore, AccessTokenStore, AuthCodeStore, ClientStore

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


class TestSiteAdapter(AuthorizationCodeGrantSiteAdapter):
    """
    This adapter renders a confirmation page so the user can confirm the auth
    request.
    """

    CONFIRMATION_TEMPLATE = """
<html>
    <body>
        <p>
            <a href="{url}&confirm=1">confirm</a>
        </p>
        <p>
            <a href="{url}&confirm=0">deny</a>
        </p>
    </body>
</html>
    """


    def render_auth_page(self, request, response, environ, scopes, client):
        url = request.path + "?" + request.query_string
        response.body = self.CONFIRMATION_TEMPLATE.format(url=url)

        return response

    def authenticate(self, request, environ, scopes, client):
        if request.method == "GET":
            if request.get_param("confirm") == "1":
                return (None, "goslim")
        raise UserNotAuthenticated

    def user_has_denied_access(self, request):
        if request.method == "GET":
            if request.get_param("confirm") == "0":
                return True
        return False


class ClientApplication(object):
    """
    Very basic application that simulates calls to the API of the
    python-oauth2 app.
    """
    #access_token_data = {}
    callback_url = "http://localhost:8081/callback"
    client_id = "abc"
    client_secret = "xyz"
    api_server_url = "http://localhost:8080"
    TEMP_TEMPLATE = """<html>
                <body>
                    <div>Access token: {access_token}</div>
                </body>
                <div>
                    <a href="/refresh">refresh</a>
                </div>
            </html>"""
    def __init__(self):
        self.access_token = None
        self.auth_token = None
        self.token_type = ""
        self.access_token_data = {}
    def __call__(self, env, start_response):
        if env["PATH_INFO"] == "/app":
            status, body, headers = self._serve_application(env)
        elif env["PATH_INFO"] == "/callback":
            status, body, headers = self._read_auth_token(env)
        elif env["PATH_INFO"] == "/refresh":
            status, body, headers = self._request_refresh(env)

        else:
            status = "301 Moved"
            body = ""
            headers = {"Location": "/app"}

        start_response(status,
                       [(header, val) for header,val in headers.iteritems()])
        return body

    def _request_access_token(self):
        print("Requesting access token...")

        post_params = {"client_id": self.client_id,
                       "client_secret": self.client_secret,
                       "code": self.auth_token,
                       "grant_type": "authorization_code",
                       "redirect_uri": self.callback_url,
                       "scope": "test"}

        token_endpoint = self.api_server_url + "/token"

        result = urllib.urlopen(token_endpoint,
                                urllib.urlencode(post_params))
        content = ""
        print "???????????"
        print "???????????"
        print "???????????"
        print "???????????"
        print type(result)
        for line in result:
            print type(line)
            print line
            content += line

        result = json.loads(content)
        self.access_token = result["access_token"]
        self.access_token_data["refresh_token"] = result["refresh_token"]
        self.token_type = result["token_type"]

        confirmation = "Received access token '%s' of type '%s'" % (self.access_token, self.token_type)
        print(confirmation)
        return "302 Found", "", {"Location": "/app"}

    def _read_auth_token(self, env):
        print("Receiving authorization token...")

        query_params = urlparse.parse_qs(env["QUERY_STRING"])

        if "error" in query_params:
            location = "/app?error=" + query_params["error"][0]
            return "302 Found", "", {"Location": location}

        self.auth_token = query_params["code"][0]

        print("Received temporary authorization token '%s'" % (self.auth_token,))

        return "302 Found", "", {"Location": "/app"}

    def _request_auth_token(self):
        print("Requesting authorization token...")

        auth_endpoint = self.api_server_url + "/authorize"
        query = urllib.urlencode({"client_id": "abc",
                                  "redirect_uri": self.callback_url,
                                  "response_type": "code",
                                  "scope": "test test2"})

        location = "%s?%s" % (auth_endpoint, query)

        return "302 Found", "", {"Location": location}

    def _serve_application(self, env):
        query_params = urlparse.parse_qs(env["QUERY_STRING"])

        if ("error" in query_params
                and query_params["error"][0] == "access_denied"):
            return "200 OK", "User has denied access", {}

        if self.access_token is None:
            if self.auth_token is None:
                return self._request_auth_token()
            else:
                return self._request_access_token()
        else:
            confirmation = "Current access token '%s' of type '%s'" % (self.access_token, self.token_type)

            # return "200 OK", str(confirmation), {}
            #
            # return response

            return ("200 OK",
                    self.TEMP_TEMPLATE.format(
                        access_token=self.access_token),
                    {"Content-Type": "text/html"})

    def _request_refresh(self,env):
        print("Requesting refresh token...")
        print self.access_token_data["refresh_token"]
        post_params = {"grant_type": "refresh_token",
                       "refresh_token": self.access_token_data["refresh_token"],
                       "client_id": "abc",
                       "client_secret": "xyz",
                       "scope": "test test2"}
            #,"data": (None,"goslim")}
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
        self.access_token_data["refresh_token"] = result["refresh_token"]

        return ("200 OK",
                self.TEMP_TEMPLATE.format(
                    access_token=self.access_token),
                {"Content-Type": "text/html"})



def run_app_server():
    app = ClientApplication()

    try:
        httpd = make_server('', 8081, app, handler_class=ClientRequestHandler)

        print("Starting Client app on http://localhost:8081/...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


def run_auth_server():
    try:
        client = MongoClient('localhost', 27017)

        db = client.test_database

        client_store = ClientStore(collection=db["clients"])

        # memory
        # client_store = ClientStore()
        # client_store.add_client(client_id="abc", client_secret="xyz",
        #                         redirect_uris=["http://localhost:8081/callback"])
        #
        # token_store = TokenStore()

        token_store = AccessTokenStore(collection=db["access_tokens"])
        code_store = AuthCodeStore(collection=db["auth_codes"])

        provider = Provider(
            access_token_store=token_store,
            auth_code_store=code_store,
            client_store=client_store,
            token_generator=Uuid4())
        provider.add_grant(
            AuthorizationCodeGrant(site_adapter=TestSiteAdapter(), scopes=["test", "test2"], unique_token=True,
                                   expires_in=1)
        )
        # auth_controller.add_grant_type(ResourceOwnerGrant(tokens_expire=600))
        provider.add_grant(
            RefreshToken(scopes=["test", "test2"], expires_in=2592000, reissue_refresh_tokens=True)
        )
        # auth_controller.add_grant_type(RefreshToken(tokens_expire=1200))
        app = Application(provider=provider)

        httpd = make_server('', 8080, app, handler_class=OAuthRequestHandler)

        print("Starting OAuth2 server on http://localhost:8080/...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


def main():
    auth_server = Process(target=run_auth_server)
    auth_server.start()
    app_server = Process(target=run_app_server)
    app_server.start()
    print("Access http://localhost:8081/app in your browser")

    def sigint_handler(signal, frame):
        print("Terminating servers...")
        auth_server.terminate()
        auth_server.join()
        app_server.terminate()
        app_server.join()

    signal.signal(signal.SIGINT, sigint_handler)

if __name__ == "__main__":
    main()
