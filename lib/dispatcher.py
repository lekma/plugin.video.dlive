# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, unicode_literals


from six import wraps
from kodi_six import xbmc, xbmcplugin
from inputstreamhelper import Helper

from .utils import parse_query, get_setting, get_subfolders, more_item
from .utils import localized_string, search_dialog
from .dlive.api import service
from .dlive.objects import Folders, Home


def action(category=0):
    def decorator(func):
        func.__action__ = True
        @wraps(func)
        def wrapper(self, **kwargs):
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


class Dispatcher(object):

    def __init__(self, url, handle):
        self.url = url
        self.handle = handle
        self.limit = get_setting("items_per_page", int)
        self.showNSFW = get_setting("show_nsfw", bool)
        self.language = xbmc.getLanguage(xbmc.ISO_639_1)


    # utils --------------------------------------------------------------------

    def play(self, item, quality=0):
        if quality == 6: # inputstream.adaptive
            if not Helper("hls").check_inputstream():
                return False
            item.setProperty("inputstreamaddon", "inputstream.adaptive")
            item.setProperty("inputstream.adaptive.manifest_type", "hls")
        xbmcplugin.setResolvedUrl(self.handle, True, item)
        return True

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
            self.addItem(more_item(self.url, action=self.action, **kwargs))
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
            self.setCategory(localized_string(self.category))
        xbmcplugin.endOfDirectory(self.handle, success)


    # actions ------------------------------------------------------------------

    @action()
    def stream(self, **kwargs):
        quality = get_setting("stream_quality", int)
        item = service.stream(quality, **kwargs)
        return self.play(item, quality) if item else False

    @action()
    def user(self, **kwargs):
        stream, vods = service.user(first=self.limit, **kwargs)
        if stream:
            self.addItem(stream.item(self.url, "stream"))
        return self.addItems(vods, **kwargs)

    @action()
    def category(self, **kwargs):
        return self.addItems(
            service.category(
                first=self.limit, showNSFW=self.showNSFW, **kwargs),
            "stream", **kwargs)

    # --------------------------------------------------------------------------

    @action()
    def home(self, **kwargs):
        return self.addItems(Home())

    @action(30007)
    def featured(self, **kwargs):
        return self.addItems(
            service.featured(userLanguageCode=self.language, **kwargs),
            "stream")

    @action(30009)
    def recommended(self, **kwargs):
        return self.addItems(service.recommended(**kwargs), "user")

    @action(30004)
    def livestreams(self, **kwargs):
        return self.addItems(
            service.livestreams(
                first=self.limit, showNSFW=self.showNSFW, **kwargs),
            "stream", **kwargs)

    @action(30006)
    def categories(self, **kwargs):
        return self.addItems(
            service.categories(first=self.limit, **kwargs),
            "category", **kwargs)


    # search -------------------------------------------------------------------

    @action(30002)
    def search(self, **kwargs):
        return self.addItems(Folders(get_subfolders("search"), **kwargs))

    @action(30003)
    def search_users(self, **kwargs):
        text = kwargs.pop("text", "") or search_dialog()
        if text:
            return self.addItems(
                service.search_users(text=text, first=self.limit, **kwargs),
                "user", text=text, **kwargs)
        return False # failing here is a bit stupid

    @action(30006)
    def search_categories(self, **kwargs):
        text = kwargs.pop("text", "") or search_dialog()
        if text:
            return self.addItems(
                service.search_categories(text=text, first=self.limit, **kwargs),
                "category", text=text, **kwargs)
        return False # failing here is a bit stupid


    # dispatch -----------------------------------------------------------------

    def dispatch(self, **kwargs):
        action = getattr(self, kwargs.pop("action", "home"))
        if not callable(action) or not getattr(action, "__action__", False):
            raise Exception("Invalid action '{}'".format(action.__name__))
        return action(**kwargs)


def dispatch(url, handle, query, *args):
    Dispatcher(url, int(handle)).dispatch(**parse_query(query))

