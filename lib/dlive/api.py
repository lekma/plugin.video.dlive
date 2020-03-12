# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, unicode_literals


import warnings

import requests
import m3u8

from . import objects, _queries_
from ..utils import StreamQuality, notify, log


class GraphQLError(Warning):

    _unknown_ = "Unknown error ({})"

    def __init__(self, errors):
        try:
            error = errors[0]
        except IndexError:
            message = self._unknown_.format("empty 'errors' list")
        else:
            if isinstance(error, dict):
                try:
                    message = error["message"]
                except KeyError:
                    message = self._unknown_.format("missing error 'message'")
            else:
                message = str(error)
            if not message:
                message = self._unknown_.format("empty error 'message'")
        super(GraphQLError, self).__init__(message)


class DLiveSession(requests.Session):

    def __init__(self, headers=None):
        super(DLiveSession, self).__init__()
        if headers:
            self.headers.update(headers)

    def request(self, *args, **kwargs):
        response = super(DLiveSession, self).request(*args, **kwargs)
        response.raise_for_status()
        return response


class DLiveService(object):

    _headers_ = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    _query_url_ = "https://graphigo.prd.dlive.tv/"

    _live_url_ = "https://live.prd.dlive.tv/hls/live/{username}.m3u8"

    def __init__(self):
        self.session = DLiveSession(headers=self._headers_)
        self.category_cache = objects.CategoryCache(self._get_categories_(first=64))

    def query(self, query, **kwargs):
        query, keys = _queries_[query]
        json = {"query": query}
        if kwargs:
            json.update(variables=kwargs)
        response = self.session.post(self._query_url_, json=json).json()
        data = response.get("data", None)
        errors = response.get("errors", None)
        if errors is not None:
            error = GraphQLError(errors)
            if data is None:
                raise error
            else:
                warnings.warn(error)
        for key in keys:
            data = data[key]
        return data

    # --------------------------------------------------------------------------

    def _query_stream_(self, **kwargs):
        return self.query("stream", **kwargs)

    def _query_user_(self, **kwargs):
        return self.query("user", **kwargs)

    def _query_streams_(self, **kwargs):
        results = self.query("streams", **kwargs)
        return (results["list"], results["pageInfo"])

    def _query_featured_(self, **kwargs):
        return (result["item"] for result in self.query("featured", **kwargs))

    def _query_recommended_(self, **kwargs):
        return (result["user"] for result in self.query("recommended", **kwargs))

    def _query_categories_(self, **kwargs):
        results = self.query("categories", **kwargs)
        return (results["list"], results["pageInfo"])

    def _search_users_(self, **kwargs):
        results = self.query("search_users", **kwargs)
        return (results["list"], results["pageInfo"])

    def _search_categories_(self, **kwargs):
        results = self.query("search_categories", **kwargs)
        return (results["list"], results["pageInfo"])

    # --------------------------------------------------------------------------

    def _stream_(self, quality=0, **kwargs):
        url = self._live_url_.format(**kwargs)
        if quality and quality < 6: # inputstream.adaptive
            manifest = m3u8.loads(self.session.get(url).text)
            qualities = [StreamQuality(playlist)
                         for playlist in manifest.playlists
                         if playlist.stream_info.resolution]
            qualities.sort(key=lambda x: x.height, reverse=True) # see Quality.best_match
            if quality == 5: # always ask
                selected = StreamQuality.select(qualities)
            else: # set quality
                selected = StreamQuality.best_match(quality, qualities)
            if selected < 0:
                return None
            url = qualities[selected].uri
        return url

    def _get_categories_(self, **kwargs):
        items, pageInfo = self._query_categories_(**kwargs)
        return objects.Categories(items, **pageInfo)

    def _categories_(self, **kwargs):
        categories = self._get_categories_(**kwargs)
        self.category_cache.update(categories)
        return categories

    def _category_(self, categoryID):
        try:
            return self.category_cache[categoryID]
        except KeyError:
            # unfortunately I couldn't find a way to get 1 category from its id
            return objects.EmptyCategory

    # --------------------------------------------------------------------------

    def stream(self, quality=0, **kwargs):
        user = objects.User(self._query_stream_(**kwargs))
        if not user.livestream:
            return notify(30016, user.displayname) # Offline
        url = self._stream_(quality, **kwargs)
        return user.livestream._item(url) if url else None

    def user(self, **kwargs):
        after = kwargs.get("after", "-1")
        user = objects.User(self._query_user_(**kwargs))
        return (user.livestream if after == "-1" else None, user.pastBroadcasts)

    def category(self, **kwargs):
        items, pageInfo = self._query_streams_(**kwargs)
        category = self._category_(kwargs["categoryID"])
        return objects.Livestreams(items, category=category.title, **pageInfo)

    # --------------------------------------------------------------------------

    def featured(self, **kwargs):
        return objects.Livestreams(self._query_featured_(**kwargs))

    def recommended(self, **kwargs):
        return objects.Users(self._query_recommended_(**kwargs))

    def livestreams(self, **kwargs):
        items, pageInfo = self._query_streams_(**kwargs)
        return objects.Livestreams(items, **pageInfo)

    def categories(self, **kwargs):
        return self._categories_(**kwargs)

    def search_users(self, **kwargs):
        items, pageInfo = self._search_users_(**kwargs)
        return objects.Users(items, **pageInfo)

    def search_categories(self, **kwargs):
        items, pageInfo = self._search_categories_(**kwargs)
        return objects.Categories(items, **pageInfo)


service = DLiveService()

