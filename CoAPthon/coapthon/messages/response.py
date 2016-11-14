from coapthon.utils import parse_blockwise
from coapthon import defines
from coapthon.messages.message import Message
from coapthon.messages.option import Option


class Response(Message):
    @property
    def location_path(self):
        """

        :rtype : String
        """
        value = []
        for option in self.options:
            if option.number == defines.OptionRegistry.LOCATION_PATH.number:
                value.append(str(option.value))
        return "/".join(value)

    @location_path.setter
    def location_path(self, path):
        path = path.strip("/")
        tmp = path.split("?")
        path = tmp[0]
        paths = path.split("/")
        for p in paths:
            option = Option()
            option.number = defines.OptionRegistry.LOCATION_PATH.number
            option.value = p
            self.add_option(option)
        # if len(tmp) > 1:
        #     query = tmp[1]
        #     self.location_query = query

    @location_path.deleter
    def location_path(self):
        self.del_option_by_number(defines.OptionRegistry.LOCATION_PATH.number)

    @property
    def location_query(self):
        """

        :rtype : String
        """
        value = []
        for option in self.options:
            if option.number == defines.OptionRegistry.LOCATION_QUERY.number:
                value.append(option.value)
        return value

    @location_query.setter
    def location_query(self, value):
        del self.location_query
        queries = value.split("&")
        for q in queries:
            option = Option()
            option.number = defines.OptionRegistry.LOCATION_QUERY.number
            option.value = str(q)
            self.add_option(option)

    @location_query.deleter
    def location_query(self):
        self.del_option_by_number(defines.OptionRegistry.LOCATION_QUERY.number)

    @property
    def max_age(self):
        """

        :rtype : Integer
        """
        value = defines.OptionRegistry.MAX_AGE.default
        for option in self.options:
            if option.number == defines.OptionRegistry.MAX_AGE.number:
                value = int(option.value)
        return value

    @max_age.setter
    def max_age(self, value):
        option = Option()
        option.number = defines.OptionRegistry.MAX_AGE.number
        option.value = int(value)
        self.add_option(option)

    @max_age.deleter
    def max_age(self):
        self.del_option_by_number(defines.OptionRegistry.MAX_AGE.number)

        #
        #
        #
        #
        # The following code is additional options.

    @property
    def error(self):
        """
        :rtype : Integer
        """
        for option in self.options:
            if option.number == defines.OptionRegistry.ERROR.number:
                return option.value
        return None

    @error.setter
    def error(self, value):
        option = Option()
        option.number = defines.OptionRegistry.ERROR.number
        option.value = int(value)
        self.add_option(option)

    @error.deleter
    def error(self):
        self.del_option_by_number(defines.OptionRegistry.ERROR.number)

    @property
    def active(self):
        """
        :rtype : String
        """
        for option in self.options:
            if option.number == defines.OptionRegistry.ACTIVE.number:
                return option.value
        return None

    @active.setter
    def active(self, value):
        option = Option()
        option.number = defines.OptionRegistry.ACTIVE.number
        option.value = str(value)
        self.add_option(option)

    @active.deleter
    def active(self):
        self.del_option_by_number(defines.OptionRegistry.ACTIVE.number)

    @property
    def exp(self):
        """
        :rtype : Integer
        """
        for option in self.options:
            if option.number == defines.OptionRegistry.EXP.number:
                return option.value
        return None

    @exp.setter
    def exp(self, value):
        option = Option()
        option.number = defines.OptionRegistry.EXP.number
        option.value = int(value)
        self.add_option(option)

    @error.deleter
    def exp(self):
        self.del_option_by_number(defines.OptionRegistry.EXP.number)