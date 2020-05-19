# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, unicode_literals


import warnings

import requests

from kodi_six import xbmc

from queries import _queries_
from iapc import Service, public
from utils import DataCache, getSetting, log


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


class Categories(DataCache):

    _type_ = int
    _key_ = "backendID"
    _missing_ = {"backendID": -1, "title": "", "imgUrl": "", "watchingCount": 0}

    def __init__(self, data):
        super(Categories, self).__init__(data["list"])

    def update(self, data):
        return super(Categories, self).update(data["list"])


# ------------------------------------------------------------------------------
# Session
# ------------------------------------------------------------------------------

class DLiveSession(requests.Session):

    def __init__(self, headers=None):
        super(DLiveSession, self).__init__()
        if headers:
            self.headers.update(headers)

    def request(self, *args, **kwargs):
        response = super(DLiveSession, self).request(*args, **kwargs)
        response.raise_for_status()
        return response


# ------------------------------------------------------------------------------
# Service
# ------------------------------------------------------------------------------

class DLiveService(Service):

    _headers_ = {}

    _query_url_ = "https://graphigo.prd.dlive.tv/"

    def __init__(self, *args, **kwargs):
        super(DLiveService, self).__init__(*args, **kwargs)
        self.session = DLiveSession(headers=self._headers_)
        self._categories_ = Categories(self.query("categories", first=48))

    def setup(self):
        self.first = getSetting("first", int)
        self.showNSFW = getSetting("showNSFW", bool)
        self.userLanguageCode = xbmc.getLanguage(xbmc.ISO_639_1)

    def start(self):
        log("starting service...")
        self.setup()
        self.serve()
        log("service stopped")

    def onSettingsChanged(self):
        self.setup()

    # --------------------------------------------------------------------------

    def query(self, key, _key_=None, **kwargs):
        query, keys = _queries_[key]
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
                warnings.warn(error) # logWarning?
        for key in keys:
            data = data[key]
        if _key_ is not None:
            return [item[_key_] for item in data]
        return data

    # public api ---------------------------------------------------------------

    @public
    def stream(self, **kwargs):
        return self.query("stream", **kwargs)

    @public
    def user(self, **kwargs):
        return self.query("user", first=self.first, **kwargs)

    @public
    def category(self, **kwargs):
        # unfortunately I couldn't find a way to get 1 category from its id
        return self._categories_[kwargs["categoryID"]]

    # --------------------------------------------------------------------------

    @public
    def featured(self, **kwargs):
        return self.query("featured", _key_="item",
                          userLanguageCode=self.userLanguageCode, **kwargs)

    @public
    def recommended(self, **kwargs):
        return self.query("recommended", _key_="user", **kwargs)

    @public
    def streams(self, **kwargs):
        return self.query("streams", first=self.first,
                          showNSFW=self.showNSFW, **kwargs)

    @public
    def categories(self, **kwargs):
        data = self.query("categories", first=self.first, **kwargs)
        self._categories_.update(data)
        return data

    @public
    def search_users(self, **kwargs):
        return self.query("search_users", first=self.first, **kwargs)

    @public
    def search_categories(self, **kwargs):
        data = self.query("search_categories", first=self.first, **kwargs)
        self._categories_.update(data)
        return data


# __main__ ---------------------------------------------------------------------

if __name__ == "__main__":

    DLiveService().start()

