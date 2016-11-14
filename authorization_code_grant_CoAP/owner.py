# -*- coding: utf-8 -*-

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
# from oauth2.store.memory import ClientStore, TokenStore
from oauth2.tokengenerator import Uuid4
from oauth2.web import AuthorizationCodeGrantSiteAdapter
from oauth2.web.wsgi import Application
from oauth2.grant import AuthorizationCodeGrant
from oauth2.store.mongodb import MongodbStore, AccessTokenStore, AuthCodeStore, ClientStore
from oauth2.datatype import AccessToken, AuthorizationCode, Client
from oauth2.error import AccessTokenNotFound, AuthCodeNotFound, \
    ClientNotFoundError
# from pymongo import MongoClient
from bson.objectid import ObjectId
import pymongo
import bz2
#
# client = pymongo.MongoClient('localhost', 27017)
#
# db = client.test_database
db = pymongo.MongoClient('localhost', 27017).test_database
# access_token_store = ClientStore(collection=db["clients"])
access_token_store = ClientStore(collection=db["user"])
password =hash("2415")
# print "ddddddddddddddddddddddd"
# print "ddddddddddddddddddddddd"
# print "ddddddddddddddddddddddd"
# print "ddddddddddddddddddddddd"
# print "ddddddddddddddddddddddd"
# print password

# client_id = db["user"].insert({
#             "username": "goslim",
#             "password": password,
#         })
# print db.collection_names()
# print db["clients"].find({"identifier": "abc"})

# print "client_id: "
# # print client_id
# print db["clients"].find_one({"_id": ObjectId('58039478956c20394251a614')})
#
# print db["clients"].remove({'_id': ObjectId("5804adeb956c2012ed3d4e89")})
# print db["access_tokens"].remove({"user_id": None})
# print db["access_tokens"].remove({"user_id": "goslim"})
# print db["user"].remove({"username": "goslim"})
# print "??????????????"
# print db["clients"].find({"identifier": "abc"}).count()
# for post in db["clients"].find({'_id': ObjectId("5804adeb956c2012ed3d4e89")}):
#     print post
#
# print "client"
# for post in db["clients"].find():
#     print post
#
# print "\naccess_tokens"
# for post in db["access_tokens"].find(sort=[("token",pymongo.DESCENDING)]):
#     print post

# print "\naccess_tokens"
# for post in db["access_tokens"].find():
#     print post

# print "\nuser"
# for post in db["user"].find({"password": (hash("2415"))}):
#     print post
#
# print "\nuser"
# for post in db["user"].find({"username": "goslim"}):
#     print post

# print db["user"].find_one({"username": "goslim"}, {"password": (hash("dfdfdf5"))})
# print db["user"].find_one({"username": "goslim", "password": (hash("2415"))})
# data = self.collection.find_one({"client_id": client_id,
#                                  "grant_type": grant_type,
#                                  "user_id": user_id},
#                                 sort=[("expires_at",
#                                        pymongo.DESCENDING)])
# print "\nauth_codes"
# for post in db["auth_codes"].find():
#     print post
#
# for post in db["access_tokens"].find({"token":"ed1bedae-a186-4301-a15f-20e466db95e9"}):
#     print type(post)
#
# for post in db["user"].find():
#     print post
# for post in db["access_tokens"].find():
#     print post
#
print db["access_tokens"].find_one({"token":"b03bade9-755a-4e84-9e3a-a2fce51436f3"})