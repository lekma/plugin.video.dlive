# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, unicode_literals


import objects
from utils import notify
from iapc import Client


# ------------------------------------------------------------------------------
# Client
# ------------------------------------------------------------------------------

class DLiveClient(object):

    _live_url_ = "https://live.prd.dlive.tv/hls/live/{username}.m3u8"

    _classes_ = {
        "stream": objects.User,
        "user": objects.User,
        "category": objects.Category,
        "featured": objects.Livestreams,
        "recommended": objects.Users,
        "streams": objects.Livestreams,
        "categories": objects.Categories,
        "search_users": objects.Users,
        "search_categories": objects.Categories
    }

    def __init__(self):
        self.client = Client()

    def query(self, key, _list_=False, **kwargs):
        cls, data = self._classes_[key], getattr(self.client, key)(**kwargs)
        if _list_:
            return cls(data["list"], **data["pageInfo"])
        return cls(data)

    # --------------------------------------------------------------------------

    def query_streams(self, **kwargs):
        return self.query("streams", _list_=True, **kwargs)

    # --------------------------------------------------------------------------

    def stream(self, **kwargs):
        user = self.query("stream", **kwargs)
        if not user.livestream:
            return notify(30016, user.displayname) # Offline
        return user.livestream._item(self._live_url_.format(**kwargs))

    def user(self, **kwargs):
        after = kwargs.get("after", "-1")
        user = self.query("user", **kwargs)
        return (user.livestream if after == "-1" else None, user.pastBroadcasts)

    def category(self, **kwargs):
        streams = self.query_streams(**kwargs)
        streams.category = self.query("category", **kwargs).title
        return streams

    # --------------------------------------------------------------------------

    def featured(self, **kwargs):
        return self.query("featured", **kwargs)

    def recommended(self, **kwargs):
        return self.query("recommended", **kwargs)

    def streams(self, **kwargs):
        return self.query_streams(**kwargs)

    def categories(self, **kwargs):
        return self.query("categories", _list_=True, **kwargs)

    def search_users(self, **kwargs):
        return self.query("search_users", _list_=True, **kwargs)

    def search_categories(self, **kwargs):
        return self.query("search_categories", _list_=True, **kwargs)


client = DLiveClient()

