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
from oauth2.grant import AuthorizationCodeGrant, RefreshToken

# # from oauth2.store.memory import ClientStore, TokenStore
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

    # < input
    # type = "text"
    # id = "url"
    # value = {url} >

    CONFIRMATION_TEMPLATE = """
<html>
        <body>
            <h1>Test Login</h1>
            <form method="POST" name="confirmation_form" action="/id_check">
                <div>
                    Username : <input name="username" type="text" />
                </div>
                <div>
                    Password : <input name="password" type="password" />
                </div>
                <div>
                    <input type="hidden" name="url" value={url}>
                </div>
                <div>
                    <input type="submit" value="submit" />
                </div>

            </form>
        </body>
</html>
    """

    def render_auth_page(self, request, response, environ, scopes, client):
        url = request.path + "?" + request.query_string
        print request.get_param("redirect_uri")
        print url
        response.body = self.CONFIRMATION_TEMPLATE.format(url=url)

        return response

    def authenticate(self, request, environ, scopes, client):
        if request.method == "GET":
            if request.get_param("confirm") == "1":
                scope = []

                if request.get_param('user_id') != None:
                    return (None, request.get_param('user_id'))
                # print tuple(scope)

                # print request.body
                return
        raise UserNotAuthenticated

    def user_has_denied_access(self, request):

        if request.method == "GET":
            if request.get_param("confirm") == "0":
                return True
        return False


def run_auth_server():
    try:
        client = MongoClient('localhost', 27017)

        db = client.test_database

        client_store = ClientStore(collection=db["clients"])

        token_store = AccessTokenStore(collection=db["access_tokens"])
        code_store = AuthCodeStore(collection=db["auth_codes"])

        provider = Provider(
            access_token_store=token_store,
            auth_code_store=code_store,
            client_store=client_store,
            token_generator=Uuid4())
        provider.add_grant(
            AuthorizationCodeGrant(site_adapter=TestSiteAdapter(), scopes=["basic", "big", "long"],
                                   unique_token=True,
                                   expires_in=20
                                   )
        )

        provider.add_grant(
            RefreshToken(scopes=["basic", "big", "long"], expires_in=2592000, reissue_refresh_tokens=True)
        )

        app = Application(provider=provider)

        httpd = make_server('', 8080, app, handler_class=OAuthRequestHandler)

        print("Starting OAuth2 server on http://localhost:8080/...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

def main():
    auth_server = Process(target=run_auth_server)
    auth_server.start()
    # app_server = Process(target=run_app_server)
    # app_server.start()
    print("Access http://localhost:8081/app in your browser")

    def sigint_handler(signal, frame):
        print("Terminating servers...")
        auth_server.terminate()
        auth_server.join()

    signal.signal(signal.SIGINT, sigint_handler)

if __name__ == "__main__":
    main()
