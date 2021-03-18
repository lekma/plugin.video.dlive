# -*- coding: utf-8 -*-


from iapc import Client
from iapc.tools import Logger, notify

from .objects import Category, Categories, Streams, User, Users


# ------------------------------------------------------------------------------
# DLiveClient

class DLiveClient(object):

    __live__ = "https://live.prd.dlive.tv/hls/live/{username}.m3u8"

    __classes__ = {
        "stream": User,
        "user": User,
        "category": Category,
        "featured": Streams,
        "recommended": Users,
        "streams": Streams,
        "categories": Categories,
        "search_users": Users,
        "search_categories": Categories
    }

    def __init__(self):
        #self.logger = Logger(component="client")
        self.__client__ = Client()

    def __query__(self, query, list=False, **kwargs):
        data = getattr(self.__client__, query)(**kwargs)
        cls = self.__classes__[query]
        return cls(data["list"], **data["pageInfo"]) if list else cls(data)

    # --------------------------------------------------------------------------

    def stream(self, **kwargs):
        user = self.__query__("stream", **kwargs)
        if not user.livestream:
            return notify(30016, user.displayname) # Offline
        return user.livestream.makeItem(self.__live__.format(**kwargs))

    def user(self, **kwargs):
        after = kwargs.get("after", "-1")
        user = self.__query__("user", **kwargs)
        return (user.livestream if after == "-1" else None, user.pastBroadcasts)

    def category(self, **kwargs):
        streams = self.streams(**kwargs)
        streams.category = self.__query__("category", **kwargs).title
        return streams

    # --------------------------------------------------------------------------

    def featured(self, **kwargs):
        return self.__query__("featured", **kwargs)

    def recommended(self, **kwargs):
        return self.__query__("recommended", **kwargs)

    def streams(self, **kwargs):
        return self.__query__("streams", list=True, **kwargs)

    def categories(self, **kwargs):
        return self.__query__("categories", list=True, **kwargs)

    def search(self, **kwargs):
        return self.__query__(kwargs.pop("query"), list=True, **kwargs)


client = DLiveClient()

