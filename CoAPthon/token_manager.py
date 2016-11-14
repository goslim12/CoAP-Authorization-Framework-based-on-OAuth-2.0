from coapthon import defines

from coapthon.utils import parse_uri
import socket
from coapthon.client.helperclient import HelperClient
import pymongo

import logging
import threading
import time




def address_registry(Resource, request):
    # print defines.OptionRegistry.URI_PATH.number in request.options
    a = ""
    db_host = 'localhost'
    db_port = 27017
    db = pymongo.MongoClient(db_host, db_port).test_database
    try:
        for option in request.options:
            if option.number == defines.OptionRegistry.BEARER.number:
                if str(option.value) not in Resource.expired_token_list:
                  Resource.token_address[str(option.value)] = request.source
                # a = str(option.value)
                # Resource.introspection[str(option.value)] = db["access_tokens"].find_one({"token": str(option.value)})
                # if temp != None:
                #      = temp
                # else:
                #     Resource.introspection[str(option.value)] = None

        # print Resource.introspection
    except AttributeError:
        return

def store_token_information(Resource, request):
    # print defines.OptionRegistry.URI_PATH.number in request.options
    a = ""
    db_host = 'localhost'
    db_port = 27017
    db = pymongo.MongoClient(db_host, db_port).test_database
    valid_scope = False
    token = None

    try:
        for option in request.options:
            if option.number == defines.OptionRegistry.BEARER.number:
                token = str(option.value)
                if db["access_tokens"].find_one({"token": str(option.value)}) is not None:
                    Resource.introspection[str(option.value)] = db["access_tokens"].find_one({"token": str(option.value)})
                # elif str(option.value) in Resource.introspection:
                #     Resource.introspection.pop(str(option.value))
                #     if str(option.value) in Resource.token_address:
                #         Resource.token_address.pop(str(option.value))
                # else:
                #     Resource.introspection[str(option.value)] = None

        for option in request.options:
            if option.number == defines.OptionRegistry.SCOPE.number:
                if token in Resource.introspection and token is not None:
                    if Resource.introspection[token] is not None:
                        for scope in Resource.introspection[token]["scopes"]:
                            if str(scope) == option.value:
                                valid_scope = True
                        if not valid_scope:
                            Resource.introspection[token] = 2

        # print Resource.token_information
    except AttributeError:
        return


def compare_token(Resource):
    # print defines.OptionRegistry.URI_PATH.number in request.options
    a = ""
    db_host = 'localhost'
    db_port = 27017
    db = pymongo.MongoClient(db_host, db_port).test_database
    temp = []
    # Resource.expired_token_list = []
    try:
        # print Resource.token_address

        for token in Resource.token_address:
            # temp = db["access_tokens"].find_one({"token": str(token)})
            print str(token)
            print Resource.introspection[str(token)]
            print "Resource.introspection[str(token)][expires_at]: "
            print Resource.introspection[str(token)]["expires_at"]
            if str(token) in Resource.introspection:
                if Resource.introspection[str(token)] != db["access_tokens"].find_one({"token": str(token)}):
                    Resource.observe_client_list.append(Resource.token_address[str(token)])
                    Resource.introspection[str(token)] = db["access_tokens"].find_one({"token": str(token)})
                elif Resource.introspection[str(token)]["expires_at"] < time.time():
                    if str(token) not in Resource.expired_token_list:
                        Resource.observe_client_list.append(Resource.token_address[str(token)])
                        Resource.expired_token_list.append(str(token))

                else:
                    print Resource.token_address[str(token)]

            # del Resource.introspection[i]
    except AttributeError:
        return


