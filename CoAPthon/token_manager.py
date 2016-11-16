from coapthon import defines

from coapthon.utils import parse_uri
import socket
from coapthon.client.helperclient import HelperClient
import pymongo

import logging
import threading
import time




def address_registry(Resource, request):

    try:
        for option in request.options:
            if option.number == defines.OptionRegistry.BEARER.number:
                if str(option.value) not in Resource.expired_token_list:
                  Resource.token_address[str(option.value)] = request.source

    except AttributeError:
        return

def store_token_information(Resource, request):
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

        for option in request.options:
            if option.number == defines.OptionRegistry.SCOPE.number:
                if token in Resource.introspection and token is not None:
                    if Resource.introspection[token] is not None:
                        for scope in Resource.introspection[token]["scopes"]:
                            if str(scope) == option.value:
                                valid_scope = True
                        if not valid_scope:
                            Resource.introspection[token] = 2

    except AttributeError:
        return


def compare_token(Resource):
    db_host = 'localhost'
    db_port = 27017
    db = pymongo.MongoClient(db_host, db_port).test_database
    try:

        for token in Resource.token_address:
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
    except AttributeError:
        return


