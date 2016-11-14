import time
from coapthon import defines

from coapthon.resources.resource import Resource
from coapthon.utils import parse_uri
import socket
from coapthon.client.helperclient import HelperClient
import pymongo

import logging
import threading
import time
import token_manager

import datetime

logger = logging.getLogger(__name__)

__author__ = 'Giacomo Tanganelli'
__version__ = "2.0"


class BasicResource(Resource):
    def __init__(self, name="BasicResource", coap_server=None):
        super(BasicResource, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.num =0;
        self.payload = str(self.num)
        self.resource_type = "rt1"
        self.content_type = "text/plain"
        self.interface_type = "if1"
        self.Bearer = {}
        self.test ="18!!!!!!!!!!!!!"
        self.AS_path = "coap://127.0.0.1:7662/bearer"
        self.op = "GET"

    def cache_token(self, response):  # pragma: no cover
        print "Callback_observe"
        print "Callback_observe"
        print "Callback_observe"
        print "Callback_observe"
        print "Callback_observe"
        print "Callback_observe"
        print "Callback_observe"
        print "Callback_observe"
        print "Callback_observe"

        # print response

        print response.pretty_print()
        print response
        check = True
        # if response.active is True or response.error is None:
        if response.error is None:
                self.Bearer[str(response.bearer)] = str(response.active)

        if response.active is not None:
            print response.active == False
            print response.active == "False"
            if response.active == "False":

                host, port, path = parse_uri(self.AS_path)
                host = socket.gethostbyname(host)
                client = HelperClient(server=(host, port))
                client.cancel_observing(response, True)

        print self.Bearer
        # while check:
        #     pass
        #
        #     if response.active is True or response.error is None:
        #         self.Bearer[str(response.bearer)] = str(response.active)
        #     # else:
        #     #     break
        #     self.payload = str(response.bearer)
        #     if response.error == 0:
        #         self.payload = "invalid_request"
        #     if response.error == 1 or response.active is False:
        #         self.payload = "invalid_token"
        #     if response.error == 2:
        #         self.payload = "insufficient_scope"

    def render_GET(self, request):
        # for option in request.options:
        #     if option.number == defines.OptionRegistry.BEARER.number:
        # str(request.bearer
        self.num += 1
        self.payload = str(self.num)


        if str(request.bearer) in self.Bearer:
            if self.Bearer[str(request.bearer)] == str(True):
                # self.payload = str(self.Bearer[str(request.bearer)])
                # return self
                pass
            else:
                self.payload = "invalid_token"
                # self.payload = "invalid_token"
        else:
            host, port, path = parse_uri(self.AS_path)
            host = socket.gethostbyname(host)
            client = HelperClient(server=(host, port))
            # response = None
            # response = client.get(path)


            print "<!!!!>"
            print "<!!!!>"
            print "<!!!!>"
            print "<!!!!>"
            print "<!!!!>"
            print "<!!!!>"
            print "<!!!!>"
            print "<!!!!>"
            print "<!!!!>"
            print "<!!!!>"
            print "<!!!!>"
            print str(request.bearer)

            response = client.introspect(path, str(request.bearer), access_path="basic")
            client.introspect_observer(path, str(request.bearer), callback=self.cache_token, access_path="basic")
            # client.introspect_observer(path, str(request.bearer), access_path="basic")


            # for option in response.options:
            #     if option.number == defines.OptionRegistry.BEARER.number:
            #         self.Bearer[str(option.value)] = response.payload
            #
            # host = socket.gethostbyname(host)
            # client_2 = HelperClient(server=(host, port))
            # client_2.stop()
            #
            # if response.active is True or response.error is None:
            if response.error is None:
                    self.Bearer[str(request.bearer)] = str(response.active)
            # print "??"
            # print "??"
            # print "??"
            # print "??"
            # print "??"
            # print self.Bearer[str(request.bearer)]
            # self.payload = str(request.bearer)
            if response.error == 0:
                self.payload = "invalid_request"
            if response.error == 1 or response.active is False:
                self.payload = "invalid_token"
            if response.error == 2:
                self.payload = "insufficient_scope"

            # return self

        # self.payload = "Invalid access"
        return self

        #return temp
        #    return self
        # return self

    def render_PUT(self, request):
        self.edit_resource(request)

        print self.payload
        return self

    def render_POST(self, request):
        print ")))))))))))))))))))))))))))))))))"
        res = self.init_resource(request, BasicResource())
        return res

    def render_DELETE(self, request):
        return True


class Storage(Resource):
    def __init__(self, name="StorageResource", coap_server=None):
        super(Storage, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = "Storage Resource for PUT, POST and DELETE"

    def render_GET(self, request):
        return self

    def render_POST(self, request):
        res = self.init_resource(request, BasicResource())
        return res


class Child(Resource):
    def __init__(self, name="ChildResource", coap_server=None):
        super(Child, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = ""

    def render_GET(self, request):
        return self

    def render_PUT(self, request):
        self.payload = request.payload
        return self

    def render_POST(self, request):
        res = BasicResource()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request):
        return True


class Separate(Resource):

    def __init__(self, name="Separate", coap_server=None):
        super(Separate, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = "Separate"
        self.max_age = 60

    def render_GET(self, request):
        print "GET GET GET"
        return self, self.render_GET_separate

    def render_GET_separate(self, request):
        time.sleep(5)
        return self

    def render_POST(self, request):
        print "POST POST POST"
        return self, self.render_POST_separate

    def render_POST_separate(self, request):
        self.payload = request.payload
        return self

    def render_PUT(self, request):
        return self, self.render_PUT_separate

    def render_PUT_separate(self, request):
        self.payload = request.payload
        return self

    def render_DELETE(self, request):
        return self, self.render_DELETE_separate

    def render_DELETE_separate(self, request):
        return True


class Long(Resource):

    def __init__(self, name="Long", coap_server=None):
        super(Long, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = "Long Time"

    def render_GET(self, request):
        time.sleep(10)
        return self


class Big(Resource):

    def __init__(self, name="Big", coap_server=None):
        super(Big, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
                       "Cras accumsan tellus quis dui lacinia eleifend. Proin ultrices rutrum orci vitae luctus. " \
                       "Nullam malesuada pretium elit, at aliquam odio vehicula in. Etiam nec maximus elit. " \
                       "Etiam at erat ac ex ornare feugiat. Curabitur sed malesuada orci, id aliquet nunc. Phasellus " \
                       "nec leo luctus, blandit lorem sit amet, interdum metus. Duis efficitur volutpat magna, ac " \
                       "ultricies nibh aliquet sit amet. Etiam tempor egestas augue in hendrerit. Nunc eget augue " \
                       "ultricies, dignissim lacus et, vulputate dolor. Nulla eros odio, fringilla vel massa ut, " \
                       "facilisis cursus quam. Fusce faucibus lobortis congue. Fusce consectetur porta neque, id " \
                       "sollicitudin velit maximus eu. Sed pharetra leo quam, vel finibus turpis cursus ac. " \
                       "Aenean ac nisi massa. Cras commodo arcu nec ante tristique ullamcorper. Quisque eu hendrerit" \
                       " urna. Cras fringilla eros ut nunc maximus, non porta nisl mollis. Aliquam in rutrum massa." \
                       " Praesent tristique turpis dui, at ultricies lorem fermentum at. Vivamus sit amet ornare neque, " \
                       "a imperdiet nisl. Quisque a iaculis libero, id tempus lacus. Aenean convallis est non justo " \
                       "consectetur, a hendrerit enim consequat. In accumsan ante a egestas luctus. Etiam quis neque " \
                       "nec eros vestibulum faucibus. Nunc viverra ipsum lectus, vel scelerisque dui dictum a. Ut orci " \
                       "enim, ultrices a ultrices nec, pharetra in quam. Donec accumsan sit amet eros eget fermentum." \
                       "Vivamus ut odio ac odio malesuada accumsan. Aenean vehicula diam at tempus ornare. Phasellus " \
                       "dictum mauris a mi consequat, vitae mattis nulla fringilla. Ut laoreet tellus in nisl efficitur," \
                       " a luctus justo tempus. Fusce finibus libero eget velit finibus iaculis. Morbi rhoncus purus " \
                       "vel vestibulum ullamcorper. Sed ac metus in urna fermentum feugiat. Nulla nunc diam, sodales " \
                       "aliquam mi id, varius porta nisl. Praesent vel nibh ac turpis rutrum laoreet at non odio. " \
                       "Phasellus ut posuere mi. Suspendisse malesuada velit nec mauris convallis porta. Vivamus " \
                       "sed ultrices sapien, at cras amet."

    def render_GET(self, request):
        return self

    def render_POST(self, request):
        if request.payload is not None:
            self.payload = request.payload
        return self


class voidResource(Resource):
    def __init__(self, name="Void"):
        super(voidResource, self).__init__(name)


class XMLResource(Resource):
    def __init__(self, name="XML"):
        super(XMLResource, self).__init__(name)
        self.value = 0
        self.payload = (defines.Content_types["application/xml"], "<value>"+str(self.value)+"</value>")

    def render_GET(self, request):
        return self


class MultipleEncodingResource(Resource):
    def __init__(self, name="MultipleEncoding"):
        super(MultipleEncodingResource, self).__init__(name)
        self.value = 0
        self.payload = str(self.value)
        self.content_type = [defines.Content_types["application/xml"], defines.Content_types["application/json"]]

    def render_GET(self, request):
        if request.accept == defines.Content_types["application/xml"]:
            self.payload = (defines.Content_types["application/xml"],  "<value>"+str(self.value)+"</value>")
        elif request.accept == defines.Content_types["application/json"]:
            self.payload = (defines.Content_types["application/json"], "{'value': '"+str(self.value)+"'}")
        elif request.accept == defines.Content_types["text/plain"]:
            self.payload = (defines.Content_types["text/plain"], str(self.value))
        return self

    def render_PUT(self, request):
        self.edit_resource(request)
        return self

    def render_POST(self, request):
        res = self.init_resource(request, MultipleEncodingResource())
        return res


class ETAGResource(Resource):
    def __init__(self, name="ETag"):
        super(ETAGResource, self).__init__(name)
        self.count = 0
        self.payload = "ETag resource"
        self.etag = str(self.count)

    def render_GET(self, request):
        return self

    def render_POST(self, request):
        self.payload = request.payload
        self.count += 1
        self.etag = str(self.count)
        return self

#
# class BEARERResource(Resource):
#     def __init__(self, name="BEARER"):
#         super(BEARERResource, self).__init__(name)
#         self.count = 0
#         self.payload = "BEARER resource"
#         self.introspection = {}
#
#     def render_GET(self, request):
#
#         for option in request.options:
#             if option.number == defines.OptionRegistry.BEARER.number:
#                 self.introspection[str(option.value)] = db["access_tokens"].find_one({"token": str(option.value)})
#                 # if temp != None:
#                 #     self.introspection = temp
#                 # else:
#                 #     self.introspection = None
#
#         print self.introspection
#         return self
#
#     def render_POST(self, request):
#         self.payload = request.payload
#         self.count += 1
#         self.etag = str(self.count)
#         # self.
#         return self

class BEARERResource(Resource):
    def __init__(self, name="Obs", coap_server=None):
        super(BEARERResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=False)
        self.payload = "Observable Resource"
        self.period = 5

        self.token_address = {}
        # self.token_information ={}
        self.observe_client_list = []
        self.introspection = {}
        self.expired_token_list = []
        # self.Bearer = None
        self.cancel = None
        self.update(True)

    def render_GET(self, request):
        # print defines.OptionRegistry.URI_PATH.number in request.options
        # a =""
        # for option in request.options:
        #     if option.number == defines.OptionRegistry.BEARER.number:
        #         self.access_token[str(option.value)] = request.source
        #         a = str(option.value)
        #         db = pymongo.MongoClient('localhost', 27017).test_database
        #         temp = db["access_tokens"].find_one({"token": str(option.value)})
        #         if temp != None:
        #             self.Bearer = temp
        #         else:
        #             self.Bearer = None
        if request.bearer is not None:
            token_manager.address_registry(self, request) # matching token and client address
            # print "!!!!"
            # print "!!!!"
            # print "!!!!"
            # print "!!!!"
            # print "!!!!"
            # print self.token_address
            # print request.bearer
            token_manager.store_token_information(self, request) # caching current token information


        # print self.access_token['ed1bedae-a186-4301-a15f-20e466db95e9'][0]
        # print self.access_token['ed1bedae-a186-4301-a15f-20e466db95e9']
        # self.access_token['obs'] - >self.access_token[token_value]
        return self

    def render_POST(self, request):
        self.payload = request.payload
        return self

    def update(self, first=False):

        # token_host <- change token's host
        # if 'obs' in self.access_token:
        #     self.payload = self.access_token['obs'][0]+":"+str(self.access_token['obs'][1])
        # self.temp = ('127.0.0.1','49310')
        self.observe_client_list = []
        for token in self.expired_token_list:
            if str(token) in self.introspection:
                del self.introspection[str(token)]
            if str(token) in self.token_address:
                del self.token_address[str(token)]

        print"!!!!"
        print"!!!!"
        print"!!!!"
        print"!!!!"
        print"!!!!"
        print"!!!!"
        print self.expired_token_list
        print "?!?!!?!?"
        print "?!?!!?!?"
        print self.token_address
        print self.introspection
        token_manager.compare_token(self)

        self.payload = None
        # self.payload = str(datetime.datetime.now())
        if not self._coap_server.stopped.isSet():

            timer = threading.Timer(self.period, self.update)
            timer.setDaemon(True)
            timer.start()

            if not first and self._coap_server is not None:
                logger.debug("Periodic Update")

                # print self.token_address
                self._coap_server.notify(self)
                self.observe_count += 1
                # self.observe_client_list = []

                # print self.token_address