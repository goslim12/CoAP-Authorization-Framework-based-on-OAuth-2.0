#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Classes for handling a HTTP request/response flow.

.. versionchanged:: 1.0.0
   Moved from package ``oauth2.web`` to ``oauth2.web.wsgi``.
"""

from oauth2.compatibility import parse_qs
from oauth2.web import Response
from oauth2.error import UserNotAuthenticated
import pymongo
import urllib

class Request(object):
    """
    Contains data of the current HTTP request.
    """
    def __init__(self, env):
        """
        :param env: Wsgi environment
        """
        self.method = env["REQUEST_METHOD"]
        self.query_params = {}
        self.query_string = env["QUERY_STRING"]
        self.path = env["PATH_INFO"]
        self.post_params = {}
        self.env_raw = env

        for param, value in parse_qs(env["QUERY_STRING"]).items():
            self.query_params[param] = value[0]

        if (self.method == "POST"
            and env["CONTENT_TYPE"] == "application/x-www-form-urlencoded"):
            self.post_params = {}
            content = env['wsgi.input'].read(int(env['CONTENT_LENGTH']))
            post_params = parse_qs(content)

            for param, value in post_params.items():
                decoded_param = param.decode('utf-8')
                decoded_value = value[0].decode('utf-8')
                self.post_params[decoded_param] = decoded_value

    def get_param(self, name, default=None):
        """
        Returns a param of a GET request identified by its name.
        """
        try:
            return self.query_params[name]
        except KeyError:
            return default

    def post_param(self, name, default=None):
        """
        Returns a param of a POST request identified by its name.
        """
        try:
            return self.post_params[name]
        except KeyError:
            return default

    def header(self, name, default=None):
        """
        Returns the value of the HTTP header identified by `name`.
        """
        wsgi_header = "HTTP_{0}".format(name.upper())

        try:
            return self.env_raw[wsgi_header]
        except KeyError:
            return default


class Application(object):
    """
    Implements WSGI.

    .. versionchanged:: 1.0.0
       Renamed from ``Server`` to ``Application``.
    """
    HTTP_CODES = {200: "200 OK",
                  301: "301 Moved Permanently",
                  302: "302 Found",
                  400: "400 Bad Request",
                  401: "401 Unauthorized",
                  404: "404 Not Found"}

    SUCCESS_TEMPLATE = """
<html>
    <body>
    <form method="GET" name="confirmation_form" action="/authorize">
        <div>
            <input type="hidden" name="redirect_uri" value={redirect_uri}>
            <input type="hidden" name="response_type" value={response_type}>
            <input type="hidden" name="client_id" value={client_id}>

            <input type="checkbox" name="chk_info1" value="basic">basic
            <input type="checkbox" name="chk_info2" value="Long">Long
            <input type="checkbox" name="chk_info3" value="Big">Big
            <input type="hidden" name="confirm" value=1>
        </div>
        <div>
            <input type="submit" value="submit" />
        </div>
    </body>
</html>
    """
    FAILED_TEMPLATE = """
<html>
    <body>
        <div style="color: red;">
            Login failed
        </div>
        <p>
            <a href="/id_check?{url}">Login again</a>
        </p>
    </body>
</html>
    """
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
                    <input type="hidden" name="url" value={url}>
                    <div>
                        <input type="submit" value="submit" />
                    </div>

                </form>
            </body>
    </html>
        """
    # SUCCESS_TEMPLATE2 = """
    # <html>
    #     <body>
    #     <form method="GET" name="confirmation_form" action="/authorize">
    #         <div>
    #             <input type="hidden" name="redirect_uri" value={redirect_uri}>
    #             <input type="hidden" name="response_type" value={response_type}>
    #             <input type="hidden" name="client_id" value={client_id}>
    #             <input type="hidden" name="confirm" value=1>
    #             <input type="hidden" name="user_id" value={username}>
    #             <div>
    #             <input type="checkbox" name="Basic" value="Basic">Basic
    #             <input type="checkbox" name="Long" value="Long">Long
    #             <input type="checkbox" name="Big" value="Big">Big
    #             </div>
    #         </div>
    #         <div>
    #             <input type="submit" value="submit" />
    #         </div>
    #     </body>
    # </html>
    #     """

    SUCCESS_TEMPLATE2 = """
    <html>
        <body>
        <form method="GET" name="confirmation_form" action="/authorize">
            <div>
                <input type="hidden" name="redirect_uri" value={redirect_uri}>
                <input type="hidden" name="response_type" value={response_type}>
                <input type="hidden" name="client_id" value={client_id}>
                <input type="hidden" name="confirm" value=1>
                <input type="hidden" name="user_id" value={username}>
                <div>
                resource : basic, long, big<br>
                Scope setting: <input name="scope" type="text" /><br>
                ex) input: basic long
            </div>
            </div>
            <div>
                <input type="submit" value="submit" />
            </div>
        </body>
    </html>
        """
# """
#                 <input type="checkbox" name="scope" value="basic">basic
#                 <input type="checkbox" name="scope" value="Long">Long
#                 <input type="checkbox" name="scope" value="Big">Big"""
    def __init__(self, provider, authorize_uri="/authorize", env_vars=None,
                 request_class=Request, token_uri="/token", id_uri="/id_check"):
        self.authorize_uri = authorize_uri
        self.env_vars = env_vars
        self.request_class = request_class
        self.provider = provider
        self.token_uri = token_uri
        self.id_path = id_uri
        self.provider.authorize_path = authorize_uri
        self.provider.token_path = token_uri
        self.user = {}
    def __call__(self, env, start_response):
        environ = {}

        if (env["PATH_INFO"] != self.authorize_uri
            and env["PATH_INFO"] != self.token_uri and env["PATH_INFO"] != self.id_path):
            start_response("404 Not Found",
                           [('Content-type', 'text/html')])
            return ["Not Found"]

        # if(env["PATH_INFO"] == self.id_uri):
        #     return "200 OK", self.LOGIN_TEMPLATE.format(), {"Content-Type": "text/html"}
        # else:
        request = self.request_class(env)

        if(env["PATH_INFO"] == self.id_path):
            response = Response()
            try:
                username = request.post_params['username']
                password = request.post_params["password"]

            except KeyError:
                # if (request.get_param("client_id") != None and
                #         request.get_param("redirect_uri") != None and
                #         request.get_param("response_type")) != None:
                    # self.client_request["client_id"] = request.get_param("client_id")
                    # self.client_request["redirect_uri"] = request.get_param("redirect_uri")
                    # self.client_request["response_type"] = request.get_param("response_type")
                    # if request.get_param("scope") != None:
                url = request.query_string
                        # print url
                    # else:

                # print self.client_request
                response.body = self.CONFIRMATION_TEMPLATE.format(url=url)

                start_response(self.HTTP_CODES[response.status_code],
                               list(response.headers.items()))

                return response.body

            db = pymongo.MongoClient('localhost', 27017).test_database
            url = request.post_params["url"]

            if db["user"].find_one({"username": username, "password": (hash(password))}) is not None:
                self.user[username] = True

                information = request.post_params['url']
                information = information.split("&")

                for i in range(len(information)):
                    if information[i].split("=")[0] == "redirect_uri":
                        redirect_uri = information[i].split("=")[1]
                    elif information[i].split("=")[0] == "response_type":
                        response_type = information[i].split("=")[1]
                    else:
                        client_id = information[i].split("=")[1]
                username = request.post_params['username']
                redirect_uri = urllib.unquote(redirect_uri)
                # response.body = self.SUCCESS_TEMPLATE.format(redirect_uri=redirect_uri,
                #                                              response_type=response_type,
                #                                              client_id=client_id)
                response.body = self.SUCCESS_TEMPLATE2.format(redirect_uri=redirect_uri,
                                                              response_type = response_type,
                                                              client_id = client_id,
                                                              username = username)
                start_response(self.HTTP_CODES[response.status_code],
                               list(response.headers.items()))
                return response.body

            else:
                response.body = self.FAILED_TEMPLATE.format(url=url)

                start_response(self.HTTP_CODES[response.status_code],
                               list(response.headers.items()))

            return response.body

        else:
            # if (request.get_param("response_type") == "code" and \
            #                 self.user[request.get_param("user_id")] == True) or \
            #                 request.get_param("response_type") != "code":
            #     if request.get_param("user_id") in self.user:
            #         self.user["user"] = False
                    # scope ="scope="
                    # if request.get_param("Basic") is not None:
                    #     scope += request.get_param("Basic")
                    # if request.get_param("Long") is not None:
                    #     if scope != "scope=":
                    #         scope += " "
                    #     scope += request.get_param("Long")
                    # if request.get_param("Big") is not None:
                    #     if scope != "scope=":
                    #         scope += " "
                    #     scope += request.get_param("Big")


                if isinstance(self.env_vars, list):
                    for varname in self.env_vars:
                        if varname in env:
                            environ[varname] = env[varname]

                response = self.provider.dispatch(request, environ)


                print ">_<"
                print ">_<"
                print ">_<"
                print ">_<"
                print ">_<"
                print ">_<"
                print ">_<"
                print ">_<"
                for i in response.headers.items():
                    print i

                start_response(self.HTTP_CODES[response.status_code],
                               list(response.headers.items()))

                return [response.body.encode('utf-8')]
