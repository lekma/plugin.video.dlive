# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, unicode_literals


import sys

from six import wraps
from kodi_six import xbmcplugin

from client import client
from objects import Home, Folders, _search_styles_
from utils import parseQuery, getMoreItem, searchDialog, localizedString


def action(category=0):
    def decorator(func):
        func.__action__ = True
        @wraps(func)
        def wrapper(self, **kwargs):
            success = False
            try:
                self.category = category
                self.action = func.__name__
                success = func(self, **kwargs)
            except Exception:
                success = False
                raise
            finally:
                self.endDirectory(success)
                del self.action, self.category
        return wrapper
    return decorator


# ------------------------------------------------------------------------------
# Dispatcher
# ------------------------------------------------------------------------------

class Dispatcher(object):

    def __init__(self, url, handle):
        self.url = url
        self.handle = handle

    # utils --------------------------------------------------------------------

    def addItem(self, item):
        if item and not xbmcplugin.addDirectoryItem(self.handle, *item.asItem()):
            raise
        return True

    def addItems(self, items, *args, **kwargs):
        if not xbmcplugin.addDirectoryItems(
            self.handle, [item.asItem()
                          for item in items.items(self.url, *args) if item]):
            raise
        if items.hasNextPage:
            kwargs["after"] = items.endCursor
            self.addItem(getMoreItem(self.url, action=self.action, **kwargs))
        if items.content:
            xbmcplugin.setContent(self.handle, items.content)
        if items.category:
            self.setCategory(items.category)
        return True

    def setCategory(self, category):
        xbmcplugin.setPluginCategory(self.handle, category)
        self.category = 0

    def endDirectory(self, success):
        if success and self.category:
            self.setCategory(localizedString(self.category))
        xbmcplugin.endOfDirectory(self.handle, success)

    def getSubfolders(self, _type, styles):
        return ({"type": _type, "style": style} for style in styles)

    # actions ------------------------------------------------------------------

    @action()
    def stream(self, **kwargs):
        item = client.stream(**kwargs)
        if not item:
            return False
        xbmcplugin.setResolvedUrl(self.handle, True, item)
        return True

    @action()
    def user(self, **kwargs):
        stream, vods = client.user(**kwargs)
        if stream:
            self.addItem(stream.item(self.url, "stream"))
        return self.addItems(vods, **kwargs)

    @action()
    def category(self, **kwargs):
        return self.addItems(client.category(**kwargs), "stream", **kwargs)

    # --------------------------------------------------------------------------

    @action()
    def home(self, **kwargs):
        return self.addItems(Home())

    @action(30007)
    def featured(self, **kwargs):
        return self.addItems(client.featured(**kwargs), "stream")

    @action(30009)
    def recommended(self, **kwargs):
        return self.addItems(client.recommended(**kwargs), "user")

    @action(30004)
    def streams(self, **kwargs):
        return self.addItems(client.streams(**kwargs), "stream", **kwargs)

    @action(30006)
    def categories(self, **kwargs):
        return self.addItems(client.categories(**kwargs), "category", **kwargs)


    # search -------------------------------------------------------------------

    @action(30002)
    def search(self, **kwargs):
        return self.addItems(
            Folders(self.getSubfolders("search", _search_styles_)))

    @action(30003)
    def search_users(self, **kwargs):
        text = kwargs.pop("text", "") or searchDialog()
        if text:
            return self.addItems(
                client.search_users(text=text, **kwargs),
                "user", text=text, **kwargs)
        return False

    @action(30006)
    def search_categories(self, **kwargs):
        text = kwargs.pop("text", "") or searchDialog()
        if text:
            return self.addItems(
                client.search_categories(text=text, **kwargs),
                "category", text=text, **kwargs)
        return False

    # dispatch -----------------------------------------------------------------

    def dispatch(self, **kwargs):
        action = getattr(self, kwargs.pop("action", "home"))
        if not callable(action) or not getattr(action, "__action__", False):
            raise Exception("Invalid action '{}'".format(action.__name__))
        return action(**kwargs)


# __main__ ---------------------------------------------------------------------

def dispatch(url, handle, query, *args):
    Dispatcher(url, int(handle)).dispatch(**parseQuery(query))


if __name__ == "__main__":

    dispatch(*sys.argv)

